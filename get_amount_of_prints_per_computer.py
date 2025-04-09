import requests
from datetime import datetime, timedelta, timezone

API_KEY = "API_HERE"
BASE_URL = "https://api.printnode.com"

# configure time, utc
today = datetime.now(timezone.utc).date()
start_of_day = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
end_of_day = start_of_day + timedelta(days=1)

def get(endpoint, params=None):
    response = requests.get(f"{BASE_URL}{endpoint}", auth=(API_KEY, ""), params=params)
    if response.status_code != 200:
        print(f"Error while downloading: {endpoint}: {response.status_code} {response.text}")
        return None
    return response.json()

# 1. get computers
computers = get("/computers")
if not computers:
    exit()

total_prints = 0

for computer in computers:
    computer_id = computer["id"]
    print(f"\n🖥️ Computer ID {computer_id}")

    # 2. get prints per computer
    printers = get(f"/computers/{computer_id}/printers")
    if not printers:
        continue

    for printer in printers:
        printer_id = printer["id"]
        printer_name = printer["name"]
        print(f"  🖨️ Printer: {printer_name} (ID: {printer_id})")

        count_today = 0
        after_id = None
        while True:
            # 3. get prints from pagination
            params = {
                "limit": 100,
                "dir": "desc",
            }
            if after_id:
                params["after"] = after_id

            jobs = get(f"/printers/{printer_id}/printjobs", params=params)
            if not jobs:
                break

            filtered_jobs = []
            for job in jobs:
                created_str = job.get("createTimestamp")
                if not created_str:
                    continue
                created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                if start_of_day <= created < end_of_day:
                    filtered_jobs.append(job)

            count_today += len(filtered_jobs)

            # end when less then limit
            if len(jobs) < 100:
                break

            # prepare id for next page
            after_id = min(job["id"] for job in jobs)

        print(f"    ✅ Today's print: {count_today}")
        total_prints += count_today

print("\n📊 Total prints today:", total_prints)
