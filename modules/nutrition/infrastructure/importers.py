"""Nutrition Import/Export System — adapter-based CSV and JSON import.

Design:
  - Each importer is an adapter class implementing a common interface
  - Future: API provider adapters (Cronometer, MyFitnessPal)
  - Never depend on Cronometer-specific formats; wrap in adapters
"""

from __future__ import annotations

import csv
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from modules.nutrition.domain import DailyNutrition, Meal, MealItem, MealType

logger = logging.getLogger("nexus.nutrition.importers")


@dataclass
class ImportResult:
    """Result of a nutrition import operation."""
    success: bool = False
    entries_imported: int = 0
    errors: list[str] = field(default_factory=list)
    days: list[DailyNutrition] = field(default_factory=list)


@dataclass
class ExportResult:
    """Result of a nutrition export operation."""
    success: bool = False
    path: str = ""
    entries_exported: int = 0
    errors: list[str] = field(default_factory=list)


# ─── Base Importer ─────────────────────────────────────────

class NutritionImporter(ABC):
    """Abstract base for all nutrition importers."""

    @abstractmethod
    def can_handle(self, filepath: str) -> bool:
        """Check if this importer can handle the given file."""
        ...

    @abstractmethod
    def import_file(self, filepath: str) -> ImportResult:
        """Import nutrition data from a file."""
        ...

    def preview(self, filepath: str) -> dict[str, Any]:
        """Preview what would be imported from a file."""
        result = self.import_file(filepath)
        return {
            "entries": len(result.days),
            "date_range": (
                f"{result.days[0].date} to {result.days[-1].date}"
                if len(result.days) >= 2
                else result.days[0].date if result.days else "None"
            ),
            "total_calories": sum(d.total_calories for d in result.days),
            "total_protein": sum(d.total_protein for d in result.days),
            "errors": result.errors,
        }


# ─── CSV Importer ──────────────────────────────────────────

class CSVNutritionImporter(NutritionImporter):
    """Import nutrition data from CSV files.

    Expected CSV columns (case-insensitive):
      date, meal_name, item_name, calories, protein_g, carbs_g, fat_g, fiber_g, quantity, unit, water_ml
    """

    def can_handle(self, filepath: str) -> bool:
        return filepath.lower().endswith(".csv")

    def import_file(self, filepath: str) -> ImportResult:
        result = ImportResult()
        try:
            with open(filepath, encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None:
                    result.errors.append("Empty CSV file")
                    return result

                days_map: dict[str, dict[str, Any]] = {}
                for row_num, row in enumerate(reader, start=2):
                    try:
                        self._process_row(row, days_map)
                    except Exception as e:
                        result.errors.append(f"Row {row_num}: {e}")

                for date_str, day_data in days_map.items():
                    meals = day_data.get("meals", [])
                    day = DailyNutrition(
                        date=date_str,
                        meals=meals,
                        water_ml=day_data.get("water_ml", 0.0),
                    )
                    result.days.append(day)
                    result.entries_imported += 1

                result.success = len(result.errors) == 0
        except FileNotFoundError:
            result.errors.append(f"File not found: {filepath}")
        except Exception as e:
            result.errors.append(f"Import failed: {e}")

        return result

    def _process_row(self, row: dict[str, str], days_map: dict[str, dict]) -> None:
        date = row.get("date", "").strip()
        if not date:
            raise ValueError("Missing 'date' column")

        if date not in days_map:
            days_map[date] = {"meals": [], "water_ml": 0.0}

        # Parse water if present
        water_str = row.get("water_ml", "").strip()
        if water_str:
            try:
                days_map[date]["water_ml"] = float(water_str)
            except ValueError:
                pass

        # Parse meal
        meal_name = row.get("meal_name", "").strip()
        item_name = row.get("item_name", "").strip()
        if not meal_name and not item_name:
            return  # Skip rows without meal or item data

        if not meal_name:
            meal_name = "Meal"

        def _float(val: str) -> float:
            try:
                return float(val) if val.strip() else 0.0
            except ValueError:
                return 0.0

        item = MealItem(
            name=item_name or meal_name,
            calories=_float(row.get("calories", "0")),
            protein_g=_float(row.get("protein_g", "0")),
            carbs_g=_float(row.get("carbs_g", "0")),
            fat_g=_float(row.get("fat_g", "0")),
            fiber_g=_float(row.get("fiber_g", "0")),
            quantity=_float(row.get("quantity", "1")),
            unit=row.get("unit", "serving").strip() or "serving",
        )

        # Find or create meal
        existing_meal = None
        for m in days_map[date].get("meals", []):
            if m.name == meal_name:
                existing_meal = m
                break

        if existing_meal:
            existing_meal.items.append(item)
        else:
            meal = Meal(name=meal_name, items=[item])
            days_map[date].setdefault("meals", []).append(meal)


# ─── JSON Importer ─────────────────────────────────────────

class JSONNutritionImporter(NutritionImporter):
    """Import nutrition data from JSON files.

    Expected JSON structure:
    {
      "days": [
        {
          "date": "2024-01-01",
          "water_ml": 3000.0,
          "meals": [
            {
              "name": "Breakfast",
              "items": [
                {"name": "Oats", "calories": 300, "protein_g": 10, ...}
              ]
            }
          ]
        }
      ]
    }
    """

    def can_handle(self, filepath: str) -> bool:
        return filepath.lower().endswith(".json")

    def import_file(self, filepath: str) -> ImportResult:
        result = ImportResult()
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                days_data = data
            elif isinstance(data, dict):
                days_data = data.get("days", data.get("entries", [data]))
            else:
                result.errors.append("Unrecognized JSON structure")
                return result

            for entry in days_data:
                try:
                    day = self._parse_day(entry)
                    result.days.append(day)
                    result.entries_imported += 1
                except Exception as e:
                    date_str = entry.get("date", "unknown")
                    result.errors.append(f"Error parsing entry {date_str}: {e}")

            result.success = len(result.errors) == 0
        except FileNotFoundError:
            result.errors.append(f"File not found: {filepath}")
        except json.JSONDecodeError as e:
            result.errors.append(f"Invalid JSON: {e}")
        except Exception as e:
            result.errors.append(f"Import failed: {e}")

        return result

    def _parse_day(self, entry: dict) -> DailyNutrition:
        meals = []
        for meal_data in entry.get("meals", []):
            items = [
                MealItem(
                    name=i.get("name", "Item"),
                    calories=float(i.get("calories", 0)),
                    protein_g=float(i.get("protein_g", i.get("protein", 0))),
                    carbs_g=float(i.get("carbs_g", i.get("carbs", 0))),
                    fat_g=float(i.get("fat_g", i.get("fat", 0))),
                    fiber_g=float(i.get("fiber_g", i.get("fiber", 0))),
                    quantity=float(i.get("quantity", 1)),
                    unit=i.get("unit", "serving"),
                )
                for i in meal_data.get("items", [])
            ]

            meal_type = None
            mt = meal_data.get("meal_type", "")
            if mt:
                try:
                    meal_type = MealType(mt)
                except ValueError:
                    pass

            meals.append(Meal(
                name=meal_data.get("name", "Meal"),
                meal_type=meal_type,
                items=items,
                eaten_at=datetime.fromisoformat(meal_data["eaten_at"]) if meal_data.get("eaten_at") else None,
                notes=meal_data.get("notes", ""),
            ))

        return DailyNutrition(
            date=entry.get("date", ""),
            meals=meals,
            water_ml=float(entry.get("water_ml", entry.get("water", 0))),
            notes=entry.get("notes", ""),
        )


# ─── Exporters ─────────────────────────────────────────────

class NutritionExporter:
    """Export nutrition data to various formats."""

    def export_csv(self, days: list[DailyNutrition], filepath: str) -> ExportResult:
        result = ExportResult()
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "date", "meal_name", "item_name", "calories",
                    "protein_g", "carbs_g", "fat_g", "fiber_g",
                    "quantity", "unit", "water_ml",
                ])
                count = 0
                for day in days:
                    for meal in day.meals:
                        for item in meal.items:
                            writer.writerow([
                                day.date, meal.name, item.name,
                                item.calories, item.protein_g,
                                item.carbs_g, item.fat_g, item.fiber_g,
                                item.quantity, item.unit, day.water_ml if len(meal.items) > 0 else "",
                            ])
                            count += 1
                result.success = True
                result.path = filepath
                result.entries_exported = count
        except Exception as e:
            result.errors.append(str(e))
        return result

    def export_json(self, days: list[DailyNutrition], filepath: str) -> ExportResult:
        result = ExportResult()
        try:
            data = {"days": []}
            for day in days:
                day_data = {
                    "date": day.date,
                    "water_ml": day.water_ml,
                    "meals": [
                        {
                            "name": meal.name,
                            "meal_type": meal.meal_type.value if meal.meal_type else None,
                            "notes": meal.notes,
                            "items": [
                                {
                                    "name": item.name,
                                    "calories": item.calories,
                                    "protein_g": item.protein_g,
                                    "carbs_g": item.carbs_g,
                                    "fat_g": item.fat_g,
                                    "fiber_g": item.fiber_g,
                                    "quantity": item.quantity,
                                    "unit": item.unit,
                                }
                                for item in meal.items
                            ],
                        }
                        for meal in day.meals
                    ],
                }
                data["days"].append(day_data)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            result.success = True
            result.path = filepath
            result.entries_exported = len(days)
        except Exception as e:
            result.errors.append(str(e))
        return result
