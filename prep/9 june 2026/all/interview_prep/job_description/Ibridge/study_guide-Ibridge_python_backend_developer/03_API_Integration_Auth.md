# 03 — API Design, Integration & Authentication (JWT/OAuth)

JD explicitly lists: REST API design, third-party integration, **Authentication (JWT/OAuth)**, error handling/validation, frontend integration. High-priority.

---

## INTERVIEWER MINDSET

> This section is where AI-assisted developers get exposed fastest. They can describe JWT structure from docs, but they can't tell you what they've actually broken in production. The veteran layer here is everything — it's the difference between "I implemented JWT auth" and "here's a failure mode that bit us and what we did about it."

**What separates junior from senior answers:**
- Junior: "JWT is stateless and has three parts: header, payload, signature."
- Senior: "JWT is stateless and that's both its power and its biggest risk. It scales because you don't need a DB lookup on every request. But stateless means you can't revoke a token instantly. Here's the pattern I use in production to handle that..."

---

## 1. REST Fundamentals

- Resources as nouns: `/ads`, `/ads/{id}`, `/ads/{id}/creatives`.
- **HTTP methods**: GET (read, safe/idempotent), POST (create), PUT (full replace, idempotent), PATCH (partial), DELETE (idempotent).
- **Status codes**: 2xx success, 3xx redirect, 4xx client error, 5xx server error.
- **Idempotency**: GET/PUT/DELETE idempotent; POST not (use idempotency keys for safe retries on payments).
- **Statelessness**: each request carries its own auth/context; no server session affinity → enables horizontal scaling.

---

## 2. Good API Contract Design (frontend collaboration)

- **Consistent response envelope**: `{ "data": ..., "meta": {...}, "error": null }` — pick a shape, never deviate.
- **Pagination**: offset/limit (`?page=2&size=20`) or **cursor-based** (better for large/changing data). Return total count + next cursor.
- **Filtering/sorting**: `?status=active&sort=-created_at`.
- **Versioning**: `/v1/...` URL prefix (simplest) or header. Never break existing consumers.
- **Consistent error shape** so frontend can handle uniformly: `{"error":{"code":"AD_NOT_FOUND","message":"..."}}`.
- **OpenAPI/Swagger** auto-docs from FastAPI = the living contract you share with React/Next.js devs.

### Senior signal on versioning
> "I use URL versioning (`/v1/`) because it's explicit and cacheable. Header versioning is cleaner but harder to test in a browser and harder for frontend devs to work with. The real discipline is: never remove a field from a response in the same version — add new fields, deprecate old ones across versions."

---

## 3. Third-Party / Service Integration

### Basic principles
- Use **`httpx.AsyncClient`** (async) — reuse one client per application lifetime, set **timeouts**.
- **Retries with exponential backoff + jitter** for transient 5xx/network errors.
- **Circuit breaker** to stop hammering a down dependency.
- **Idempotency keys** when calling external mutating APIs.
- Handle partial failures gracefully — never let a slow third party block all requests.

### The Flaky API Playbook — what a senior actually does

This is a four-layer defense. Describe it in order:

**Layer 1: Timeout** — Every external call has a connect timeout and a read timeout. Without this, a hung external service hangs your thread/coroutine forever.

**Layer 2: Retry with exponential backoff + jitter**

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    reraise=True
)
async def call_payment_api(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
        response = await client.post(
            "https://payments.example.com/charge",
            json=payload
        )
        response.raise_for_status()
        return response.json()
```

**Layer 3: Circuit breaker** — After N consecutive failures, open the circuit and fail immediately without calling the service. After a cooldown, allow one probe request. If it succeeds, close the circuit. Libraries: `circuitbreaker`, or custom implementation. This prevents thundering herd when a dependency recovers.

**Layer 4: Degraded response** — If the circuit is open, return a cached result, a default, or a graceful error to the user. Don't just throw a 500. "Payment service temporarily unavailable, please retry" is better than a cascade failure.

### Senior signal answer (practice out loud)
> "When integrating with a flaky API, I apply four layers: timeout to bound worst-case latency, retry with exponential backoff and jitter for transient errors, a circuit breaker to stop hammering a down service, and a degraded response so users get something useful instead of a 500. In production I've seen teams that only have the retry layer — when the third-party goes down, retries storm the service during recovery and make it worse. The circuit breaker is what prevents that."

### Why jitter matters
Without jitter, retries from hundreds of instances all fire at the same time after the same backoff interval — a synchronized thundering herd. Jitter randomizes the wait so retries spread out over time.

---

## 4. Webhook Hardening

Webhooks are a common interview topic and a common production failure point.

### The four rules of webhook hardening

**1. Verify the signature immediately**
```python
import hmac, hashlib

def verify_stripe_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    # Use hmac.compare_digest — constant-time comparison prevents timing attacks
    return hmac.compare_digest(expected, signature)
```

**2. Respond 202 immediately** — before any processing. Webhook senders have short timeouts (Stripe: 30s). If you process synchronously and it takes 35s, Stripe marks it failed and retries, causing double-processing.

**3. Process async** — Put the event on a queue (Redis, SQS, Celery) and return 202. A background worker processes it. This decouples your processing latency from the sender's timeout.

**4. Idempotency keys** — Senders retry on network failure. You may receive the same event multiple times. Store processed event IDs and skip duplicates:
```python
if await redis.setnx(f"webhook:{event.id}", "1"):
    await redis.expire(f"webhook:{event.id}", 86400)  # 24h TTL
    await process_event(event)
# else: already processed, skip silently
```

### Common weak answer
"I just process the webhook and return 200." — No signature verification (security hole), no idempotency (double-charges), synchronous processing (reliability hole). Three failure modes in one answer.

---

## 5. Authentication vs Authorization

- **AuthN** = who you are (login). **AuthZ** = what you're allowed to do (permissions/roles).
- You built **attribute-level RBAC** (Role-Based Access Control) at Brane → strong AuthZ story. Use it.

---

## 6. JWT — Be Precise and Know the Failure Modes

### Structure
- **Stateless token**, 3 parts: `header.payload.signature`, base64url-encoded, dot-separated.
  - Header: alg (e.g. HS256/RS256) + type.
  - Payload: **claims** — `sub` (user id), `exp` (expiry), `iat`, `iss`, `aud`, custom (roles).
  - Signature: signs header+payload with secret (HS256, symmetric) or private key (RS256, asymmetric).
- **Flow**: user logs in → server issues JWT → client sends `Authorization: Bearer <token>` → server **verifies signature + expiry** (no DB lookup → scales horizontally).

### The silent JWT mistake that bites AI-assisted developers
**JWT is signed, not encrypted.** The payload is base64url-encoded — that's encoding, not encryption. Anyone can decode it in the browser in 2 seconds:

```javascript
// In the browser console
JSON.parse(atob(token.split('.')[1]))
// → { "sub": "user123", "email": "john@company.com", "role": "admin", "exp": 1750000000 }
```

In production I've seen teams put the user's email, role, internal user ID, and subscription tier in the JWT "for convenience" — all visible in the Network tab to anyone who opens DevTools. If a user changes their role or gets suspended, the old token still has the old claims until expiry.

**Rule:** Put the minimum in the JWT. `sub` (user ID) + `exp` + `iss`. Fetch sensitive details from DB/cache on the server side. Roles are borderline — acceptable if short-lived, risky if long-lived.

### JWT Revocation — the real production problem

The fundamental tension: JWTs are stateless (no DB lookup = scales), but revocation requires state (was this token invalidated?).

**Production pattern: short-lived access token + refresh token + Redis blacklist**

```
Access token:  15 minutes expiry
Refresh token: 7 days expiry, stored in HttpOnly cookie
```

**On logout or compromise:**
1. Add the access token's `jti` (JWT ID claim — a unique ID per token) to Redis with TTL matching token expiry.
2. On each request, check Redis blacklist before accepting token.
3. Delete the refresh token from DB.

```python
# Issuing tokens — add jti
import uuid
payload = {
    "sub": user_id,
    "jti": str(uuid.uuid4()),  # unique per token
    "exp": datetime.utcnow() + timedelta(minutes=15)
}

# Checking revocation
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    jti = payload.get("jti")
    if await redis.get(f"revoked:{jti}"):
        raise HTTPException(401, "Token revoked")
    return payload

# On logout
async def logout(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    ttl = payload["exp"] - int(datetime.utcnow().timestamp())
    await redis.setex(f"revoked:{payload['jti']}", ttl, "1")
```

The blacklist only needs to live as long as the token. After expiry, the token is invalid anyway.

### HS256 vs RS256
- HS256: symmetric — same secret signs and verifies. Simple for single-service. If the secret leaks, game over.
- RS256: asymmetric — private key signs, public key verifies. Better for multi-service: API gateway can verify tokens without holding the signing key. Auth service holds private key; all other services hold only the public key.

### FastAPI JWT sketch
```python
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_token(sub: str):
    payload = {
        "sub": sub,
        "jti": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(401, "Invalid token")
    return payload
```
Password hashing: **bcrypt / argon2** via `passlib` — never store plaintext. Never use MD5 or SHA-256 for passwords — they're fast, and fast is bad for password hashing.

### Follow-up questions
- "What's in the JWT payload and is it safe to put user roles there?" → signed not encrypted, visible in browser.
- "How do you handle logout with JWTs?" → Redis blacklist + `jti` claim.
- "What happens if your JWT secret leaks?" → all tokens are compromised, rotate immediately, all users re-authenticate.

---

## 7. OAuth2 / OIDC — Know the Full Flow with Failure Points

### Concepts
- **OAuth2** = delegated **authorization** (let App A access resources on behalf of a user without sharing password).
- **Roles**: Resource Owner (user), Client (your app), Authorization Server (Google/Auth0), Resource Server (API).
- **OIDC** = thin identity layer on top of OAuth2 → adds **ID token** (who the user is). OAuth2 = authorization; OIDC = authentication.

### Authorization Code Flow — step by step with what can go wrong

```
1. User clicks "Login with Google"
   → App redirects to: https://accounts.google.com/oauth2/auth
     ?client_id=YOUR_ID
     &redirect_uri=https://yourapp.com/callback
     &response_type=code
     &scope=openid email
     &state=RANDOM_STRING    ← CSRF protection
     &code_challenge=...     ← PKCE (for SPAs)

2. Google authenticates user, user consents to scopes
   → Google redirects to: https://yourapp.com/callback?code=AUTH_CODE&state=RANDOM_STRING

3. Your server exchanges code for tokens (server-side, POST to Google):
   POST /token
   grant_type=authorization_code
   &code=AUTH_CODE
   &redirect_uri=https://yourapp.com/callback
   &client_id=YOUR_ID
   &client_secret=YOUR_SECRET   ← Never send this to browser

4. Google returns: { access_token, id_token, refresh_token }

5. Your server extracts user identity from id_token (OIDC)
   → Creates or updates your user record
   → Issues your own session/JWT
```

**What can go wrong at each step:**
- Step 1: Not validating `state` → CSRF attack (attacker can link their account to victim's session).
- Step 2: `redirect_uri` not exactly matching registered URI → code leaks to attacker.
- Step 3: Using the code more than once → auth servers reject it (codes are single-use).
- Step 4: Not validating the `id_token` signature → accepting forged identity claims.
- Step 5: Trusting the `email` claim without checking `email_verified` → user may not own that email.

**PKCE (Proof Key for Code Exchange):** For SPAs and mobile apps that can't hold a client secret, PKCE replaces the secret. App generates a `code_verifier`, sends `code_challenge` (hash of verifier) in step 1, sends `code_verifier` in step 3. The auth server verifies they match. This prevents auth code interception attacks.

### Client Credentials Flow (machine-to-machine)
No user involved. Service sends `client_id` + `client_secret` directly for an access token. Used for internal service-to-service calls. Never use in a browser — secret would be exposed.

---

## 8. OWASP API Top 10 — Know the Top 3 Cold

### #1 — Broken Object Level Authorization (BOLA / IDOR)

The most common API security bug. An authenticated user accesses another user's data by changing an ID in the URL.

```
GET /api/ads/123  → returns your ad ✓
GET /api/ads/124  → should return 403, but returns another user's ad ✗
```

The API authenticates the user but doesn't check if the user owns object 124.

**Fix:** Every object fetch must check ownership or permission:
```python
@app.get("/ads/{ad_id}")
async def get_ad(ad_id: int, current_user = Depends(get_current_user)):
    ad = await db.get(Ad, ad_id)
    if not ad or ad.owner_id != current_user.id:
        raise HTTPException(404)  # 404 not 403 — don't reveal the object exists
```

### #2 — Broken Authentication

Weak authentication implementations:
- No brute force protection on `/login` (rate limit it)
- Accepting expired or unsigned JWTs
- Short JWT secrets brute-forceable offline
- Storing tokens in localStorage (XSS-accessible)
- No HTTPS (tokens interceptable)

### #3 — Broken Object Property Level Authorization (Mass Assignment)

User can set fields they shouldn't by sending extra fields in a request body.

```python
# BAD — Pydantic model without excluding internal fields
class UpdateUser(BaseModel):
    name: str
    email: str
    is_admin: bool  # User should NOT be able to set this

# GOOD — separate input model from domain model
class UpdateUserInput(BaseModel):
    name: str
    email: str
    # is_admin not here — can't be set via API
```

In FastAPI, always use separate input Pydantic models that only expose the fields users are allowed to set. Never pass `**request.dict()` directly to an ORM model.

---

## 9. API Security Checklist (Senior Signal)

- HTTPS everywhere; validate & sanitize all input (Pydantic); parameterized SQL (no injection).
- AuthN on every protected route; BOLA checks — every object access verifies ownership.
- Rate limiting / throttling on auth endpoints (prevent brute force).
- CORS (Cross-Origin Resource Sharing) locked to known origins — not `*` in production.
- Don't leak internals in errors: generic 500 to client, full stack trace in structured logs.
- Secrets in env/secret manager; rotate keys; least privilege IAM.
- Webhook signature verification, idempotency, async processing.

### "What is the most common API security mistake you've seen?"

**Model answer (shows production experience):**
> "Missing object-level authorization — BOLA. It's OWASP #1 for a reason. The team implements authentication correctly — tokens, password hashing, HTTPS — but then writes every endpoint as 'if the user is logged in, return the object.' A logged-in attacker just iterates IDs to access any object in the system. I've seen this in production codebases where the auth middleware was solid but the route handlers had zero ownership checks. The fix is a policy: every data-fetching route must explicitly check that the requesting user has permission to see that specific resource, not just that they're authenticated."

---

## 10. Likely Questions — with Framing

1. **Explain JWT structure and auth flow end-to-end.** → §6. Walk header/payload/signature, then the request flow. Volunteer that it's signed not encrypted.
2. **JWT vs session-based auth — trade-offs?** → Stateless/scales vs revocable/simpler. JWTs need Redis for revocation to match session flexibility.
3. **Access vs refresh token — why two?** → Short-lived access token limits exposure window. Long-lived refresh token lets users stay logged in without re-authenticating. Refresh token stored in HttpOnly cookie.
4. **How do you handle logout with JWTs?** → Redis blacklist + `jti` claim. This is a trap — "just delete the token on the client" is wrong.
5. **OAuth2 authorization code flow — walk through it.** → §7. Know all five steps and what breaks at each.
6. **AuthN vs AuthZ? RBAC — how did you implement it?** → Your Brane attribute-level RBAC story.
7. **How do you handle a flaky third-party API?** → §3. Timeout → retry with backoff/jitter → circuit breaker → degraded response. Name `tenacity`.
8. **How do you design pagination?** → Cursor-based for large datasets, offset/limit for simple cases. Cursor is stable when data changes.
9. **How do you prevent SQL injection?** → Parameterized queries / ORM (SQLAlchemy). Never string-format SQL.
10. **Where do you store the JWT on the client and why?** → HttpOnly cookie (not accessible to JS, prevents XSS). LocalStorage is XSS-accessible. Memory is safest but lost on page reload.
11. **OWASP API Top 10 — name the top 3.** → BOLA, Broken Authentication, Broken Object Property Level Authorization. Explain each with a one-sentence example.
12. **What's the most common API security mistake you've seen?** → §9 model answer. Tell it like a war story.
