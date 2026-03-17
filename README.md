# JYRY AI Backend

AI-powered teaching platform by **JYRY GROUP** — starting with a German Teacher agent (A1–B2).

## Architecture

```
JYRY AI Backend
├── AgentRouter          ← Central dispatcher (registry pattern)
└── Agents
    └── german_teacher   ← JYRY AI German Teacher (v1)
        ├── correct_writing   → Goethe-style correction + scoring
        ├── explain_grammar   → Grammar explanations
        └── free_chat         → Open-ended teaching conversation
```

## Tech Stack

- **Python 3.11+** / **FastAPI** (async)
- **Claude API** (`claude-sonnet-4-6` by default)
- **Pydantic v2** for validation

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run the server
uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `GET` | `/api/v1/agents` | List registered agents |
| `POST` | `/api/v1/chat` | Send task to an agent |

Interactive docs available at: `http://localhost:8000/docs`

## Usage Examples

### Correct Writing (A2 level, Arabic explanations)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "german_teacher",
    "payload": {
      "task": "correct_writing",
      "level": "A2",
      "text": "Ich gehe gestern in die Schule und lerne viel Sachen.",
      "language": "ar"
    }
  }'
```

**Response:**
```json
{
  "task": "correct_writing",
  "level": "A2",
  "original_text": "Ich gehe gestern in die Schule und lerne viel Sachen.",
  "corrected_text": "Ich bin gestern in die Schule gegangen und habe viele Sachen gelernt.",
  "corrections": [
    "Verb tense: use Perfekt for past events — 'gehe' → 'bin gegangen'",
    "Adjective agreement: 'viel Sachen' → 'viele Sachen'"
  ],
  "explanation": "استخدمنا زمن Perfekt لأن الحدث وقع في الماضي...",
  "score": {
    "grammar": 15,
    "vocabulary": 20,
    "structure": 18,
    "clarity": 19,
    "total": 72
  },
  "encouragement": "ممتاز! أنت تتحسن بسرعة كبيرة",
  "model_used": "claude-sonnet-4-6"
}
```

### Explain Grammar (B1 level, German)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "german_teacher",
    "payload": {
      "task": "explain_grammar",
      "level": "B1",
      "text": "Konjunktiv II",
      "language": "de"
    }
  }'
```

### Free Chat (A1 level, Arabic)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "german_teacher",
    "payload": {
      "task": "free_chat",
      "level": "A1",
      "text": "Wie sagt man ich bin hungrig auf Deutsch?",
      "language": "ar"
    }
  }'
```

## Scoring Rubric (Goethe-Institut Style)

| Dimension | German | Arabic | Points |
|-----------|--------|--------|--------|
| Grammar | Grammatik | النحو | 0–25 |
| Vocabulary | Wortschatz | المفردات | 0–25 |
| Structure | Struktur | التنظيم | 0–25 |
| Clarity | Verständlichkeit | الوضوح | 0–25 |
| **Total** | | | **0–100** |

## Adding a New Agent

1. Create `app/agents/my_agent/` with `agent.py`, `schemas.py`, `prompts.py`
2. Inherit from `BaseAgent`, implement `agent_id` and `process()`
3. Add one line to `app/router/agent_router.py`:
   ```python
   self.register(MyAgent())
   ```

That's it — the `/api/v1/chat` endpoint automatically supports the new agent.

## Running Tests

```bash
pytest tests/ -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | *required* | Your Claude API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Model to use |
| `MAX_TOKENS` | `2048` | Max tokens per response |
| `APP_ENV` | `development` | Environment name |
| `LOG_LEVEL` | `INFO` | Logging level |
