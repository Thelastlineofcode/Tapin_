# Event APIs Status Report

## ✅ Working APIs

### Ticketmaster Discovery API
**Status:** ✅ FULLY FUNCTIONAL

**Your API Key:** `qgvFszyOMAW7tADHTsBTNA4Hs3vcNYev`

**Rate Limits:**
- 5,000 requests per day
- 5 requests per second

**Available Endpoints:**
- `GET /api/events/ticketmaster` - Search Ticketmaster events
- `GET /api/events/all` - Aggregated events (currently only Ticketmaster)

**Test Result:**
```bash
$ curl "http://localhost:5000/api/events/ticketmaster?city=Houston&state=TX"
✅ Returns Houston Texans, concerts, shows, and more
```

**Query Parameters:**
- `city` - City name (default: "Houston")
- `state` - State code (default: "TX")
- `country` - Country code (default: "US")
- `category` - Classification name (e.g., "music", "sports")
- `q` - Keyword search
- `size` - Results per page (default: 20, max: 50)
- `page` - Page number

**Example Queries:**
```bash
# All events in Houston
curl "http://localhost:5000/api/events/ticketmaster?city=Houston&state=TX"

# Music events only
curl "http://localhost:5000/api/events/ticketmaster?city=Houston&state=TX&category=music"

# Search for specific artist
curl "http://localhost:5000/api/events/ticketmaster?city=Houston&q=Taylor+Swift"

# Get more results
curl "http://localhost:5000/api/events/ticketmaster?city=Houston&size=50"
```

---

## ❌ Not Working APIs

### Eventbrite API
**Status:** ❌ DEPRECATED

**Issue:** Eventbrite deprecated their public events search API (`/v3/events/search/`) in February 2020.

**Current Limitation:** The Eventbrite API now only allows access to events from your own organization, not public event searches.

**Your API Key:** `LY2TF2BN5FLHXKC7L3P2` (valid but limited functionality)

**Alternative:** The `/api/events/eventbrite` endpoint now returns a helpful error message explaining this limitation and suggesting Ticketmaster as an alternative.

**What You Can Do With Eventbrite API:**
- List events from your own organization: `GET /v3/organizations/{org_id}/events/`
- Get specific event details: `GET /v3/events/{event_id}/`
- List events from a specific venue: `GET /v3/venues/{venue_id}/events/`

---

## 🔜 Future APIs to Add

### 1. SeatGeek API
- Free tier available
- Good for concerts, sports, theater
- Documentation: https://platform.seatgeek.com/

### 2. Meetup API (OAuth required)
- Great for community events
- Requires OAuth setup
- Documentation: https://www.meetup.com/api/

### 3. Local City APIs
Many cities have their own event APIs:
- Houston: https://www.houstontx.gov/api/
- Austin: https://data.austintexas.gov/
- Open data portals often include events

### 4. Yelp Events API
- Restaurant and business events
- Free tier: 500 calls/day
- Documentation: https://www.yelp.com/developers/documentation/v3

---

## 📊 Current Implementation Summary

**Working Endpoints:**
```
✅ GET /api/events/ticketmaster       - Ticketmaster events (WORKING)
✅ GET /api/events/all                - All events (currently just Ticketmaster)
⚠️  GET /api/events/eventbrite       - Returns deprecation notice
```

**API Keys Configured:**
```
✅ TICKETMASTER_API_KEY = qgvFszyOMAW7tADHTsBTNA4Hs3vcNYev
⚠️  EVENTBRITE_API_KEY  = LY2TF2BN5FLHXKC7L3P2 (limited to your org only)
```

---

## 🚀 Quick Start

1. **Start the backend:**
   ```bash
   cd backend
   python3 app.py
   ```

2. **Test Ticketmaster API:**
   ```bash
   curl "http://localhost:5000/api/events/ticketmaster?city=Houston&state=TX" | jq
   ```

3. **Get all events:**
   ```bash
   curl "http://localhost:5000/api/events/all?city=Houston&state=TX" | jq
   ```

---

## 📝 Response Format

All working endpoints return JSON:

```json
{
  "events": [
    {
      "id": "tm_G5dIZ...",
      "source": "ticketmaster",
      "name": "Houston Texans vs. Buffalo Bills",
      "start": "2025-11-15",
      "start_time": "19:00:00",
      "url": "https://www.ticketmaster.com/...",
      "venue": "NRG Stadium",
      "venue_address": "NRG Pkwy",
      "image": "https://s1.ticketm.net/..."
    }
  ],
  "total": 50,
  "pagination": {...}
}
```

---

## 🎯 Next Steps

1. **Consider adding SeatGeek** - They have a good free tier for event data
2. **Test with your frontend** - Connect the `/api/events/all` endpoint to your UI
3. **Add caching** - Consider caching API responses to stay within rate limits
4. **Add filtering** - Implement category and date range filters in your frontend

---

**Last Updated:** November 11, 2025
**Tested By:** Claude Code
**Status:** Production Ready ✅
