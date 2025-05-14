# Krowoc Frontend

This is the frontend for the Krowoc application, built with Next.js, TypeScript, and Tailwind CSS.

## Tech Stack

- [Next.js](https://nextjs.org/) - React framework
- [TypeScript](https://www.typescriptlang.org/) - Type-safe JavaScript
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [React Query](https://tanstack.com/query/latest) - Data fetching library

## Getting Started

First, install dependencies:

```bash
npm install
# or
yarn install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

- `/components` - Reusable UI components
  - `/layout` - Layout components including the main application layout
  - `/auth` - Authentication-related components
- `/pages` - Next.js pages
  - `/auth` - Authentication pages (login, signup, password reset)
- `/styles` - Global CSS styles including Tailwind imports
- `/lib` - Utility functions and shared logic
- `/types` - TypeScript type definitions

## Authentication Setup

This project uses [Supabase](https://supabase.com/) for authentication. To set up authentication:

1. Create a Supabase project at [https://app.supabase.com/](https://app.supabase.com/)
2. Get your project URL and anon key from the Supabase dashboard
3. Create a `.env.local` file in the frontend directory with the following variables:

```
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Application URLs (for OAuth redirects)
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

4. For OAuth providers (Google, GitHub, Microsoft), configure them in the Supabase Authentication settings:
   - Set the callback URL to: `http://localhost:3000/auth/callback` (for local development)
   - For production, use your production URL: `https://your-domain.com/auth/callback`

## Building for Production

```bash
npm run build
# or
yarn build
```

## Deployment

The application can be deployed using:

```bash
npm run start
# or
yarn start
```

Or using the provided Docker configuration:

```bash
docker-compose up frontend
``` 