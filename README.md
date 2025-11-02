# Voice Agent Platform

A real-time voice-enabled AI assistant with ultra-low latency using Pipecat, Cartesia, Cerebras, and ElevenLabs.

## Features

- 🎤 **Real-time Voice Conversations** with <1s end-to-end latency
- 🧠 **Intelligent Responses** powered by Cerebras Llama 3.3-70B (450 tok/sec)
- 🔊 **Natural Voice Synthesis** using ElevenLabs Flash v2.5 (75ms latency)
- 📝 **Fast Speech Recognition** with Cartesia Ink-Whisper (fastest TTCT)
- 🔄 **Multi-turn Context** maintains conversation history
- ⚡ **Interruption Handling** allows natural conversation flow
- 🌐 **Dual Transport** WebSocket (dev) or Daily WebRTC (production)

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Get API Keys

Sign up and get API keys from:
- **Cartesia**: https://cartesia.ai
- **Cerebras**: https://cloud.cerebras.ai (free tier: 1M tokens/day)
- **ElevenLabs**: https://elevenlabs.io
- **Daily** (optional): https://dashboard.daily.co

### 3. Configure Environment

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API keys
vim .env
```

### 4. Validate Configuration

```bash
uv run voice-agent config-check
```

### 5. Start the Voice Agent

```bash
# Start with default settings (WebSocket transport)
uv run voice-agent start

# Or with Daily WebRTC (production)
uv run voice-agent start --transport daily

# Enable verbose logging
uv run voice-agent start --verbose
```

## CLI Commands

The voice agent provides a modern CLI powered by Typer with helpful commands and options.

### `voice-agent start`

Start the voice agent with the specified configuration.

**Options:**
- `-t, --transport [websocket|daily]` - Transport type (default: from .env)
- `-e, --env-file PATH` - Path to custom .env file
- `-s, --system-prompt TEXT` - Custom system prompt for the LLM
- `-v, --verbose` - Enable verbose/debug logging

**Examples:**

```bash
# Start with WebSocket transport (default)
uv run voice-agent start

# Start with Daily WebRTC transport
uv run voice-agent start --transport daily

# Use custom .env file
uv run voice-agent start --env-file .env.production

# Enable verbose logging
uv run voice-agent start --verbose

# Custom system prompt
uv run voice-agent start --system-prompt "You are a helpful coding assistant."

# Combine multiple options
uv run voice-agent start -t daily -v
```

### `voice-agent version`

Show version information and component details.

```bash
uv run voice-agent version
```

### `voice-agent config-check`

Validate configuration and check API keys without starting the agent.

```bash
# Check default .env
uv run voice-agent config-check

# Check custom .env file
uv run voice-agent config-check --env-file .env.production
```

### `voice-agent --help`

Show all available commands and options.

```bash
uv run voice-agent --help
uv run voice-agent start --help
```

## Transport Options

### WebSocket (Development)

- ✅ Simple setup, no external dependencies
- ✅ Easy debugging
- ✅ Good for local testing
- ⚠️ Higher latency (200-400ms)
- ⚠️ Not recommended for production

```bash
# Via CLI
uv run voice-agent start --transport websocket

# Or via .env
TRANSPORT_TYPE=websocket
```

### Daily WebRTC (Production)

- ✅ Ultra-low latency (<100ms)
- ✅ Production-grade reliability
- ✅ Handles packet loss and jitter
- ✅ Global edge network
- ⚠️ Requires Daily.co account

```bash
# Via CLI
uv run voice-agent start --transport daily

# Or via .env
TRANSPORT_TYPE=daily
DAILY_ROOM_URL=https://your-domain.daily.co/your-room
DAILY_TOKEN=your_meeting_token
```

## Architecture

### Technology Stack

- **STT**: Cartesia Ink-Whisper (fastest TTCT, $0.13/hr)
- **LLM**: Cerebras Llama 3.3-70B (450 tokens/sec, <10ms processing)
- **TTS**: ElevenLabs Flash v2.5 (75ms inference, streaming)
- **VAD**: Silero (voice activity detection)
- **Framework**: Pipecat (voice agent orchestration)
- **CLI**: Typer (modern CLI interface)

### Pipeline Flow

```
Audio Input → VAD → STT → Context → LLM → TTS → Audio Output
     ↑                                                ↓
     └────────────── Transport Layer ────────────────┘
```

## Configuration

All configuration is managed via environment variables (see `.env.example`):

### Required

- `CARTESIA_API_KEY` - Cartesia STT API key
- `CEREBRAS_API_KEY` - Cerebras LLM API key
- `ELEVENLABS_API_KEY` - ElevenLabs TTS API key

### Transport

- `TRANSPORT_TYPE` - Transport type: `websocket` or `daily` (default: websocket)
- `WS_HOST` - WebSocket host (default: localhost)
- `WS_PORT` - WebSocket port (default: 8765)
- `DAILY_API_KEY` - Daily.co API key (if using Daily)
- `DAILY_ROOM_URL` - Daily.co room URL
- `DAILY_TOKEN` - Daily.co meeting token

### Voice Agent

- `ELEVENLABS_VOICE_ID` - ElevenLabs voice ID (default: Rachel)
- `LLM_MODEL` - Cerebras model (default: llama-3.3-70b)
- `LLM_TEMPERATURE` - Temperature 0.0-2.0 (default: 0.7)
- `LLM_MAX_TOKENS` - Max tokens per response (default: 150)
- `AUDIO_SAMPLE_RATE` - Sample rate in Hz (default: 16000)
- `TTS_OPTIMIZE_LATENCY` - TTS latency optimization 0-4 (default: 3)

### Logging

- `LOG_LEVEL` - Log level: DEBUG, INFO, WARNING, ERROR (default: INFO)

## Cost Estimate

**Per 5-minute conversation:**
- STT (5 min × $0.13/60 min): $0.011
- LLM (~5,000 tokens): $0.003
- TTS (~750 characters): $0.005
- **Total**: ~$0.02

**Development (100 hours):**
- Using free tiers: ~$35-50
- Without free tiers: ~$178

## Development

### Project Structure

```
voice-agent-trial/
├── config/
│   └── settings.py          # Configuration management
├── services/
│   ├── stt_service.py       # Cartesia STT
│   ├── llm_service.py       # Cerebras LLM
│   ├── tts_service.py       # ElevenLabs TTS
│   └── transport.py         # Transport factory
├── utils/
│   └── logger.py            # Structured logging
├── voice_agent.py           # Main CLI application
├── pyproject.toml           # Project config
└── README.md                # This file
```

### Running Tests

```bash
# Test configuration
uv run voice-agent config-check

# Test imports
uv run python -c "import voice_agent; print('OK')"
```

### Formatting and Linting

```bash
# Format code
uv run ruff format .

# Lint and auto-fix
uv run ruff check --fix .
```

## Troubleshooting

### Missing API Keys

If you see "Configuration Error: Missing required environment variables":
1. Ensure `.env` file exists: `cp .env.example .env`
2. Add your API keys to `.env`
3. Run `uv run voice-agent config-check` to validate

### Import Errors

If you see "No module named 'X'":
```bash
uv sync --extra dev
```

### Transport Connection Issues

**WebSocket:**
- Check `WS_HOST` and `WS_PORT` in `.env`
- Ensure port is not in use: `lsof -i :8765`

**Daily:**
- Verify `DAILY_ROOM_URL` and `DAILY_TOKEN` are set
- Check room exists at https://dashboard.daily.co

### High Latency

1. Switch from WebSocket to Daily WebRTC: `--transport daily`
2. Check network conditions
3. Enable verbose logging: `--verbose`

## Documentation

- **PRD**: [PRD.md](PRD.md) - Complete technical specifications
- **Pipecat Docs**: https://docs.pipecat.ai
- **Cartesia Docs**: https://docs.cartesia.ai
- **Cerebras Docs**: https://cerebras.ai/developer
- **ElevenLabs Docs**: https://elevenlabs.io/docs

## License

MIT
