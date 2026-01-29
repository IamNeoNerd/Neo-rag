# Frontend Requirements & Pending Features

> Features that will be implemented in the frontend to give users control over configuration and monitoring.

---

## 1. Custom API Key Integration

Users will provide their own LLM API keys through the frontend settings, rather than storing them server-side.

### Requirements
- [ ] Settings page with API key input fields
- [ ] Support for multiple providers:
  - OpenAI API Key
  - Anthropic API Key  
  - Cohere API Key
- [ ] Client-side validation (format check)
- [ ] Secure transmission to backend (per-request header)
- [ ] No server-side storage of keys (session-only)

### Backend Changes Needed
- [ ] Accept API keys via request headers (`X-OpenAI-Key`, etc.)
- [ ] Update services to use per-request keys
- [ ] Add endpoint to validate API key without storing

---

## 2. Rate Limiting Configuration

Rate limits will be configurable by users through frontend settings.

### Requirements
- [ ] Settings panel for rate limit configuration
- [ ] Configurable limits:
  - Requests per minute (default: 60)
  - Requests per hour (default: 1000)
  - Burst limit (default: 10)
- [ ] Display current usage vs limits
- [ ] Visual indicator when approaching limits

### Backend Changes Needed
- [ ] Endpoint to update rate limit settings
- [ ] Per-user rate limit storage
- [ ] Include limits in rate-limit-status response

---

## 3. Health Monitoring Dashboard

Frontend will display real-time health status of all connected services.

### Requirements
- [ ] Health status panel on main dashboard
- [ ] Service status indicators:
  - Neon PostgreSQL (connected/disconnected)
  - Neo4j Aura (connected/disconnected)
  - OpenAI API (working/error)
  - Anthropic API (working/error)
  - Cohere API (working/error)
- [ ] Auto-refresh every 30 seconds
- [ ] Manual refresh button
- [ ] Error details on hover/click

### Backend Changes Needed
- [ ] Enhanced `/health` endpoint with LLM status
- [ ] LLM connectivity test endpoint
- [ ] Detailed error messages in health response

---

## 4. Connection Pooling Status

Display database connection pool statistics.

### Requirements
- [ ] Pool status in health monitoring
- [ ] Show active/available connections
- [ ] Warning when pool is near capacity

---

## Implementation Priority

| Feature | Priority | Effort |
|---------|----------|--------|
| Health Monitoring | High | Medium |
| Custom API Keys | High | Medium |
| Rate Limit Config | Medium | Low |
| Pool Status Display | Low | Low |

---

## API Endpoints Needed

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Enhanced health with LLM status |
| `/api/v1/validate-key` | POST | Validate API key without storing |
| `/api/v1/settings/rate-limit` | PUT | Update rate limit settings |
| `/rate-limit-status` | GET | Current rate limit stats (exists) |
