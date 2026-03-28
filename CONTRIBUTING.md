# Contributing to Auto Idea Combiner

Thank you for your interest in contributing!

## Branch Strategy

```
main          ← stable, production-ready
feature/xxx   ← new features
fix/xxx       ← bug fixes
docs/xxx      ← documentation only
refactor/xxx  ← refactoring without behavior change
```

Always branch from `main` and open a PR back to `main`.

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Wikipedia collector module
fix: correct endpoint path in client.ts
docs: update SETUP.md with Windows instructions
refactor: simplify scoring weight normalization
chore: bump dependencies
```

## Backend (Python)

**Code style**: Ruff

```bash
cd backend
uv run ruff check .
uv run ruff format .
```

**Type checking**: mypy (strict mode)

```bash
uv run mypy backend/
```

**Tests** (when added):

```bash
uv run pytest
```

Requirements:
- Python 3.11+
- All public functions must have type annotations
- New modules need `__init__.py`
- No secrets in source code — use `.env` only

## Frontend (TypeScript / React)

**Linting**:

```bash
cd frontend
pnpm lint
```

**Type checking**:

```bash
pnpm tsc --noEmit
```

Requirements:
- TypeScript strict mode (no `any` without justification)
- React components: functional components + hooks only
- Tailwind CSS for styling (no inline styles)
- All API calls go through `src/api/client.ts`

## Pull Request Checklist

- [ ] Branch name follows convention (`feature/`, `fix/`, etc.)
- [ ] Commit messages follow Conventional Commits
- [ ] Backend: `ruff check` passes
- [ ] Frontend: `tsc --noEmit` passes
- [ ] No API keys or secrets committed
- [ ] PR description explains what and why

## Project Structure

```
backend/         # Python FastAPI backend
  collectors/    # Data collection (local files, clipboard, APIs)
  processing/    # Text cleaning + concept extraction
  embedding/     # Vector embedding + ChromaDB
  combiner/      # Concept pair selection logic
  llm/           # LLM adapters + prompts
  scoring/       # Idea scoring
  feedback/      # Weight learning from feedback
  models/        # SQLite models

frontend/        # Tauri 2.x + React 18
  src/
    api/         # Backend API client
    components/  # Reusable UI components
    pages/       # Tab-level page components
    types/       # Shared TypeScript types
  src-tauri/     # Rust/Tauri configuration
```
