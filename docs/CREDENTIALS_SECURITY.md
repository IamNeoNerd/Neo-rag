# Credentials & Security

## Key Principles
- All API keys are entered by user in backend dashboard.
- Keys are stored encrypted (AES-256 at rest).
- Keys never leave backend except for runtime model calls.

## Verification Flow
1. User enters API key & base URL.
2. Backend pings provider's `/models` or similar endpoint.
3. If success → mark provider "Active".
4. If fail → return error to UI.

## Supported Providers
- OpenAI
- Anthropic
- Cohere
- Local inference endpoints (user-provided base URL)

---

## Testing Keys
- Use test endpoints where possible.
- Never store plaintext keys in logs.

---

## Mobile-first Note
- Credentials are stored centrally; mobile app never caches them locally.