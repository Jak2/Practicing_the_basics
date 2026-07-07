# 07 — DevOps, CI/CD, Logging/Monitoring & Git

JD: "Knowledge of CI/CD (Continuous Integration/Continuous Deployment) and API logging and Monitoring", "Git for branching, merging, PRs, code reviews", "Agile". You won't be deeply tested but need fluent vocabulary.

---

## jak_ai_job_coach — Before You Start

**Interviewer perspective:** DevOps questions at the senior level are not trivia quizzes ("what does git rebase do"). They're testing whether you've lived through the *painful scenarios* — a broken pipeline blocking the team, a bad deploy at 2pm Friday, a merge conflict on a shared branch. The candidate who's only read about this answers in the abstract. The candidate who's shipped answers in the specific.

**Senior signal vs junior signal:**
- Junior: Knows the commands. Describes the happy path.
- Senior: Knows when to break the rules (rebase vs merge), knows how to triage a broken pipeline systematically, knows how rollback actually works for each deploy strategy, and gives feedback in code review without creating friction.

**Your real experience to anchor on:** GitLab CI/CD, Docker, K8s (Kubernetes) pod monitoring at Nokia. You've shipped production systems with AI assistance. Own that. The story isn't "I used AI tools" — the story is "I understand the systems I shipped and I can debug them when they break."

---

## 1. Git (you use Git/GitLab daily — make answers crisp)
- **Core**: `clone, add, commit, push, pull, fetch, status, log, diff`.
- **Branching**: `git branch`, `git checkout -b`, feature branches off `main`/`develop`.
- **Merge vs rebase**: merge preserves history (merge commit); rebase rewrites for linear history. **Never rebase shared/pushed branches.**
- **Pull Request / Merge Request**: propose changes → review → CI runs → merge. You authored review checklists — strong story.
- **Conflict resolution**: editing both sides, `git mergetool`, then commit.
- **Useful**: `git stash`, `git cherry-pick`, `git revert` (safe undo, new commit) vs `git reset` (moves HEAD, can lose work), `git tag` (releases).
- **Branching strategies**: Git Flow (develop/feature/release/hotfix), **trunk-based** (short-lived branches off main + feature flags — modern default), GitHub Flow.
- **Good commits**: small, atomic, meaningful messages; PRs reviewable in size.

### Veteran layer — the merge vs rebase reality

> "The merge vs rebase debate sounds academic until you're dealing with a 40-commit feature branch that diverged 3 weeks ago. My rule of thumb: I use **rebase for local cleanup before a PR** — squash the noisy 'wip', 'fix typo', 'try again' commits into logical units that tell a coherent story. I use **merge for integrating into shared branches** — you want the record of when that feature landed and from where. The hard rule I follow: never rebase after you've pushed, because you're rewriting history that other people may have based work on. If my branch is messy before a PR, I'll do an interactive rebase locally, force-push *my own branch* (never main), and then the reviewer gets a clean, readable history."

**Follow-up they might ask:** "What's an interactive rebase?" — Answer: `git rebase -i HEAD~N` lets you squash, reorder, edit, or drop the last N commits before pushing. Useful for turning a messy local history into clean logical commits.

**Common weak answer to avoid:** "I always merge because rebase is dangerous." That's a junior answer that signals you've never needed to clean up a feature branch. The senior answer shows you use both deliberately.

---

## 2. CI/CD
- **CI (Continuous Integration)**: on every push/PR, automatically **lint + test + build** → catch breakage early. (You built a CI prompt-regression suite — relevant!)
- **CD (Continuous Delivery/Deployment)**: automatically package and deploy to staging/prod after CI passes.
- **Pipeline stages**: checkout → install deps → lint (ruff/flake8/black) → tests (pytest) → build image → push to registry → deploy → smoke test.
- **Tools**: GitLab CI (`.gitlab-ci.yml` — you've used GitLab), GitHub Actions, Jenkins.
- **Deployment strategies**: blue-green, canary, rolling — reduce risk/downtime.
- **Artifacts/registry**: Docker images pushed to a container registry.

### Scenario: "How do you handle a broken CI pipeline that's blocking the team?"

**Interviewer perspective:** They want to see calm, systematic diagnosis and team-first thinking — not heroics and not panic.

**Model answer:**
> "First thing: is this *flaky* or *systemic*? I look at whether it's failing consistently or intermittently. A flaky test (race condition, external API dependency) gets a retry and a filed ticket — you don't hold the team hostage to a known flaky test. A systemic failure gets triaged immediately.
>
> For a systemic failure: I read the actual error output rather than the summary (CI summaries often point to the symptom, not the cause). I check: Did a dependency version change? Did someone merge something that changed shared fixtures? Is it an infra issue (runner out of disk, registry unreachable) or a code issue?
>
> If it's going to take more than 15 minutes to fix and it's blocking merges, I communicate that clearly to the team — 'pipeline is broken on main, cause is X, ETA for fix is Y, don't merge until I clear it.' If we have a hotfix that genuinely can't wait, I'd work with the team lead to do a manual deploy or cut a hotfix branch that bypasses the broken step with eyes-open justification.
>
> The thing I don't do: silently disable the failing step to unblock myself and leave a trap for the next person."

**Senior signal:** Distinguishes flaky vs systemic, communicates proactively, doesn't disable tests as a shortcut.

### Scenario: "Deployment went wrong — how do you roll back?"

**Interviewer perspective:** Tests whether you understand that rollback isn't the same for every deployment strategy. Junior answer: "I'd revert the code." Senior answer: understands the mechanics differ.

**Model answer:**
> "It depends on the deployment strategy.
>
> **Blue-green**: This is the easiest rollback. You have two identical environments — blue is live, green has the new version. If green is bad, you flip the load balancer back to blue. Zero-downtime, instant, and the bad version is just sitting there if you need to debug it. The cost is you need double the infrastructure running.
>
> **Canary**: Also easy. You're routing a percentage of traffic (say 10%) to the new version. Rollback is just routing 0% to the new version and 100% back to stable. You probably caught the issue before it hit most users.
>
> **Rolling**: This is the hard one. You're replacing pods one at a time. If the issue appears partway through, you have a mix of old and new versions running. You need to know *at which pod version* the issue appeared, and whether any data or schema changes are involved. If the new version wrote data the old version can't read, rolling back is risky. This is why I'm careful about schema changes with rolling deploys — you need backward-compatible migrations that can run before the code change, not at the same time.
>
> In practice: after a bad deploy I first check if it's a code issue or a config/infra issue. Code issue: trigger the rollback for the deploy strategy in use. Config issue: fix forward if it's fast. I also make sure to capture logs from the bad version before the rollback so we can do a proper post-mortem."

**Follow-up they might ask:** "What's a post-mortem?" — Answer: Blameless writeup after an incident — what happened, timeline, root cause, what we're changing to prevent recurrence. Blameless means you're fixing systems, not punishing people.

---

## 3. Docker & containers (on your resume)
- **Image** (immutable blueprint) vs **container** (running instance).
- **Dockerfile** basics: base image, copy code, install deps, expose port, CMD. Multi-stage builds to shrink images.
- **docker-compose** for local multi-service (API + Postgres + Redis).
- Best practices (you authored Docker checklists!): small base (slim/alpine), non-root user, layer caching, `.dockerignore`, pin versions, no secrets in image.

### Veteran layer — the Docker mistakes that bite AI-assisted devs

> "The Docker mistake that bites developers who move fast: the image works locally but fails in CI because they used a mutable `latest` tag for the base image and it silently got updated overnight. `FROM python:latest` in your Dockerfile means you're at the mercy of whatever was published that day. Pin your base image versions — `FROM python:3.11.9-slim` — so the build is reproducible.
>
> The second mistake: secrets passed as `ENV` in a Dockerfile leak into `docker history` and get baked into every layer. Anyone who pulls the image can run `docker history --no-trunc` and read them. Secrets go in at runtime — environment injection via your orchestrator (K8s Secrets, ECS task definition env vars), not in the Dockerfile. Use `ARG` for build-time values that aren't secrets, and inject actual secrets at runtime."

**Follow-up they might ask:** "What's a multi-stage build?" — Answer: Use one stage (e.g., a full build image) to compile/install dependencies, then copy only the artifacts into a minimal final stage. The result image doesn't contain the build tools, which shrinks it significantly and reduces the attack surface.

---

## 4. Kubernetes (on resume — basic talking points)
- Orchestrates containers: **Pods, Deployments (replicas/rolling updates), Services (networking), ConfigMaps/Secrets, Ingress**.
- Self-healing (restarts failed pods), horizontal pod autoscaling, declarative YAML.
- You validated "K8s pod health and real-time cluster dashboards" at Nokia — concrete.

---

## 5. Code Review — "Describe your code review process"

**Interviewer perspective:** This is a culture and seniority signal. They want to know if you review for *substance* or just rubber-stamp. They also want to know if you give feedback in a way that creates collaboration or friction.

**Model answer:**
> "I review in roughly this order of priority:
>
> **Correctness first**: Does this code do what it says? Are there edge cases where it breaks — empty lists, null values, concurrent writes? Does it handle errors, or does it let exceptions propagate silently?
>
> **Security boundaries**: Is user input sanitized? Are there any places where data from one user could leak to another? Are secrets hardcoded? Are we trusting client-supplied IDs without ownership checks?
>
> **Error handling and observability**: If something goes wrong, will we know? Is there logging at the right level? Are errors surfaced to the caller or swallowed?
>
> **Test coverage**: Not 100% coverage for its own sake — but are the important paths tested? Is the happy path covered? Are the error paths covered? If I break this code, will a test catch it?
>
> **Performance patterns**: N+1 queries are the most common one — looping over a result set and querying inside the loop. I look for these specifically because they're easy to introduce and catastrophic at scale.
>
> **What I don't nitpick**: style. If the project has a linter and formatter configured, I don't leave comments about indentation or naming conventions — that's the linter's job. I only comment on style if it genuinely affects readability and the linter doesn't cover it.
>
> **How I give feedback**: I ask questions rather than give commands. 'What happens here if the list is empty?' gets a better response than 'This will crash on empty lists, fix it.' The goal is the reviewer and the author both understanding the code better, not a power dynamic."

**Senior signal:** Prioritizes correctness and security over style. Mentions specific patterns (N+1). Describes the *tone* of feedback, not just the content.

---

## 6. Logging & Monitoring (JD explicit)
- **Structured logging** (JSON) with levels (DEBUG/INFO/WARN/ERROR), **correlation/request IDs** to trace a request across services. Logs to stdout (12-factor) → collected centrally (ELK/Loki/CloudWatch).
- **Metrics**: Prometheus + Grafana; track **RED** (Rate, Errors, Duration) / latency p50/p95/p99, throughput, error rate, resource use.
- **Tracing**: OpenTelemetry / Jaeger — follow a request across microservices.
- **Alerting**: thresholds → PagerDuty/Slack. **Health endpoints** for liveness/readiness.
- API logging specifics: log method, path, status, latency, user/request id — **never log secrets/PII/tokens**.

### Scenario: "What's the first thing you look at when there's a production incident?"

**Interviewer perspective:** Tests incident response maturity. The wrong answer is "I start looking everywhere." The right answer shows a systematic sequence that narrows the blast radius quickly.

**Model answer:**
> "My sequence is: alerts → which service → error logs with request ID → metrics → recent deploy.
>
> **Alerts first**: What fired? The alert message should tell me the symptom — high error rate, latency spike, health check failing. That points me to the service.
>
> **Error logs with request ID**: I go to the logs for that service and look at the errors. If we have structured logging with correlation IDs, I can trace a failing request end-to-end — what came in, where it broke, what the exception was. This is usually where I find the root cause or the first clear signal.
>
> **Metrics**: When did this start? I pull up the dashboard for that service — error rate, latency, throughput. I'm looking for the inflection point. Did it degrade gradually (a slow memory leak) or spike suddenly (a bad deploy or a downstream dependency going down)?
>
> **Recent deploy**: Did we ship something in the last few hours? If yes, that's the prime suspect. I check the diff for that service — what changed? This isn't blame, it's just the most common cause of sudden incidents.
>
> What I'm *not* doing: randomly restarting services or rolling back before I understand what's broken. A rollback is the right call if the evidence points to a bad deploy, but rolling back without diagnosis means you might roll back a fix or introduce a different problem.
>
> Once I have a hypothesis, I communicate to the team — 'here's what I think is wrong, here's what I'm doing, here's ETA.' Silence during an incident is almost as bad as the incident itself."

**Senior signal:** Systematic sequence, not chaos. Explicit about what *not* to do (blind restarts, silent rollbacks). Includes communication as part of incident response.

---

## 7. Agile (behavioral fuel)
- Scrum: sprints (1–2 wks), standups, sprint planning, retro, review/demo, backlog grooming.
- Roles: PO (priorities), Scrum Master, dev team. Stories, story points, velocity.
- Kanban: continuous flow, WIP limits.
- You delivered "Agile sprint reports", "zero missed deliveries" — use these.

---

## 8. Likely questions (full list)
1. Merge vs rebase — when do you use each? (§1 veteran layer)
2. Walk me through your Git workflow / how you handle a PR.
3. What's in a CI/CD pipeline? What runs on a PR? (§2)
4. How do you handle a broken CI pipeline that's blocking the team? (§2 scenario)
5. How do you deploy without downtime? (§2 rollback scenario)
6. Deployment went wrong — how do you roll back? (§2 rollback scenario)
7. Dockerfile best practices? (§3 + veteran layer)
8. How do you monitor/log a production API? (§6)
9. What's the first thing you look at during a production incident? (§6 scenario)
10. Describe your code review process. (§5)
11. How do you handle a merge conflict?
12. Describe your Agile process / how you handle sprint work. (§7)
