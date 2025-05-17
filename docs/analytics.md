# Analytics Implementation

This document outlines the analytics and tracking implementation using PostHog in the Krowoc application.

## Overview

The analytics implementation provides:

1. Event tracking in both frontend and backend
2. Correlation ID propagation between systems
3. User identification and session tracking
4. Error tracking and monitoring

## Frontend Implementation

The frontend uses `posthog-js` to track user interactions and page views.

### Key Components

- `lib/analytics.ts`: Central module for PostHog initialization and tracking utilities
- Correlation ID generation for cross-system tracking
- Integration with API requests to link backend interactions

### Standard Events

| Event Name | Description | Properties |
|------------|-------------|------------|
| `$pageview` | Page view tracking | `pageName` |
| `prompt_created` | New prompt creation | `promptId`, `source` |
| `prompt_executed` | Prompt execution | `promptId`, `model`, `success` |
| `login_success` | Successful login | `provider` |
| `login_failed` | Failed login attempt | `provider`, `error_type` |
| `api_request` | API request | `endpoint`, `method`, `correlationId` |

### Usage Example

```typescript
import { trackEvent, usePostHog } from '../lib/analytics';

// In a component
usePostHog('PromptEditor');

// Track a specific event
trackEvent('prompt_created', { promptId: '123', source: 'editor' });
```

## Backend Implementation

The backend uses the PostHog Python library to track server-side events.

### Key Components

- `utils/analytics.py`: PostHog integration for event tracking
- `utils/middleware.py`: Request middleware for tracking and correlation ID propagation
- Error handlers with automatic tracking

### Standard Events

| Event Name | Description | Properties |
|------------|-------------|------------|
| `api_request` | API request tracking | `endpoint`, `method`, `status` |
| `prompt_execution` | Prompt execution | `prompt_id`, `model`, `token_count`, `success`, `duration_ms` |
| `login` | Authentication event | `provider`, `success`, `error_type` |
| `error` | Application error | `error_type`, `message`, `context` |

### Usage Example

```python
from backend.utils.analytics import track_event, track_prompt_execution

# Track a general event
track_event('custom_event', {'key': 'value'})

# Track a prompt execution
track_prompt_execution(
    prompt_id='123',
    model='gpt-4',
    token_count=150,
    success=True,
    duration_ms=350
)
```

## Correlation IDs

Correlation IDs are used to track user journeys across systems. They are:

1. Generated on the frontend for each interaction
2. Passed to the backend via the `X-Correlation-ID` header
3. Returned in response headers
4. Attached to all related events in both systems

### Flow Diagram

```
Frontend                   Backend
+----------------+         +----------------+
| Generate ID    |-------->| Extract ID     |
+----------------+         | from request   |
                           +----------------+
                                   |
                                   v
+----------------+         +----------------+
| Store ID from  |<--------| Return ID in   |
| response       |         | response       |
+----------------+         +----------------+
        |                          |
        v                          v
+----------------+         +----------------+
| Attach ID to   |         | Attach ID to   |
| events         |         | events         |
+----------------+         +----------------+
```

## Configuration

### Environment Variables

- `NEXT_PUBLIC_POSTHOG_KEY`: PostHog API key for frontend
- `NEXT_PUBLIC_POSTHOG_HOST`: PostHog instance URL (default: app.posthog.com)
- `POSTHOG_API_KEY`: PostHog API key for backend
- `POSTHOG_HOST`: PostHog instance URL for backend

### Local Development

In development mode:
- Frontend events are logged to console instead of being sent
- Backend events are logged but not sent to PostHog

## Adding New Events

When adding new events:

1. Use semantic naming following the `object_action` pattern (e.g., `prompt_created`)
2. Include contextual properties but avoid sensitive data
3. Document the event in this file
4. Ensure correlation IDs are propagated where applicable 