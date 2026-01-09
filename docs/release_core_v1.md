# Core v1 Release Procedure

This file documents the exact commands for tagging and branching Core v1.
Do not run these commands here; execute them manually when ready.

Suggested commit message
```
chore(release): freeze Core v1 frontend contract
```

Commands
```
git status
git add docs tests src
git commit -m "chore(release): freeze Core v1 frontend contract"

git tag core-v1.0.0
git branch release/core-v1

git push origin main
git push origin core-v1.0.0
git push origin release/core-v1
```

Branch protection checklist (GitHub)
- Require PRs for `main` and `release/core-v1`
- Require status checks: `black --check .`, `ruff .`, `pytest -q`
- Require signed commits (optional)
- Block force pushes
