import sys
from datetime import datetime, UTC
from core.config import get_config
from core.manifest import append_post
from core.models import PostEntry
from core.run_log import (
    new_run, new_step, finish_step, finish_run, append_run,
    StepLog,
)
from agents.trend_discovery import TrendDiscovery
from agents.content_generator import ContentGenerator
from agents.image_generator import ImageGenerator
from agents.git_publisher import GitPublisher

DEFAULT_MANIFEST = "manifest.json"
DEFAULT_RUN_LOG = "run_log.json"


class Orchestrator:
    def __init__(
        self,
        config_path: str = "config.yaml",
        manifest_path: str = DEFAULT_MANIFEST,
        run_log_path: str = DEFAULT_RUN_LOG,
    ):
        self.config = get_config(config_path)
        self.manifest_path = manifest_path
        self.run_log_path = run_log_path
        self.trend = TrendDiscovery(self.config)
        self.content = ContentGenerator(self.config)
        self.image = ImageGenerator(self.config) if self.config.llm.provider == "google" else None
        self.git = GitPublisher(self.config)

    def run(self, n_topics: int, n_prompts: int, n_workflows: int, categories: list[str], draft: bool = False) -> None:
        run = new_run()
        overall_status = "success"

        # ── Step 1: Trend Discovery ──────────────────────────────────────
        td_step = new_step("trend_discovery", "TrendDiscovery.run()", "agents/trend_discovery.py")
        try:
            topics, source_results = self.trend.run(categories, n_topics)
            for src, data in source_results.items():
                child = new_step(f"fetch_{src}", f"_fetch_{src}()", "agents/trend_discovery.py")
                if data["skipped"]:
                    finish_step(child, "skipped", detail="disabled in config.yaml")
                elif data["error"]:
                    finish_step(child, "failed", error=data["error"])
                    overall_status = "partial"
                else:
                    finish_step(child, "success", detail=f"{data['count']} topic(s) returned")
                td_step.children.append(child)
            finish_step(td_step, "success", detail=f"{len(topics)} topic(s) fetched")
        except Exception as e:
            topics = []
            finish_step(td_step, "failed", error=str(e))
            overall_status = "partial"
        run.steps.append(td_step)

        # ── Steps 2-4: Generate + publish per topic ──────────────────────
        for topic in topics:
            for _ in range(n_prompts):
                step = self._logged_generate(topic, "prompt", draft)
                if step.status == "failed":
                    overall_status = "partial"
                run.steps.append(step)
            for _ in range(n_workflows):
                step = self._logged_generate(topic, "workflow", draft)
                if step.status == "failed":
                    overall_status = "partial"
                run.steps.append(step)

        finish_run(run, overall_status)
        append_run(run, self.run_log_path)

    def _logged_generate(self, topic, post_type: str, draft: bool = False) -> StepLog:
        short_title = topic.title[:40] + ("…" if len(topic.title) > 40 else "")
        parent = new_step(
            f"gen_{post_type}",
            f'_generate_and_publish("{short_title}", {post_type})',
            "agents/orchestrator.py",
        )

        # ── Content generation ───────────────────────────────────────────
        cg = new_step("content_gen", "ContentGenerator.run()", "agents/content_generator.py")
        try:
            slug, content = self.content.run(topic, post_type)
            finish_step(cg, "success", detail=f"slug: {slug}")
        except Exception as e:
            finish_step(cg, "failed", error=str(e))
            parent.children.append(cg)
            print(f"[ContentPilot] content gen failed for '{topic.title}': {e}", file=sys.stderr)
            return finish_step(parent, "failed", error="content generation failed")
        parent.children.append(cg)

        # ── Image generation (prompts only) ──────────────────────────────
        image_path = None
        if post_type == "prompt" and self.image is not None:
            image_target = str(self.git.drafts_dir) if draft else self.config.target_repo
            ig = new_step("image_gen", "ImageGenerator.run()", "agents/image_generator.py")
            try:
                image_path = self.image.run(topic.title, slug, image_target)
                if image_path:
                    content = content.replace('image: ""', f'image: "/{image_path}"', 1)
                    finish_step(ig, "success", detail=image_path)
                else:
                    finish_step(ig, "failed", error="no image bytes returned by API")
            except Exception as img_err:
                finish_step(ig, "failed", error=str(img_err))
                print(f"[ContentPilot] image gen failed for '{slug}': {img_err}", file=sys.stderr)
            parent.children.append(ig)

        # ── Git publish ──────────────────────────────────────────────────
        gp = new_step("git_publish", "GitPublisher.publish()", "agents/git_publisher.py")
        try:
            commit_sha = self.git.publish(slug, content, post_type, draft=draft)
            finish_step(gp, "success", detail=f"commit: {commit_sha[:8]}" if commit_sha else "draft saved")
        except Exception as e:
            finish_step(gp, "failed", error=str(e))
            parent.children.append(gp)
            return finish_step(parent, "failed", error="git publish failed")
        parent.children.append(gp)

        # ── Git push (live posts only — drafts are never pushed) ─────────
        push_status = None
        if not draft:
            push_step = new_step("git_push", "GitPublisher.push()", "agents/git_publisher.py")
            push_status = self.git.push()
            if push_status == "pushed":
                finish_step(push_step, "success", detail="pushed to remote")
            elif push_status == "no_remote":
                finish_step(push_step, "skipped", detail="no remote configured")
            else:
                finish_step(push_step, "failed", error="push failed — see stderr")
            parent.children.append(push_step)

        # ── Manifest ─────────────────────────────────────────────────────
        content_dir = self.config.content_paths.prompts if post_type == "prompt" else self.config.content_paths.workflows
        post = PostEntry(
            slug=slug,
            title=topic.title,
            type=post_type,
            category=topic.category,
            topic=topic.title,
            status="draft" if draft else "published",
            push_status=push_status,
            created_at=datetime.now(UTC),
            file_path=f"{content_dir}/{slug}.md",
            image_path=image_path,
            source_url=topic.url,
            git_commit=commit_sha,
        )
        append_post(post, self.manifest_path)
        return finish_step(parent, "success", detail=f"{'draft saved' if draft else 'published'}: {slug}")
