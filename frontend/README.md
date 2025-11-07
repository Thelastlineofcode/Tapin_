# Tapin Frontend

React-based frontend for the Tapin marketplace platform, built with Vite.

## Prerequisites

- Node.js 20+ recommended
- npm (comes with Node.js)

## Quick Start

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

The frontend will be available at **http://localhost:5173**

## Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── services/       # API service layer
│   ├── utils/          # Utility functions
│   └── App.jsx         # Main app component
├── public/             # Static assets
├── index.html          # HTML entry point
└── package.json        # Dependencies and scripts
```

## Backend Integration

The frontend expects the backend API to be running at `http://127.0.0.1:5000`.

To connect to a different backend URL, update the API base URL in your service layer or create a `.env` file:

```env
VITE_API_URL=http://127.0.0.1:5000
```

## Development Roadmap

### Current Features

- Basic React setup with Vite
- Fast development with HMR (Hot Module Replacement)

### Planned Features

- [ ] Authentication UI (login, register, password reset)
- [ ] Listings browsing and search
- [ ] Interactive map for listing locations
- [ ] User profile and dashboard
- [ ] Create/edit/delete listings
- [ ] Responsive design system
- [ ] Form validation and error handling

## Technology Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** (planned) - Client-side routing
- **Axios** (planned) - HTTP client for API calls

## Development Notes

- Uses ES modules (type: "module" in package.json)
- Hot Module Replacement (HMR) for fast development
- Production builds are optimized and minified

## Deployment

Build the production bundle:

```bash
npm run build
```

The `dist/` folder will contain the optimized static files ready for deployment.

Preview the production build locally:

```bash
npm run preview
```

## Contributing

When adding new features:

1. Create components in `src/components/`
2. Add API calls in `src/services/`
3. Keep the README updated with new features and setup steps
