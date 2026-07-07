**Reliability:**
- `Input validation at boundaries` (API inputs, file/DB reads)
- `Explicit error handling per failure` type, not broad `except:` catches
- `Retries with backoff` on external calls, with a max-attempts cap
- `Idempotency` where operations can be retried safely
- `Tests`: `unit tests for logic`, `integration tests for external dependencies`, edge cases (empty, null, boundary values)
- `Logging at failure points`, not just success — so failures are visible, not silent

**Scalability:**
- `Stateless services` where possible, so horizontal scaling doesn't need sticky sessions
- `Async/concurrency for I/O-bound work` (DB calls, API calls) instead of blocking sequential calls
- `Caching for repeated/expensive lookups`
- Connection pooling for DB/network resources instead of opening new connections per request
- Load-test before assuming a design scales — don't guess at capacity

I'm not certain which of these you want expanded with a concrete example from your own resume (e.g. the Redis caching + gRPC gateway work) — say which, if you want that instead of the general list.