import os
import csv
import time
from github import Github
from dotenv import load_dotenv
from datetime import datetime



from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).parent / ".env")
token = os.getenv("GITHUB_TOKEN")
print(f"Token loaded: {token[:10]}...")  # prints first 10 characters only
token=os.getenv("GITHUB_TOKEN")
from github import Auth
g = Github(auth=Auth.Token(token))
print(g.rate_limiting)
print(g.rate_limiting_resettime)


#repos to scrape
REPOS = [
    "psf/requests",
    "pallets/flask",
    "tiangolo/fastapi"
]
#main scraping function
def check_rate_limit():
    remaining, limit = g.rate_limiting
    
    if remaining < 10:
        reset_time = g.rate_limiting_resettime
        wait_seconds = reset_time - int(time.time()) + 60
        print(f"Rate limit low ({remaining} left). Waiting {wait_seconds}s...")
        time.sleep(wait_seconds)

def scrape_prs(repo_name, max_prs=50):
    print(f"Scraping {repo_name}...")
    repo = g.get_repo(repo_name)
    pulls = repo.get_pulls(state="closed", sort="updated", direction="desc")

    rows = []
    count = 0

    for pr in pulls:
        check_rate_limit()
        if count >= max_prs:
            break

        if not pr.merged:
            continue

        try:
            diff = pr.get_files()
            reviews = pr.get_reviews()
            comments = pr.get_review_comments()

            for comment in comments:
                rows.append({
                    "repo": repo_name,
                    "pr_number": pr.number,
                    "author": pr.user.login,
                    "diff_hunk": comment.diff_hunk,
                    "review_comment": comment.body,
                    "label": ""
                })

            count += 1
            time.sleep(1)

        except Exception as e:
            print(f"Error on PR #{pr.number}: {e}")
            continue

    return rows



#save to csv

def save_to_csv(rows, filename="data/raw_prs.csv"):
    if not rows:
        print("No data to save")
        return

    fieldnames = ["repo", "pr_number", "author", 
                  "diff_hunk", "review_comment", "label"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {filename}")




#run everything
if __name__ == "__main__":
    all_rows = []

    for repo in REPOS:
        rows = scrape_prs(repo, max_prs=20)
        all_rows.extend(rows)
        print(f"Got {len(rows)} comments from {repo}")
        time.sleep(2)

    save_to_csv(all_rows)
    print(f"Total: {len(all_rows)} rows collected")