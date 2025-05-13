## Krowoc Development Plan

This plan outlines the development of Krowoc, a platform for managing and executing prompts across multiple LLM providers. We will use a modern technology stack, prioritize a clean user experience, and adhere to best practices for software development.

---

### I. Project Overview
_This section defines what the project aims to build, its core scope, and the high-level outcomes expected for the MVP._

#### 1. Project Goals
- Develop a user-friendly web application for creating, organizing, and executing prompts.
- Integrate with multiple LLM providers (OpenAI, Anthropic Claude, Google Gemini) via the `aisuite` library.
- Enable users to bring their own API keys for LLM providers.
- Provide a landing page dashboard with key usage metrics.
- Implement a browser extension for easy prompt capture.
- Ensure a robust and scalable architecture.
- Prioritize real data and avoid mock data.
- Deliver a Minimum Viable Product (MVP) with core functionality.

#### 2. Scope
- User authentication and multi-tenant profiles.
- Prompt metadata management (CRUD).
- LLM integration and credential management.
- Prompt execution workflow.
- Response management.
- Browser clipper extension.
- Usage and cost tracking (dashboard on the landing page).
- Frontpage leaderboard based on execution and community votes.
- Deployment on suitable platforms.

---

### II. Tasks and Deliverables
_Tracks execution scope and maps individual tasks to technical and business deliverables._

#### Core Deliverables

| Category                 | Task                                                                 | Deliverable                                     |
|--------------------------|----------------------------------------------------------------------|--------------------------------------------------|
| Project Setup           | Scaffold projects, Git setup, dev scripts                           | Initialized codebases                           |
| Development Environment | Create docker-compose setup, seed data scripts, hot-reloading       | Developer-friendly local setup                  |
| API Contract Setup      | Define GraphQL schema, generate JSON Schema, implement Pydantic models | Type-safe, validated API contracts           |
| Database                | Create Alembic migration framework, implement migration validation  | Versioned, testable data model                  |
| Authentication          | Configure Supabase Auth with PKCE, implement token handling         | Secure, standards-compliant auth flow           |
| Core Monitoring         | Implement health checks, correlation IDs, PostHog integration       | Observable platform with diagnostics            |
| Prompt Authoring       | Add support for prompt metadata (title, description, prompt text, tags, model preference)   | Prompt creation/edit UI and schema updates       |
| Backend (Flask)         | GraphQL endpoints, LLM integration, cost tracking, DLQ handling, logging | Working REST API, async handlers, logs, observability |
| Backend Testing         | Unit + integration tests with `pytest`                               | CI-ready test coverage                          |
| Logging & Debugging     | Structured logs with `loguru`                                        | Debuggable production logs                      |
| Frontend (NextJS)       | UI components, state management, PromptEditorForm integration in Home & Prompts tabs, PostHog session replay + event analytics | Functional and styled UI with observability |
| Frontend Testing        | Unit + E2E with Jest + Playwright                                    | CI-ready test suite                             |
| Prompt Execution        | Streaming responses, `aisuite` SDK use                               | LLM response UX complete                        |
| Credential Management   | Secure storage + retrieval of API keys                              | Settings page and backend endpoints             |
| Dashboard & Metrics     | Usage charts via VisActor                                            | Functional analytics dashboard                  |
| Deployment              | Dockerized services deployed to Vercel/Render, Postgres provisioned via Supabase/Railway | Live MVP + deployment docs                      |
| Documentation           | Dev onboarding, usage guides, API docs                              | Full developer documentation                    |
| User Testing & Feedback | Session planning, usability evaluation                               | Feedback report                                 |

---

### III. Implementation Timeline and Phases
_Outlines development phases with estimated timeframes and dependencies._

#### Phase 1: Foundation (Week 1-2)
- Project setup and repository initialization
- Development environment configuration
- Database schema design and initial migrations
- Authentication integration with Supabase
- API contract definition with GraphQL
- Core monitoring setup

#### Phase 2: Core Features (Week 3-6)
- Backend API implementation
- Frontend UI components and views
- Prompt management functionality
- LLM integration via aisuite
- User authentication flows
- Basic analytics tracking

#### Phase 3: Enhancement (Week 7-9)
- Advanced prompt features (versioning, tagging)
- Dashboard metrics and visualizations
- Performance optimization
- Comprehensive testing
- Caching implementation
- Security hardening

#### Phase 4: Launch Preparation (Week 10-12)
- End-to-end testing
- User acceptance testing
- Documentation completion
- CI/CD pipeline refinement
- Production environment setup
- Launch readiness validation

#### Critical Path Items
- Database schema design (blocks most backend development)
- Authentication implementation (blocks user-specific features)
- GraphQL schema definition (blocks frontend-backend integration)
- LLM integration (core product functionality)

---

### IV. Technical Design
_Outlines the architecture, security posture, and platform infrastructure guiding development._

#### Stack Optimization and Security Enhancements
- **Unified Data Store:** Migrate entirely to Postgres for all user, admin, and application data; deprecate Pocketbase to reduce integration complexity.
- **Authentication:** Replace Pocketbase auth with Supabase Auth using OAuth2 with PKCE support and automatic refresh token rotation.
- **Session Management:**
  - Use JWTs stored in HTTP-only cookies with CSRF protection.
  - Implement token expiration (15m–1h) and refresh token logic.
- **API Design:** 
  - Adopt GraphQL for consistent API contracts
  - Define core GraphQL schema types and queries
  - Generate JSON Schema from GraphQL for validation
  - Implement Pydantic models that mirror GraphQL types for backend validation
  - Autogenerate OpenAPI specs for documentation
- **Frontend State:** Use React Query (TanStack) for data fetching and cache invalidation.
- **Secrets Management:** Move API key storage to HashiCorp Vault or Doppler from day one.
- **Observability:** 
  - Integrate request-level correlation IDs across frontend and backend
  - Implement health check endpoints with standardized response format
  - Configure structured logging with context preservation
- **Containerization:** 
  - Add Docker support with dev + prod-ready images
  - Create docker-compose setup for local development
- **Performance Baseline:**
  - Define SLOs (e.g., P95 API latency < 800ms)
  - Use synthetic monitoring to validate uptime and prompt execution flow
- **API Gateway:** Use Flask as the unified gateway for all requests; centralize rate limiting, auth validation, and logging.
- **DLQ Strategy:** Store failed executions in Postgres with reason, timestamp, retry count. Expose admin-only endpoints for retry + inspection.
- **Cost Controls:**
  - Log token usage and LLM cost approximation per execution.
  - Enforce per-user cost ceilings on Free tier executions.

#### Data Model Evolution
- **Unified Approach:** Use Postgres for all data storage, including user authentication, profiles, prompts, executions, votes, and analytics.
- **Rationale:** Centralizing storage in Postgres reduces complexity, avoids data duplication, and simplifies schema migrations and query operations.


- **Task Orchestration:** Use **Prefect** as the orchestration layer to support multi-stage prompt workflows.
- **Task Worker:** Introduce a Prefect-based task worker for background jobs such as leaderboard scoring, prompt enrichment, and retryable execution chains.
- This separation allows Flask to remain focused on API serving while long-running or complex logic is handled reliably in the background.

#### Monitoring & Observability
- **Error Tracking:** Use PostHog for capturing frontend and backend exceptions and user behavior.
- **Product Analytics:** Integrate PostHog to measure feature usage, funnel performance, and user engagement.
- **Logging:** Backend logs will be captured with `loguru`, while frontend logs will be piped to PostHog where feasible.
- **Metrics Monitoring (optional):** Plan for adding Prometheus + Grafana stack or an external APM tool (e.g., Datadog) if scale or complexity increases.

#### Technology Stack
- **Messaging & Caching:** Redis Pub/Sub for lightweight async messaging, Redis Streams for event transport, Redis for caching, session storage, and rate limiting
- **Frontend:** NextJS (React + TypeScript), Tailwind CSS, VisActor
- **Backend:** Flask (Python), Prefect for orchestration
- **Database:** Postgres (unified data store for user, prompts, and execution data)
- **LLM Integration:** [`aisuite`](https://github.com/andrewyng/aisuite)
- **Logging:** Python `loguru` for structured and streamlined logging in Flask (for relational data)

#### System Architecture
- **Observability:** PostHog integrated for frontend and backend error tracking, session replay, and product analytics.
- **Logging:** `loguru` for backend logs; important logs may be forwarded to PostHog.
- **Frontend:** Next.js for user interface and interactions
- **Backend:** Flask for business logic and LLM communication
- **Orchestration:** Prefect task worker for background jobs and multi-stage workflows
- **Database:** Postgres for user/admin data, prompts, executions, versioning, votes, and analytics
- **Messaging:** Redis Pub/Sub for async tasks, Redis Streams as optional lightweight event transport

---

### V. Development Process
_Defines how the team will set up, build, test, and deploy both backend and frontend systems._

#### 1. Project Setup
- **Repository Initialization**
  - Create separate folders for frontend, backend, and orchestration services
  - Setup Git with protected main branch, dev and feature branches
- **Development Environment**
  - Create docker-compose setup for local development
  - Implement development seed data scripts
  - Set up hot-reloading for both frontend and backend
- **Backend Setup (Flask)**
  - Create virtual environment, install Flask, setup initial route structure
  - Configure `.env` files with LLM provider keys, DB credentials, logging level
  - Implement health check endpoints with standardized format
  - Set up basic request logging with correlation IDs
- **Database (Postgres)**
  - Create Alembic migration framework and initial schemas
  - Define rollback procedures for failed migrations
  - Implement migration CI/CD validation pipeline
  - Define schema migrations for initial tables: users, prompts, executions, votes
  - Connect Flask with SQLAlchemy ORM
- **Observability Setup**
  - Install PostHog SDKs on both frontend and backend
  - Configure PostHog for frontend and backend error tracking
  - Add loguru to Flask with rotation, error filtering, and request metadata

#### 2. Backend Development
- **Authentication Implementation**
  - Enable OAuth providers (Google, GitHub, Microsoft) via Supabase Auth
  - Configure PKCE flow for all OAuth providers
  - Implement token validation and refresh logic
  - Add HTTP-only cookie storage with CSRF protection
  - Set up OAuth credentials for each provider in a secure `.env` or secret store
  - Handle sign-in redirects, token exchange, and session persistence
  - Sync profile data (email, display name, avatar) into user profile schema
- **API Contract Implementation**
  - Define GraphQL schema with core types and queries
  - Generate JSON Schema from GraphQL for validation
  - Implement Pydantic models matching GraphQL types
- **Redis Integration**
  - Use Pub/Sub for prompt execution events
  - Use Redis Streams for multi-consumer workflows like leaderboard updates
  - Implement IP/user-based rate limiting logic
  - Store short-lived sessions or tokens in Redis (if not fully handled by Supabase)
  - Set up Redis cache with environment-specific TTLs
- **Feature Flag Integration**
  - Integrate Unleash for feature flagging infrastructure from day one
- **Prompt Management**
  - Implement prompt usage quotas based on user tier (Free, Power, Team)
  - Track prompt_count per user and enforce limits at the API level
  - Return quota exceeded error if prompt creation is blocked
  - Extend prompt schema to include:
    - `title`: required string
    - `description`: optional string
    - `prompt_text`: required string
    - `tags`: array of optional strings
    - `model_whitelist`: optional list of LLM provider IDs
  - Validate allowed LLMs at creation and restrict execution accordingly
  - Update prompt creation and update API endpoints to accept and validate new fields
  - Introduce prompt lifecycle states: Draft → Published → Archived
- **LLM Integration**
  - Integrate with `aisuite`
  - Implement streaming LLM responses
  - Define retry strategy for failed prompt executions (e.g., 2 retries with exponential backoff)
  - Set timeout thresholds (e.g., 30s max response window for LLMs)
- **Workflow Orchestration**
  - Introduce a Prefect orchestration layer to support scalable, multi-stage prompt workflows
  - Ensure Postgres schema supports prompts, executions, versions, and votes
- **Analytics & Monitoring**
  - Track login events in PostHog:
    - `login_success` with provider and user ID
    - `login_failed` with provider and error reason (non-sensitive only)
  - Integrate PostHog for capturing backend exceptions, funnel metrics, and session-based diagnostics
  - Implement comprehensive logging using `loguru`

#### 3. Frontend Development
- **Type Safety Implementation**
  - Create TypeScript interfaces mirroring backend Pydantic models
  - Set up zod schemas for client-side validation
  - Implement GraphQL typed queries with codegen
- **State Management**
  - Implement React Query for data fetching and cache invalidation
  - Set up optimistic updates for common interactions
  - Configure proper error boundaries and fallbacks
- **Authentication UI**
  - Track login events in PostHog:
    - `login_success` with provider and user ID
    - `login_failed` with provider and error reason (non-sensitive only)
  - Implement OAuth login options (Google, GitHub, Microsoft) on sign-in page
  - Show login provider options based on environment configuration
  - Manage login redirect and session persistence
- **Core Components**
  - Implement a reusable PromptEditorForm component used across views
    - Accepts props for mode (create/edit), initial values, and context (e.g., 'home', 'prompts')
  - Add prompt creation support in:
    - **Home Tab**: Button triggers modal or drawer with `PromptEditorForm`
    - **Prompts Tab**: Sticky "+ New Prompt" button opens `PromptEditorForm`, refreshes list post-submit
- **Quota Management UI**
  - Add visual usage indicator for prompt quota in Home and Prompts tabs
  - Show "Upgrade" CTA when nearing or exceeding quota limit
  - Display toast or modal when prompt limit is reached
- **Form Validation**
  - Add prompt creation form supporting:
    - Title, Description, Prompt Text
    - Tag multi-select input
    - Optional model selection with validation and help text
  - Disable execution on incompatible models if a whitelist is defined
  - Display a notice when model-specific restriction is active
- **Analytics & Monitoring**
  - Track `prompt_created` event in PostHog with originating context
  - Integrate PostHog JavaScript SDK to track UI events, exceptions, prompt interactions, and usage funnels
  - Implement session replay for debugging via PostHog (e.g., identify issues in prompt editor or execution flows)
  - Add error boundary reporting to PostHog
- **Application Views**
  - **Home:** API Key Usage, Total Prompts Created, 5 Most Recent Prompts Executed
  - **Dashboard:** Prompt Executions, Execution Trend, Performance Overview, Execution Success Rate, Active Prompts
  - **Prompts:** Paginated prompt card list view with sorting and filtering options
  - Create/Edit, Detail, Settings
- **UI Implementation**
  - Build React + Tailwind UI components
  - Implement responsive design for all views
  - Ensure accessibility compliance (WCAG AA)
- **API Integration**
  - GraphQL query hooks with proper loading/error states
  - Websocket connection for real-time LLM response rendering
  - Optimistic UI updates for better UX
- **Development Tooling**
  - Set up hot-reloading for frontend
  - Implement storybook for component development
  - Create mock API responses for offline development

---

### VI. UI/UX Design
_Describes the core UI views and surface areas where users will interact with Krowoc._

#### Surface Areas

| View      | Key Features                                                                 |
|-----------|------------------------------------------------------------------------------|
| Home      | API Key Usage, Total Prompts Created, 5 Most Recent Executions              |
| Dashboard | Prompt Executions, Execution Trend, Success Rate, Active Prompts            |
| Prompts   | Paginated list, filters (category, tags), sorting (usage, votes, createdAt) |
| Settings  | API key management, profile settings                                        |

---

### VII. Testing and Quality Assurance
_Outlines the approach to testing, quality control, and validation._

#### Backend Testing
- Implement unit tests with pytest for core business logic
- Create integration tests for API endpoints
- Set up database testing with test fixtures
- Add contract testing for API schemas

#### Frontend Testing
- Implement component tests with React Testing Library
- Add E2E tests with Playwright for critical user journeys
- Set up visual regression testing for UI components
- Configure storybook testing for component states

#### API Contract Testing
- Validate schema consistency between frontend and backend
- Test GraphQL schema against generated TypeScript types
- Verify JSON Schema validation in API responses

#### Performance Testing
- Set up benchmark tests for API response times
- Create load tests for concurrent user scenarios
- Test streaming response performance

#### User Testing
- Conduct usability testing with representative users
- Gather feedback on UX friction points
- Validate feature discoverability

---

### VIII. Deployment and Operations
_Details the approach to deployment, monitoring, and ongoing operations._

#### Infrastructure Setup
- Set up Vercel project for frontend deployment
- Configure Render/Heroku for backend services
- Provision Redis Cloud instance
- Set up Supabase project for auth and database

#### CI/CD Pipeline
- Automated Testing:
  - Implement CI using GitHub Actions for continuous integration
  - Run backend unit and integration tests automatically
  - Execute frontend component and E2E tests
  - Generate test coverage reports
- Code Quality:
  - Configure type checking for both frontend and backend
  - Set up linters and style checkers (ESLint, Prettier, Pylint, Black)
  - Implement code complexity metrics with thresholds
  - Enforce code review requirements
- Deployment Automation:
  - Run backend unit tests, linters, and type checks
  - Bundle frontend and deploy preview via Vercel
  - Validate schema migrations with Postgres tests
  - Set up production deployment workflow with approval gates
- Database Safety:
  - Validate database migrations in CI before deployment
  - Create rollback scripts for database changes
  - Test migrations against schema snapshot
- Security Scanning:
  - Implement dependency vulnerability scanning
  - Run SAST (Static Application Security Testing)
  - Scan Docker images for vulnerabilities
- Documentation:
  - Automatically generate API documentation
  - Update schema documentation from code
  - Maintain changelog from commit messages
- Workflow Enforcement:
  - Ensure merge protection and enforce test pass status on main branches
  - Require code review approvals
  - Enforce conventional commit message format
  - Automate release version bumping

#### Environment Configuration
- Set up separate development, staging, and production environments
- Configure environment-specific variables
- Implement secrets management for sensitive credentials

#### Monitoring Setup
- Configure health check monitoring
- Set up error alerting for critical issues
- Implement logging pipelines

#### Performance Engineering
- Database Optimization:
  - Implement connection pooling for database access
  - Create efficient indexes for common query patterns
  - Set up query monitoring and optimization
- Caching Strategy:
  - Implement tiered caching with appropriate TTLs:
    - Application memory cache for hot data
    - Redis cache for shared application data
    - CDN for static assets
  - Create cache invalidation hooks for data changes
- Load Testing:
  - Conduct load testing using k6 or Locust targeting API endpoints and orchestration tasks
  - Define baseline metrics: P95 latency, throughput per user, time to first byte for streaming responses
  - Simulate scaled user scenarios for performance testing
- Performance Monitoring:
  - Set up real-time performance dashboards
  - Configure alerts for performance degradation
  - Implement user-facing performance metrics
- Optimization:
  - Identify and optimize slow database queries
  - Implement frontend performance optimization (code splitting, lazy loading)
  - Configure CDN for edge caching of static assets
  - Continuously monitor these metrics during deployment cycles

#### Deployment Documentation
- Create runbooks for common deployment scenarios
- Document rollback procedures
- Provide environment setup instructions

---

### IX. Risks and Mitigation
_Identifies technical and operational risks and how they will be managed._

| Risk                                 | Mitigation Strategy                                                                 |
|--------------------------------------|--------------------------------------------------------------------------------------|
| API Key Security                     | Move from Pocketbase storage to Vault/KMS for API key encryption post-MVP          |
| Versioning Ambiguity in Prompts     | Lock published prompts, introduce immutable version snapshots                      |
| Score Freshness Bias                | Introduce decay-based adjustments for recency in rankings                          |
| Rate Limiting / Abuse               | Add per-user and per-IP rate limits, monitor abuse patterns with PostHog           |
| Scaling Blind Spots                 | Add performance simulations for high-load and failover conditions                  |
| Observability Gaps                  | Include end-to-end tracing and correlation IDs between frontend and backend        |

---

### X. Strategic Initiatives
_Documents broader system capabilities such as orchestration, AI enhancement, and extensibility._

#### 1. Feature Flag Infrastructure
- Integrate Unleash to manage rollouts, A/B testing, and beta access control.
- Allow granular control of experimental or tiered features via feature toggles.
- Enable backend flags that frontend can dynamically query.

#### 2. AI-Driven Features (Current Scope)
- **Prompt Suggestions**: Suggest prompts based on historical success patterns or similarity to previous inputs.
- **Prompt Optimization**: Enable LLM-generated prompt rewrites based on observed outcomes or goals.
- **Vector Search**: Use vector embeddings to allow semantic prompt search (e.g., pgvector, Weaviate).
- **Autonomous Prompt Agents**: Enable background AI agents to scan domains of interest and suggest new prompts (crawler-based).
- **Periodic Prompt Generation**: Auto-generate and schedule prompt suggestions based on user preferences and interest history.

#### 3. Frontpage Prompt Ranking
_Implementation details for the leaderboard feature._

To power the frontpage, prompts will be ranked based on two key metrics:

1. **Executions in the Last 24 Hours (E)**
2. **Community Votes (V)**

**Score Calculation (Simple Weighted Model):**
```
score = (E / max(E)) * 0.6 + (V / max(V)) * 0.4
```
- Normalize each KPI by its max value in the top 50 pool.
- Weight executions more (0.6) to reflect real-world usage.
- Update scores hourly and refresh frontpage ranking accordingly.

**Implementation Steps:**
- Track prompt executions with timestamps.
- Store and update community votes.
- Calculate both simple weighted and Wilson-based scores.
- Build backend API for top prompts based on computed scores.
- Render a visually engaging leaderboard with ranks, stats, and upvote interaction.

#### 4. Data Model Strategy
- Enhance prompt ranking logic by incorporating Wilson score confidence interval for fairer rankings, especially with low-vote prompts.
  - Formula:
    ```
    score = (p + z^2/(2n) - z * sqrt((p*(1-p)+z^2/(4n))/n)) / (1+z^2/n)
    ```
    Where:
    - `p` = upvotes / total votes
    - `n` = total number of votes
    - `z` = 1.96 (for 95% confidence)
  - This model favors prompts with high confidence in their quality, not just raw vote counts.
- Introduce a Prefect orchestration layer to support scalable, multi-stage prompt workflows
- Introduce prompt lifecycle states: Draft → Published → Archived
- Add import/export support for prompts via JSON to promote portability
- Support default LLM + parameter templates at the prompt level
- Consider orchestration frameworks (e.g., Temporal or Prefect) for future complex workflows

---

### XI. Go-To-Market Strategy
_Outlines adoption targets, pricing tiers, success metrics, and the phased launch plan._

#### 1. Target Users

| Persona                  | Description                                                                             |
|--------------------------|-----------------------------------------------------------------------------------------|
| Prompt Engineers         | Power users managing prompt libraries and fine-tuning usage across LLMs                |
| Internal AI Product Teams| Cross-functional teams building GenAI into products, requiring versioned prompt control|
| AI-curious Developers    | Engineers prototyping workflows using their own LLM keys                               |
| Enterprise Enablement    | Knowledge workers in large orgs running prompts tied to business tools                 |

#### 2. Lifecycle & Adoption Plan

| Tier        | Prompt Limit | Features                                                                      |
|-------------|--------------|-------------------------------------------------------------------------------|
| Free Tier   | 50 prompts   | BYO API key, limited analytics, community leaderboard                        |
| Power User  | Unlimited    | Prompt tagging, version history, execution analytics                         |
| Team Plan   | Unlimited    | Shared prompt libraries, access control, organization-wide dashboards        |


#### 3. Success Metrics

| Metric                            | Purpose                                               |
|----------------------------------|-------------------------------------------------------|
| Weekly Active Prompt Creators    | Captures creator engagement                          |
| Time to First Successful Execution (TTFSE) | Measures onboarding friction             |
| Prompt Execution Completion Rate | Detects errors, informs reliability                   |
| Prompt Usage per User            | Identifies power users and advocates                  |

#### 4. Launch Plan

| Phase            | Audience                    | Goals                                               |
|------------------|-----------------------------|-----------------------------------------------------|
| Alpha (Internal) | Core devs/testers           | Bug discovery, UX gaps                              |
| Private Beta     | 3–5 external design partners| Validate use cases, pricing insight, feature gaps   |
| Public Launch    | General developer community | Broader adoption, feedback-driven growth            |

---

### XII. Roadmap
_Defines major future features that are valuable but not required in the MVP._

#### 1. Roadmap Items

| Feature             | Description                                                         | Status                |
|---------------------|---------------------------------------------------------------------|-----------------------|
| Clipper Extension  | Build Chrome/Safari extension, URL & snippet capture functionality  | Planned for post-MVP |
| Leaderboard Experience | Showcase trending prompts with usage and engagement metrics             | Planned for post-MVP |