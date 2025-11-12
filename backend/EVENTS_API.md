# Events API Documentation

This backend provides multiple endpoints to fetch public events from various sources.

## Available Endpoints

### 1. Eventbrite Events
**Endpoint:** `GET /api/events/eventbrite`

Fetch events from Eventbrite.

**Query Parameters:**
- `location` - Location to search (default: "Houston, TX")
- `radius` - Search radius (default: "25mi")
- `page` - Page number for pagination
- `categories` - Filter by category
- `q` - Search query

**Example:**
```bash
curl "http://localhost:5000/api/events/eventbrite?location=Houston,TX&q=music"
```

### 2. Ticketmaster Events
**Endpoint:** `GET /api/events/ticketmaster`

Fetch events from Ticketmaster Discovery API.

**Query Parameters:**
- `city` - City name (default: "Houston")
- `state` - State code (default: "TX")
- `country` - Country code (default: "US")
- `category` - Classification name (e.g., "music", "sports")
- `q` - Keyword search
- `size` - Results per page (default: 20)
- `page` - Page number

**Example:**
```bash
curl "http://localhost:5000/api/events/ticketmaster?city=Houston&state=TX&category=music"
```

### 3. All Events (Aggregated)
**Endpoint:** `GET /api/events/all`

Fetch and aggregate events from all configured sources (Eventbrite + Ticketmaster).

**Query Parameters:**
- `location` - Location for Eventbrite (default: "Houston, TX")
- `city` - City for Ticketmaster (default: "Houston")
- `state` - State for Ticketmaster (default: "TX")

**Example:**
```bash
curl "http://localhost:5000/api/events/all?city=Houston&state=TX"
```

**Response includes:**
- `events[]` - Array of events from all sources
- `total` - Total number of events found
- `errors[]` - Any errors from individual sources
- `sources_queried[]` - List of sources attempted

## Setup Instructions

### 1. Get API Keys

#### Eventbrite
1. Visit https://www.eventbrite.com/platform/api
2. Create an account or sign in
3. Create a new app to get your API key
4. Add to `.env`: `EVENTBRITE_API_KEY=your-key-here`

#### Ticketmaster
1. Visit https://developer.ticketmaster.com/
2. Sign up for a developer account
3. Get your API key from the dashboard
4. Add to `.env`: `TICKETMASTER_API_KEY=your-key-here`

#### Meetup (Coming Soon)
1. Visit https://www.meetup.com/api/
2. Sign in and request API access
3. Add to `.env`: `MEETUP_API_KEY=your-key-here`

#### PredictHQ (Coming Soon)
1. Visit https://www.predicthq.com/
2. Sign up for an account
3. Add to `.env`: `PREDICTHQ_API_KEY=your-key-here`

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys.

### 3. Test the Endpoints

Start the Flask backend:
```bash
cd backend
python app.py
```

Test with curl:
```bash
# Test Eventbrite
curl "http://localhost:5000/api/events/eventbrite"

# Test Ticketmaster
curl "http://localhost:5000/api/events/ticketmaster"

# Test aggregated endpoint
curl "http://localhost:5000/api/events/all"
```

## Response Format

All endpoints return JSON with this structure:

```json
{
  "events": [
    {
      "id": "event-id",
      "source": "eventbrite|ticketmaster",
      "name": "Event Name",
      "description": "Event description",
      "start": "2025-11-15T19:00:00",
      "url": "https://...",
      "venue": "Venue Name",
      "image": "https://..."
    }
  ],
  "total": 10,
  "pagination": {...}
}
```

## Error Handling

If an API key is not configured:
```json
{
  "error": "API key not configured"
}
```

If a source fails (aggregated endpoint only):
```json
{
  "events": [...],
  "errors": [
    {"source": "eventbrite", "error": "error message"}
  ]
}
```

## Rate Limits

- **Eventbrite:** Check their API documentation for current limits
- **Ticketmaster:** 5,000 calls/day, 5 requests/second
