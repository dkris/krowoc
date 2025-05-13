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

### II. Technical Design
_Outlines the architecture, security posture, and platform infrastructure guiding development._

#### Stack Optimization and Security Enhancements
- **Unified Data Store:** Migrate entirely to Postgres for all user, admin, and application data; deprecate Pocketbase to reduce integration complexity.
- **Authentication:** Replace Pocketbase auth with Supabase Auth using OAuth2 with PKCE support and automatic refresh token rotation.
- **Session Management:**
  - Use JWTs stored in HTTP-only cookies with CSRF protection.
  - Implement token expiration (15m–1h) and refresh token logic.
- **API Design:** Adopt GraphQL for consistent API contracts; autogenerate OpenAPI specs for documentation.
- **Frontend State:** Use React Query (TanStack) for data fetching and cache invalidation.
- **Secrets Management:** Move API key storage to HashiCorp Vault or Doppler from day one.
- **Observability:** Integrate request-level correlation IDs across frontend and backend.
- **Containerization:** Add Docker support with dev + prod-ready images.
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

#### 3. Technology Stack
- **Messaging & Caching:** Redis Pub/Sub for lightweight async messaging, Redis Streams for event transport, Redis for caching, session storage, and rate limiting
- **Frontend:** NextJS (React + TypeScript), Tailwind CSS, VisActor
- **Backend:** Flask (Python), Prefect for orchestration
- **Database:** Postgres (unified data store for user, prompts, and execution data)
- **LLM Integration:** [`aisuite`](https://github.com/andrewyng/aisuite)
- **Logging:** Python `loguru` for structured and streamlined logging in Flask (for relational data)

#### 4. System Architecture
- **Observability:** PostHog integrated for frontend and backend error tracking, session replay, and product analytics.
- **Logging:** `loguru` for backend logs; important logs may be forwarded to PostHog.
- **Frontend:** Next.js for user interface and interactions
- **Backend:** Flask for business logic and LLM communication
- **Orchestration:** Prefect task worker for background jobs and multi-stage workflows
- **Database:** Postgres for user/admin data, prompts, executions, versioning, votes, and analytics
- **Messaging:** Redis Pub/Sub for async tasks, Redis Streams as optional lightweight event transport

---

### III. Development Process
_Defines how the team will set up, build, test, and deploy both backend and frontend systems._

#### 1. Project Setup
- **OAuth Configuration**
  - Enable OAuth providers (Google, GitHub, Microsoft) via Supabase Auth
  - Set up OAuth credentials for each provider in a secure `.env` or secret store
  - Configure redirect URIs and scopes per provider requirements
  - Handle sign-in redirects, token exchange, and session persistence
  - Sync profile data (email, display name, avatar) into user profile schema
- **Repository Initialization**
  - Create separate folders for frontend, backend, and orchestration services
  - Setup Git with protected main branch, dev and feature branches
- **Backend Setup (Flask)**
  - Create virtual environment, install Flask, setup initial route structure
  - Configure `.env` files with LLM provider keys, DB credentials, logging level
- **Database (Postgres)**
  - Define schema migrations using Alembic or SQL files
  - Create initial tables: users, prompts, executions, votes
  - Connect Flask with SQLAlchemy ORM
- **Observability**
  - Install PostHog SDKs on both frontend and backend
  - Add loguru to Flask with rotation, error filtering, and request metadata
- **Testing & Quality**
  - Add pytest and Playwright scaffolding
  - Define test strategy for API endpoints and user flows
- **CI/CD**
  - Setup GitHub Actions workflow:
    - Linting and type-checks
    - Backend test runner
    - Frontend preview deploy to Vercel
    - Postgres migration validation
- **Deployment**
  - Configure deployment to Vercel (frontend), Render/Heroku (backend)
  - Setup staging and production environments with secrets

#### 2. Backend Development (Flask)
- Integrate Redis:
  - Use Pub/Sub for prompt execution events
  - Use Redis Streams for multi-consumer workflows like leaderboard updates
  - Implement IP/user-based rate limiting logic
  - Store short-lived sessions or tokens in Redis (if not fully handled by Supabase)
- Integrate Unleash for feature flagging infrastructure from day one
- Track login events in PostHog:
  - `login_success` with provider and user ID
  - `login_failed` with provider and error reason (non-sensitive only)
- Implement OAuth login via Supabase Auth (Google, GitHub, Microsoft)
- Handle token validation, session storage, and user mapping
- Sync user profile info (name, email, avatar) to internal schema
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
- Integrate PostHog for capturing backend exceptions, funnel metrics, and session-based diagnostics
- Unit and integration tests with pytest
- Introduce a Prefect orchestration layer to support scalable, multi-stage prompt workflows
- Introduce prompt lifecycle states: Draft → Published → Archived
- Ensure Postgres schema supports prompts, executions, versions, and votes
- RESTful APIs for prompts, execution, user and usage data
- Integrate with `aisuite`
- Streaming LLM responses
- Comprehensive logging using `loguru`
- Frontpage leaderboard logic:
  - Track prompt executions with timestamps
  - Record and store community votes
  - Aggregate and normalize execution and vote KPIs
  - Calculate ranking scores and expose API endpoint for top 50 prompts
- Define retry strategy for failed prompt executions (e.g., 2 retries with exponential backoff)
- Set timeout thresholds (e.g., 30s max response window for LLMs)

#### 3. Frontend Development (NextJS)
- Track login events in PostHog:
  - `login_success` with provider and user ID
  - `login_failed` with provider and error reason (non-sensitive only)
- Implement OAuth login options (Google, GitHub, Microsoft) on sign-in page
- Show login provider options based on environment configuration
- Manage login redirect and session persistence
- Add visual usage indicator for prompt quota in Home and Prompts tabs
- Show "Upgrade" CTA when nearing or exceeding quota limit
- Display toast or modal when prompt limit is reached
- Implement a reusable PromptEditorForm component used across views
  - Accepts props for mode (create/edit), initial values, and context (e.g., 'home', 'prompts')
- Add prompt creation support in:
  - **Home Tab**: Button triggers modal or drawer with `PromptEditorForm`
  - **Prompts Tab**: Sticky "+ New Prompt" button opens `PromptEditorForm`, refreshes list post-submit
- Track `prompt_created` event in PostHog with originating context
- Add prompt creation form supporting:
  - Title, Description, Prompt Text
  - Tag multi-select input
  - Optional model selection with validation and help text
- Disable execution on incompatible models if a whitelist is defined
- Display a notice when model-specific restriction is active
- Integrate PostHog JavaScript SDK to track UI events, exceptions, prompt interactions, and usage funnels
- Implement session replay for debugging via PostHog (e.g., identify issues in prompt editor or execution flows)
- Unit and E2E tests with Jest and Playwright
- Build React + Tailwind UI components
- Views:
  - **Home:** API Key Usage, Total Prompts Created, 5 Most Recent Prompts Executed
  - **Dashboard:** Prompt Executions, Execution Trend, Performance Overview, Execution Success Rate, Active Prompts
  - **Prompts:** Paginated prompt card list view with sorting and filtering options
  - Create/Edit, Detail, Settings
- State management
- API integration
- Real-time LLM response rendering

#### 4. Testing
- Unit and integration tests
- E2E tests with Playwright
- User testing and feedback

#### 5. Deployment
- Deploy to Vercel/Netlify (frontend), Heroku/Render (backend), Redis Cloud
- Deployment documentation

#### 6. Performance Engineering
- Conduct load testing using k6 or Locust targeting API endpoints and orchestration tasks
- Define baseline metrics: P95 latency, throughput per user, time to first byte for streaming responses
- Continuously monitor these metrics during deployment cycles

#### 7. CI/CD Integration
- Implement CI using GitHub Actions:
  - Run backend unit tests, linters, and type checks
  - Bundle frontend and deploy preview via Vercel
  - Validate schema migrations with Postgres tests
- Ensure merge protection and enforce test pass status on main branches

---

### IV. UI/UX Design
_Describes the core UI views and surface areas where users will interact with Krowoc._

#### Surface Areas

| View      | Key Features                                                                 |
|-----------|------------------------------------------------------------------------------|
| Home      | API Key Usage, Total Prompts Created, 5 Most Recent Executions              |
| Dashboard | Prompt Executions, Execution Trend, Success Rate, Active Prompts            |
| Prompts   | Paginated list, filters (category, tags), sorting (usage, votes, createdAt) |
| Settings  | API key management, profile settings                                        |

---

### V. Tasks and Deliverables
_Tracks execution scope and maps individual tasks to technical and business deliverables._

#### Tasks and Deliverables

| Category                 | Task                                                                 | Deliverable                                     |
|--------------------------|----------------------------------------------------------------------|--------------------------------------------------|
| Project Setup           | Scaffold projects, Git setup, dev scripts                           | Initialized codebases                           |
| Database                | Define schema in Postgres                                        | Data model in place                             |
| Prompt Authoring       | Add support for prompt metadata (title, description, prompt text, tags, model preference)   | Prompt creation/edit UI and schema updates       |
| Backend (Flask)         | GraphQL endpoints, LLM integration, cost tracking, DLQ handling, logging, PostHog analytics integration | Working REST API, async handlers, logs, observability |
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

### VI. Frontpage Prompt Ranking (Post-MVP Backend Support)
_Explains the algorithm and backend implementation details for future leaderboard features._

_See also: [Strategic Initiatives](#viii-strategic-initiatives) → Data Model Strategy for scoring logic._

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

---

### VII. Risks and Mitigation
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

### VIII. Strategic Initiatives
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

#### 3. Data Model Strategy
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

### IX. Go-To-Market Strategy
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

### X. Roadmap
_Defines major future features that are valuable but not required in the MVP._

#### 1. Roadmap Items

| Feature             | Description                                                         | Status                |
|---------------------|---------------------------------------------------------------------|-----------------------|
| Clipper Extension  | Build Chrome/Safari extension, URL & snippet capture functionality  | Planned for post-MVP |
| Leaderboard Experience | Showcase trending prompts with usage and engagement metrics             | Planned for post-MVP |
