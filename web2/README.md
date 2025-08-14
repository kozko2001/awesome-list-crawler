# Web2 - Awesome List Crawler Frontend

A modern, terminal-style frontend for browsing awesome GitHub repositories with a sleek hacker aesthetic.

## Features

- **Timeline View**: Browse repositories chronologically with infinite scroll
- **Search**: Real-time search with debounced queries and suggestions
- **I'm Feeling Lucky**: Discover random repositories
- **Terminal Design**: Black/white/green color scheme with monospace fonts
- **Performance**: Optimized with React Query caching and virtual scrolling
- **Testing**: Comprehensive unit and E2E tests

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4 with custom terminal theme
- **Data Fetching**: TanStack Query (React Query)
- **Icons**: Lucide React
- **Testing**: Jest, React Testing Library, Playwright
- **Deployment**: Docker + Kubernetes

## Development

### Prerequisites

- Node.js 18+
- Backend API running at `localhost:8000`

### Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production  
npm run start        # Start production server
npm run lint         # Run ESLint
npm run test         # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run test:e2e     # Run E2E tests with Playwright
```

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API URL
```

## Design System

### Colors
- **Background**: `#000000` (terminal-bg)
- **Text**: `#ffffff` (terminal-text)
- **Accent**: `#00ff41` (terminal-green)
- **Borders**: `#333333` (terminal-border)

### Typography
- **Font**: JetBrains Mono (monospace)
- **Styles**: Terminal cursor effects, glow text, custom animations

## API Integration

Connects to the backend API with the following endpoints:

- `GET /api/v1/timeline` - Paginated timeline
- `GET /api/v1/search` - Search repositories
- `GET /api/v1/lucky` - Random repository
- `GET /api/v1/health` - Health check

## Testing

### Unit Tests
```bash
npm run test
```

### E2E Tests
```bash
npm run test:e2e
```

## Deployment

Deployed at `web2.awesome.allocsoc.net` with Docker + Kubernetes.
