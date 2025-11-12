#!/usr/bin/env python3
"""
Simple test script to verify event API keys are working.
Doesn't require dotenv - reads .env file manually.
Run from backend directory: python3 test_apis_simple.py
"""
import os
import sys

# Try to import requests
try:
    import requests
except ImportError:
    print("❌ 'requests' module not installed")
    print("   Install with: pip3 install requests")
    sys.exit(1)


def load_env_file():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    env_vars = {}

    if not os.path.exists(env_path):
        print(f"❌ .env file not found at: {env_path}")
        return env_vars

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def test_eventbrite(api_key):
    """Test Eventbrite API connection."""
    print("\n🎫 Testing Eventbrite API...")

    if not api_key or api_key == "your-eventbrite-api-key-here":
        print("⚠️  EVENTBRITE_API_KEY not configured")
        return False

    print(f"✓ API Key found: {api_key[:10]}...")

    try:
        url = "https://www.eventbriteapi.com/v3/events/search/"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {
            "location.address": "Houston, TX",
            "location.within": "25mi",
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
        if e.response.status_code == 401:
            print("   Invalid API key or unauthorized")
        print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_ticketmaster(api_key):
    """Test Ticketmaster API connection."""
    print("\n🎟️  Testing Ticketmaster API...")

    if not api_key or api_key == "your-ticketmaster-api-key-here":
        print("⚠️  TICKETMASTER_API_KEY not configured")
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
        if e.response.status_code == 401:
            print("   Invalid API key")
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

    # Load environment variables
    env_vars = load_env_file()

    eventbrite_key = env_vars.get('EVENTBRITE_API_KEY', '')
    ticketmaster_key = env_vars.get('TICKETMASTER_API_KEY', '')

    # Run tests
    results = {
        "eventbrite": test_eventbrite(eventbrite_key),
        "ticketmaster": test_ticketmaster(ticketmaster_key),
    }

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    for api, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{api.capitalize():20} {status}")

    all_passed = all(results.values())
    print("\n" + ("✅ All tests passed!" if all_passed else "⚠️  Some tests failed"))

    if all_passed:
        print("\n🎉 Your event APIs are ready to use!")
        print("   Start the Flask server: python3 app.py")
        print("   Test endpoints:")
        print("     - http://localhost:5000/api/events/eventbrite")
        print("     - http://localhost:5000/api/events/ticketmaster")
        print("     - http://localhost:5000/api/events/all")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
