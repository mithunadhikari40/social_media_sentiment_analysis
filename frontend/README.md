# Social Media Analysis Dashboard

A modern web application for analyzing social media sentiment and trends, built with React, TypeScript, and Material-UI.

## Features

- 🔐 **User Authentication** - Secure login and registration with JWT
- 📊 **Interactive Dashboards** - Visualize social media analytics
- 🔍 **Advanced Analysis** - Perform sentiment analysis on social media data
- 📈 **Reports** - Generate and download detailed reports
- 🎨 **Responsive Design** - Works on desktop and mobile devices
- 🌓 **Dark/Light Mode** - Built-in theme support

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **UI Framework**: Material-UI (MUI) with Material 3 design
- **State Management**: React Query, Context API
- **Routing**: React Router v6
- **Form Handling**: Formik with Yup validation
- **Charts**: Recharts and Chart.js
- **HTTP Client**: Axios

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
4. Update the environment variables in `.env` as needed

### Running the Development Server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to view it in your browser.

### Building for Production

```bash
npm run build
```

This will create a production-ready build in the `dist` directory.

## Project Structure

```
src/
├── api/                 # API service functions
├── assets/              # Static assets (images, styles, etc.)
├── components/          # Reusable UI components
│   ├── common/          # Common components (buttons, loaders, etc.)
│   └── layout/          # Layout components (header, sidebar, etc.)
├── context/             # React context providers
├── hooks/               # Custom React hooks
├── pages/               # Page components
│   ├── auth/            # Authentication pages
│   ├── dashboard/       # Dashboard components
│   └── ...
├── theme/               # MUI theme configuration
└── utils/               # Utility functions
```

## Environment Variables

Create a `.env` file in the root directory and add the following variables:

```env
VITE_API_URL=http://localhost:8000  # backend API URL
NODE_ENV=development
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking


