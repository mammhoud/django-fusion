# Tinker API Reference

Complete API documentation for the Tinker template customizer and AI chat service.

## Base URL

- **Local Development:** `http://localhost:5073`
- **Docker Compose:** `http://cypercloud.localhost:5073` (via Traefik)
- **Production:** `https://cypercloud.structa.cloud` (via Traefik with HTTPS)

---

## Chat & Conversation API

### List Recent Conversations

**Request:**
```http
GET / HTTP/1.1
Accept: text/html
```

**Response:**
```html
200 OK
Content-Type: text/html

<!-- Homepage with conversation list -->
```

**Context Variables:**
- `recent_conversations` – Last 5 conversations ordered by updated_at
- `customizer_apps` – List of configured sites
- `model_choices` – Available AI models
- `default_model_id` – Default model for new conversations

---

### Create New Conversation

**Request:**
```http
POST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded

message=Write+a+React+component&model_id=gemma3-4b
```

**Parameters:**
- `message` (required) – Initial user message
- `model_id` (optional) – Model to use; defaults to "gemma3-4b"

**Response:**
```http
302 Found
Location: /chat/3/?model_id=gemma3-4b
```

Redirects to the new conversation view with streaming enabled.

---

### View Conversation

**Request:**
```http
GET /chat/{conversation_id}/ HTTP/1.1
Accept: text/html
```

**URL Parameters:**
- `conversation_id` (required) – ID of the conversation
- `model_id` (query, optional) – Override model for new messages

**Response:**
```html
200 OK
Content-Type: text/html

<!-- Chat interface with conversation history -->
```

**Context Variables:**
- `conversation` – The Conversation object
- `messages` – All messages in the conversation
- `messages_with_content` – Messages with formatted HTML content
- `customizer_apps` – Available sites
- `sidebar_templates` – Templates for the default website
- `recent_conversations` – Last 5 conversations

---

### Send Message to Conversation

**Request:**
```http
POST /chat/{conversation_id}/ HTTP/1.1
Content-Type: application/x-www-form-urlencoded

message=Modify+the+component+to...&model_id=gpt-4o
```

**URL Parameters:**
- `conversation_id` (required)

**Form Parameters:**
- `message` (required) – User message text
- `model_id` (optional, query or form) – AI model to use

**Response:**
```html
200 OK
Content-Type: text/html

<!-- User message HTML + AI response placeholder + SSE script -->
<div class="d-flex justify-content-end mb-3">
    <div class="message-bubble user-message">
        <!-- User message content -->
    </div>
</div>

<div class="d-flex justify-content-start mb-3" id="ai-response-{message_id}">
    <div class="ai-avatar">...</div>
    <div class="message-bubble ai-message">
        <div id="ai-content-{message_id}"></div>
        <small id="ai-timestamp-{message_id}"></small>
    </div>
</div>

<script>
    const eventSource = new EventSource('/chat/{id}/stream/?message_id={message_id}');
    // ... SSE handling ...
</script>
```

**Error Responses:**
```http
400 Bad Request
Content-Type: text/plain

Message cannot be empty
```

---

### Stream AI Response (Server-Sent Events)

**Request:**
```http
GET /chat/{conversation_id}/stream/ HTTP/1.1
Accept: text/event-stream

?message_id={message_id}&model_id=gemma3-4b
```

**URL Parameters:**
- `conversation_id` (required)
- `message_id` (query, required) – ID of the user message
- `model_id` (query, optional) – AI model to use

**Response (Streaming):**
```
200 OK
Content-Type: text/event-stream
Cache-Control: no-cache

data: {"type": "token", "content": "Here"}

data: {"type": "token", "content": " is"}

data: {"type": "token", "content": " a"}

data: {"type": "done", "timestamp": "10:30 AM", "model": "Gemma 3 4B"}
```

**Event Types:**
- `token` – Streaming content chunk
  ```json
  {"type": "token", "content": "text chunk"}
  ```
- `done` – Stream complete
  ```json
  {"type": "done", "timestamp": "10:30 AM", "model": "Model Name"}
  ```
- `error` – Stream error
  ```json
  {"type": "error", "content": "Error message"}
  ```

**Notes:**
- Connection stays open; browser handles reconnection
- Used by HTMX and vanilla JS EventSource API
- Supports both Ollama and Ceptor-AI backends

---

### Stream with Ceptor-AI Backend

**Request:**
```http
GET /chat/{conversation_id}/ceptor-stream/ HTTP/1.1
?message_id={message_id}&model_id=ceptor-openai
```

**URL Parameters:**
- `conversation_id` (required)
- `message_id` (query, required)
- `model_id` (query, required) – One of:
  - `ceptor-chat`
  - `ceptor-openai`
  - `ceptor-claude`
  - `ceptor-gemini`

**Response:**
Same SSE format as `/stream/`, but uses configured Ceptor AI backends.

---

### Render Markdown to HTML

**Request:**
```http
POST /chat/{conversation_id}/render-markdown/ HTTP/1.1
Content-Type: application/json
X-CSRFToken: {csrf_token}

{"content": "# Title\n\n**Bold text**"}
```

**Request Body:**
- `content` (required) – Markdown text

**Response:**
```json
200 OK
Content-Type: text/html

<h1>Title</h1>
<p><strong>Bold text</strong></p>
```

**Supported Markdown:**
- Headers: `# H1`, `## H2`, etc.
- Bold: `**text**`
- Italic: `*text*`
- Code blocks: ` ```code``` `
- Inline code: `` `code` ``
- Links: `[text](url)`
- Lists: `- item`

---

## Template Discovery API

### List Configured Websites

**Request:**
```http
GET /api/websites/ HTTP/1.1
Accept: text/html
```

**Response:**
```html
200 OK
Content-Type: text/html

<!-- List of configured websites with links -->
```

**Context:**
- `websites` – List of configured sites from `CUSTOMIZER_APPS`

---

### Get Pages for Website

**Request (HTML):**
```http
GET /api/pages/{website_slug}/ HTTP/1.1
Accept: text/html
```

**Request (JSON):**
```http
GET /api/pages/{website_slug}/?format=json HTTP/1.1
Accept: application/json
```

**URL Parameters:**
- `website_slug` (required) – One of: `precis-ctc`, `lms`, `VResume`

**Response (HTML):**
```html
200 OK
Content-Type: text/html

<!-- Page cards and template grid -->
```

**Response (JSON):**
```json
200 OK
Content-Type: application/json

{
  "website": {
    "slug": "precis-ctc",
    "name": "CTC Research",
    "template_root": "/path/to/templates"
  },
  "pages": [
    {
      "path": "home/main.html",
      "name": "Home",
      "sections": [...]
    }
  ],
  "sections": [
    {
      "page_path": "home/main.html",
      "name": "hero",
      "type": "component",
      "template": "components/sections/hero.html"
    }
  ]
}
```

**Error Response:**
```json
404 Not Found
{"error": "Unknown website"}
```

---

## HTMX Fragment Endpoints

These endpoints return partial HTML for HTMX integration.

### Page Navigator Fragment

**Request:**
```http
GET /fragments/page-navigator/ HTTP/1.1
```

**Response:**
```html
200 OK

<!-- Website navigation links for sidebar -->
```

---

### Page Card Grid Fragment

**Request:**
```http
GET /fragments/page-cards/{website_slug}/ HTTP/1.1
```

**Response:**
```html
200 OK

<!-- Bootstrap grid of page cards -->
```

---

### Page Section List Fragment

**Request:**
```http
GET /fragments/sections/{website_slug}/{page_path}/ HTTP/1.1
```

**URL Parameters:**
- `website_slug` (required)
- `page_path` (required) – URL-encoded path like `home%2Fmain.html`

**Response:**
```html
200 OK

<!-- List of sections/components for the page -->
```

---

### Template Sidebar Fragment

**Request:**
```http
GET /fragments/sidebar/{website_slug}/ HTTP/1.1
?model_id=gemma3-4b
```

**Response:**
```html
200 OK

<!-- Sidebar showing templates and sections -->
```

---

## Ceptor-AI Integration API

### Health Check

**Request:**
```http
GET /api/ceptor/health/ HTTP/1.1
Accept: application/json
```

**Response:**
```json
200 OK
{
  "package": "ceptor-ai",
  "installed": true,
  "version": "0.1.0",
  "services": {
    "ai_backends": ["ollama", "openai", "claude", "gemini"],
    "mcp_tools": ["web_search", "code_executor", "file_reader"]
  }
}
```

---

### Preload Configurations

**Request:**
```http
GET /api/ceptor/config/preload/ HTTP/1.1
Accept: application/json
```

**Response:**
```json
200 OK
{
  "agent_configs": {
    "django-architect": {...},
    "frontend-developer": {...}
  },
  "models": {
    "gemma3": {"name": "Gemma 3 4B", "provider": "ollama"},
    "gpt-4o": {"name": "GPT-4o", "provider": "openai"}
  }
}
```

**Location:** Loads from `application/kilo/agent/*.json` in project root.

---

### AI Completion (Streaming)

**Request:**
```http
POST /api/ceptor/ai/complete/?stream=1 HTTP/1.1
Content-Type: application/json

{
  "backend": "openai",
  "model": "gpt-4o",
  "prompt": "Generate a Vue.js component for..."
}
```

**Request Body:**
- `backend` (required) – One of: `ollama`, `openai`, `claude`, `gemini`
- `model` (optional) – Model ID; uses backend default if omitted
- `prompt` (required) – Input prompt text

**Response (Streaming):**
```
200 OK
Content-Type: text/event-stream

data: {"token": "Here"}
data: {"token": " is"}
data: {"token": " a"}
data: {"done": true}
```

---

### AI Completion (Non-Streaming)

**Request:**
```http
POST /api/ceptor/ai/complete/ HTTP/1.1
Content-Type: application/json

{
  "backend": "ollama",
  "model": "gemma3:4b",
  "prompt": "Explain React hooks"
}
```

**Response:**
```json
200 OK
{
  "backend": "ollama",
  "model": "gemma3:4b",
  "reply": "React hooks are functions that let you 'hook into' React state..."
}
```

**Error Responses:**
```json
400 Bad Request
{"error": "Invalid backend"}

503 Service Unavailable
{"error": "ceptor-ai is not installed"}

500 Internal Server Error
{"error": "Ceptor AI error: connection refused"}
```

---

### Execute MCP Tool

**Request:**
```http
GET /api/ceptor/mcp/{tool_name}/ HTTP/1.1
?param1=value1&param2=value2
```

**URL Parameters:**
- `tool_name` (required) – MCP tool name
- Additional parameters depend on the tool

**Response:**
```json
200 OK
{
  "tool": "web_search",
  "result": {...}
}
```

**Error Responses:**
```json
404 Not Found
{"error": "Tool not found"}

503 Service Unavailable
{"error": "ceptor-ai is not installed"}

500 Internal Server Error
{"error": "Tool execution failed: ..."}
```

---

## Model Management API

### Model Choices

Available via context in views:

```python
{
  "default_model_id": "gemma3-4b",
  "model_choices": [
    ("gemma3-4b", "Gemma 3 4B (Local)"),
    ("gpt-4o", "GPT-4o"),
    ("claude-3-sonnet", "Claude 3 Sonnet"),
    ("gemini-pro", "Gemini Pro"),
    ("ceptor-chat", "Ceptor Chat"),
    ("ceptor-openai", "Ceptor OpenAI"),
    ("ceptor-claude", "Ceptor Claude"),
    ("ceptor-gemini", "Ceptor Gemini"),
  ]
}
```

---

## Error Handling

### Common HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 302 | Redirect (e.g., after creating conversation) |
| 400 | Bad Request (missing/invalid parameters) |
| 404 | Not Found (unknown resource) |
| 405 | Method Not Allowed (POST on GET-only endpoint) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (Ceptor AI not running) |

### Error Response Format

**HTML (from views):**
```html
400 Bad Request
Content-Type: text/plain

Message cannot be empty
```

**JSON (from API endpoints):**
```json
400 Bad Request
Content-Type: application/json

{"error": "descriptive error message"}
```

---

## Authentication & CSRF

### CSRF Protection

- **GET requests:** No token required
- **POST requests:** Require valid `csrfmiddlewaretoken`

**Getting CSRF Token:**
```javascript
// From form hidden input
const token = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Or from cookie
const token = document.cookie
  .split('; ')
  .find(row => row.startsWith('csrftoken='))
  .split('=')[1];
```

**Using CSRF Token:**
```javascript
fetch('/chat/5/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': token,
    'Content-Type': 'application/x-www-form-urlencoded'
  },
  body: 'message=Hello&model_id=gemma3-4b'
});
```

### Session

- Sessions are stored in Django's session framework
- Cookie-based authentication
- Secure cookies in production (HTTPS only)

---

## Rate Limiting

Currently no rate limiting is enforced. Recommended settings for production:

```python
# In Django middleware or load balancer
RATE_LIMIT = "100/hour"  # Requests per hour per IP
```

---

## CORS

CORS is not currently enabled. To enable:

```python
# settings.py
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
]
```

---

## Examples

### cURL: Create Conversation

```bash
curl -X POST http://localhost:5073/ \
  -d "message=Create a button component&model_id=gemma3-4b" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -L
```

### JavaScript: Send Message with SSE

```javascript
const conversationId = 3;
const message = "Make this button blue";

// Send message
const formData = new FormData();
formData.append('message', message);
formData.append('model_id', 'gpt-4o');

const response = await fetch(`/chat/${conversationId}/`, {
  method: 'POST',
  headers: {
    'X-CSRFToken': csrfToken,
  },
  body: formData
});

const html = await response.text();
document.getElementById('messages').insertAdjacentHTML('beforeend', html);

// SSE is auto-started by the script in the response
```

### Python: Query Conversations

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from chat.models import Conversation, Message

# Get recent conversations
conversations = Conversation.objects.all().order_by('-updated_at')[:5]

for conv in conversations:
    print(f"{conv.id}: {conv.title}")
    print(f"  Messages: {conv.messages.count()}")
    print(f"  Updated: {conv.updated_at}")
    print()
```

### Postman: API Collection

See `cypercloud/docs/postman-collection.json` for a Postman collection of all API endpoints.

---

## Versioning

API version: **1.0.0**

No breaking changes planned in the near term. Backwards compatibility is maintained for query parameters and JSON response schemas.

For major changes, consider API versioning:
- `/api/v1/...` – Current version
- `/api/v2/...` – Future breaking changes

---

## Support

For issues or questions:
1. Check `README.md` for common troubleshooting
2. Review Django logs: `tail -f logs/django.log`
3. Check Ceptor-AI service status: `GET /api/ceptor/health/`
4. Run Django checks: `python manage.py check`
