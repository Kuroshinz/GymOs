"""Script to seed the new newbie presets from the ChatGPT conversation into GymOS."""

import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.workout_program.manager import ProgramManager
from modules.workout.infrastructure.models import init_db, GoalConfigModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gymos.db")
PPL_NEWBIE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "program_ppl_ul_newbie.json")
UL_NEWBIE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "program_ul_newbie.json")

def main():
    print("Seeding new newbie presets...")
    init_db(DB_PATH)
    prog_mgr = ProgramManager(DB_PATH)
    
    # 1. Check & Seed PPL Newbie
    if os.path.exists(PPL_NEWBIE_PATH):
        # We check if already exists by checking the name
        exists = any(p["name"] == "PPL-UL Newbie" for p in prog_mgr.list_programs())
        if not exists:
            print("Importing PPL-UL Newbie...")
            prog_id, res = prog_mgr.import_and_save(PPL_NEWBIE_PATH)
            if prog_id:
                print(f"Successfully imported PPL-UL Newbie (ID: {prog_id})")
            else:
                print(f"Failed to import PPL-UL Newbie: {res.errors}")
        else:
            print("PPL-UL Newbie already exists.")
            
    # 2. Check & Seed Upper-Lower Newbie
    ul_id = None
    if os.path.exists(UL_NEWBIE_PATH):
        exists = any(p["name"] == "Upper-Lower Newbie" for p in prog_mgr.list_programs())
        if not exists:
            print("Importing Upper-Lower Newbie...")
            ul_id, res = prog_mgr.import_and_save(UL_NEWBIE_PATH)
            if ul_id:
                print(f"Successfully imported Upper-Lower Newbie (ID: {ul_id})")
            else:
                print(f"Failed to import Upper-Lower Newbie: {res.errors}")
        else:
            print("Upper-Lower Newbie already exists.")
            # find ID
            for p in prog_mgr.list_programs():
                if p["name"] == "Upper-Lower Newbie":
                    ul_id = p["id"]
                    
    # 3. Activate Upper-Lower Newbie (as per ChatGPT newest guidance)
    if ul_id:
        print(f"Activating Upper-Lower Newbie program...")
        success = prog_mgr.switch_to_program(ul_id)
        if success:
            print("Successfully activated Upper-Lower Newbie!")
        else:
            print("Failed to activate Upper-Lower Newbie.")
            
    # 4. Seed/Update Goal Config in DB (Lean bulk: target 72.0 kg, 300 kcal surplus)
    engine = create_engine(f"sqlite:///{DB_PATH}")
    with Session(engine) as session:
        goal = session.query(GoalConfigModel).filter_by(id="default").first()
        if not goal:
            goal = GoalConfigModel(
                id="default",
                target_weight_kg=72.0,
                target_calorie_surplus=300
            )
            session.add(goal)
            print("Created default goal config (Lean bulk: target 72.0kg, 300 kcal surplus)")
        else:
            goal.target_weight_kg = 72.0
            goal.target_calorie_surplus = 300
            print("Updated goal config to Lean bulk (target 72.0kg, 300 kcal surplus)")
        session.commit()
        
    prog_mgr.dispose()
    print("Done!")

if __name__ == "__main__":
    main()
