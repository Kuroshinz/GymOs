# Module Boundaries

## Rules

1. **No circular imports** between layers
2. **Domain has zero dependencies** on infrastructure
3. **Application depends on domain** only
4. **Presentation depends on application**
5. **Infrastructure implements application ports**

## Dependency Flow

```
Presentation → Application → Domain
                    ↓
           Infrastructure
```

## Enforcement

- `domain/` imports only stdlib + shared types
- `application/` imports domain + shared
- `infrastructure/` imports application interfaces
- `presentation/` imports application

## Cross-Module Communication

- Modules communicate **only** via EventBus events
- No direct imports between modules (e.g., Workout → Nutrition)
- Events define the contract between modules
