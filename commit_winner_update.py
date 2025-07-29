import json
import subprocess
from pathlib import Path

# 🔧 Set your project path
project_dir = Path(__file__).parent
winners_file = project_dir / "winners.json"
house_file = project_dir / "current_house.json"

try:
    with open(winners_file, "r", encoding="utf-8") as f:
        winners = json.load(f)
    last_winner = winners[-1]

    name = last_winner["name"].replace("Winner: ", "")
    suburb = last_winner["image"].split("/")[0].replace("_houses", "")
    image = last_winner["image"].split("/")[-1]

    commit_msg = f"🏆 Added winner {name} for {suburb} ({image})"

    # Stage files
    subprocess.run(["git", "add", "winners.json", "current_house.json"], check=True)

    # Commit with custom message
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

    # Push to GitHub
    subprocess.run(["git", "push", "origin", "main"], check=True)

    print(f"✅ Success: {commit_msg}")

except Exception as e:
    print(f"❌ Error: {e}")
