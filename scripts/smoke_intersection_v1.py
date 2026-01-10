import json
import sys
import requests

API = "http://127.0.0.1:8000"

def main() -> int:
    # Use a known location that should geocode cleanly (or already in cache)
    compute_payload = {
        "name": "Ada Lovelace",
        "birth": {
            "date": "1990-01-01",
            "time": "12:00",
            "timezone": "Europe/London",
            "location": {"city": "London", "region": "England", "country": "UK"},
        },
    }

    # 1) Compute profile
    r1 = requests.post(f"{API}/profile/compute", json=compute_payload, timeout=60)
    print("compute status:", r1.status_code)
    if r1.status_code != 200:
        print(r1.text)
        return 1

    profile = r1.json()

    # 2) Intersection
    r2 = requests.post(f"{API}/profile/intersection", json={"profile": profile}, timeout=60)
    print("intersection status:", r2.status_code)
    if r2.status_code != 200:
        print(r2.text)
        return 1

    report = r2.json()
    print(json.dumps(report, indent=2)[:4000])  # cap output
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
