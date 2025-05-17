import posthog from 'posthog-js';
import { useEffect } from 'react';

// PostHog public API key should be in environment variables
const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY;
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com';

// Initialize PostHog if API key is available
export const initPostHog = () => {
  if (typeof window !== 'undefined' && POSTHOG_KEY) {
    posthog.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      capture_pageview: true,
      loaded: (posthog) => {
        if (process.env.NODE_ENV === 'development') {
          // In development, log events instead of sending them
          posthog.opt_out_capturing();
          console.log('PostHog initialized in development mode (not sending events)');
        }
      },
    });
  }
};

// Custom React hook for using PostHog with Page View tracking
export const usePostHog = (pageName: string) => {
  useEffect(() => {
    // Capture page view when component mounts
    if (POSTHOG_KEY) {
      if (process.env.NODE_ENV === 'production') {
        posthog.capture('$pageview', { pageName });
      } else {
        console.log(`[PostHog] Pageview: ${pageName}`);
      }
    }
  }, [pageName]);
};

// Utility function for tracking user events
export const trackEvent = (
  eventName: string, 
  properties: Record<string, any> = {},
  requestId?: string
) => {
  if (POSTHOG_KEY) {
    const eventProps = { ...properties };
    
    // Attach correlation ID if available
    if (requestId) {
      eventProps.requestId = requestId;
    }
    
    if (process.env.NODE_ENV === 'production') {
      posthog.capture(eventName, eventProps);
    } else {
      console.log(`[PostHog] Event: ${eventName}`, eventProps);
    }
  }
};

// Get the PostHog distinct ID for the current user
export const getDistinctId = (): string => {
  if (typeof window !== 'undefined' && POSTHOG_KEY) {
    return posthog.get_distinct_id();
  }
  return 'unknown';
};

// Identify user with additional properties
export const identifyUser = (
  userId: string, 
  properties: Record<string, any> = {}
) => {
  if (POSTHOG_KEY && userId) {
    if (process.env.NODE_ENV === 'production') {
      posthog.identify(userId, properties);
    } else {
      console.log(`[PostHog] Identify user: ${userId}`, properties);
    }
  }
};

// Generate a new correlation ID for tracking across systems
export const generateCorrelationId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
};

// Add correlation ID to outgoing API requests
export const addCorrelationIdToRequest = (headers: Headers): string => {
  const correlationId = generateCorrelationId();
  headers.append('X-Correlation-ID', correlationId);
  return correlationId;
};

// Track API request with correlation ID
export const trackApiRequest = (
  endpoint: string,
  method: string,
  correlationId: string
) => {
  trackEvent('api_request', {
    endpoint,
    method,
    correlationId
  });
  return correlationId;
};

export default {
  initPostHog,
  usePostHog,
  trackEvent,
  identifyUser,
  generateCorrelationId,
  addCorrelationIdToRequest,
  trackApiRequest
}; 