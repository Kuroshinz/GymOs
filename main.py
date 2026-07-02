#!/usr/bin/env python3
"""NEXUS - Next Evolution Exercise & Unified System"""

import asyncio
import sys
from datetime import datetime

from nexus import platform
from core.event_bus import Event


class DemoCLI:
    def __init__(self) -> None:
        self._running = True

    async def run(self) -> None:
        await platform.start()
        self._register_demo_handlers()

        while self._running:
            print("\n" + "=" * 50)
            print("  NEXUS PLATFORM DEMO")
            print("=" * 50)
            print("  1. Start a workout")
            print("  2. Complete workout")
            print("  3. Log a meal")
            print("  4. Show platform status")
            print("  5. Test Event Bus flow")
            print("  0. Exit")
            print("=" * 50)

            choice = input("  Choose: ").strip()
            await self._handle_choice(choice)

        await platform.shutdown()

    def _register_demo_handlers(self) -> None:
        bus = platform.event_bus

        async def on_workout_created(event: Event) -> None:
            print(f"  [Engine] WorkoutEngine received: workout {event.data['id']} created")
        bus.on("workout.created", on_workout_created)

        async def on_workout_completed(event: Event) -> None:
            d = event.data
            print(f"  [Engine] AnalyticsEngine: logging {d['volume']}kg volume")
            print(f"  [Engine] RecoveryEngine: calculating recovery from {d['duration']}min workout")
            print(f"  [Engine] PredictionEngine: predicting next performance...")
        bus.on("workout.completed", on_workout_completed)

        async def on_meal_logged(event: Event) -> None:
            d = event.data
            print(f"  [Engine] NutritionEngine: {d['calories']}kcal logged")
            print(f"  [Engine] AnalyticsEngine: updating nutrition trends")
        bus.on("nutrition.meal_logged", on_meal_logged)

    async def _handle_choice(self, choice: str) -> None:
        if choice == "1":
            name = input("  Workout name: ").strip() or "Upper Body"
            workout_id = datetime.now().strftime("%Y%m%d%H%M%S")
            await platform.event_bus.emit("workout.created", {
                "id": workout_id,
                "name": name,
                "started_at": datetime.now().isoformat(),
            })
            print(f"  ✅ Workout '{name}' started (ID: {workout_id})")

        elif choice == "2":
            wid = input("  Workout ID: ").strip() or "demo"
            await platform.event_bus.emit("workout.completed", {
                "workout_id": wid,
                "duration": 45,
                "volume": 8520,
                "exercises": 6,
            })
            print(f"  ✅ Workout {wid} completed")

        elif choice == "3":
            meal = input("  Meal name: ").strip() or "Chicken Rice"
            cal = float(input("  Calories: ").strip() or "750")
            prot = float(input("  Protein (g): ").strip() or "45")
            await platform.event_bus.emit("nutrition.meal_logged", {
                "meal": meal,
                "calories": cal,
                "protein": prot,
                "date": datetime.now().date().isoformat(),
            })
            print(f"  ✅ '{meal}' logged")

        elif choice == "4":
            print(f"\n  Platform: {platform.__class__.__name__}")
            print(f"  Status: {'Running' if platform._initialized else 'Stopped'}")
            print(f"  Services in DI container: {len(platform.container._services)}")
            print(f"  Event handlers: {sum(len(v) for v in platform.event_bus._handlers.values())}")
            print(f"  Plugins registered: {len(platform.plugins.all)}")

        elif choice == "5":
            print("\n  Simulating full workout flow with Event Bus...")
            wid = "flow-" + datetime.now().strftime("%H%M%S")
            await platform.event_bus.emit("workout.created", {"id": wid, "name": "Full Flow Demo"})
            await asyncio.sleep(0.3)
            await platform.event_bus.emit("workout.completed", {"workout_id": wid, "duration": 60, "volume": 12000})
            await asyncio.sleep(0.3)
            await platform.event_bus.emit("nutrition.meal_logged", {"meal": "Post-workout shake", "calories": 400, "protein": 30})

        elif choice == "0":
            self._running = False

        else:
            print("  Invalid choice")


async def async_main() -> None:
    cli = DemoCLI()
    await cli.run()


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
