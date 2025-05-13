# Authentication Foundation

This directory contains the Supabase authentication foundation for the Krowoc application.

## Files

- `supabase.ts` - Supabase client configuration and authentication utility functions
- `AuthContext.tsx` - React context for managing authentication state across the application
- `useAuthForm.ts` - Custom hook for handling authentication form validation and submission

## Authentication Flow

1. Users can sign up or log in via email/password or OAuth providers (Google, GitHub, Microsoft)
2. Authentication state is stored in Supabase and managed via the AuthContext
3. Protected routes check authentication status and redirect as needed
4. The middleware handles server-side authentication checking

## OAuth Configuration

To set up OAuth providers:

1. Configure each provider in the Supabase dashboard
2. Set the callback URL to: `[YOUR_SITE_URL]/auth/callback`
3. Store the provider credentials securely in the Supabase dashboard

## Additional Features

- Password reset functionality
- Server-side route protection via middleware
- Client-side route protection via ProtectedRoute component
- Authenticated user profile display
- Redirect handling after authentication 