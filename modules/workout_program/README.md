# Workout Program Module

## Responsibilities
- Import workout programs from JSON files
- Validate program structure and exercise references
- Store programs in SQLite database
- Activate/switch between workout programs
- Provide program data to the UI and GymBrain

## Dependencies
- `shared/knowledge_loader.py` — Exercise ID validation via KnowledgeLoader
- `data/gymos.db` — SQLite database via ProgramRepository
- `data/program.json` — Canonical default program

## Exported Types
- `WorkoutProgram`, `ProgramDay`, `ProgramExercise` — domain models
- `ProgramValidator`, `ValidationResult`, `ValidationError` — validation types
- `ProgramImporter` — JSON import logic
- `ProgramRepository` — SQLite storage
- `ProgramManager` — public facade (import, activate, list, switch)

## Extension Points
- **New program format**: Add parser in `importer.py` that returns `WorkoutProgram`
- **Custom validation rules**: Extend `ProgramValidator` with additional checks
- **Program marketplace**: Add `ProgramImporter.from_url()` for remote program import

## Known Limitations
- Flat structure (not 4-layered DDD) — acceptable for current complexity
- Program auto-import only on first run (no re-import mechanism for updates)
- No program export to JSON

## Architecture

```
workout_program/
├── domain.py         # WorkoutProgram, ProgramDay, ProgramExercise
├── validator.py      # ProgramValidator, ValidationResult, ValidationError
├── importer.py       # ProgramImporter (JSON → domain)
├── repository.py     # ProgramRepository (domain → SQLite)
└── manager.py        # ProgramManager (public facade)
```

## Roadmap
- Sprint 3.3+ : Add program export to JSON
- Sprint 3.3+ : Add program comparison/diff view
- Sprint 3.4+ : Support custom program creation in UI
