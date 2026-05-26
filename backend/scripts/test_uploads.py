import os
import sys

import requests

BASE = "http://127.0.0.1:8000"
FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def main():
    r = requests.post(
        f"{BASE}/api/auth/login/",
        json={"username": "analyst", "password": "analyst123"},
        timeout=10,
    )
    if r.status_code != 200:
        print("LOGIN FAILED", r.status_code)
        sys.exit(1)
    token = r.json()["data"]["access"]
    headers = {"Authorization": f"Bearer {token}"}

    tests = [
        ("sap", "sample_sap.csv"),
        ("utility", "sample_utility.csv"),
        ("travel", "sample_travel.csv"),
    ]
    for src, filename in tests:
        path = os.path.join(FIXTURES, filename)
        with open(path, "rb") as f:
            resp = requests.post(
                f"{BASE}/api/upload/{src}/",
                headers=headers,
                files={"file": f},
                timeout=120,
            )
        if resp.status_code == 201:
            d = resp.json().get("data", {})
            print(
                f"{src}: OK  parsed={d.get('rows_parsed')} "
                f"failed={d.get('rows_failed')} status={d.get('status')}"
            )
        else:
            print(f"{src}: FAIL {resp.status_code}", resp.text[:400])

    for src in ["sap", "utility", "travel"]:
        rec = requests.get(
            f"{BASE}/api/records/",
            headers=headers,
            params={"source_type": src},
            timeout=10,
        )
        data = rec.json()
        count = data.get("count", len(data.get("results", [])))
        print(f"  DB records ({src}): {count}")


if __name__ == "__main__":
    main()
