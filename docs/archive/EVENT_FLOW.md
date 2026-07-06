# Event Flow

## Workout Lifecycle

```
WorkoutPublisher                  EventBus                    Subscribers
──────────────                    ────────                    ───────────
publish_workout_started()  ───>  WorkoutStarted
                                ├── AnalyticsSubscriber (logs)
                                ├── GymBrainSubscriber (queues)
                                └── DashboardSubscriber (updates)

publish_set_completed()    ───>  SetCompleted
                                └── AnalyticsSubscriber (logs)

publish_exercise_completed() ──> ExerciseCompleted
                                └── AnalyticsSubscriber (logs)

publish_workout_completed() ──>  WorkoutCompleted
                                ├── PRSubscriber
                                │   └── publishes PersonalRecordUnlocked
                                │       ├── AnalyticsSubscriber
                                │       ├── DashboardSubscriber
                                │       └── GymBrainSubscriber
                                ├── RecoverySubscriber
                                │   └── publishes RecoveryScoreUpdated
                                │       ├── AnalyticsSubscriber
                                │       └── GymBrainSubscriber
                                ├── VolumeSubscriber (records volume)
                                ├── AnalyticsSubscriber (logs)
                                ├── DashboardSubscriber (updates)
                                └── GymBrainSubscriber (queues)
```

## Program Lifecycle

```
ProgramPublisher                  EventBus                    Subscribers
──────────────                    ────────                    ───────────
publish_program_imported()  ──>   ProgramImported
                                ├── AnalyticsSubscriber (logs)
                                └── DashboardSubscriber (updates)

publish_program_activated() ──>   ProgramActivated
                                ├── AnalyticsSubscriber (logs)
                                ├── DashboardSubscriber (updates)
                                └── GymBrainSubscriber (records)
```

## Knowledge Lifecycle

```
KnowledgePublisher                EventBus                    Subscribers
────────────────                  ────────                    ───────────
publish_exercise_updated()  ──>   ExerciseKnowledgeUpdated
                                ├── AnalyticsSubscriber (logs)
                                └── GymBrainSubscriber (queues)
```

## Nutrition Lifecycle

```
NutritionPublisher                EventBus                    Subscribers
─────────────────                 ────────                    ───────────
publish_meal_logged()       ──>   MealLogged
                                └── AnalyticsSubscriber (logs)
```

## Body Weight

```
WorkoutPublisher                  EventBus                    Subscribers
──────────────                    ────────                    ───────────
publish_body_weight_updated() ──> BodyWeightUpdated
                                ├── AnalyticsSubscriber (logs)
                                ├── DashboardSubscriber (updates)
                                └── GymBrainSubscriber (records)
```

## Correlation Chain Example

A single workout completion triggers a chain of events, all linked by the same `correlation_id`:

```
WorkoutCompleted(correlation_id="abc123")
  └── PersonalRecordUnlocked(correlation_id="abc123")
  └── RecoveryScoreUpdated(correlation_id="abc123")
```

This enables tracing a complete user action across the entire system.
