#!/usr/bin/env python3
"""
Quick test script to verify event API keys are working.
Run from backend directory: python3 test_event_apis.py
"""
import os
import sys
from dotenv import load_dotenv
import requests

# Load environment variables
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(repo_root, '.env'))

def test_eventbrite():
    """Test Eventbrite API connection."""
    print("\n🎫 Testing Eventbrite API...")
    api_key = os.environ.get('EVENTBRITE_API_KEY')

    if not api_key:
        print("❌ EVENTBRITE_API_KEY not found in environment")
        return False

    if api_key == "your-eventbrite-api-key-here":
        print("⚠️  EVENTBRITE_API_KEY is still a placeholder")
        return False

    print(f"✓ API Key found: {api_key[:10]}...")

    try:
        url = "https://www.eventbriteapi.com/v3/events/search/"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {
            "location.address": "Houston, TX",
            "location.within": "25mi",
            "expand": "venue",
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        event_count = len(data.get("events", []))
        print(f"✅ Eventbrite API working! Found {event_count} events")

        if event_count > 0:
            first_event = data["events"][0]
            print(f"   Sample: {first_event.get('name', {}).get('text', 'N/A')}")

        return True

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_ticketmaster():
    """Test Ticketmaster API connection."""
    print("\n🎟️  Testing Ticketmaster API...")
    api_key = os.environ.get('TICKETMASTER_API_KEY')

    if not api_key:
        print("❌ TICKETMASTER_API_KEY not found in environment")
        return False

    if api_key == "your-ticketmaster-api-key-here":
        print("⚠️  TICKETMASTER_API_KEY is still a placeholder")
        return False

    print(f"✓ API Key found: {api_key[:10]}...")

    try:
        url = "https://app.ticketmaster.com/discovery/v2/events"
        params = {
            "apikey": api_key,
            "city": "Houston",
            "stateCode": "TX",
            "size": 5,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        event_count = len(data.get("_embedded", {}).get("events", []))
        total = data.get("page", {}).get("totalElements", 0)

        print(f"✅ Ticketmaster API working! Found {total} total events (showing {event_count})")

        if event_count > 0:
            first_event = data["_embedded"]["events"][0]
            print(f"   Sample: {first_event.get('name', 'N/A')}")

        return True

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all API tests."""
    print("=" * 60)
    print("🧪 Event API Connection Tests")
    print("=" * 60)

    results = {
        "eventbrite": test_eventbrite(),
        "ticketmaster": test_ticketmaster(),
    }

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    for api, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{api.capitalize():20} {status}")

    all_passed = all(results.values())
    print("\n" + ("✅ All tests passed!" if all_passed else "❌ Some tests failed"))

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
