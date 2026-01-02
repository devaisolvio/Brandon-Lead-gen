# Brandon Lead Generation Frontend

A modern React + Vite + Tailwind CSS frontend for managing lead generation pipelines.

## Features

- 🎨 Beautiful, modern UI with Tailwind CSS
- ⚡ Fast development with Vite
- 🔄 Real-time pipeline status updates
- 📊 Status monitoring dashboard
- 🚀 Start/stop pipeline controls

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Configuration

The frontend connects to the Flask backend on `http://localhost:5000` by default.

To change the API URL, create a `.env` file:
```
VITE_API_URL=http://localhost:5000
```

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Available Pipelines

- **Apollo Lead Generation**: Scrape and process leads from Apollo.io
- **Google Maps Scraper**: Scrape businesses from Google Maps
- **HubSpot Leads**: Pull and evaluate contacts from HubSpot CRM

