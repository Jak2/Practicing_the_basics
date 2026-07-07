#!/usr/bin/env bash
# One job, one script: pulls real file content from nested project repos
# into this workspace repo, then pushes a snapshot of the whole workspace
# into a subfolder of Jak2/Practicing_the_basics.
#
# Step 1 (sync nested projects): each of these folders has its own .git, so
# a plain `git add` would stage them as empty "embedded repo" pointers, not
# real file content. This temporarily hides each nested .git, commits the
# real files into the workspace repo, then restores every .git — those
# project repos keep working independently, untouched, afterward.
#
# Step 2 (push snapshot): uses `git archive` (not rsync/cp) so only
# committed, .gitignore-respecting files get exported — real .env secrets,
# venvs, and books/ never leave this machine.
#
# Re-run anytime: re-clones the target fresh and re-syncs nested projects,
# so there's no stale-state risk.

set -euo pipefail

WORKSPACE_DIR="/media/asterisk/windows_drive/project/learn"
TARGET_REPO="https://github.com/Jak2/Practicing_the_basics.git"
TARGET_SUBPATH="prep/9 june 2026/all"
CLONE_DIR="/tmp/practicing_the_basics"
BACKUP_DIR="/tmp/nested_git_backup_$$"
SYNC_COMMIT_MSG="Sync nested project files into workspace repo"
PUSH_COMMIT_MSG="Add 9 june 2026 workspace snapshot"

NESTED_REPOS=(
  "interview_prep/resume_prep"
  "interview_prep/job_description/right_job.in"
  "my_learning_projects/Bias_Fairness_Auditor_Report"
  "my_learning_projects/Blog"
  "my_learning_projects/contentpilot"
  "my_learning_projects/contentPilot2.0"
  "my_learning_projects/ems_2.0"
  "my_learning_projects/expense_tracker"
  "my_learning_projects/llm-eval-framework"
  "my_learning_projects/outflo"
  "my_learning_projects/portfolio"
  "my_learning_projects/Prompt_Regression_Suite_Report"
  "my_learning_projects/trend_engine"
  "my_learning_projects/tools/career-ops"
  "my_learning_projects/tools/markitdown"
)

cd "$WORKSPACE_DIR"
mkdir -p "$BACKUP_DIR"

restore_git_dirs() {
  echo "Restoring nested .git directories..."
  for repo in "${NESTED_REPOS[@]}"; do
    if [ -d "$BACKUP_DIR/$repo" ]; then
      mkdir -p "$(dirname "$WORKSPACE_DIR/$repo")"
      mv "$BACKUP_DIR/$repo" "$WORKSPACE_DIR/$repo/.git"
    fi
  done
  rm -rf "$BACKUP_DIR"
}
trap restore_git_dirs EXIT

echo "=== Step 1: syncing nested project files into workspace repo ==="
echo "Hiding nested .git directories so their files get added as content..."
for repo in "${NESTED_REPOS[@]}"; do
  if [ -d "$WORKSPACE_DIR/$repo/.git" ]; then
    mkdir -p "$BACKUP_DIR/$(dirname "$repo")"
    mv "$WORKSPACE_DIR/$repo/.git" "$BACKUP_DIR/$repo"
  fi
done

git add -A
git commit -m "$SYNC_COMMIT_MSG" || echo "Nothing changed, skipping commit."

echo "=== Step 2: pushing workspace snapshot ==="
echo "Cloning target repo fresh..."
rm -rf "$CLONE_DIR"
git clone "$TARGET_REPO" "$CLONE_DIR"

echo "Exporting tracked files from $WORKSPACE_DIR (git archive, respects .gitignore)..."
mkdir -p "$CLONE_DIR/$TARGET_SUBPATH"
git archive HEAD | tar -x -C "$CLONE_DIR/$TARGET_SUBPATH"

echo "Committing and pushing..."
cd "$CLONE_DIR"
git add -A
git commit -m "$PUSH_COMMIT_MSG" || echo "Nothing changed, skipping commit."
git push origin master

echo "Cleaning up temp clone..."
cd /
rm -rf "$CLONE_DIR"

echo "Done. Pushed to $TARGET_REPO under '$TARGET_SUBPATH'."
# restore_git_dirs runs automatically via the EXIT trap, even on error
