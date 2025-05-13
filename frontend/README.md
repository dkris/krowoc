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
- `/pages` - Next.js pages
- `/styles` - Global CSS styles including Tailwind imports
- `/lib` - Utility functions and shared logic
- `/types` - TypeScript type definitions

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