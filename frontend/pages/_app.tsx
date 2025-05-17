import type { AppProps } from 'next/app'
import { Layout } from '../components/layout'
import '../styles/globals.css'
import { AuthProvider } from '../lib/AuthContext'
import { useEffect } from 'react'
import { initPostHog } from '../lib/analytics'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Create a client
const queryClient = new QueryClient()

export default function App({ Component, pageProps }: AppProps) {
  // Initialize PostHog on the client side
  useEffect(() => {
    initPostHog()
  }, [])

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </AuthProvider>
    </QueryClientProvider>
  )
} 
