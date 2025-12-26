# FII Portfolio Manager - Frontend

This is the frontend application for the FII (Fundos Imobiliários) Portfolio Manager.

## Prerequisites

- Node.js 18+ and npm (or yarn/pnpm)

## Installation

```bash
# Install dependencies
npm install
```

## Running the Application

```bash
# Development mode with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/          # Reusable components
│   └── ProtectedRoute.tsx
├── pages/              # Page components
│   ├── LoginPage.tsx
│   └── HomePage.tsx
├── services/           # API services
│   ├── api.ts
│   └── authService.ts
├── styles/             # CSS files
│   ├── global.css
│   ├── login.css
│   └── home.css
├── App.tsx             # Main app component with routing
└── index.tsx           # Entry point
```

## Authentication Flow

1. User navigates to the application (any route)
2. If not authenticated, redirected to `/login`
3. User enters credentials and submits login form
4. On successful login:
   - Access token and refresh token stored in localStorage
   - User redirected to home page (`/`)
5. Protected routes check for access token
6. API interceptor automatically adds Bearer token to requests
7. On 401 errors, interceptor attempts token refresh
8. If refresh fails, user is logged out and redirected to `/login`

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Features Implemented

- ✅ Login page with form validation
- ✅ Protected routes (requires authentication)
- ✅ Automatic token refresh on 401 errors
- ✅ Home page with logout functionality
- ✅ Responsive design
- ✅ Error handling and user feedback

## Testing the Application

1. Start the backend API server:
   ```bash
   cd ../backend
   uvicorn app.main:app --reload
   ```

2. Start the frontend development server:
   ```bash
   npm run dev
   ```

3. Open your browser to `http://localhost:5173` (or the port shown in terminal)

4. Try logging in with test credentials from the backend database

## Next Steps

- Add user registration page
- Implement portfolio dashboard
- Add transaction management
- Add dividend tracking
- Create reports and analytics
