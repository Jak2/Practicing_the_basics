# 02 — Python Backend Fundamentals

Senior backend interviews probe language depth + concurrency + clean code. You know most of this from shipping production systems. The goal here is to give you **defensible mental models** — not bullet points an interviewer will drill through in 30 seconds.

---

## INTERVIEWER MINDSET

> What the interviewer is actually testing: Can this person reason about the language, or did they just use AI to write code they can't explain? They'll ask a surface question, get your answer, then ask a follow-up about a corner case. If the story breaks on the follow-up, you're a junior with a senior title.

**What separates junior from senior answers:**
- Junior: "The GIL prevents multiple threads from running at the same time."
- Senior: "The GIL is a CPython implementation detail. For I/O-bound work, it barely matters because threads release it during I/O syscalls. For CPU-bound work, it's fatal and you need multiprocessing. But most Python performance problems aren't the GIL — they're N+1 queries, missing indexes, or loading too much data into memory."

---

## 1. Concurrency Model (must be fluent)

### What the interviewer is probing
Your mental model of Python's execution environment. Can you reason about when concurrency helps vs hurts? Have you actually debugged a production race condition?

### The concepts
- **GIL (Global Interpreter Lock):** Only one thread executes Python bytecode at a time in CPython.
  - **Threading** → good for I/O-bound (threads release GIL during I/O waits).
  - **Multiprocessing** → good for CPU-bound (separate processes, true parallelism, separate GIL per process).
  - **AsyncIO** → single-threaded cooperative concurrency for I/O-bound at high scale (no thread overhead, no GIL fights at all).
- Rule of thumb: **I/O-bound → async or threads; CPU-bound → multiprocessing / Celery / native libs (numpy bypasses GIL in C)**.

### Veteran layer — the thing most candidates get wrong
The GIL is often cited as the reason to avoid threading, but it's rarely the actual bottleneck people think it is. I/O-bound async code doesn't fight the GIL at all — asyncio is single-threaded by design. Only CPU-bound threads actually compete for the GIL.

In production, I've seen teams rewrite threaded I/O code to async expecting a 10x gain and get 2x, because the real bottleneck was database round trips, not thread scheduling. Profile before you refactor concurrency.

### Common weak answer
"I use asyncio because the GIL makes threading useless." — Wrong. Threading is perfectly fine for I/O-bound work. This answer tells the interviewer you heard the GIL talking point but don't understand it.

### Senior signal answer (practice out loud)
> "The GIL means CPython can't run Python bytecode on multiple cores simultaneously, which kills CPU-bound threading. But for I/O-bound work, threads release the GIL during syscalls, so threading works fine there. AsyncIO is better than threading for I/O when you have thousands of concurrent connections — lower overhead, no shared state bugs. For CPU-bound work, I reach for multiprocessing or Celery, or I push the work to a C extension like numpy that releases the GIL internally."

### Follow-up question the interviewer will ask
**"When would you choose threading over asyncio for I/O?"**

Answer: When you're using a synchronous library you can't change. Classic example: a legacy database driver that has no async support, or `requests` instead of `httpx`. You can't just sprinkle `await` on a sync function — you'd block the event loop. Threading lets you run those sync calls without rewriting the library. In FastAPI, `run_in_threadpool` does exactly this for sync dependencies.

---

## 2. AsyncIO Essentials

- `async def` = coroutine; `await` yields control to event loop.
- `asyncio.gather(*coros)` → run many concurrently (fan-out third-party calls).
- `asyncio.create_task()` → schedule background coroutine without blocking.
- **Never block the event loop**: no `time.sleep` (use `asyncio.sleep`), no sync DB calls, no sync HTTP.
- `async with` / `async for` for async context managers and iterators.

### Veteran layer
One production mistake I've seen repeatedly: calling a sync function from an async route and wondering why the server freezes under load. You have one event loop. Block it for 200ms with a sync call and every other request stalls. In FastAPI, if you define a route as `def` instead of `async def`, FastAPI runs it in a threadpool automatically. If you use `async def` with a blocking call inside, you've just broken the entire app under load.

---

## 3. Data Model / Language Depth

### 3a. Mutable vs Immutable
- Immutable: `int`, `str`, `float`, `tuple`, `frozenset` — safe as dict keys, safe as default args.
- Mutable: `list`, `dict`, `set` — never use as default argument values.

### 3b. Mutable Default Argument Trap

**What the interviewer is probing:** Do you actually write Python day-to-day, or do you just know the happy path?

```python
# BUG — list is created ONCE at function definition time
def append_item(item, lst=[]):
    lst.append(item)
    return lst

append_item(1)  # [1]
append_item(2)  # [1, 2] — NOT [2] — surprise!

# Fix
def append_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### Senior signal answer
> "The default argument is evaluated once when the function is defined, not each time it's called. So a mutable default like a list is shared across all calls. I've seen this cause subtle bugs in cache implementations and stateful helpers. The fix is always `None` as the sentinel and create the mutable inside the function body."

### Follow-up: "What else could go wrong with default args?"

Answer: Class-level mutable attributes have the exact same problem:
```python
class Config:
    tags = []  # Shared across ALL instances — same trap

    def add_tag(self, tag):
        self.tags.append(tag)

# Fix: initialize in __init__
class Config:
    def __init__(self):
        self.tags = []
```
This bites people in ORMs (Object-Relational Mappers) and dataclasses if you're not careful.

### 3c. Generators / `yield`

**What the interviewer is probing:** Do you write memory-efficient code, or do you load everything into RAM?

```python
# Bad — loads 1M rows into memory
def get_all_users():
    return db.query("SELECT * FROM users").fetchall()

# Good — streams row by row
def stream_users():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    for row in cursor:
        yield row
```

### Veteran production use
I used generators when processing 1M+ row export jobs. Loading 1M rows returns a 4GB Python list that crashes the process. Streaming with `yield` keeps memory flat at ~100KB regardless of result size. The caller iterates and processes in chunks, writing to CSV or pushing to S3 as it goes. This is the single most impactful Python optimization I've applied in production for data pipelines.

Generator expressions `(x for x in range(1M))` are lazy too — prefer them over list comprehensions when you don't need random access.

### 3d. Decorators — the real production uses

**What the interviewer is probing:** Can you write a decorator from scratch? Do you know what `functools.wraps` does and why it matters?

```python
import functools
import time

def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @functools.wraps(func)  # preserves __name__, __doc__ — critical for debugging
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # exponential backoff
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def call_external_api(payload):
    ...
```

### Real production decorator uses
- **Retry with backoff** — network calls, LLM API calls
- **Rate limiting** — per-user endpoint throttling
- **Auth/permission checks** — `@require_role("admin")`
- **Caching** — `@lru_cache`, `@cache` (Python 3.9+), Redis-backed cache decorator
- **Timing/instrumentation** — emit metrics for slow functions
- **Transaction management** — auto-commit/rollback DB transactions

### Common weak answer
"Decorators are used for logging." — This is true but thin. It signals you've read about decorators but haven't built production systems with them. Name the real use cases.

### Follow-up: "What does `functools.wraps` do and why does it matter?"

Without `@functools.wraps(func)`, your decorated function loses its name and docstring — `wrapper.__name__` is `"wrapper"` instead of `"call_external_api"`. This breaks logging, error messages, and Swagger docs in FastAPI. It's one line that shows you understand the decorator fully.

---

## 4. Pydantic (you use it — know v2)

- Models validate + coerce types; `BaseModel`, `Field(...)` for constraints/defaults.
- Validators: `@field_validator`, `@model_validator`.
- `model_dump()` / `model_dump_json()` (v2; was `.dict()`/`.json()` in v1).
- `pydantic-settings` for env-based config.
- Why: declarative validation, serialization, settings — the backbone of FastAPI contracts.

### Veteran layer
Pydantic v2 is ~5-17x faster than v1 due to the Rust core. If you're on a team that hasn't migrated, migration pain is real: validators changed from `@validator` to `@field_validator`, `orm_mode=True` became `model_config = ConfigDict(from_attributes=True)`. Know the migration story if it comes up.

---

## 5. OOP & Design

- Classes, `@classmethod`/`@staticmethod`/`@property`, dunder methods (`__repr__`, `__eq__`).
- **SOLID** at a high level — Single responsibility, dependency inversion (DI in FastAPI is this).
- **Composition over inheritance.**

### classmethod vs staticmethod — a question that exposes shallow understanding

```python
class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        # cls = the class itself — can call cls() to create instances
        # Works correctly even in subclasses
        return cls(name=data["name"], role=data["role"])

    @staticmethod
    def validate_role(role: str) -> bool:
        # No access to cls or self — just a namespaced function
        return role in ("admin", "editor", "viewer")
```

**Key distinction:** `@classmethod` receives the class as first arg (`cls`) — useful for alternative constructors or factory methods. `@staticmethod` gets nothing — it's a plain function that lives in the class namespace for organizational purposes only.

### Follow-up: "When would you use a classmethod over a regular class constructor?"
When you want multiple ways to construct an object. `User.from_dict(data)`, `User.from_jwt(token)`, `User.guest()` — all factory methods using `@classmethod`. FastAPI's dependency injection pattern uses this heavily.

---

## 6. Python Patterns a Senior Engineer Actually Uses

### 6a. Context Managers for Resource Management

```python
from contextlib import contextmanager

@contextmanager
def db_transaction(session):
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Usage — cleanup guaranteed even on exception
with db_transaction(get_session()) as session:
    session.add(new_record)
```

**Why it matters in production:** Without context managers, cleanup code lives in `finally` blocks scattered everywhere. Context managers centralize it. In data pipelines, I use them for: DB connections, file handles, acquiring/releasing locks, opening/closing HTTP clients, and managing temporary directories.

### 6b. Dataclasses vs Pydantic — the actual tradeoff

| | Dataclass | Pydantic BaseModel |
|---|---|---|
| Validation | None (or manual) | Automatic, rich |
| Performance | Faster | Slightly slower (but v2 is fast) |
| Serialization | Manual | Built-in `model_dump()` |
| Config/settings | No | Yes (`pydantic-settings`) |
| Use case | Internal data containers, DTOs | API request/response, config |

**Senior signal:** "I use dataclasses for internal value objects where I control all inputs and don't need validation overhead. I use Pydantic for anything crossing a trust boundary — API inputs, config from env, external data. The moment you need `.model_dump()` or field validation, Pydantic pays for itself."

### 6c. `__slots__` — when it actually matters

```python
class Point:
    __slots__ = ("x", "y")  # No __dict__ — lower memory per instance

    def __init__(self, x, y):
        self.x = x
        self.y = y
```

Use `__slots__` when you're creating millions of instances of a simple class (coordinates, events, messages). Reduces per-instance memory by ~40-60% by eliminating the `__dict__`. Not worth it for typical service-layer classes.

### 6d. Type Hints in Production

**What breaks without type hints:**
- IDEs give no autocomplete on return types
- Mypy/Pyright can't catch type mismatches before runtime
- FastAPI can't generate OpenAPI docs correctly
- New developers can't understand function contracts without reading the body

**The real value:** Type hints are documentation that the tool can verify. I've caught dozens of bugs at lint time that would have been silent runtime errors. In a FastAPI codebase, they're not optional — they drive the entire request/response contract.

---

## 7. Error Handling

- Specific exceptions over bare `except:`. Custom exception classes per domain.
- `try/except/else/finally`. Re-raise with context (`raise NewException(...) from original_exc`).
- Don't swallow errors silently — log them. Fail fast on programmer errors; handle/retry on transient errors.

### Veteran layer
The `raise X from Y` syntax preserves the original traceback as `__cause__`. Without it, you lose the root cause in logs. I always use it when wrapping exceptions:
```python
try:
    result = external_api.call()
except httpx.TimeoutException as e:
    raise ServiceUnavailableError("Payment service timed out") from e
```

---

## 8. Testing (JD values reliability)

- **pytest**: fixtures, parametrize, `monkeypatch`, markers.
- Mocking: `unittest.mock` / `pytest-mock` — mock external services/DB.
- FastAPI: `TestClient`, dependency overrides, test DB (sqlite/transaction rollback).
- Coverage, and the testing pyramid (many unit, fewer integration, few e2e).
- You ran Robot Framework + authored review checklists — strong testing story.

---

## 9. AI-Assisted Dev Traps — Questions to Expose Shallow Understanding

These are questions interviewers use to find candidates who used AI to write code they can't explain. Know the answers cold.

**"Walk me through this decorator — what exactly happens line by line?"**
If you can't trace execution order of a decorator (outer function, inner function, `functools.wraps`, argument passing), you'll fail this. Practice with the retry decorator above.

**"What's the difference between `is` and `==`?"**
`is` checks identity (same object in memory). `==` checks equality (same value). `None` check should always be `x is None`, never `x == None`. CPython interns small integers and short strings, so `1 is 1` is True but `1000 is 1000` may not be. This is a trap.

**"What happens when Python evaluates `a = [] ; b = a ; b.append(1)`?"**
Both `a` and `b` point to the same list object. `a` is now `[1]`. This is a reference, not a copy. Use `b = a.copy()` or `b = list(a)` for a shallow copy, or `copy.deepcopy(a)` for a deep copy.

**"If I inherit from two classes that both define `__init__`, what happens?"**
Python uses MRO (Method Resolution Order) — C3 linearization. `super().__init__()` calls the next class in the MRO chain. This is where multiple inheritance gets dangerous. Senior answer: "I try to avoid multiple inheritance of mutable state. I use mixins for behavior, not state."

---

## 10. Performance Habits

- Profile before optimizing (`cProfile`, `py-spy` for production profiling without stopping the process).
- Use sets/dicts for membership (O(1)); avoid N+1 DB queries; batch.
- Connection pooling; caching; pagination; streaming.
- `py-spy` is the veteran tool — it attaches to a running Python process and shows where time is spent without modifying code.

---

## 11. Packaging & Environment

- Virtualenv / `venv`, `pip`, `requirements.txt` or `pyproject.toml` (Poetry/uv).
- 12-factor: config in env, stateless processes, logs to stdout.
- `__name__ == "__main__"`, modules vs packages.

---

## GAP FILL: Python Profiling Tools

**Why this matters:** A senior backend engineer owns performance. "How would you diagnose a slow Python service?" expects this answer.

### The three tools

**1. `cProfile` — CPU profiling (built-in)**

Counts how many times each function is called and how long each takes.

```python
import cProfile
cProfile.run('my_slow_function(data)', sort='cumulative')
```

Output: sorted table — `ncalls`, `tottime` (in this function only), `cumtime` (this function + callees). Look for functions with high `cumtime` and many calls.

**Run from CLI:**
```bash
python -m cProfile -s cumulative my_script.py | head -30
```

**Limitation:** Adds overhead, can't attach to a running process.

**2. `py-spy` — sampling profiler for live processes (production-safe)**

Attaches to a running Python process without modifying code or restarting. No overhead in production.

```bash
pip install py-spy
py-spy top --pid 12345           # live top-like view
py-spy record -o profile.svg --pid 12345   # flame graph
py-spy dump --pid 12345          # stack trace snapshot
```

**When to use:** Service is slow in production, you can't add instrumentation, you need a snapshot of where time is being spent right now.

**3. `memory_profiler` — line-by-line memory usage**

```python
from memory_profiler import profile

@profile
def load_large_dataset():
    data = [row for row in open("big_file.csv")]
    processed = [transform(row) for row in data]
    return processed
```

Output: shows memory delta per line — reveals where objects accumulate.

```bash
python -m memory_profiler my_script.py
```

### The profiling workflow (production story version)

> "When the NFTRACE pipeline was taking 40+ seconds for large captures, I didn't guess — I ran py-spy against the running process and got a flame graph. It showed 80% of time in one XML parsing function that was being called once per packet instead of once per file. That one-line architectural fix — move the parse outside the loop — dropped runtime to 4 seconds. The lesson: profile before optimizing, or you'll optimize the wrong thing."

**Interview spoken answer:**
> "For profiling a slow Python service I have three tools depending on context. `cProfile` for development — it's built-in and gives you call counts and cumulative time per function. `py-spy` for production — it's a sampling profiler that attaches to a running process with `--pid`, produces flame graphs, and has essentially no overhead. `memory_profiler` when I suspect a memory leak — it gives you line-by-line memory delta so you can see exactly where objects are accumulating. The workflow is: suspect something is slow, attach py-spy and get a flame graph, identify the hot path, then use cProfile locally to drill into that specific area."

---

## GAP FILL: Async SQLAlchemy + asyncpg

**Why this matters:** Production FastAPI uses async DB access. SQLAlchemy in sync mode blocks the event loop. A senior FastAPI developer is expected to know this.

### The setup

```python
# requirements: sqlalchemy[asyncio] asyncpg

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, pool_size=10, max_overflow=5)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

Key change: `postgresql+asyncpg://` driver prefix. `create_async_engine` instead of `create_engine`.

### FastAPI dependency injection

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Usage in a route

```python
from sqlalchemy import select
from fastapi import Depends

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404)
    return user
```

Note: `await db.execute(...)` — all queries are awaited. ORM lazy loading doesn't work in async mode; you must use `selectinload` or `joinedload` explicitly.

### Sync vs Async SQLAlchemy comparison

| | Sync (`create_engine`) | Async (`create_async_engine`) |
|---|---|---|
| Driver | psycopg2 | asyncpg |
| Route type | `def` route | `async def` route |
| Lazy loading | Works | Broken (raises `MissingGreenlet` error) |
| Event loop | Blocks on query | Yields during query |
| Pool | ThreadPoolExecutor | asyncio-native |

**Interview spoken answer:**
> "In production FastAPI, I use async SQLAlchemy with the asyncpg driver — the connection string is `postgresql+asyncpg://` instead of `postgresql+psycopg2://`. You use `create_async_engine` and `AsyncSession`, and every query is awaited. The main gotcha is that SQLAlchemy's lazy loading doesn't work in async context — accessing a relationship attribute after the session closes raises a `MissingGreenlet` error. The fix is to use `selectinload` or `joinedload` in the query to eagerly load what you need. The payoff is that under high concurrency, your FastAPI routes yield back to the event loop during database I/O instead of blocking, which massively improves throughput on I/O-heavy endpoints."

---

## 12. Likely Questions — with Framing

1. **GIL — what is it, how do you work around it?** → §1. Lead with the I/O vs CPU distinction, mention asyncio doesn't fight GIL at all.
2. **Threading vs multiprocessing vs asyncio?** → §1. Give concrete use-case for each.
3. **Mutable default argument bug?** → §3b. Show the code, explain why, give the fix, mention class-level mutable attributes.
4. **Write a decorator from scratch.** → §3d. Write the retry decorator. Include `functools.wraps`.
5. **What's a generator / when do you use it?** → §3c. Say "1M row DB export" — concrete production use.
6. **classmethod vs staticmethod?** → §5. Give the factory method example.
7. **Dataclass vs Pydantic?** → §6b. Trust boundary is the key concept.
8. **How do you handle config and secrets?** → env + pydantic-settings, never hardcode, Secret Manager in prod.
9. **How do you test backend code with external dependencies?** → mock/fixtures, dependency override in FastAPI.
10. **`is` vs `==`?** → identity vs equality, `None` should always use `is`.
11. **Shallow vs deep copy?** → `list.copy()` vs `copy.deepcopy()`, when each matters.
12. **How does Python GC work?** → reference counting + cycle collector for circular references.
