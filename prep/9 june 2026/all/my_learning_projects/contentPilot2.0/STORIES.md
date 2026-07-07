# ContentPilot — Stories From the Field

This file exists for one reason: features are easy to list and easy to forget *why they
matter*. Every scenario below is either something that has actually happened while building
and testing ContentPilot, or something realistic enough that it will happen the first month
someone other than the builder relies on it. Read this before designing Phase 4 (scheduling +
drafts) or any future phase — it's the "why," not the "what."

---

## Prologue: The 2 AM Promise

Somewhere in a `README.md`, ContentPilot makes a promise:

> "It runs on a schedule, checks for trending content, generates posts, and pushes them
> live — without you doing anything."

That sentence is the whole pitch. It's also, as of today, not quite true — and the gap between
the promise and the reality is where every story below comes from.

---

## Story 1: The Midnight Run That Wasn't

**User story:** *As a solo builder, I want ContentPilot to publish new content while I sleep,
so that my site stays active without me manually running a script every morning.*

It's 11:58 PM. Before bed, the plan is simple: set up a cron job, let ContentPilot run at
6 AM, wake up to fresh posts. The command goes into `crontab -e`:

```
0 6 * * * cd ~/contentpilot && python main.py
```

Morning comes. No new posts. No error either — just silence. The cron log shows the process
started and exited in under a second. The reason: `main.py` opens with
`IntPrompt.ask("How many trending topics today")` — a blocking prompt waiting for keyboard
input that will never arrive from a cron job. Typer's `IntPrompt` doesn't time out; it just
sits there until cron kills the job for exceeding some invisible limit, or it silently exits
because there's no TTY to read from.

**The failure scenario, concretely:** a headless, non-interactive invocation of `main.py`
cannot get past the first question. There is currently no `--topics N` style flag — interactive
prompts are the *only* entry point. This is not a bug so much as a missing feature, but it's
the one that makes the README's core promise false today.

**What "done" looks like:** `contentpilot run --topics 3 --prompts 1 --workflows 1 --categories all`
runs to completion with zero keyboard input, exit code reflects success/failure, and cron (or
any scheduler) can rely on it.

---

## Story 2: The Commit That Ate a Day's Work

**User story:** *As a developer actively working in my target repo, I want ContentPilot to
touch only the files it generates, so that running it doesn't interfere with my own
uncommitted work.*

Picture a Tuesday afternoon. Someone is mid-refactor on their site's homepage — new files
staged with `git add`, not yet committed, waiting for a coffee break to finish the change.
They remember ContentPilot hasn't run today, so they fire it off in another terminal tab to
keep content fresh in the background.

Twenty seconds later, `git log` shows a new commit: `content: add prompt 'some-ai-topic'`.
That sounds right — except `git show --stat` on that commit reveals it also contains the
half-finished homepage refactor. `GitPublisher.publish()` called `self.repo.index.commit()`,
and `index.commit()` doesn't commit *the file it just added* — it commits **everything
currently staged**, indiscriminately. The refactor, mid-thought and not ready for review, is
now in the commit history and — if `push()` succeeds — on the remote.

**The failure scenario, concretely:** any staged-but-uncommitted change in the target repo at
the moment ContentPilot runs gets silently folded into its auto-generated commit and
potentially pushed live. No warning, no diff shown, no confirmation. The user finds out only by
reading the commit contents after the fact — if they think to check at all.

**What "done" looks like (fixed 2026-07-02):** `GitPublisher.publish()` and `delete()` now use
pathspec-scoped commits (`git commit -m "..." -- <path>`), which commit *only* changes to the
specified file, leaving anything else staged exactly as the user left it. Covered by
`test_publish_does_not_commit_unrelated_staged_changes` in `tests/agents/test_git_publisher.py`.
This was the single highest-severity issue found in this codebase — worth remembering as the
reason draft-mode (Story 3) isn't optional polish, it's a second, independent safety net on
top of this fix.

---

## Story 3: The Post About ZCode

**User story:** *As a site owner, I want a chance to review AI-generated content before it's
public, so that hallucinated or embarrassing content never reaches my actual audience.*

A test run, two topics, local model (`phi3:mini`, chosen because it's free and fast). One post
comes out solid — a real synthetic-biology story, accurately dated, factually coherent. The
second post is titled *"Unveiling ZCode — A New Era for GLM."* It describes, in confident
prose, a product that does not exist, made by a company that does not exist, with a fabricated
image path in the frontmatter. The model took a fragment of a real headline and confabulated an
entire announcement around it.

In today's pipeline, both posts follow the identical path: generate → write file → `git commit`
→ `git push`. There is no checkpoint between "the model finished generating text" and "this
text is now live on the internet under this site's name." If this had been a real scheduled run
against a real site with a real audience, the fabricated post would have been public before
anyone read it.

**The failure scenario, concretely:** small/local models (and even larger ones, occasionally)
hallucinate confidently and undetectably from a glance — the ZCode post *reads* professionally.
Nothing in the current pipeline distinguishes "plausible but false" from "true." Auto-publish
is the only mode that exists.

**What "done" looks like:** a `draft` status becomes real (already added to
`PostEntry.status` as of 2026-07-02, ahead of the pipeline wiring). Scheduled/unattended runs
default to writing drafts, not live posts — a human approves or rejects each one from the
dashboard before it ever reaches the target repo. `--publish` (or a dashboard toggle) remains
available for someone who trusts a specific model/config enough to skip the checkpoint
deliberately — but that becomes an opt-in choice, not the only path.

---

## Story 4: "Wait, Where Did It Push To?"

**User story:** *As someone testing ContentPilot for the first time, I want it to be obvious
whether my changes went to my real site or nowhere at all, so I don't waste time checking a
live site that was never touched.*

The dashboard says "Done! Check your dashboard: http://localhost:8000." A post appears in the
list, styled and complete, with a git commit SHA next to it. Naturally, the next move is to
check the live site. Nothing's changed. Deploy log shows no new build. Minutes pass before the
realization: the run's `target_repo` was pointed at a scratch/test directory with no `origin`
remote configured, so `push()` failed with `"No item found with id origin"` — logged as a
one-line warning to stderr, easy to miss in a scrollback, invisible from the dashboard entirely.

**The failure scenario, concretely:** the dashboard's success language ("Done!", a commit SHA
shown) doesn't distinguish "committed locally" from "pushed to a live remote." A user can
reasonably read a commit SHA as proof of a live deploy when it's proof of neither more nor less
than a local commit.

**What "done" looks like:** the dashboard's post/pipeline views should surface push status
explicitly — not just a commit SHA, but whether `push()` actually succeeded, and if not, why.
This becomes more important, not less, once scheduled unattended runs exist: nobody's watching
stderr at 6 AM.

---

## Story 5: One Process to Rule Them All

**User story:** *As the person operating this tool, I want a single place to see what's
scheduled, trigger a run manually, and approve what's waiting — instead of juggling a crontab,
a terminal, and a dashboard that don't talk to each other.*

This is less a failure story and more the shape of the fix. Once scheduling and drafts both
exist, there are three ways a pipeline run could start: a cron job calling the CLI with flags,
a person clicking "Run Now" in the dashboard, or a recurring job the scheduler fires on its
own. All three should hand off to the exact same `Orchestrator.run(...)`, so behavior never
diverges between "the version that ran automatically" and "the version I ran by hand." And all
three should leave their output in the same place — the dashboard's drafts queue — so there's
one queue to check, not three logs in three terminals.

**What "done" looks like:** the FastAPI dashboard process is the single thing worth keeping
running. It hosts the scheduler (APScheduler, in-process, per the Design Standards section of
`README.md`), exposes a "Run Now" trigger, and is where drafts get approved or rejected. Cron
remains available as a flag-driven alternative for headless setups that skip the dashboard
entirely — but for anyone running the dashboard, it *is* the control panel.

---

## Epilogue

None of these stories describe ContentPilot as broken. The pipeline works — trend discovery,
generation, image creation, git operations, the dashboard's three pages, all 39 tests passing.
What these stories describe is the gap between "a tool that works when you run it" and "a
system you can trust to run itself." That gap is exactly Phase 4, and it's why draft-by-default
and the git-commit fix aren't the interesting 20% of the work — they're the entire reason the
other 80% is safe to automate.
