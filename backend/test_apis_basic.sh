#!/bin/bash
# Simple shell script to test event APIs using curl
# Run from anywhere: bash backend/test_apis_basic.sh

set -e

echo "============================================================"
echo "🧪 Event API Connection Tests (using curl)"
echo "============================================================"

# Load .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
elif [ -f "../.env" ]; then
    export $(grep -v '^#' ../.env | xargs)
else
    echo "❌ .env file not found"
    exit 1
fi

# Test Eventbrite
echo ""
echo "🎫 Testing Eventbrite API..."
if [ -z "$EVENTBRITE_API_KEY" ] || [ "$EVENTBRITE_API_KEY" = "your-eventbrite-api-key-here" ]; then
    echo "⚠️  EVENTBRITE_API_KEY not configured"
else
    echo "✓ API Key found: ${EVENTBRITE_API_KEY:0:10}..."

    response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $EVENTBRITE_API_KEY" \
        "https://www.eventbriteapi.com/v3/events/search/?location.address=Houston,TX&location.within=25mi" 2>&1 || echo "000")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        event_count=$(echo "$body" | grep -o '"events":\[' | wc -l)
        echo "✅ Eventbrite API working! (HTTP $http_code)"
        echo "   $(echo "$body" | head -c 100)..."
    else
        echo "❌ Eventbrite API failed (HTTP $http_code)"
        echo "   $(echo "$body" | head -c 200)"
    fi
fi

# Test Ticketmaster
echo ""
echo "🎟️  Testing Ticketmaster API..."
if [ -z "$TICKETMASTER_API_KEY" ] || [ "$TICKETMASTER_API_KEY" = "your-ticketmaster-api-key-here" ]; then
    echo "⚠️  TICKETMASTER_API_KEY not configured"
else
    echo "✓ API Key found: ${TICKETMASTER_API_KEY:0:10}..."

    response=$(curl -s -w "\n%{http_code}" \
        "https://app.ticketmaster.com/discovery/v2/events?apikey=$TICKETMASTER_API_KEY&city=Houston&stateCode=TX&size=5" 2>&1 || echo "000")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        echo "✅ Ticketmaster API working! (HTTP $http_code)"
        echo "   $(echo "$body" | head -c 100)..."
    else
        echo "❌ Ticketmaster API failed (HTTP $http_code)"
        echo "   $(echo "$body" | head -c 200)"
    fi
fi

echo ""
echo "============================================================"
echo "✅ API key testing complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Install Python dependencies: pip3 install -r backend/requirements.txt"
echo "  2. Start Flask server: cd backend && python3 app.py"
echo "  3. Test endpoints:"
echo "     curl http://localhost:5000/api/events/eventbrite"
echo "     curl http://localhost:5000/api/events/ticketmaster"
echo "     curl http://localhost:5000/api/events/all"
