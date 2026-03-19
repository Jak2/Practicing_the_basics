# PROJECT REPORT 04
# Social Media Posting Automation System
### Social Media APIs · n8n · Playwright · Scheduling · Analytics

---

**Document Version:** 1.0.0
**Classification:** Technical Design & Implementation Report
**Prepared By:** Senior Systems Architect
**Date:** 2026-03-20
**Status:** Ready for Implementation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Requirements](#system-requirements)
3. [Architecture Overview](#architecture-overview)
4. [Platform API Coverage](#platform-api-coverage)
5. [Environment Setup & Configuration](#environment-setup--configuration)
6. [Step-by-Step Implementation](#step-by-step-implementation)
7. [Browser Automation Fallback](#browser-automation-fallback)
8. [Scheduling & Queue Management](#scheduling--queue-management)
9. [Analytics & Performance Tracking](#analytics--performance-tracking)
10. [Rate Limiting & Anti-Detection](#rate-limiting--anti-detection)
11. [Testing & Validation](#testing--validation)

---

## 1. Executive Summary

The Social Media Posting Automation System is the final stage of the AI influencer pipeline. It receives a completed video file and its metadata (caption, hashtags, platform targets) from the upstream Video Production Pipeline (Report 03) and distributes the content across multiple social platforms automatically, on a defined posting schedule.

The system operates on two tiers:

**Tier 1 — Official API Integration:**
Platforms that provide usable APIs for automated posting are handled via direct REST API calls. This includes X (Twitter), YouTube, and Facebook/Instagram via the Meta Graph API.

**Tier 2 — Browser Automation Fallback:**
Platforms with restrictive or unavailable APIs for video posting (notably TikTok's direct upload restrictions) are handled via **Playwright** headless browser automation, which simulates a human user logging in and uploading the content.

All posting jobs are managed through an **n8n workflow** with built-in scheduling, retry logic, error alerting, and a performance analytics feedback loop.

---

## 2. System Requirements

### 2.1 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4-core | 8-core |
| RAM | 8 GB | 16 GB |
| Storage | 20 GB SSD | 100 GB SSD |
| OS | Ubuntu 22.04 | Ubuntu 22.04 LTS |
| Network | 100 Mbps | 1 Gbps (video uploads are large) |

### 2.2 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11.x | Publisher service runtime |
| Docker | 26.x | Container isolation |
| n8n | Latest | Workflow orchestration & scheduling |
| PostgreSQL | 15.x | Job queue, posting history, analytics |
| Redis | 7.x | Rate limit tracking & job deduplication |
| Playwright | 1.44.x | Browser automation for TikTok |
| Chromium | Latest | Headless browser (installed by Playwright) |

### 2.3 Python Package Dependencies

```
fastapi>=0.111.0
uvicorn>=0.30.0
pydantic>=2.7.0
httpx>=0.27.0
playwright>=1.44.0
google-auth>=2.29.0
google-auth-oauthlib>=1.2.0
google-api-python-client>=2.130.0
tweepy>=4.14.0
requests>=2.31.0
python-dotenv>=1.0.0
apscheduler>=3.10.4
redis>=5.0.0
asyncpg>=0.29.0
structlog>=24.2.0
prometheus-client>=0.20.0
```

### 2.4 Platform API Credentials Required

| Platform | Credential Type | Where to Get |
|----------|----------------|-------------|
| X (Twitter) | OAuth 2.0 (User Context) | developer.twitter.com |
| YouTube | OAuth 2.0 + Service Account | console.cloud.google.com |
| Instagram | Meta Graph API Token | developers.facebook.com |
| Facebook | Meta Graph API Token | developers.facebook.com |
| TikTok | Session cookies (browser auth) | Extracted via Playwright login |

---

## 3. Architecture Overview

### 3.1 System Diagram

```
                   +--------------------------------+
                   |   Video Production Pipeline    |
                   |         (Report 03)            |
                   +---------------+----------------+
                                   |
                           POST /publish
                    {video_path, caption, hashtags,
                     platforms, scheduled_time}
                                   |
                                   v
+------------------------------------------------------------------+
|                     PUBLISHER SERVICE (FastAPI)                  |
|                                                                  |
|  +--------------------------+    +---------------------------+   |
|  |    Job Queue Manager     |    |    Platform Router        |   |
|  |    (PostgreSQL + Redis)  |    |                           |   |
|  +-----------+--------------+    |  [x_publisher]            |   |
|              |                   |  [youtube_publisher]      |   |
|              v                   |  [instagram_publisher]    |   |
|  +-----------+--------------+    |  [facebook_publisher]     |   |
|  |   Scheduler (APScheduler)|    |  [tiktok_playwright]      |   |
|  |   - Checks queue         |    +---------------------------+   |
|  |   - Fires at exact time  |                                    |
|  +---------------------------+                                   |
+------------------------------------------------------------------+
              |                          |
    +---------+---------+       +--------+---------+
    | Official APIs     |       | Browser Automation|
    |                   |       |  (Playwright)     |
    | Twitter v2 API    |       |                   |
    | YouTube Data v3   |       | TikTok upload     |
    | Meta Graph API    |       | (headless Chrome) |
    +-------------------+       +------------------+
              |
              v
    +------------------+
    |  Analytics Loop  |
    |  (fetch metrics  |
    |  after 24h/7d)   |
    +------------------+
              |
              v
    +------------------+
    |  n8n Dashboard   |
    |  (success/fail   |
    |  alerts + stats) |
    +------------------+
```

### 3.2 Job State Machine

```
CREATED
  |
  v
SCHEDULED  (waiting for scheduled_time)
  |
  v
PROCESSING  (actively uploading to platform)
  |
  v
[conditional]
  |-- SUCCESS --> PUBLISHED --> [analytics fetch after 24h]
  |-- FAILURE --> RETRYING  --> [up to 3 retries with exponential backoff]
                      |
                      v
                   FAILED  (alert sent to n8n webhook)
```

---

## 4. Platform API Coverage

### 4.1 X (Twitter) — Tweepy + Twitter API v2

**Posting method:** Media upload v1.1 (for video) + Tweets v2 (for tweet creation)
**Video limit:** 512 MB, max 2:20 duration, MP4 H.264
**Rate limits:** 1,500 tweets/month on Basic ($100/mo), 17 tweets/day on Free tier

```python
# publishers/x_publisher.py
import tweepy
import time
import structlog
from pathlib import Path

log = structlog.get_logger()

class XPublisher:
    def __init__(self, bearer_token: str, api_key: str, api_secret: str,
                 access_token: str, access_secret: str):
        # v1.1 client for media upload (v2 doesn't support video upload yet)
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)

        # v2 client for tweet creation
        self.client_v2 = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key, consumer_secret=api_secret,
            access_token=access_token, access_token_secret=access_secret
        )

    def publish(self, video_path: str, caption: str, hashtags: list[str]) -> dict:
        hashtag_str = " ".join(f"#{h.lstrip('#')}" for h in hashtags[:5])
        full_caption = f"{caption}\n\n{hashtag_str}"[:280]

        log.info("x.upload.start", path=video_path)

        # Step 1: Upload video via chunked media upload
        media = self.api_v1.media_upload(
            filename=video_path,
            media_category="tweet_video",
            chunked=True
        )
        media_id = media.media_id

        # Step 2: Wait for processing
        self._wait_for_media_processing(media_id)

        # Step 3: Create tweet with media
        response = self.client_v2.create_tweet(
            text=full_caption,
            media_ids=[str(media_id)]
        )

        tweet_id = response.data["id"]
        log.info("x.publish.success", tweet_id=tweet_id)
        return {"platform": "x", "post_id": tweet_id,
                "url": f"https://x.com/i/web/status/{tweet_id}"}

    def _wait_for_media_processing(self, media_id: int, timeout: int = 300):
        start = time.time()
        while time.time() - start < timeout:
            status = self.api_v1.get_media_upload_status(media_id)
            state = status.processing_info.get("state") if hasattr(status, "processing_info") else "succeeded"

            if state == "succeeded":
                return
            elif state == "failed":
                raise RuntimeError(f"Twitter media processing failed: {status.processing_info}")

            wait = status.processing_info.get("check_after_secs", 5)
            time.sleep(wait)

        raise TimeoutError("Twitter media upload processing timed out")
```

### 4.2 YouTube — Google API Python Client

**Posting method:** YouTube Data API v3 `videos.insert`
**Video format:** MP4 H.264, any resolution up to 4K
**Quota:** 10,000 units/day; video insert costs 1,600 units (~6 uploads/day on free quota)

```python
# publishers/youtube_publisher.py
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import structlog

log = structlog.get_logger()

class YouTubePublisher:
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(self, credentials_json_path: str):
        creds = Credentials.from_authorized_user_file(credentials_json_path, self.SCOPES)
        self.youtube = build("youtube", "v3", credentials=creds)

    def publish(self, video_path: str, title: str, description: str,
                hashtags: list[str], category_id: str = "28") -> dict:
        """category_id 28 = Science & Technology"""
        hash_str = " ".join(f"#{h.lstrip('#')}" for h in hashtags[:15])
        full_description = f"{description}\n\n{hash_str}\n\n#Shorts"

        body = {
            "snippet": {
                "title": title[:100],
                "description": full_description[:5000],
                "tags": hashtags[:500],
                "categoryId": category_id,
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
                "madeForKids": False
            }
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=10 * 1024 * 1024  # 10 MB chunks
        )

        log.info("youtube.upload.start", path=video_path)
        request = self.youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                log.info("youtube.upload.progress", pct=int(status.progress() * 100))

        video_id = response["id"]
        log.info("youtube.publish.success", video_id=video_id)
        return {"platform": "youtube", "post_id": video_id,
                "url": f"https://youtube.com/shorts/{video_id}"}
```

### 4.3 Instagram Reels — Meta Graph API

**Posting method:** Two-step process: create container → publish container
**Requirements:** Instagram Business or Creator account linked to a Facebook Page
**Video limit:** MP4, 9:16, 3-90 seconds, < 1 GB

```python
# publishers/instagram_publisher.py
import httpx
import time
import structlog

log = structlog.get_logger()
GRAPH_URL = "https://graph.facebook.com/v20.0"

class InstagramPublisher:
    def __init__(self, access_token: str, instagram_account_id: str):
        self.token = access_token
        self.account_id = instagram_account_id

    def publish(self, video_url: str, caption: str, hashtags: list[str]) -> dict:
        """
        video_url must be a publicly accessible URL (not a local file path).
        Upload your video to S3/Cloudflare R2 first.
        """
        hash_str = " ".join(f"#{h.lstrip('#')}" for h in hashtags[:30])
        full_caption = f"{caption}\n\n{hash_str}"

        # Step 1: Create media container
        log.info("instagram.container.create")
        container_resp = httpx.post(
            f"{GRAPH_URL}/{self.account_id}/media",
            params={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": full_caption,
                "share_to_feed": "true",
                "access_token": self.token
            }
        )
        container_resp.raise_for_status()
        container_id = container_resp.json()["id"]

        # Step 2: Wait for container to be ready
        self._wait_for_container(container_id)

        # Step 3: Publish the container
        log.info("instagram.container.publish", container_id=container_id)
        publish_resp = httpx.post(
            f"{GRAPH_URL}/{self.account_id}/media_publish",
            params={"creation_id": container_id, "access_token": self.token}
        )
        publish_resp.raise_for_status()
        media_id = publish_resp.json()["id"]

        log.info("instagram.publish.success", media_id=media_id)
        return {"platform": "instagram", "post_id": media_id}

    def _wait_for_container(self, container_id: str, timeout: int = 600):
        start = time.time()
        while time.time() - start < timeout:
            status_resp = httpx.get(
                f"{GRAPH_URL}/{container_id}",
                params={"fields": "status_code,status", "access_token": self.token}
            )
            data = status_resp.json()
            status_code = data.get("status_code")

            if status_code == "FINISHED":
                return
            elif status_code == "ERROR":
                raise RuntimeError(f"Instagram container failed: {data}")

            log.info("instagram.container.waiting", status=status_code)
            time.sleep(15)

        raise TimeoutError("Instagram container processing timed out")
```

---

## 5. Environment Setup & Configuration

### 5.1 Project Directory Structure

```
publisher-service/
+-- docker-compose.yml
+-- .env
+-- requirements.txt
+-- src/
|   +-- main.py
|   +-- publishers/
|   |   +-- x_publisher.py
|   |   +-- youtube_publisher.py
|   |   +-- instagram_publisher.py
|   |   +-- facebook_publisher.py
|   |   +-- tiktok_playwright.py
|   +-- queue/
|   |   +-- job_manager.py
|   |   +-- scheduler.py
|   +-- analytics/
|   |   +-- metrics_fetcher.py
|   |   +-- dashboard.py
|   +-- config/
|       +-- settings.py
+-- credentials/
|   +-- youtube_token.json         # OAuth token (gitignored)
|   +-- google_client_secret.json  # OAuth client (gitignored)
+-- playwright_state/
    +-- tiktok_state.json          # Saved browser auth state (gitignored)
```

### 5.2 Environment Variables

```env
# .env

# Database
DATABASE_URL=postgresql://publisher:password@postgres:5432/publisher_db
REDIS_URL=redis://:password@redis:6379/0

# X (Twitter)
X_BEARER_TOKEN=<your-bearer-token>
X_API_KEY=<your-api-key>
X_API_SECRET=<your-api-secret>
X_ACCESS_TOKEN=<your-access-token>
X_ACCESS_SECRET=<your-access-secret>

# YouTube
YOUTUBE_CREDENTIALS_PATH=/app/credentials/youtube_token.json

# Instagram & Facebook (Meta Graph API)
META_ACCESS_TOKEN=<your-long-lived-access-token>
INSTAGRAM_ACCOUNT_ID=<your-ig-account-id>
FACEBOOK_PAGE_ID=<your-fb-page-id>

# Video CDN (for Instagram - must be public URL)
CDN_BASE_URL=https://your-r2-bucket.r2.dev

# Application
LOG_LEVEL=INFO
DEFAULT_POST_TIMES=08:00,12:00,18:00  # UTC posting schedule
N8N_ALERT_WEBHOOK=http://n8n:5678/webhook/publish-alerts
```

### 5.3 Database Schema

```sql
-- publishing_jobs table
CREATE TABLE publishing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_path TEXT NOT NULL,
    caption TEXT NOT NULL,
    hashtags TEXT[] NOT NULL,
    platforms TEXT[] NOT NULL,
    scheduled_time TIMESTAMPTZ NOT NULL,
    status TEXT DEFAULT 'scheduled',  -- scheduled|processing|published|failed|retrying
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    error_message TEXT
);

-- platform_posts table (one row per platform per job)
CREATE TABLE platform_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES publishing_jobs(id),
    platform TEXT NOT NULL,       -- x|youtube|instagram|facebook|tiktok
    post_id TEXT,                 -- Platform's returned post/video ID
    post_url TEXT,
    status TEXT DEFAULT 'pending',
    published_at TIMESTAMPTZ,
    error_message TEXT
);

-- post_analytics table (filled by analytics fetcher after 24h and 7d)
CREATE TABLE post_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_post_id UUID REFERENCES platform_posts(id),
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    views BIGINT DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    follows_gained INTEGER DEFAULT 0,
    reach BIGINT DEFAULT 0
);
```

---

## 6. Step-by-Step Implementation

### Step 1 — Job Manager

```python
# src/queue/job_manager.py
import uuid
from datetime import datetime, timezone
from typing import Optional
import asyncpg
import structlog

log = structlog.get_logger()

class JobManager:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db = db_pool

    async def create_job(
        self,
        video_path: str,
        caption: str,
        hashtags: list[str],
        platforms: list[str],
        scheduled_time: datetime
    ) -> str:
        job_id = str(uuid.uuid4())
        await self.db.execute(
            """INSERT INTO publishing_jobs
               (id, video_path, caption, hashtags, platforms, scheduled_time)
               VALUES ($1, $2, $3, $4, $5, $6)""",
            job_id, video_path, caption, hashtags, platforms, scheduled_time
        )
        log.info("job.created", job_id=job_id, platforms=platforms,
                 scheduled_time=scheduled_time.isoformat())
        return job_id

    async def get_due_jobs(self) -> list[dict]:
        """Fetch all jobs scheduled for now or earlier that are not yet processed."""
        rows = await self.db.fetch(
            """SELECT * FROM publishing_jobs
               WHERE status = 'scheduled'
               AND scheduled_time <= NOW()
               ORDER BY scheduled_time ASC
               LIMIT 10"""
        )
        return [dict(row) for row in rows]

    async def mark_processing(self, job_id: str):
        await self.db.execute(
            "UPDATE publishing_jobs SET status='processing' WHERE id=$1", job_id
        )

    async def mark_published(self, job_id: str):
        await self.db.execute(
            "UPDATE publishing_jobs SET status='published', published_at=NOW() WHERE id=$1",
            job_id
        )

    async def mark_failed(self, job_id: str, error: str, retry: bool = True):
        if retry:
            await self.db.execute(
                """UPDATE publishing_jobs
                   SET status='retrying', retry_count=retry_count+1, error_message=$2
                   WHERE id=$1 AND retry_count < 3""",
                job_id, error
            )
        else:
            await self.db.execute(
                "UPDATE publishing_jobs SET status='failed', error_message=$2 WHERE id=$1",
                job_id, error
            )

    async def save_platform_post(self, job_id: str, platform: str,
                                  post_id: str, post_url: Optional[str]):
        await self.db.execute(
            """INSERT INTO platform_posts (job_id, platform, post_id, post_url, status, published_at)
               VALUES ($1, $2, $3, $4, 'published', NOW())""",
            job_id, platform, post_id, post_url
        )
```

### Step 2 — Scheduler

```python
# src/queue/scheduler.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.queue.job_manager import JobManager
from src.publishers.router import PublisherRouter
import httpx
import os
import structlog

log = structlog.get_logger()
N8N_WEBHOOK = os.getenv("N8N_ALERT_WEBHOOK")

class PublishScheduler:
    def __init__(self, job_manager: JobManager, router: PublisherRouter):
        self.job_manager = job_manager
        self.router = router
        self.scheduler = AsyncIOScheduler()

    def start(self):
        # Check for due jobs every 60 seconds
        self.scheduler.add_job(self._process_due_jobs, "interval", seconds=60)
        self.scheduler.start()
        log.info("scheduler.started")

    async def _process_due_jobs(self):
        due_jobs = await self.job_manager.get_due_jobs()
        if not due_jobs:
            return

        log.info("scheduler.found_jobs", count=len(due_jobs))
        tasks = [self._execute_job(job) for job in due_jobs]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_job(self, job: dict):
        job_id = str(job["id"])
        await self.job_manager.mark_processing(job_id)

        results = []
        errors = []

        for platform in job["platforms"]:
            try:
                result = await self.router.publish(
                    platform=platform,
                    video_path=job["video_path"],
                    caption=job["caption"],
                    hashtags=job["hashtags"]
                )
                await self.job_manager.save_platform_post(
                    job_id, platform, result["post_id"], result.get("url")
                )
                results.append(result)
                log.info("job.platform.success", job_id=job_id, platform=platform)
            except Exception as e:
                log.error("job.platform.failed", job_id=job_id, platform=platform, error=str(e))
                errors.append({"platform": platform, "error": str(e)})

        if errors:
            await self.job_manager.mark_failed(job_id, str(errors), retry=len(results) == 0)
            await self._alert_n8n(job_id, errors)
        else:
            await self.job_manager.mark_published(job_id)

    async def _alert_n8n(self, job_id: str, errors: list):
        if not N8N_WEBHOOK:
            return
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(N8N_WEBHOOK, json={"job_id": job_id, "errors": errors})
        except Exception:
            pass  # Don't let alert failure crash the pipeline
```

### Step 3 — Publisher Router

```python
# src/publishers/router.py
from src.publishers.x_publisher import XPublisher
from src.publishers.youtube_publisher import YouTubePublisher
from src.publishers.instagram_publisher import InstagramPublisher
from src.publishers.tiktok_playwright import TikTokPlaywrightPublisher
from src.config.settings import settings

class PublisherRouter:
    def __init__(self):
        self._publishers = {
            "x": XPublisher(
                bearer_token=settings.X_BEARER_TOKEN,
                api_key=settings.X_API_KEY,
                api_secret=settings.X_API_SECRET,
                access_token=settings.X_ACCESS_TOKEN,
                access_secret=settings.X_ACCESS_SECRET
            ),
            "youtube": YouTubePublisher(settings.YOUTUBE_CREDENTIALS_PATH),
            "instagram": InstagramPublisher(settings.META_ACCESS_TOKEN,
                                            settings.INSTAGRAM_ACCOUNT_ID),
            "tiktok": TikTokPlaywrightPublisher()
        }

    async def publish(self, platform: str, video_path: str,
                      caption: str, hashtags: list[str]) -> dict:
        publisher = self._publishers.get(platform)
        if not publisher:
            raise ValueError(f"No publisher configured for platform: {platform}")

        # Run sync publishers in thread pool to avoid blocking
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, publisher.publish, video_path, caption, hashtags
        )
```

### Step 4 — FastAPI Entry Point

```python
# src/main.py
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncpg

from src.queue.job_manager import JobManager
from src.queue.scheduler import PublishScheduler
from src.publishers.router import PublisherRouter
from src.config.settings import settings

db_pool = None
job_manager = None
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, job_manager, scheduler
    db_pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=2, max_size=10)
    job_manager = JobManager(db_pool)
    router = PublisherRouter()
    scheduler = PublishScheduler(job_manager, router)
    scheduler.start()
    yield
    await db_pool.close()

app = FastAPI(title="Social Media Publisher Service", lifespan=lifespan)

class PublishRequest(BaseModel):
    video_path: str
    caption: str
    hashtags: list[str]
    platforms: list[str]
    scheduled_time: Optional[datetime] = None

@app.post("/publish")
async def publish(request: PublishRequest):
    scheduled_time = request.scheduled_time or datetime.now(timezone.utc)
    job_id = await job_manager.create_job(
        video_path=request.video_path,
        caption=request.caption,
        hashtags=request.hashtags,
        platforms=request.platforms,
        scheduled_time=scheduled_time
    )
    return {"job_id": job_id, "scheduled_time": scheduled_time.isoformat()}

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    row = await db_pool.fetchrow(
        "SELECT * FROM publishing_jobs WHERE id=$1", job_id
    )
    if not row:
        raise HTTPException(404, "Job not found")
    return dict(row)

@app.get("/analytics/{job_id}")
async def get_analytics(job_id: str):
    rows = await db_pool.fetch(
        """SELECT pp.platform, pa.*
           FROM platform_posts pp
           LEFT JOIN post_analytics pa ON pa.platform_post_id = pp.id
           WHERE pp.job_id = $1""",
        job_id
    )
    return [dict(r) for r in rows]
```

---

## 7. Browser Automation Fallback

### TikTok Publisher via Playwright

TikTok does not provide a public API for automated video uploads for most accounts. The standard industry approach is Playwright-driven browser automation.

```python
# src/publishers/tiktok_playwright.py
from playwright.sync_api import sync_playwright, BrowserContext
from pathlib import Path
import time
import structlog

log = structlog.get_logger()
AUTH_STATE_PATH = "playwright_state/tiktok_state.json"

class TikTokPlaywrightPublisher:
    """
    Uploads video to TikTok using Playwright browser automation.

    IMPORTANT: First-time setup requires running save_auth_state() interactively
    to log in manually and persist the session cookies.
    """

    def save_auth_state(self):
        """Run this ONCE manually to log in and save session state."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Visible browser for manual login
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.tiktok.com/login")
            input("Log in manually, then press ENTER to save session state...")
            Path(AUTH_STATE_PATH).parent.mkdir(exist_ok=True)
            context.storage_state(path=AUTH_STATE_PATH)
            browser.close()
            log.info("tiktok.auth_state.saved")

    def publish(self, video_path: str, caption: str, hashtags: list[str]) -> dict:
        """Upload video to TikTok using saved browser session."""
        hash_str = " ".join(f"#{h.lstrip('#')}" for h in hashtags[:20])
        full_caption = f"{caption} {hash_str}"[:2200]

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context(storage_state=AUTH_STATE_PATH)
            page = context.new_page()

            try:
                log.info("tiktok.upload.start")

                # Navigate to upload page
                page.goto("https://www.tiktok.com/upload?lang=en", wait_until="networkidle")
                page.wait_for_selector("input[type='file']", timeout=30000)

                # Upload video file
                page.set_input_files("input[type='file']", video_path)
                page.wait_for_selector(".upload-progress-percent", timeout=120000)
                page.wait_for_function(
                    "document.querySelector('.upload-progress-percent')?.textContent === '100%'",
                    timeout=300000
                )

                # Fill caption
                caption_box = page.locator("div[contenteditable='true']").first
                caption_box.click()
                caption_box.fill(full_caption)

                # Wait for upload to complete processing
                time.sleep(5)

                # Click Post button
                post_btn = page.locator("button:has-text('Post')")
                post_btn.click()
                page.wait_for_url("**/profile**", timeout=60000)

                log.info("tiktok.upload.success")
                # TikTok doesn't return a video ID via browser automation easily
                return {"platform": "tiktok", "post_id": f"tiktok_{int(time.time())}"}

            except Exception as e:
                page.screenshot(path=f"tmp/tiktok_error_{int(time.time())}.png")
                raise RuntimeError(f"TikTok upload failed: {e}")
            finally:
                browser.close()
```

---

## 8. Scheduling & Queue Management

### Optimal Posting Schedule (by Platform)

| Platform | Best Times (UTC) | Frequency |
|----------|-----------------|-----------|
| TikTok | 12:00, 15:00, 21:00 | 1-3x daily |
| Instagram Reels | 08:00, 12:00, 19:00 | 1-2x daily |
| YouTube Shorts | 14:00, 17:00 | 1x daily |
| X (Twitter) | 09:00, 15:00, 21:00 | 1-3x daily |

### n8n Workflow for Scheduled Publishing

```json
{
  "name": "Daily Content Publisher",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": { "interval": [{"field": "cronExpression", "expression": "0 8,12,18 * * *"}] }
      }
    },
    {
      "name": "Fetch Next Job",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://publisher-service:8000/jobs/next",
        "method": "GET"
      }
    },
    {
      "name": "Trigger Publish",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://publisher-service:8000/publish",
        "method": "POST",
        "sendBody": true,
        "bodyParameters": { "value": "={{ $json }}" }
      }
    }
  ]
}
```

---

## 9. Analytics & Performance Tracking

### Analytics Fetcher (runs 24h and 7d after publish)

```python
# src/analytics/metrics_fetcher.py
import tweepy
import httpx
from src.config.settings import settings

class AnalyticsFetcher:

    def fetch_x_metrics(self, tweet_id: str) -> dict:
        client = tweepy.Client(bearer_token=settings.X_BEARER_TOKEN)
        tweet = client.get_tweet(
            tweet_id,
            tweet_fields=["public_metrics", "non_public_metrics"],
            user_auth=True
        )
        m = tweet.data.public_metrics
        return {
            "views": m.get("impression_count", 0),
            "likes": m.get("like_count", 0),
            "comments": m.get("reply_count", 0),
            "shares": m.get("retweet_count", 0)
        }

    def fetch_instagram_metrics(self, media_id: str) -> dict:
        resp = httpx.get(
            f"https://graph.facebook.com/v20.0/{media_id}/insights",
            params={
                "metric": "reach,plays,likes,comments,shares",
                "access_token": settings.META_ACCESS_TOKEN
            }
        )
        data = {item["name"]: item["values"][0]["value"] for item in resp.json()["data"]}
        return {
            "views": data.get("plays", 0),
            "reach": data.get("reach", 0),
            "likes": data.get("likes", 0),
            "comments": data.get("comments", 0),
            "shares": data.get("shares", 0)
        }

    def fetch_youtube_metrics(self, video_id: str) -> dict:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(settings.YOUTUBE_CREDENTIALS_PATH)
        youtube = build("youtube", "v3", credentials=creds)

        response = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()

        stats = response["items"][0]["statistics"]
        return {
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0))
        }
```

---

## 10. Rate Limiting & Anti-Detection

### Rate Limit Tracker (Redis)

```python
# src/queue/rate_limiter.py
import redis
import time

class RateLimiter:
    LIMITS = {
        "x": {"calls": 17, "window": 86400},          # 17 posts/day (free tier)
        "youtube": {"calls": 6, "window": 86400},      # 6 uploads/day (quota)
        "instagram": {"calls": 50, "window": 3600},    # 50 posts/hour
        "tiktok": {"calls": 5, "window": 86400},       # Conservative: 5/day
    }

    def __init__(self, redis_client: redis.Redis):
        self.r = redis_client

    def is_allowed(self, platform: str) -> bool:
        limit = self.LIMITS.get(platform)
        if not limit:
            return True

        key = f"rate_limit:{platform}:{int(time.time() // limit['window'])}"
        current = self.r.incr(key)
        if current == 1:
            self.r.expire(key, limit["window"])

        return current <= limit["calls"]
```

### Anti-Detection Best Practices for Playwright

| Technique | Implementation |
|-----------|---------------|
| Realistic viewport | `viewport={"width": 1366, "height": 768}` |
| User agent rotation | Use realistic Chrome UA strings |
| Random delays | `time.sleep(random.uniform(1.5, 4.0))` between actions |
| Mouse movement simulation | `page.mouse.move()` with random offsets before clicks |
| Persistent cookies | Always use `storage_state` (saved auth) |
| Avoid VPN/proxy on upload | Upload from stable residential IP |
| One account per browser profile | Never share cookies between accounts |

---

## 11. Testing & Validation

### End-to-End Test

```bash
# Submit a test publish job
curl -X POST http://localhost:8001/publish \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/output/test_video.mp4",
    "caption": "Testing our AI influencer pipeline!",
    "hashtags": ["AI", "Tech", "Innovation"],
    "platforms": ["x"],
    "scheduled_time": null
  }'

# Response: { "job_id": "abc-123", "scheduled_time": "2026-03-20T08:00:00Z" }

# Check job status
curl http://localhost:8001/jobs/abc-123

# Check analytics (after 24h)
curl http://localhost:8001/analytics/abc-123
```

### Smoke Test Checklist

- [ ] X: Test tweet with video appears on profile
- [ ] YouTube: Short appears in Shorts tab with correct title/description
- [ ] Instagram: Reel appears on profile with hashtags
- [ ] TikTok: Video uploaded, visible after ~5 min processing
- [ ] n8n: Alert webhook fires on failure
- [ ] Analytics: Metrics fetched and stored in `post_analytics` table after 24h
- [ ] Rate limiter: Rejects calls exceeding platform limits
- [ ] Retry logic: Failed jobs retry 3 times with exponential backoff

---

*End of Report 04 — Social Media Posting Automation System*
