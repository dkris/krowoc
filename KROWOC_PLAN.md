## Krowoc Development Plan

This plan outlines the development of Krowoc, a platform for managing and executing prompts across multiple LLM providers. We will use a modern technology stack, prioritize a clean user experience, and adhere to best practices for software development.

---

### I. Project Overview

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

#### Data Model Evolution
- **Hybrid Approach:** Use Pocketbase for user authentication, profiles, and admin UI management.
- **Relational Data Store:** Use Postgres for core domain entities like prompts, executions, votes, LLM usage logs, and versioning.
- **Orchestration Integration:** Use Prefect as the task orchestrator to manage inter-system consistency, background scoring, and batch tasks.
- **Rationale:** Pocketbase simplifies dev/admin UX, while Postgres ensures relational integrity, indexing, and analytical performance.

#### Orchestration Strategy
- **Task Orchestration:** Use **Prefect** as the orchestration layer to support multi-stage prompt workflows.
- **Task Worker:** Introduce a Prefect-based task worker for background jobs such as leaderboard scoring, prompt enrichment, and retryable execution chains.
- This separation allows Flask to remain focused on API serving while long-running or complex logic is handled reliably in the background.

#### Monitoring & Observability
- **Error Tracking:** Use PostHog for capturing frontend and backend exceptions and user behavior.
- **Product Analytics:** Integrate PostHog to measure feature usage, funnel performance, and user engagement.
- **Logging:** Backend logs will be captured with `loguru`, while frontend logs will be piped to PostHog where feasible.
- **Metrics Monitoring (optional):** Plan for adding Prometheus + Grafana stack or an external APM tool (e.g., Datadog) if scale or complexity increases.

#### 3. Technology Stack
- **Frontend:** NextJS (React + TypeScript), Tailwind CSS, VisActor
- **Backend:** Flask (Python), Prefect for orchestration, Kafka for async task messaging
- **Database:** Pocketbase (for authentication/admin), Postgres (for relational data)
- **LLM Integration:** [`aisuite`](https://github.com/andrewyng/aisuite)
- **Logging:** Python's `loguru` for structured and streamlined logging in Flask

#### 4. System Architecture
- **Observability:** PostHog integrated for frontend and backend error tracking, session replay, and product analytics.
- **Logging:** `loguru` for backend logs; important logs may be forwarded to PostHog.
- **Frontend:** Next.js for user interface and interactions
- **Backend:** Flask for business logic and LLM communication
- **Orchestration:** Prefect task worker for background jobs and multi-stage workflows
- **Database:** Pocketbase for user/admin data; Postgres for prompt, execution, versioning, votes, and analytics
- **Messaging:** Kafka for async tasks and event queueing

---

### III. Development Process

#### 1. Project Setup
- Set up NextJS, Flask, Pocketbase projects
- Git setup and branching strategy
- Unified startup script
- Initialize Pocketbase, and Postgres schema

#### 2. Backend Development (Flask)
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
- Integrate Postgres alongside Pocketbase to manage prompts, executions, versions, and votes
- RESTful APIs for prompts, execution, user and usage data
- Integrate with `aisuite`
- Kafka integration
- Streaming LLM responses
- Comprehensive logging using `loguru`
- Frontpage leaderboard logic:
  - Track prompt executions with timestamps
  - Record and store community votes
  - Aggregate and normalize execution and vote KPIs
  - Calculate ranking scores and expose API endpoint for top 50 prompts
- Define retry strategy for failed prompt executions (e.g., 2 retries with exponential backoff)
- Set timeout thresholds (e.g., 30s max response window for LLMs)
- Implement dead-letter queue using Kafka for unrecoverable jobs

#### 3. Frontend Development (NextJS)
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
- Deploy to Vercel/Netlify (frontend), Heroku/Render (backend), Pocketbase Cloud
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

#### Surface Areas

| View      | Key Features                                                                 |
|-----------|------------------------------------------------------------------------------|
| Home      | API Key Usage, Total Prompts Created, 5 Most Recent Executions              |
| Dashboard | Prompt Executions, Execution Trend, Success Rate, Active Prompts            |
| Prompts   | Paginated list, filters (category, tags), sorting (usage, votes, createdAt) |
| Settings  | API key management, profile settings                                        |

---

### V. Tasks and Deliverables

#### Tasks and Deliverables

| Category                 | Task                                                                 | Deliverable                                     |
|--------------------------|----------------------------------------------------------------------|--------------------------------------------------|
| Project Setup           | Scaffold projects, Git setup, dev scripts                           | Initialized codebases                           |
| Database                | Define schema in Pocketbase                                          | Data model in place                             |
| Prompt Authoring       | Add support for prompt metadata (title, description, prompt text, tags, model preference)   | Prompt creation/edit UI and schema updates       |
| Backend (Flask)         | API endpoints, LLM integration, Kafka, logging, PostHog analytics integration | Working REST API, async handlers, logs, observability |
| Backend Testing         | Unit + integration tests with `pytest`                               | CI-ready test coverage                          |
| Logging & Debugging     | Structured logs with `loguru`                                        | Debuggable production logs                      |
| Frontend (NextJS)       | UI components, state management, PromptEditorForm integration in Home & Prompts tabs, PostHog session replay + event analytics | Functional and styled UI with observability |
| Frontend Testing        | Unit + E2E with Jest + Playwright                                    | CI-ready test suite                             |
| Prompt Execution        | Streaming responses, `aisuite` SDK use                               | LLM response UX complete                        |
| Credential Management   | Secure storage + retrieval of API keys                              | Settings page and backend endpoints             |
| Dashboard & Metrics     | Usage charts via VisActor                                            | Functional analytics dashboard                  |
| Deployment              | Deploy to Vercel/Heroku, document setup                             | Live MVP + deployment docs                      |
| Documentation           | Dev onboarding, usage guides, API docs                              | Full developer documentation                    |
| User Testing & Feedback | Session planning, usability evaluation                               | Feedback report                                 |

---

### VI. Frontpage Prompt Ranking (Post-MVP Backend Support)

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

#### 1. Data Model Strategy
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

#### 1. Roadmap Items

| Feature             | Description                                                         | Status                |
|---------------------|---------------------------------------------------------------------|-----------------------|
| Clipper Extension  | Build Chrome/Safari extension, URL & snippet capture functionality  | Planned for post-MVP |
| Leaderboard Experience | Showcase trending prompts with usage and engagement metrics             | Planned for post-MVP |