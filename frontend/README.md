# Medical Appointment Frontend

A sleek and minimal Next.js frontend for the Medical Appointment Assistant application.

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend FastAPI server running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Features

- **Minimal Landing Page**: Clean and modern design with patient ID input
- **Interactive Chat UI**: Real-time chat interface connected to the FastAPI backend
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Built with Tailwind CSS for a sleek, minimal aesthetic

## Project Structure

```
frontend/
├── app/
│   ├── globals.css      # Global styles with Tailwind
│   ├── layout.tsx       # Root layout component
│   └── page.tsx         # Landing page and main entry point
├── components/
│   └── ChatInterface.tsx # Chat UI component
├── package.json
├── next.config.js       # Next.js configuration with API proxy
└── tailwind.config.js   # Tailwind CSS configuration
```

## Backend Connection

The frontend connects to the FastAPI backend through a Next.js API rewrite configured in `next.config.js`. The backend should be running on `http://localhost:8000`.

## Development

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

