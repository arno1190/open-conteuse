# Codex cloud operation

This repository is designed for bounded autonomous tasks. AGENTS.md provides the working contract; docs/ROADMAP.md provides task order. A GitHub Actions check is not an always-running Codex agent.

## Environment

Python 3.11+ and Git are sufficient for M1. Run `sh scripts/check.sh`. GitHub Actions uses Python 3.12. A future firmware environment should install the selected pinned toolchain only after the board and upstream decision; do not require it for host tests.

Configure a reusable Codex Cloud environment with this repository on main and GitHub write access. No AI/content-provider secrets are required for M1. Do not copy cloud login tokens into the repository. A task that runs only on a transient default computer must push its commits before ending, following the publication policy in AGENTS.md.

## First task prompt

> Work in arno1190/open-conteuse. Read AGENTS.md and docs/ROADMAP.md. Implement M1 as a complete runnable vertical slice, starting from the current validator. Make routine choices autonomously, test failure paths, document actual results and update the roadmap. For this first iteration, if you do all work yourself without subagents, run the checks and commit/push directly to main. If you spawn subagents or delegate implementation, use a feature branch and open a reviewable PR instead. The orchestration agent may authorize and execute the merge, or enable auto-merge, after reviewing the complete diff and confirming checks pass for the exact PR head commit; record authorization and the reviewed SHA in the PR. New commits require renewed review. Subagents cannot authorize their own merges. Respect branch protection and required reviews/checks. Never force-push, and preserve concurrent contributions. If hardware or credentials block a later feature, record that dependency and continue the independent software work. No purchases or paid services. Finish with implemented scope, checks, limitations and next task.

## Verify dispatch

Record the returned cloud task URL and check its status before claiming it is running. Local `codex login status` alone does not prove cloud task API access. Dispatch/authentication failures must be reported explicitly. Do not claim continuous development after a task ends; launch another task or configure an owner-approved automation separately.

## Bootstrap access check (2026-11-17)

The current managed cloud computer runs the host checks successfully. Creating `arno1190/open-conteuse` with the connected GitHub integration failed with `Resource not accessible by integration (createRepository)`. No remote repository was created by that attempt. The Codex CLI reports a ChatGPT login, but `codex cloud list --json` fails with HTTP 401 (`Could not parse your authentication token`). No separate Codex Cloud task has been submitted.

To unblock: create an empty GitHub repository named `arno1190/open-conteuse` (without an initial README/licence/gitignore), grant the connected GitHub app access, then push this committed main branch. Reauthenticate the Codex Cloud CLI or use the Codex UI to create a Cloud environment for the new repository and run the first-task prompt above. Verify the task URL/status. These are service permission/authentication failures, not code-test failures.

## GitHub access resolved (2026-11-17)

The owner created the public repository. Verified ADMIN access and successfully pushed the prepared main branch to https://github.com/arno1190/open-conteuse. The earlier repository-creation blocker is resolved; cloud task authentication is a separate check.
