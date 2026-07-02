import sys, os, subprocess

token = input("GitHub Personal Access Token: ").strip()
username = input("GitHub Username: ").strip()
repo_name = "GymOS"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create repo via GitHub API
import requests
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
resp = requests.post(
    "https://api.github.com/user/repos",
    json={"name": repo_name, "description": "GYM OS ULTIMATE - Personal Fitness Operating System", "private": False},
    headers=headers
)

if resp.status_code == 201:
    print(f"Repo created: {resp.json()['html_url']}")
elif resp.status_code == 422:
    print("Repo may already exist, attempting to push...")
else:
    print(f"Error: {resp.status_code} - {resp.text}")
    sys.exit(1)

# Git commands
subprocess.run(["git", "init"], check=True)
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "Initial commit: Gym OS Ultimate - complete fitness desktop application"], check=True)

repo_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
subprocess.run(["git", "branch", "-M", "main"], check=True)
subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

print(f"\nSuccessfully pushed to: https://github.com/{username}/{repo_name}")
