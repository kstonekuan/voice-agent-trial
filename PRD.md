# Product Requirements Document: Voice Agent Platform

**Version:** 1.0
**Date:** January 2025
**Status:** Draft
**Author:** Voice Agent Development Team

---

## 1. Executive Summary

### 1.1 Overview

This document outlines the requirements for building a real-time voice-enabled personal AI assistant capable of natural, low-latency conversations. The system leverages cutting-edge speech recognition, language modeling, and voice synthesis technologies to create an engaging conversational experience.

### 1.2 Core Technology Stack

- **Orchestration Framework:** Pipecat (Python-based voice agent framework)
- **Speech-to-Text (STT):** Cartesia Ink-Whisper
- **Large Language Model (LLM):** Cerebras Llama 3.3-70B
- **Text-to-Speech (TTS):** ElevenLabs Flash v2.5
- **Transport Layer:** Configurable (Daily WebRTC / WebSocket)

### 1.3 Key Objectives

1. **Ultra-Low Latency**: Achieve sub-1 second end-to-end response times for natural conversation flow
2. **High Accuracy**: Maintain >90% transcription accuracy and generate contextually appropriate responses
3. **Cost Efficiency**: Optimize for development and testing budget (~$125-200/month for 100 hours)
4. **Flexibility**: Support multiple transport options for testing different network conditions
5. **Local Testing**: Enable complete local development and testing environment

### 1.4 Target Use Case

**Primary:** Personal AI assistant for general conversational interactions, scheduling, information retrieval, and task assistance via voice interface.

**Deployment:** Local testing environment with clear path to production deployment.

### 1.5 Success Criteria

- End-to-end latency consistently under 1 second
- Natural conversation flow with interruption handling
- Successful multi-turn dialogues maintaining context
- Cost-effective operation within budget constraints
- Easy switching between WebRTC and WebSocket transports for performance testing

---

## 2. Product Overview

### 2.1 Problem Statement

Building real-time voice agents presents several challenges:

1. **Latency Accumulation**: Each component (STT, LLM, TTS) adds latency, making sub-second responses difficult
2. **Integration Complexity**: Coordinating multiple AI services requires complex orchestration
3. **Cost Management**: Voice AI services can be expensive, especially during development and testing
4. **Network Variability**: Real-world network conditions (jitter, packet loss) degrade voice quality
5. **Context Management**: Maintaining conversation state across multiple turns is non-trivial

### 2.2 Solution Approach

This voice agent platform addresses these challenges through:

**Component Selection for Speed:**
- Cartesia Ink-Whisper: Fastest time-to-complete-transcript (TTCT) in the industry
- Cerebras: Ultra-fast LLM inference (450 tokens/sec) with <10ms processing time
- ElevenLabs Flash v2.5: 75ms TTS inference with streaming support

**Orchestration Excellence:**
- Pipecat framework handles complex pipeline coordination
- Streaming architecture minimizes perceived latency
- Built-in interruption handling for natural conversations

**Cost Optimization:**
- Cartesia STT at $0.13/hour (50%+ cheaper than alternatives)
- Cerebras free tier: 1M tokens/day during launch period
- Efficient resource usage through Voice Activity Detection (VAD)

**Flexible Transport:**
- WebSocket for simple development/testing
- WebRTC (Daily.co) for production-grade reliability
- Environment-based configuration for easy switching

### 2.3 Target Users

**Primary Developers:**
- Voice AI engineers building conversational applications
- Python developers familiar with async programming
- Teams exploring voice interface for existing products

**End Users:**
- Individuals seeking voice-based personal assistant capabilities
- Users preferring natural language interaction over typed commands
- Scenarios requiring hands-free operation

### 2.4 Key Differentiators

1. **Performance-First Stack**: Every component selected for minimal latency
2. **Cost Leadership**: Most affordable STT option (Cartesia) combined with efficient LLM
3. **Testing Flexibility**: Configurable transport enables performance comparison
4. **Production-Ready**: Clear path from local testing to scaled deployment
5. **Best-in-Class Components**: Industry-leading services in each category

---

## 3. Technical Architecture

### 3.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                         │
│                    (Microphone → Speaker)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSPORT LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Option A: Daily WebRTC (Production)                     │   │
│  │  - Ultra-low latency (<100ms)                            │   │
│  │  - Handles packet loss, jitter                           │   │
│  │  - Production-grade reliability                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Option B: WebSocket (Development)                       │   │
│  │  - Simple setup, no external dependencies                │   │
│  │  - Higher latency (200-400ms)                            │   │
│  │  - Best for prototyping and testing                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PIPECAT ORCHESTRATION LAYER                     │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Pipeline  │→ │   Frames    │→ │  Processors │             │
│  │  Management │  │ Audio/Text  │  │   Routing   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└────────────────────────┬────────────────────────────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    ▼                    ▼                    ▼
┌─────────┐      ┌──────────────┐      ┌─────────┐
│   VAD   │      │   Context    │      │  Audio  │
│ (Silero)│      │  Aggregator  │      │ Filters │
└─────────┘      └──────────────┘      └─────────┘
    │                    │                    │
    └────────────────────┼────────────────────┘
                         │
    ┌────────────────────┴────────────────────┐
    ▼                                         ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│  SPEECH-TO-TEXT (STT)   │      │                         │
│  Cartesia Ink-Whisper   │      │  (Audio Input Path)     │
│  - Fastest TTCT         │      │                         │
│  - ~150-250ms latency   │      └─────────────────────────┘
│  - $0.13/hour           │
│  - WebSocket streaming  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT MANAGEMENT                            │
│  - Conversation history                                          │
│  - System prompts                                                │
│  - Message formatting for LLM                                    │
└───────────┬─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│  LLM INFERENCE          │
│  Cerebras               │
│  Llama 3.3-70B          │
│  - 450 tokens/sec       │
│  - <10ms processing     │
│  - ~240ms TTFB          │
│  - Streaming output     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  TEXT-TO-SPEECH (TTS)   │
│  ElevenLabs Flash v2.5  │
│  - 75ms inference       │
│  - WebSocket streaming  │
│  - Natural voice        │
│  - Low latency mode     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSPORT LAYER                               │
│                (Audio streaming to user)                         │
└───────────┬─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         USER HEARS RESPONSE                      │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

**Input Pipeline (User speaks → System understands):**

1. **Audio Capture**: User's voice captured via microphone
2. **Transport**: Audio streamed to server via WebRTC or WebSocket
3. **VAD Processing**: Silero VAD detects speech start/end, filters silence
4. **STT Conversion**: Cartesia Ink-Whisper transcribes speech to text (streaming)
5. **Context Assembly**: Text combined with conversation history
6. **LLM Processing**: Cerebras generates response based on context

**Output Pipeline (System responds → User hears):**

7. **TTS Synthesis**: ElevenLabs converts LLM text to audio (streaming)
8. **Transport**: Audio streamed back to client
9. **Audio Playback**: User hears response through speakers/headphones

**Key Characteristic: Parallel Streaming**
- All components stream data in real-time
- TTS begins synthesis as soon as first LLM tokens arrive
- User hears response while LLM is still generating
- Perceived latency much lower than sum of component latencies

### 3.3 Component Interaction

**Frame-Based Communication:**

Pipecat uses a frame-based architecture where all data flows through typed frames:

- **AudioRawFrame**: Raw audio data (PCM samples)
- **TextFrame**: Text data (transcriptions, LLM output)
- **TranscriptionFrame**: STT results with metadata
- **LLMMessagesFrame**: Formatted messages for LLM
- **StartFrame/EndFrame**: Pipeline control signals
- **InterimTranscriptionFrame**: Partial STT results (streaming)

**Processor Pipeline:**

```python
pipeline = Pipeline([
    transport.input(),        # Audio in
    vad,                      # Voice activity detection
    stt,                      # Cartesia STT (AudioFrame → TextFrame)
    context_aggregator,       # Text → LLMMessagesFrame
    llm,                      # LLMMessagesFrame → TextFrame (response)
    tts,                      # TextFrame → AudioFrame
    transport.output(),       # Audio out
])
```

Each processor:
- Receives frames from previous processor
- Transforms/processes the data
- Emits new frames to next processor
- Can be asynchronous for non-blocking operation

---

## 4. Core Technology Stack

### 4.1 Orchestration Framework: Pipecat

**What It Is:**
Open-source Python framework for building real-time voice and multimodal conversational AI agents.

**Why Pipecat:**
- Purpose-built for voice agents (not a general-purpose framework)
- Handles complex audio/video transport coordination
- Modular, composable architecture (swap components easily)
- Built-in integrations with 50+ AI services
- Active development and community support (8.6k GitHub stars)
- Production-ready with real-world deployments

**Key Features:**
- WebRTC and WebSocket transport support
- Voice Activity Detection (Silero VAD)
- Streaming by default (minimize latency)
- Interruption handling (users can interrupt agent)
- Context management for multi-turn conversations
- Function calling support (agent can trigger actions)
- Observability (OpenTelemetry, metrics)

**Version Requirements:**
- Python 3.10+ (3.12 recommended)
- BSD-2-Clause license (permissive)

**Installation:**
```bash
pip install "pipecat-ai[daily,cartesia,cerebras,elevenlabs]"
```

### 4.2 Transport Layer: Daily WebRTC / WebSocket

**Option A: Daily (WebRTC) - Production-Grade**

**What It Is:**
WebRTC infrastructure-as-a-service that handles peer-to-peer audio/video connections with server-side processing capabilities.

**Why Daily for Production:**
- Ultra-low latency (20-150ms, optimized <100ms)
- Automatic handling of network variability
- Packet loss concealment and jitter buffering
- Global edge network for geographic optimization
- Multi-user session support
- Built-in recording and streaming
- Production-proven reliability

**Use Cases:**
- Production deployment
- Performance testing
- Multi-user scenarios
- Phone connectivity (SIP/PSTN)

**Cost:**
- Free tier: 1,000 minutes/month
- Paid plans scale with usage

**Option B: WebSocket - Development-Friendly**

**What It Is:**
Bidirectional communication protocol over TCP for real-time data exchange.

**Why WebSocket for Development:**
- Simple setup (no external service dependencies)
- Easier debugging (HTTP-based)
- Faster iteration during development
- No API keys needed for basic setup
- Direct control over implementation

**Limitations:**
- Higher latency (200-400ms due to TCP overhead)
- TCP head-of-line blocking degrades quality on poor networks
- Not recommended for production voice agents
- No built-in jitter buffering or packet loss handling

**Use Cases:**
- Local development
- Initial prototyping
- Controlled network environments
- Testing and debugging

**Configuration Strategy:**

```python
# Environment-based transport selection
transport_type = os.getenv("TRANSPORT_TYPE", "daily")

if transport_type == "daily":
    transport = DailyTransport(
        room_url=os.getenv("DAILY_ROOM_URL"),
        token=os.getenv("DAILY_TOKEN"),
        params=DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        )
    )
elif transport_type == "websocket":
    transport = WebSocketTransport(
        params=WebSocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        )
    )
```

### 4.3 Voice Activity Detection: Silero VAD

**What It Is:**
Neural network-based voice activity detection model that identifies speech segments in audio streams.

**Why Silero VAD:**
- Built-in with Pipecat (no additional setup)
- High accuracy distinguishing speech from silence/noise
- Low computational overhead
- Enables efficient STT usage (only process speech segments)
- Critical for natural interruption handling

**Key Functions:**
- Detect speech start (trigger STT)
- Detect speech end (finalize transcription)
- Filter silence and background noise
- Enable push-to-talk alternatives (automatic speech detection)

**Parameters:**
- Sensitivity threshold (adjustable)
- Minimum speech duration
- Minimum silence duration

---

## 5. Component Deep-Dive: Speech-to-Text (Cartesia Ink-Whisper)

### 5.1 Overview

**Model:** Cartesia Ink-Whisper
**Type:** Streaming speech-to-text optimized for conversational AI
**Base:** Variant of OpenAI Whisper with custom optimizations

### 5.2 Why Cartesia Ink-Whisper

**Performance Leadership:**
- **Fastest TTCT (Time-to-Complete-Transcript)** of any streaming STT model
- TTCT measures how quickly the full transcript is ready once user stops talking
- Critical metric for voice agents (faster TTCT = faster responses)

**Cost Leadership:**
- **$0.13/hour** - most affordable streaming STT available
- 50%+ cheaper than Deepgram ($0.30/hr) and AssemblyAI ($0.27/hr)
- Ideal for budget-conscious development and testing

**Conversational AI Optimization:**
- Dynamic chunking technology for variable-length audio segments
- Handles pauses and silence without hallucinations
- Optimized for telephony, background noise, accents, disfluencies
- Better accuracy than baseline Whisper (whisper-large-v3-turbo)

**Integration Simplicity:**
- Built-in Pipecat support via `CartesiaSTTService`
- WebSocket-based streaming (low latency)
- Simple configuration

### 5.3 Technical Specifications

**Supported Languages:**
- 100+ languages
- Uses ISO-639-1 format (e.g., "en", "es", "fr")
- Defaults to English

**Audio Formats:**
- **Recommended:** pcm_s16le (16-bit signed integer PCM, little-endian)
- Also supports: pcm_s32le, pcm_f16le, pcm_f32le, pcm_mulaw, pcm_alaw

**Sample Rates:**
- Default: 16,000 Hz
- Configurable based on needs

**Latency:**
- Fastest TTCT in industry (exact ms varies by audio length)
- Estimated: 150-250ms for typical conversational segments
- Streaming architecture minimizes perceived delay

**Accuracy:**
- Better word error rate (WER) than baseline Whisper V3 Turbo
- Specifically tuned for real-world conversational conditions
- Strong performance on proper nouns and technical terms

### 5.4 Pipecat Integration

**Installation:**
```bash
pip install "pipecat-ai[cartesia]"
```

**Basic Configuration:**
```python
from pipecat.services.cartesia.stt import CartesiaSTTService
import os

stt = CartesiaSTTService(
    api_key=os.getenv("CARTESIA_API_KEY")
)
```

**Advanced Configuration:**
```python
from pipecat.services.cartesia.stt import (
    CartesiaSTTService,
    CartesiaLiveOptions
)

stt = CartesiaSTTService(
    api_key=os.getenv("CARTESIA_API_KEY"),
    sample_rate=16000,
    live_options=CartesiaLiveOptions(
        model='ink-whisper',      # Model name
        language='en',            # Language code (ISO-639-1)
        encoding='pcm_s16le',     # Audio encoding
        sample_rate=16000         # Sample rate in Hz
    )
)
```

**Service Methods:**
- `start()`: Initiates WebSocket connection
- `stop()`: Gracefully terminates service
- `cancel()`: Aborts transcription immediately
- `process_frame()`: Handles incoming audio frames
- `can_generate_metrics()`: Supports performance monitoring

### 5.5 Dynamic Chunking Technology

**Problem Solved:**
Traditional STT models struggle with pauses, often producing hallucinations or errors during silence.

**Cartesia's Solution:**
- Intelligent audio segmentation based on natural speech patterns
- Variable-length chunks optimized per audio segment
- Reduces errors during pauses, hesitations, and silence
- Maintains accuracy across different speaking styles

**Result:**
More natural transcriptions that accurately capture conversational speech patterns.

### 5.6 Pricing

**Streaming API:**
- 1 credit per second of audio
- Credits convert to **$0.13/hour of audio**

**Batch API:**
- 1 credit per 2 seconds (half price of streaming)
- Not applicable for real-time voice agents

**Example Costs:**
- 100 hours testing: 100 × $0.13 = **$13**
- 1,000 hours production: 1,000 × $0.13 = **$130**

### 5.7 Comparison to Alternatives

| Feature | Cartesia Ink-Whisper | AssemblyAI Universal-2 | Deepgram Nova-3 |
|---------|---------------------|----------------------|-----------------|
| **Latency (TTCT)** | **Fastest** (~150-250ms est.) | 300-600ms | ~200-260ms |
| **Pricing** | **$0.13/hr** | $0.27/hr | ~$0.30/hr |
| **Accuracy (WER)** | Better than Whisper V3 | 14.5% (best) | 18.3% |
| **Optimization** | Conversational AI, telephony | Domain-specific | Real-time agents |
| **Special Features** | Dynamic chunking | Slam-1 language model | Flux end-of-turn detection |
| **Languages** | 100+ | 90+ | 36 |
| **Pipecat Support** | ✅ Built-in | ✅ Built-in | ✅ Built-in |
| **Best For** | **Cost + Speed** | Highest accuracy | Balanced performance |

**Recommendation:** Cartesia Ink-Whisper for this project due to:
1. Lowest cost (critical for testing phase)
2. Fastest response times (best user experience)
3. Purpose-built for conversational AI
4. Excellent Pipecat integration

---

## 6. Component Deep-Dive: LLM Inference (Cerebras)

### 6.1 Overview

**Platform:** Cerebras Cloud (cloud.cerebras.ai)
**Model:** Llama 3.3-70B (default for Pipecat integration)
**Hardware:** CS-3 system with Wafer Scale Engine 3 (WSE-3)

### 6.2 Why Cerebras

**Unprecedented Speed:**
- **450 tokens/second** for Llama 3.3-70B
- **1,800 tokens/second** for Llama 3.1-8B
- 20x faster than traditional GPU clouds
- <10ms processing time vs 700ms on GPUs

**Ultra-Low Latency:**
- **~240ms Time-to-First-Byte (TTFB)** for Llama 3.1-405B
- **~70ms response time** for smaller models
- Critical for voice agents requiring <100ms LLM latency

**Architectural Advantage:**
- Traditional GPUs: Must move 140GB+ model parameters for each token (memory bandwidth bottleneck)
- Cerebras WSE-3: Keeps entire model on-chip, eliminating memory bottleneck
- Result: Consistent, predictable performance

**Cost-Effectiveness:**
- **Free tier:** 1 million tokens/day during launch period
- **Paid:** $0.60 per million tokens (Llama 3.3-70B)
- Fraction of GPU-based competitor pricing

**OpenAI Compatibility:**
- Fully compatible with OpenAI Chat Completions API
- Drop-in replacement (only change API key and base URL)
- Works with existing OpenAI SDK code

### 6.3 Technical Specifications

**Available Models:**
- Llama 3.1-8B ($0.10/M tokens)
- Llama 3.1-70B ($0.60/M tokens)
- **Llama 3.3-70B** ($0.60/M tokens) ← Recommended
- Llama 3.1-405B (pricing TBD)

**Model Selection Criteria:**
- **Llama 3.3-70B**: Best balance of quality, speed, and cost for voice agents
- **Llama 3.1-8B**: Maximum speed (1,800 tok/sec) if quality sufficient
- **Llama 3.1-405B**: Complex reasoning requiring largest model

**Performance Metrics:**
- Token generation: 450 tokens/sec (Llama 3.3-70B)
- TTFB: ~240ms
- Processing overhead: <10ms
- Streaming: Full support for real-time output

**API Compatibility:**
- OpenAI-compatible Chat Completions endpoint
- Streaming responses via Server-Sent Events (SSE)
- Function calling support
- System/user/assistant message roles

### 6.4 Pipecat Integration

**Installation:**
```bash
pip install "pipecat-ai[cerebras]"
```

**Configuration:**
```python
from pipecat.services.cerebras import CerebrasLLMService
import os

llm = CerebrasLLMService(
    api_key=os.getenv("CEREBRAS_API_KEY"),
    model="llama-3.3-70b"
)
```

**With System Prompt:**
```python
from pipecat.processors.aggregators.llm_response import (
    LLMUserContextAggregator,
    LLMAssistantContextAggregator,
)

# Define system prompt
system_prompt = """You are a helpful personal AI assistant.
Engage in natural conversation, provide concise responses,
and maintain context across multiple turns. Keep responses
brief for voice interaction (1-3 sentences typically)."""

# Context aggregators for conversation management
user_context = LLMUserContextAggregator()
assistant_context = LLMAssistantContextAggregator()

llm = CerebrasLLMService(
    api_key=os.getenv("CEREBRAS_API_KEY"),
    model="llama-3.3-70b",
    params={
        "temperature": 0.7,
        "max_tokens": 150,  # Limit for voice responses
        "top_p": 0.9,
    }
)
```

**Under the Hood:**
- `CerebrasLLMService` inherits from `OpenAILLMService`
- Base URL: `https://api.cerebras.ai/v1`
- Uses same patterns as OpenAI integration
- Full streaming support built-in

### 6.5 Voice Agent Optimization

**Response Length Management:**
For voice interactions, configure LLM for concise responses:

```python
params = {
    "temperature": 0.7,      # Balanced creativity/consistency
    "max_tokens": 150,       # Typical: 1-3 sentences
    "top_p": 0.9,           # Nucleus sampling
    "frequency_penalty": 0.2,  # Reduce repetition
}
```

**System Prompt Best Practices:**
```python
system_prompt = """You are a voice-based personal AI assistant.

Guidelines:
- Respond conversationally and naturally
- Keep responses brief (1-3 sentences for most queries)
- For complex topics, offer to elaborate if user wants details
- Use spoken language, not written (e.g., "twenty twenty-five" not "2025")
- Avoid formatting like bullet points (hard to speak naturally)
- If uncertain, say so clearly and concisely

Your goal is natural, helpful conversation optimized for voice interaction."""
```

### 6.6 Pricing & Cost Management

**Free Tier:**
- 1 million tokens/day
- Sufficient for extensive testing (100+ hours of conversation)
- No credit card required

**Paid Tier:**
- Llama 3.3-70B: $0.60 per million tokens
- Typical conversation: ~500-1000 tokens per exchange
- 100 hours testing: ~100M tokens = **$60**

**Cost Optimization:**
- Set `max_tokens` appropriately (150 for voice)
- Use temperature/top_p to reduce unnecessary verbosity
- Monitor usage via Cerebras dashboard

### 6.7 Performance for Voice Agents

**Latency Breakdown:**
1. **TTFB (First token):** ~240ms (smaller models ~70ms)
2. **Token generation:** 450 tokens/sec = ~2.2ms per token
3. **Typical response (50 tokens):** ~240ms + (50 × 2.2ms) = ~350ms total

**Streaming Advantage:**
- TTS begins synthesis as soon as first tokens arrive
- User hears response starting at ~240ms (TTFB)
- Remaining tokens stream while user is already hearing speech
- Perceived latency much lower than total generation time

**Why This Matters:**
For natural conversation, <500ms LLM response is critical. Cerebras achieves this easily, while traditional LLMs often exceed 1-2 seconds.

---

## 7. Component Deep-Dive: Text-to-Speech (ElevenLabs Flash v2.5)

### 7.1 Overview

**Model:** Flash v2.5 (ultra-low latency TTS)
**Provider:** ElevenLabs
**Type:** Streaming text-to-speech optimized for real-time applications

### 7.2 Why ElevenLabs Flash v2.5

**Ultra-Low Latency:**
- **75ms inference time** (model processing)
- Total TTFB: 150-200ms (US), 230ms (Europe), 250-350ms (Asia)
- Fastest commercial TTS available

**High-Quality Voice Synthesis:**
- Natural-sounding speech
- Emotional expressiveness
- Clear pronunciation
- Minimal artifacts

**Streaming Support:**
- **WebSocket streaming** (recommended for voice agents)
- HTTP streaming (SSE - Server-Sent Events)
- Audio chunks delivered as generated (low latency)

**Voice Variety:**
- 1,000+ pre-made voices
- 32 languages supported
- Custom voice cloning available
- Emotion and style control

**Production-Ready:**
- Enterprise-grade reliability
- Global CDN for low-latency delivery
- Comprehensive API documentation
- Active development and support

### 7.3 Technical Specifications

**Model Options (Latency Ranking - Fastest to Slowest):**
1. **Flash v2.5** ← Recommended for voice agents
2. Turbo v2.5
3. Multilingual v2
4. Standard models

**Voice Type Latency:**
1. Default voices (formerly premade) - Fastest
2. Synthetic voices - Fast
3. Instant Voice Clones (IVC) - Moderate
4. Professional Voice Clones - Slowest

**Audio Output Formats:**
- MP3 (various bitrates)
- PCM (uncompressed)
- μ-law (8-bit telephony)
- AAC, FLAC, Opus

**Sample Rates:**
- 16 kHz (voice optimized, lowest latency)
- 24 kHz (balanced)
- 44.1 kHz (high quality, higher latency)

**Language Support:**
- 32 languages fully supported
- Multilingual models available
- Language auto-detection
- Cross-language voice cloning

### 7.4 Latency Optimization

**Key Parameter: `optimize_streaming_latency`**

Values 0-4 control latency/quality trade-off:

| Level | Description | Latency Impact | Use Case |
|-------|-------------|----------------|----------|
| 0 | Default (no optimization) | Baseline | Not recommended for real-time |
| 1 | Normal optimization | ~50% improvement | Balanced approach |
| 2 | Strong optimization | ~75% improvement | Good for most voice agents |
| 3 | Maximum optimization | ~85% improvement | **Recommended for voice agents** |
| 4 | Max + text normalizer off | Best latency | May mispronounce some text |

**Recommendation:** Use level 3 for best balance of latency and quality.

**Additional Optimization Tips:**
1. Use Flash v2.5 model (not Turbo or Multilingual)
2. Select Default or Synthetic voice types
3. Enable WebSocket streaming
4. Use 16 kHz sample rate
5. Set `optimize_streaming_latency: 3`

### 7.5 Pipecat Integration

**Installation:**
```bash
pip install "pipecat-ai[elevenlabs]"
```

**WebSocket Configuration (Recommended):**
```python
from pipecat.services.elevenlabs import ElevenLabsTTSService
import os

tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id="21m00Tcm4TlvDq8ikWAM",  # Default voice (Rachel)
    model="eleven_flash_v2_5",
    optimize_streaming_latency=3,     # Maximum optimization
    sample_rate=16000,                # Voice-optimized sample rate
)
```

**Custom Voice Selection:**
```python
# List available voices via ElevenLabs API or dashboard
# Popular low-latency voices:
voice_options = {
    "rachel": "21m00Tcm4TlvDq8ikWAM",     # Female, American
    "drew": "29vD33N1CtxCmqQRPOHJ",       # Male, American
    "clyde": "2EiwWnXFnvU5JabPnv8n",      # Male, American
}

tts = ElevenLabsTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id=voice_options["rachel"],
    model="eleven_flash_v2_5",
    optimize_streaming_latency=3,
    sample_rate=16000,
)
```

**HTTP Configuration (Alternative):**
```python
from pipecat.services.elevenlabs import ElevenLabsHttpTTSService

tts = ElevenLabsHttpTTSService(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_id="21m00Tcm4TlvDq8ikWAM",
    model="eleven_flash_v2_5",
)
```

**Note:** WebSocket is strongly recommended for voice agents due to bidirectional streaming and lower latency.

### 7.6 WebSocket Streaming Features

**Bidirectional Streaming:**
- Text input streamed to ElevenLabs in real-time
- Audio output streamed back as generated
- Perfect for LLM token streams (synthesis starts immediately)

**Auto Mode:**
- Automatic chunk management
- ElevenLabs determines optimal text segments
- No manual flushing required

**Flush Command:**
- Manually trigger synthesis of buffered text
- Useful for controlling speech timing
- Ensures complete utterances

### 7.7 Pricing

**Pricing Model:**
- Session-based pricing
- Charges per character processed
- Streaming includes overhead but optimized for efficiency

**Typical Tiers:**
- Free tier: Limited characters/month
- Creator: ~10M characters/month
- Pro: ~100M characters/month
- Enterprise: Custom limits

**Cost Estimation:**
- Average response: 100-200 characters
- 1,000 responses: ~150,000 characters
- Typical cost: ~$1-2 per 1,000 responses (varies by tier)

**For 100 Hours Testing:**
- Assume ~5,000 interactions
- ~750,000 characters total
- Estimated cost: **$50-100** (depending on tier)

### 7.8 Performance for Voice Agents

**Latency Breakdown:**
1. **Inference:** 75ms (model processing)
2. **Network (US):** 75-125ms
3. **Total TTFB:** 150-200ms (to first audio chunk)

**Streaming Behavior:**
- First audio chunk: ~150-200ms after first text token
- Subsequent chunks: continuous stream
- User hears speech starting ~150-200ms after LLM begins responding

**Perceived Latency:**
Much lower than component sum due to:
- LLM streams tokens → TTS synthesizes in parallel
- TTS streams audio → User hears in parallel
- Pipeline parallelism = sub-500ms perceived response

### 7.9 Alternative: Cartesia Sonic TTS

**Note:** While ElevenLabs is the primary choice, Cartesia Sonic TTS is worth considering:

**Cartesia Sonic Benefits:**
- 90ms streaming latency (slightly better than ElevenLabs)
- Unified vendor (same as STT = single API key, billing)
- Emotional expression and laughter
- 40+ languages

**Trade-offs:**
- ElevenLabs: More established, larger voice library, proven reliability
- Cartesia: Newer, unified stack benefit, potentially lower total cost

**Recommendation:**
- **Start with ElevenLabs** (proven, reliable)
- **Consider Cartesia Sonic** if unified stack appeals or during optimization phase

---

## 8. Transport Layer Configuration & Comparison

### 8.1 Overview

The transport layer is responsible for bidirectional audio streaming between the user's client (browser/app) and the voice agent server. Pipecat supports multiple transport options, with WebRTC and WebSocket being the primary choices.

### 8.2 WebRTC vs WebSocket Detailed Comparison

| Aspect | WebRTC (Daily.co) | WebSocket |
|--------|------------------|-----------|
| **Protocol** | UDP-based (SRTP for media) | TCP-based |
| **Latency** | **20-150ms** (optimized <100ms) | 200-400ms |
| **Packet Loss Handling** | Built-in loss concealment, FEC | **TCP retransmission** (head-of-line blocking) |
| **Jitter Handling** | Adaptive jitter buffering | Manual implementation required |
| **Network Adaptation** | Dynamic bitrate/quality adjustment | Fixed quality, prone to degradation |
| **Production Readiness** | **✅ Production-grade** | ⚠️ Prototype/controlled environments only |
| **Audio Quality** | Smooth, optimized for voice | Can be choppy on poor networks |
| **Setup Complexity** | Higher (requires Daily account) | Lower (just WebSocket server) |
| **External Dependencies** | Daily.co service | None (self-hosted) |
| **Cost** | Free tier + paid plans | Infrastructure costs only |
| **NAT/Firewall Traversal** | Built-in (STUN/TURN) | May require configuration |
| **Multi-user Support** | Native (conference calls) | Custom implementation needed |
| **Recording/Analytics** | Built-in | Custom implementation needed |
| **Best For** | **Production deployments** | Development & testing |

### 8.3 When to Use Each Transport

**Use WebRTC (Daily) when:**
- Deploying to production
- Need reliable performance across varying network conditions
- Building multi-user voice applications
- Require <100ms latency for best UX
- Want built-in recording and analytics
- Need phone connectivity (SIP/PSTN)

**Use WebSocket when:**
- Local development and testing
- Prototyping and proof-of-concept
- Controlled network environment (LAN, high-quality WAN)
- Want faster iteration without external dependencies
- Debugging transport-level issues

### 8.4 Environment-Based Configuration Pattern

**Recommended Approach:**

Use environment variables to make transport selection configurable without code changes:

```python
import os
from pipecat.transports.services.daily import DailyTransport, DailyParams
from pipecat.transports.services.websocket import WebSocketTransport, WebSocketParams
from pipecat.vad.silero import SileroVADAnalyzer

def create_transport():
    """Factory function for creating configurable transport."""
    transport_type = os.getenv("TRANSPORT_TYPE", "daily")  # Default to Daily

    # Common VAD configuration
    vad = SileroVADAnalyzer()

    if transport_type == "daily":
        return DailyTransport(
            room_url=os.getenv("DAILY_ROOM_URL"),
            token=os.getenv("DAILY_TOKEN"),
            params=DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad,
                transcription_enabled=False,  # Using Cartesia STT
            )
        )
    elif transport_type == "websocket":
        return WebSocketTransport(
            host=os.getenv("WS_HOST", "localhost"),
            port=int(os.getenv("WS_PORT", 8765)),
            params=WebSocketParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad,
            )
        )
    else:
        raise ValueError(f"Unknown transport type: {transport_type}")

# Usage in main application
transport = create_transport()
```

**Environment Configuration (.env file):**

```bash
# For WebRTC (Daily) transport
TRANSPORT_TYPE=daily
DAILY_ROOM_URL=https://your-domain.daily.co/your-room-name
DAILY_TOKEN=your_daily_meeting_token

# For WebSocket transport
TRANSPORT_TYPE=websocket
WS_HOST=localhost
WS_PORT=8765
```

### 8.5 Daily (WebRTC) Setup Guide

**1. Create Daily Account:**
- Sign up at https://dashboard.daily.co/
- Free tier includes 1,000 minutes/month

**2. Create Room:**
```bash
# Via Daily REST API
curl -X POST https://api.daily.co/v1/rooms \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "enable_screenshare": false,
      "enable_chat": false,
      "enable_people_ui": false,
      "start_video_off": true,
      "start_audio_off": false
    }
  }'
```

**3. Generate Meeting Token:**
```bash
curl -X POST https://api.daily.co/v1/meeting-tokens \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "room_name": "your-room-name",
      "is_owner": true
    }
  }'
```

**4. Configure Environment:**
```bash
TRANSPORT_TYPE=daily
DAILY_API_KEY=your_api_key
DAILY_ROOM_URL=https://your-domain.daily.co/your-room-name
DAILY_TOKEN=your_meeting_token
```

### 8.6 WebSocket Setup Guide

**Server Setup:**

```python
import asyncio
from pipecat.transports.services.websocket import WebSocketServerTransport

async def main():
    transport = WebSocketServerTransport(
        host="localhost",
        port=8765,
        params=WebSocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        )
    )

    # Create and run pipeline
    pipeline = Pipeline([
        transport.input(),
        # ... other processors
        transport.output(),
    ])

    await pipeline.run()

if __name__ == "__main__":
    asyncio.run(main())
```

**Client Setup (JavaScript):**

```javascript
import { PipecatClient } from "@pipecat-ai/client-js";
import { WebSocketTransport } from "@pipecat-ai/websocket-transport";

const client = new PipecatClient({
  transport: new WebSocketTransport(),
  enableMic: true,
  enableCam: false,
  callbacks: {
    onConnected: () => console.log("Connected to voice agent"),
    onDisconnected: () => console.log("Disconnected"),
    onError: (error) => console.error("Error:", error),
  }
});

// Connect to WebSocket server
await client.connect({ ws_url: 'ws://localhost:8765' });
```

### 8.7 Testing Strategy

**Development Phase:**
```bash
# Use WebSocket for fast iteration
export TRANSPORT_TYPE=websocket
export WS_HOST=localhost
export WS_PORT=8765
python voice_agent.py
```

**Performance Testing Phase:**
```bash
# Switch to WebRTC to test production-like conditions
export TRANSPORT_TYPE=daily
export DAILY_ROOM_URL=your_room_url
export DAILY_TOKEN=your_token
python voice_agent.py
```

**Comparative Testing:**

Run the same conversation through both transports and measure:
- End-to-end latency
- Audio quality (subjective)
- Reliability (dropouts, errors)
- Network resilience (simulate packet loss)

### 8.8 Performance Impact on End-to-End Latency

**WebRTC (Daily) Pipeline:**
```
Audio Capture       → 10-20ms
WebRTC Transport    → 50-100ms
VAD Detection       → 50ms
Cartesia STT        → 150-250ms
Cerebras LLM        → 240ms (TTFB)
ElevenLabs TTS      → 150-200ms
WebRTC Transport    → 50-100ms
Audio Playback      → 10-20ms
─────────────────────────────────
TOTAL: 710-980ms (perceived <600ms due to streaming)
```

**WebSocket Pipeline:**
```
Audio Capture       → 10-20ms
WebSocket Transport → 100-200ms
VAD Detection       → 50ms
Cartesia STT        → 150-250ms
Cerebras LLM        → 240ms (TTFB)
ElevenLabs TTS      → 150-200ms
WebSocket Transport → 100-200ms
Audio Playback      → 10-20ms
─────────────────────────────────
TOTAL: 810-1140ms (perceived <800ms due to streaming)
```

**Key Insight:** WebRTC saves 100-200ms per direction (200-400ms total) compared to WebSocket, making a significant difference in perceived responsiveness.

---

## 9. Functional Requirements

### 9.1 Core Capabilities

**FR-1: Real-Time Voice Conversations**
- System SHALL support bidirectional voice communication
- End-to-end latency SHALL be consistently under 1 second
- Audio quality SHALL be clear and natural-sounding
- System SHALL handle standard conversational turn-taking

**FR-2: Speech Recognition**
- System SHALL accurately transcribe user speech to text (>90% accuracy)
- System SHALL support English language (extensible to 100+ languages)
- System SHALL handle natural speech patterns (pauses, hesitations, disfluencies)
- System SHALL filter background noise and non-speech audio

**FR-3: Natural Language Understanding & Generation**
- System SHALL understand user intent from transcribed text
- System SHALL generate contextually appropriate responses
- System SHALL maintain conversation context across multiple turns
- System SHALL support conversation history of at least 10 exchanges

**FR-4: Voice Synthesis**
- System SHALL convert text responses to natural-sounding speech
- System SHALL support multiple voice options (male/female, accents)
- System SHALL maintain consistent voice throughout conversation
- Speech output SHALL be clear and easily understood

**FR-5: Interruption Handling**
- System SHALL detect when user starts speaking during agent response
- System SHALL immediately stop speaking when interrupted
- System SHALL process new user input without requiring restart
- System SHALL maintain conversation context through interruptions

### 9.2 Configuration & Flexibility

**FR-6: Configurable Transport Layer**
- System SHALL support WebRTC transport via Daily.co
- System SHALL support WebSocket transport for development
- Transport selection SHALL be configurable via environment variable
- System SHALL function identically regardless of transport choice

**FR-7: Environment Configuration**
- All API keys SHALL be configurable via environment variables
- Transport type SHALL be selectable without code changes
- System SHALL provide clear error messages for missing configuration
- Default values SHALL enable quick local testing

### 9.3 Conversation Management

**FR-8: Context Persistence**
- System SHALL maintain conversation history during session
- System SHALL track user and assistant messages in order
- System SHALL support retrieval of conversation history
- System SHALL allow context window configuration

**FR-9: System Prompt Customization**
- System SHALL support configurable system prompts
- System prompts SHALL guide agent personality and behavior
- Prompts SHALL be optimized for voice interactions (concise responses)
- System SHALL allow runtime prompt updates

**FR-10: Multi-Turn Dialogue**
- System SHALL handle follow-up questions referencing previous context
- System SHALL resolve pronouns and references to earlier conversation
- System SHALL maintain topic coherence across turns
- System SHALL gracefully handle topic changes

### 9.4 Audio Processing

**FR-11: Voice Activity Detection**
- System SHALL automatically detect speech start and end
- System SHALL filter silence and background noise
- VAD sensitivity SHALL be configurable
- System SHALL trigger STT only on detected speech (cost optimization)

**FR-12: Audio Quality Management**
- System SHALL support configurable audio sample rates (16kHz default)
- System SHALL handle audio encoding formats (PCM, μ-law, etc.)
- System SHALL maintain consistent audio levels
- System SHALL minimize audio artifacts and distortion

### 9.5 Error Handling & Reliability

**FR-13: Graceful Degradation**
- System SHALL handle API service outages gracefully
- System SHALL provide meaningful error messages to users
- System SHALL attempt automatic retry with exponential backoff
- System SHALL log errors for debugging and monitoring

**FR-14: Connection Management**
- System SHALL detect transport connection failures
- System SHALL attempt automatic reconnection
- System SHALL preserve conversation context during reconnection
- System SHALL notify user of connection status changes

---

## 10. Non-Functional Requirements

### 10.1 Performance Requirements

**NFR-1: Latency Targets**
- **End-to-end latency:** <1000ms (target: <800ms with WebRTC)
- **Speech-to-Text:** <300ms time-to-complete-transcript
- **LLM First Token:** <300ms time-to-first-byte
- **Text-to-Speech:** <200ms time-to-first-audio-byte
- **Perceived latency:** <600ms (through streaming parallelism)

**NFR-2: Throughput**
- System SHALL support minimum 1 concurrent conversation (local testing)
- System SHALL be designed for horizontal scaling to 100+ concurrent users
- Audio processing SHALL not introduce buffering delays
- Frame processing SHALL maintain real-time performance

**NFR-3: Resource Utilization**
- CPU usage SHALL remain under 50% on development machine (4-core minimum)
- Memory usage SHALL not exceed 2GB per conversation
- Network bandwidth SHALL not exceed 100 kbps per audio stream
- Disk I/O SHALL be minimal (logging only)

### 10.2 Accuracy Requirements

**NFR-4: Speech Recognition Accuracy**
- Word Error Rate (WER) SHALL be <10% for clear speech
- System SHALL correctly transcribe >90% of common words
- System SHALL handle proper nouns with reasonable accuracy
- System SHALL minimize hallucinations during silence or pauses

**NFR-5: Response Quality**
- LLM responses SHALL be contextually appropriate >95% of the time
- Responses SHALL maintain conversation coherence
- System SHALL avoid repetitive or nonsensical outputs
- Responses SHALL be optimized for voice delivery (concise, natural)

### 10.3 Reliability Requirements

**NFR-6: Availability**
- System SHALL achieve >95% uptime during testing phase
- Component failures SHALL not crash entire system
- System SHALL recover from transient errors automatically
- Planned maintenance SHALL be minimized

**NFR-7: Data Integrity**
- Conversation history SHALL be preserved accurately
- Audio frames SHALL not be lost or corrupted
- Transcriptions SHALL match actual audio content
- Context SHALL persist correctly across turns

### 10.4 Usability Requirements

**NFR-8: Ease of Setup**
- Initial setup SHALL be completable in <30 minutes
- Installation SHALL require minimal manual steps
- Documentation SHALL be clear and comprehensive
- Error messages SHALL be actionable

**NFR-9: Configuration Flexibility**
- All major parameters SHALL be configurable via environment variables
- Configuration changes SHALL not require code modifications
- Default settings SHALL work out-of-box for testing
- Transport switching SHALL be accomplished with single env variable change

### 10.5 Maintainability Requirements

**NFR-10: Code Quality**
- Code SHALL follow Python PEP 8 style guidelines
- Functions SHALL be modular and single-responsibility
- Code SHALL include docstrings for major functions
- Configuration SHALL be separated from business logic

**NFR-11: Logging & Monitoring**
- System SHALL log all major events (connections, errors, completions)
- Logs SHALL include timestamps and severity levels
- Performance metrics SHALL be collectible
- Debug mode SHALL provide detailed execution traces

### 10.6 Security Requirements

**NFR-12: API Key Management**
- API keys SHALL NEVER be hardcoded in source
- All credentials SHALL be stored in environment variables or secure storage
- API keys SHALL not appear in logs or error messages
- Access to credentials SHALL be restricted

**NFR-13: Data Privacy**
- Voice data SHALL be transmitted over encrypted connections only
- Conversation data SHALL not be stored unnecessarily
- User audio SHALL comply with privacy best practices
- Third-party API usage SHALL comply with terms of service

### 10.7 Cost Efficiency

**NFR-14: Development Cost Targets**
- 100 hours testing: <$200 total across all services
- Single conversation: <$0.10 average cost
- VAD SHALL minimize unnecessary STT API calls
- Token limits SHALL prevent runaway LLM costs

**NFR-15: Resource Optimization**
- Audio quality settings SHALL balance quality vs cost
- LLM max_tokens SHALL be set appropriately for voice (150 tokens)
- STT SHALL only process detected speech segments
- Idle connections SHALL not incur unnecessary charges

---

## 11. Development Setup & Installation

### 11.1 Prerequisites

**System Requirements:**
- Operating System: Linux, macOS, or Windows with WSL2
- Python: 3.10 or higher (3.12 recommended)
- RAM: Minimum 4GB (8GB recommended)
- CPU: 4+ cores recommended
- Network: Stable internet connection for API calls

**Required Accounts & API Keys:**
1. **Cartesia** (cartesia.ai)
   - Sign up for account
   - Generate API key from dashboard
   - Free tier available for testing

2. **Cerebras** (cloud.cerebras.ai)
   - Create account
   - Generate API key
   - Free tier: 1M tokens/day

3. **ElevenLabs** (elevenlabs.io)
   - Register account
   - Get API key from profile
   - Free tier available

4. **Daily.co** (dashboard.daily.co) - *Optional, for WebRTC*
   - Create account
   - Generate API key
   - Free tier: 1,000 minutes/month

### 11.2 Installation Steps

**1. Clone/Create Project Directory:**
```bash
mkdir voice-agent-trial
cd voice-agent-trial
```

**2. Create Virtual Environment:**
```bash
# Using venv
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using uv (recommended)
uv venv
source .venv/bin/activate
```

**3. Install Pipecat with Dependencies:**
```bash
# Using pip
pip install "pipecat-ai[daily,cartesia,cerebras,elevenlabs]"

# Or using uv (faster)
uv pip install "pipecat-ai[daily,cartesia,cerebras,elevenlabs]"
```

**4. Create Environment Configuration:**

Create `.env` file in project root:

```bash
# Cartesia STT Configuration
CARTESIA_API_KEY=your_cartesia_api_key_here

# Cerebras LLM Configuration
CEREBRAS_API_KEY=your_cerebras_api_key_here

# ElevenLabs TTS Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Transport Configuration
# Options: "daily" or "websocket"
TRANSPORT_TYPE=websocket

# Daily (WebRTC) Configuration - if using Daily
DAILY_API_KEY=your_daily_api_key_here
DAILY_ROOM_URL=https://your-domain.daily.co/your-room
DAILY_TOKEN=your_meeting_token_here

# WebSocket Configuration - if using WebSocket
WS_HOST=localhost
WS_PORT=8765

# Optional: Logging Configuration
LOG_LEVEL=INFO
```

**5. Install Additional Dependencies:**
```bash
# For environment variable management
pip install python-dotenv

# For logging
pip install structlog
```

### 11.3 Project Structure

```
voice-agent-trial/
├── .env                    # Environment variables (DO NOT commit)
├── .env.example            # Template for environment variables
├── .gitignore             # Git ignore file
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── PRD.md                 # This document
├── voice_agent.py         # Main application
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration management
├── services/
│   ├── __init__.py
│   ├── stt_service.py     # STT initialization
│   ├── llm_service.py     # LLM initialization
│   ├── tts_service.py     # TTS initialization
│   └── transport.py       # Transport factory
└── utils/
    ├── __init__.py
    ├── logger.py          # Logging utilities
    └── metrics.py         # Performance monitoring
```

### 11.4 Basic Application Template

**voice_agent.py:**

```python
import asyncio
import os
from dotenv import load_dotenv

from pipecat.pipeline import Pipeline
from pipecat.services.cartesia.stt import CartesiaSTTService, CartesiaLiveOptions
from pipecat.services.cerebras import CerebrasLLMService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.vad.silero import SileroVADAnalyzer
from pipecat.processors.aggregators.llm_response import (
    LLMUserContextAggregator,
    LLMAssistantContextAggregator,
)

# Load environment variables
load_dotenv()

async def main():
    # Initialize VAD
    vad = SileroVADAnalyzer()

    # Initialize STT (Cartesia)
    stt = CartesiaSTTService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        sample_rate=16000,
        live_options=CartesiaLiveOptions(
            model='ink-whisper',
            language='en',
            encoding='pcm_s16le',
            sample_rate=16000
        )
    )

    # Initialize LLM (Cerebras)
    system_prompt = """You are a helpful personal AI assistant.
    Keep responses brief and conversational (1-3 sentences).
    Use natural spoken language, not written formatting."""

    llm = CerebrasLLMService(
        api_key=os.getenv("CEREBRAS_API_KEY"),
        model="llama-3.3-70b",
        params={
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9,
        }
    )

    # Initialize TTS (ElevenLabs)
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
        model="eleven_flash_v2_5",
        optimize_streaming_latency=3,
        sample_rate=16000,
    )

    # Initialize Transport (configurable)
    transport = create_transport(vad)

    # Create Pipeline
    pipeline = Pipeline([
        transport.input(),
        vad,
        stt,
        LLMUserContextAggregator(),
        llm,
        LLMAssistantContextAggregator(),
        tts,
        transport.output(),
    ])

    # Run pipeline
    print("Starting voice agent...")
    await pipeline.run()

def create_transport(vad):
    """Factory function for creating transport based on environment."""
    transport_type = os.getenv("TRANSPORT_TYPE", "websocket")

    if transport_type == "daily":
        from pipecat.transports.services.daily import DailyTransport, DailyParams
        return DailyTransport(
            room_url=os.getenv("DAILY_ROOM_URL"),
            token=os.getenv("DAILY_TOKEN"),
            params=DailyParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad,
            )
        )
    elif transport_type == "websocket":
        from pipecat.transports.services.websocket import WebSocketServerTransport, WebSocketParams
        return WebSocketServerTransport(
            host=os.getenv("WS_HOST", "localhost"),
            port=int(os.getenv("WS_PORT", 8765)),
            params=WebSocketParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                vad_analyzer=vad,
            )
        )
    else:
        raise ValueError(f"Unknown transport type: {transport_type}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 11.5 Running the Application

**Start the Voice Agent:**
```bash
# Activate virtual environment
source venv/bin/activate  # or: source .venv/bin/activate

# Run with WebSocket transport (default)
python voice_agent.py

# Or switch to Daily WebRTC
export TRANSPORT_TYPE=daily
python voice_agent.py
```

**Connect Client:**

For WebSocket:
```bash
# Open client HTML file in browser or use custom client
# Connect to ws://localhost:8765
```

For Daily:
```bash
# Navigate to Daily room URL in browser
# Or use Pipecat client SDK
```

### 11.6 Verification Steps

**1. Check API Connections:**
```python
# Test script: test_apis.py
import os
from dotenv import load_dotenv

load_dotenv()

# Test Cartesia
from pipecat.services.cartesia.stt import CartesiaSTTService
stt = CartesiaSTTService(api_key=os.getenv("CARTESIA_API_KEY"))
print("✓ Cartesia STT initialized")

# Test Cerebras
from pipecat.services.cerebras import CerebrasLLMService
llm = CerebrasLLMService(api_key=os.getenv("CEREBRAS_API_KEY"))
print("✓ Cerebras LLM initialized")

# Test ElevenLabs
from pipecat.services.elevenlabs import ElevenLabsTTSService
tts = ElevenLabsTTSService(api_key=os.getenv("ELEVENLABS_API_KEY"))
print("✓ ElevenLabs TTS initialized")

print("\nAll services initialized successfully!")
```

**2. Test Audio Pipeline:**
- Speak into microphone
- Verify transcription appears in logs
- Verify LLM response generated
- Verify audio playback through speakers

**3. Monitor Performance:**
- Check latency in logs
- Verify sub-1s end-to-end response time
- Monitor CPU/memory usage
- Check API usage in service dashboards

### 11.7 Troubleshooting

**Common Issues:**

| Issue | Solution |
|-------|----------|
| "API key invalid" | Verify `.env` file exists and keys are correct |
| "Connection refused" | Check transport configuration (Daily room/WebSocket port) |
| "No audio input" | Verify microphone permissions in browser/OS |
| "High latency" | Switch from WebSocket to Daily WebRTC |
| "Import errors" | Reinstall with correct extras: `pip install "pipecat-ai[...]"` |
| "Module not found" | Ensure virtual environment is activated |

---

## 12. Cost Estimation & Budget

### 12.1 Service-by-Service Breakdown

**Cartesia STT (Ink-Whisper)**
- **Pricing:** $0.13/hour of audio
- **100 hours testing:** 100 × $0.13 = **$13.00**
- **1,000 hours scaled:** 1,000 × $0.13 = **$130.00**
- **Most affordable option:** 50%+ cheaper than alternatives

**Cerebras LLM (Llama 3.3-70B)**
- **Pricing:** $0.60 per million tokens
- **Free tier:** 1 million tokens/day (sufficient for extensive testing)
- **Estimated tokens per 100 hours:**
  - Average conversation: 10 exchanges
  - Average tokens per exchange: ~1,000 (500 input + 500 output)
  - Total: ~100M tokens
- **100 hours testing:** 100M × $0.60 = **$60.00** (or **$0 with free tier**)
- **1,000 hours scaled:** 1B × $0.60 = **$600.00**

**ElevenLabs TTS (Flash v2.5)**
- **Pricing:** Character-based (session pricing)
- **Estimated characters per 100 hours:**
  - Average response: 150 characters
  - Conversations: ~5,000 responses
  - Total: 750,000 characters
- **100 hours testing:** ~**$50-100** (depending on tier)
- **Creator tier:** $22/month (62.8 hours included)
- **Pro tier:** $99/month (300 hours included)

**Daily.co (WebRTC Transport - Optional)**
- **Free tier:** 1,000 minutes/month = ~16.7 hours
- **100 hours testing:** Requires paid plan
- **Paid plans:** Start at ~$20/month + usage
- **100 hours cost:** **$0-50** (depending on plan)
- **Note:** Only needed if using WebRTC; WebSocket is free

### 12.2 Total Cost Scenarios

**Scenario A: Development/Testing (100 hours, using free tiers)**
```
Cartesia STT:           $13.00
Cerebras LLM:           $0.00  (free tier: 1M tokens/day)
ElevenLabs TTS:         $22.00 (Creator tier subscription)
Daily.co Transport:     $0.00  (using WebSocket instead)
────────────────────────────────
TOTAL (Month 1):        $35.00
```

**Scenario B: Development/Testing (100 hours, no free tier)**
```
Cartesia STT:           $13.00
Cerebras LLM:           $60.00
ElevenLabs TTS:         $75.00 (estimated usage-based)
Daily.co Transport:     $30.00 (if using WebRTC)
────────────────────────────────
TOTAL:                  $178.00
```

**Scenario C: Production Scale (1,000 hours/month)**
```
Cartesia STT:           $130.00
Cerebras LLM:           $600.00 (1B tokens)
ElevenLabs TTS:         $330.00 (Business tier)
Daily.co Transport:     $200.00 (scaled WebRTC usage)
────────────────────────────────
TOTAL:                  $1,260.00
```

### 12.3 Cost Optimization Strategies

**1. Leverage Free Tiers During Development**
- Cerebras: 1M tokens/day = ~30M/month (covers extensive testing)
- ElevenLabs: Free tier for initial proof-of-concept
- Daily.co: 1,000 minutes/month for WebRTC testing
- **Potential savings:** ~$60-100/month

**2. Use VAD to Minimize STT Costs**
- VAD filters silence and non-speech audio
- Reduces STT API calls by ~30-50%
- **Savings:** ~$4-6 per 100 hours

**3. Optimize LLM Token Usage**
- Set `max_tokens: 150` for voice responses
- Use concise system prompts
- Implement token counting and limits
- **Savings:** ~$20-40 per 100 hours

**4. WebSocket for Development, WebRTC for Production**
- Use free WebSocket during development
- Switch to Daily only for production deployment or testing
- **Savings:** ~$30-50/month during development

**5. Monitor and Alert on Usage**
- Set up usage alerts in service dashboards
- Track cost per conversation
- Identify and optimize expensive operations
- **Prevents:** Cost overruns and surprises

### 12.4 Cost Per Conversation

**Typical 5-minute conversation:**
```
STT (5 min × $0.13/60 min):     $0.011
LLM (~5,000 tokens):             $0.003 (Cerebras)
TTS (~750 characters):           $0.005
Transport (Daily, if used):      $0.003
─────────────────────────────────────────
TOTAL PER CONVERSATION:          $0.022
```

**Cost-effective at scale:**
- 1,000 conversations/month: ~$22
- 10,000 conversations/month: ~$220
- 100,000 conversations/month: ~$2,200

### 12.5 Comparison to Alternatives

**This Stack (Pipecat + Cartesia + Cerebras + ElevenLabs):**
- 100 hours: ~$35-178
- Per conversation: ~$0.02

**Alternative 1: All-in-one (ElevenLabs Conversational AI Platform):**
- Pricing: $0.10/minute = $6.00/hour
- 100 hours: $600
- Per conversation (5 min): $0.50
- **25x more expensive**

**Alternative 2: Premium Stack (AssemblyAI + OpenAI + ElevenLabs):**
- AssemblyAI: $0.27/hr
- OpenAI GPT-4: $15/1M tokens
- ElevenLabs: Same
- 100 hours: ~$250-350
- **2-3x more expensive**

**Alternative 3: Budget Stack (Whisper + Groq + Cartesia Sonic):**
- Whisper (local): $0 (but requires GPU)
- Groq: $0.27/M tokens
- Cartesia Sonic: Similar to ElevenLabs
- 100 hours: ~$30-60
- **Similar cost, but local Whisper adds complexity**

**Conclusion:** The selected stack (Cartesia + Cerebras + ElevenLabs) provides the best balance of cost, performance, and simplicity.

---

## 13. Implementation Phases

### 13.1 Phase 1: Foundation Setup (Week 1)

**Objectives:**
- Set up development environment
- Integrate core components
- Establish basic voice pipeline
- Verify end-to-end functionality

**Tasks:**
1. Create project structure and virtual environment
2. Install Pipecat with all dependencies
3. Configure environment variables (.env file)
4. Implement basic voice_agent.py with WebSocket transport
5. Integrate Cartesia STT, Cerebras LLM, ElevenLabs TTS
6. Test each component individually
7. Run first end-to-end voice conversation
8. Document setup process

**Deliverables:**
- Working voice agent with WebSocket transport
- Complete environment configuration
- Component integration test results
- Setup documentation

**Success Criteria:**
- Voice agent successfully handles single-turn conversation
- All API services connect and respond
- End-to-end latency measured and logged
- No critical errors or crashes

### 13.2 Phase 2: Transport & Multi-turn Support (Week 2)

**Objectives:**
- Add Daily WebRTC transport option
- Implement configurable transport switching
- Support multi-turn conversations
- Add context management

**Tasks:**
1. Set up Daily.co account and create room
2. Implement transport factory pattern
3. Add environment-based transport selection
4. Integrate LLMUserContextAggregator and LLMAssistantContextAggregator
5. Test context persistence across multiple turns
6. Optimize system prompts for voice interactions
7. Test both WebRTC and WebSocket transports
8. Compare performance between transports

**Deliverables:**
- Configurable transport layer (WebRTC/WebSocket)
- Multi-turn conversation support
- Context management implementation
- Transport performance comparison report

**Success Criteria:**
- Successfully switch between transports via environment variable
- Maintain context for 10+ conversation turns
- WebRTC latency <800ms, WebSocket <1000ms
- Graceful handling of transport disconnections

### 13.3 Phase 3: Optimization & Reliability (Week 3)

**Objectives:**
- Optimize latency and performance
- Implement error handling and recovery
- Add logging and monitoring
- Improve interruption handling

**Tasks:**
1. Profile and optimize component latencies
2. Implement exponential backoff retry logic
3. Add comprehensive logging (structlog)
4. Implement performance metrics collection
5. Test and refine interruption handling
6. Add connection recovery mechanisms
7. Optimize VAD sensitivity for environment
8. Test under various network conditions

**Deliverables:**
- Optimized pipeline with <600ms perceived latency
- Robust error handling and recovery
- Comprehensive logging system
- Performance monitoring dashboard (optional)

**Success Criteria:**
- Consistent <800ms end-to-end latency with WebRTC
- >95% successful conversation completion rate
- Graceful recovery from API failures
- Smooth interruption handling

### 13.4 Phase 4: Testing & Refinement (Week 4)

**Objectives:**
- Comprehensive testing across scenarios
- Fine-tune system prompts and parameters
- Document learnings and best practices
- Prepare for production deployment (future)

**Tasks:**
1. Test with various accents and speaking styles
2. Test in noisy environments (background noise)
3. Test with different conversation topics
4. Optimize system prompts based on results
5. Test cost optimization strategies (VAD, token limits)
6. Load testing (if applicable)
7. Document edge cases and limitations
8. Create deployment guide for future production

**Deliverables:**
- Comprehensive test results and analysis
- Optimized system prompts and configurations
- Best practices documentation
- Production deployment guide

**Success Criteria:**
- >90% STT accuracy across test scenarios
- >95% contextually appropriate LLM responses
- Natural conversation flow in 95% of tests
- Complete documentation for production deployment

### 13.5 Phase 5: Future Enhancements (Ongoing)

**Potential Enhancements:**
1. Multi-language support (leverage Cartesia's 100+ languages)
2. Custom wake word detection
3. Function calling / tool use (calendar integration, web search, etc.)
4. Conversation summarization
5. Sentiment analysis and emotion detection
6. Voice authentication
7. Multi-user support (conference calls)
8. Persistent conversation history (database integration)
9. Analytics dashboard
10. Mobile client applications

**Prioritization:**
- Determine based on use case evolution
- Consider user feedback and requirements
- Balance complexity vs value

---

## 14. Success Metrics & KPIs

### 14.1 Technical Performance Metrics

**Latency Metrics:**
- **End-to-end latency:** Target <800ms (WebRTC), <1000ms (WebSocket)
- **STT latency:** <250ms time-to-complete-transcript
- **LLM latency:** <300ms time-to-first-byte
- **TTS latency:** <200ms time-to-first-audio-byte
- **Perceived latency:** <600ms (through streaming)

**Accuracy Metrics:**
- **STT Word Error Rate (WER):** <10% for clear speech
- **STT accuracy:** >90% word-level accuracy
- **LLM relevance:** >95% contextually appropriate responses
- **Context retention:** >95% accuracy across 10-turn conversations

**Reliability Metrics:**
- **Uptime:** >95% availability during testing
- **Error rate:** <5% of conversations encounter errors
- **Recovery rate:** >90% automatic recovery from transient errors
- **Connection stability:** <2% disconnection rate

**Resource Utilization:**
- **CPU usage:** <50% average on 4-core system
- **Memory usage:** <2GB per conversation
- **Network bandwidth:** <100 kbps per stream
- **API response time:** <500ms for 95th percentile

### 14.2 User Experience Metrics

**Conversation Quality:**
- **Natural flow:** Subjective rating >4/5 by testers
- **Interruption handling:** >90% smooth interruption recovery
- **Turn-taking:** <10% awkward pauses or overlaps
- **Response appropriateness:** >95% relevant and helpful

**Audio Quality:**
- **Speech clarity:** >4/5 subjective rating
- **Voice naturalness:** >4/5 subjective rating
- **Audio artifacts:** <5% occurrence rate
- **Volume consistency:** Consistent levels throughout conversation

**Ease of Use:**
- **Setup time:** <30 minutes for new developers
- **Configuration ease:** Environment variable changes without code
- **Error message clarity:** >90% actionable error messages
- **Documentation quality:** >4/5 rating by new users

### 14.3 Cost Efficiency Metrics

**Development Phase:**
- **Monthly cost (100 hours):** <$200 target
- **Cost per conversation:** <$0.10 target
- **Free tier utilization:** >50% of testing uses free tiers
- **Cost overrun incidents:** 0 surprise charges

**Scaling Metrics:**
- **Cost scaling factor:** Linear with usage (no step functions)
- **Optimization savings:** >20% reduction through VAD and token limits
- **Cost per user per month:** <$5 at 100+ users

### 14.4 Measurement & Monitoring

**Implementation:**

```python
# Example metrics collection
import time
from dataclasses import dataclass
from typing import Dict

@dataclass
class ConversationMetrics:
    start_time: float
    stt_latency: float = 0
    llm_latency: float = 0
    tts_latency: float = 0
    total_latency: float = 0
    tokens_used: int = 0
    characters_synthesized: int = 0
    errors: int = 0

def log_metrics(metrics: ConversationMetrics):
    """Log conversation metrics for analysis."""
    print(f"""
    Conversation Metrics:
    - Total Latency: {metrics.total_latency:.0f}ms
    - STT Latency: {metrics.stt_latency:.0f}ms
    - LLM Latency: {metrics.llm_latency:.0f}ms
    - TTS Latency: {metrics.tts_latency:.0f}ms
    - Tokens Used: {metrics.tokens_used}
    - TTS Characters: {metrics.characters_synthesized}
    - Errors: {metrics.errors}
    """)
```

**Dashboards & Reporting:**
- Track metrics in service dashboards (Cerebras, Cartesia, ElevenLabs)
- Implement local metrics aggregation
- Weekly performance reports during testing
- Cost tracking spreadsheet

---

## 15. Risks & Mitigation Strategies

### 15.1 Technical Risks

**Risk 1: API Service Outages**
- **Impact:** High - System becomes non-functional
- **Probability:** Low-Medium (cloud services have occasional outages)
- **Mitigation:**
  - Implement exponential backoff retry logic
  - Add circuit breaker pattern for repeated failures
  - Graceful degradation messaging to user
  - Monitor service status pages
  - Consider fallback providers for critical components
- **Contingency:** Switch to alternative providers (e.g., Deepgram for STT, OpenAI for LLM)

**Risk 2: Latency Exceeds 1 Second**
- **Impact:** Medium - Poor user experience
- **Probability:** Medium (network variability, component delays)
- **Mitigation:**
  - Use WebRTC transport (lower latency than WebSocket)
  - Optimize component configurations (TTS latency level 3, etc.)
  - Profile and identify bottlenecks
  - Consider geographic proximity to API servers
  - Implement streaming to minimize perceived latency
- **Contingency:** Evaluate faster alternatives (e.g., Cartesia Sonic TTS, Groq LLM)

**Risk 3: Poor STT Accuracy in Noisy Environments**
- **Impact:** Medium - Misunderstood user intent
- **Probability:** Medium (depends on deployment environment)
- **Mitigation:**
  - Use Cartesia's noise-handling optimizations
  - Fine-tune VAD sensitivity
  - Implement noise suppression preprocessing
  - Test in realistic environments
  - Provide clear audio quality feedback to user
- **Contingency:** Switch to more robust STT (Deepgram with noise suppression)

**Risk 4: Context Window Limitations**
- **Impact:** Low-Medium - Loss of conversation coherence
- **Probability:** Medium (long conversations exceed limits)
- **Mitigation:**
  - Implement context window management (sliding window)
  - Summarize old conversations to preserve key context
  - Monitor context size and warn user
  - Set reasonable conversation length limits
- **Contingency:** Implement conversation summarization with periodic resets

### 15.2 Cost Risks

**Risk 5: Unexpected Cost Overruns**
- **Impact:** High - Budget exceeded
- **Probability:** Medium (usage estimation errors, pricing changes)
- **Mitigation:**
  - Set up billing alerts in all service dashboards
  - Implement usage tracking and limits
  - Use free tiers during development
  - Monitor cost per conversation
  - Implement rate limiting and quotas
- **Contingency:** Pause development, analyze usage, optimize or switch providers

**Risk 6: Pricing Model Changes**
- **Impact:** Medium - Increased costs or forced migration
- **Probability:** Low-Medium (startup pricing often changes)
- **Mitigation:**
  - Diversify across multiple providers
  - Design modular architecture for easy provider swaps
  - Monitor service announcements and pricing pages
  - Build relationships with provider account teams
- **Contingency:** Migration plan to alternative providers

### 15.3 Integration Risks

**Risk 7: Pipecat Framework Limitations or Bugs**
- **Impact:** Medium-High - Development blocked
- **Probability:** Low-Medium (active project but evolving)
- **Mitigation:**
  - Use stable release versions
  - Test thoroughly before production
  - Monitor Pipecat GitHub issues and discussions
  - Contribute bug fixes and improvements
  - Maintain direct API integration knowledge
- **Contingency:** Fall back to direct API integrations without Pipecat

**Risk 8: API Breaking Changes**
- **Impact:** Medium - Integration breaks, requires updates
- **Probability:** Low (but higher for newer services like Cartesia)
- **Mitigation:**
  - Pin dependency versions (requirements.txt)
  - Monitor provider changelogs and deprecation notices
  - Test updates in staging before production
  - Maintain abstraction layers for easy provider swaps
- **Contingency:** Rapid update cycle, temporary rollback to working versions

### 15.4 Operational Risks

**Risk 9: Scaling Challenges**
- **Impact:** High - Cannot handle production load
- **Probability:** Low (for local testing), High (for production)
- **Mitigation:**
  - Design for horizontal scaling from start
  - Use stateless architecture where possible
  - Plan infrastructure early (Kubernetes, serverless, etc.)
  - Load test before production launch
  - Work with providers on scaling limits
- **Contingency:** Gradual rollout, rate limiting, queue management

**Risk 10: Security Vulnerabilities**
- **Impact:** High - Data breach, API key compromise
- **Probability:** Low-Medium (depends on deployment security)
- **Mitigation:**
  - Never commit API keys to version control
  - Use environment variables and secret management
  - Implement least-privilege access controls
  - Regular security audits
  - Encrypt data in transit (HTTPS/WSS)
- **Contingency:** Key rotation procedures, incident response plan

### 15.5 Risk Matrix

| Risk | Impact | Probability | Priority | Status |
|------|--------|-------------|----------|--------|
| API Service Outages | High | Low-Med | **High** | Mitigated |
| Latency > 1s | Medium | Medium | **High** | Mitigated |
| Poor STT Accuracy | Medium | Medium | Medium | Mitigated |
| Context Limits | Low-Med | Medium | Medium | Mitigated |
| Cost Overruns | High | Medium | **High** | Mitigated |
| Pricing Changes | Medium | Low-Med | Medium | Monitored |
| Pipecat Issues | Med-High | Low-Med | Medium | Monitored |
| API Breaking Changes | Medium | Low | Low | Monitored |
| Scaling Challenges | High | Low/High* | Medium | Planned |
| Security Issues | High | Low-Med | **High** | Mitigated |

*Low for local testing, High for production

---

## 16. Future Considerations & Enhancements

### 16.1 Feature Enhancements

**Multi-Language Support:**
- Leverage Cartesia's 100+ language support
- Implement language detection and switching
- Multi-lingual conversation support
- Region-specific voice selection

**Function Calling / Tool Use:**
- Calendar integration (schedule appointments)
- Web search integration (real-time information)
- Email composition and sending
- Smart home control
- API integrations for specific domains

**Advanced Context Management:**
- Persistent conversation history (database storage)
- Cross-session context retrieval
- User preferences and personalization
- Conversation summarization
- Semantic search across conversation history

**Sentiment & Emotion Analysis:**
- Real-time sentiment detection
- Emotional response adaptation
- Tone matching with user
- Mental health support indicators

**Voice Customization:**
- Custom voice cloning for consistent brand voice
- Voice style adaptation (formal, casual, etc.)
- Multilingual voice consistency
- Age/gender/accent customization

### 16.2 Technical Improvements

**Performance Optimization:**
- Edge deployment for lower latency
- Regional API endpoint selection
- Caching frequent responses
- Predictive prefetching
- Optimized audio codecs

**Reliability Enhancements:**
- Multi-provider fallbacks (automatic switching)
- Circuit breaker patterns
- Health check monitoring
- Automatic failover
- Distributed tracing

**Observability:**
- Real-time performance dashboard
- Cost tracking and visualization
- User journey analytics
- Error tracking and alerting (Sentry integration)
- A/B testing framework

**Security Hardening:**
- End-to-end encryption
- Voice authentication / biometrics
- PII detection and redaction
- Compliance certifications (HIPAA, SOC 2)
- Rate limiting and abuse prevention

### 16.3 Alternative Component Exploration

**Alternative TTS: Cartesia Sonic**
- **Benefit:** Unified vendor (Cartesia STT + TTS)
- **Latency:** 90ms (slightly better than ElevenLabs 75ms)
- **Cost:** Potentially lower for combined usage
- **When to switch:** If vendor consolidation desired

**Alternative STT Options:**
- **Deepgram Nova-3:** If higher accuracy needed (18.3% WER vs Whisper baseline)
- **Deepgram Flux:** If conversation-aware end-of-turn detection desired
- **AssemblyAI:** If domain-specific models needed (medical, sales, etc.)

**Alternative LLM Options:**
- **OpenAI GPT-4o:** If highest quality responses needed (higher cost)
- **Groq:** If even faster inference needed (but smaller context window)
- **Anthropic Claude:** If nuanced reasoning important (slower)

**All-in-One Platform:**
- **ElevenLabs Conversational AI:** If simplicity valued over cost ($0.10/min)
- **Deepgram Voice Agent API:** If single-vendor solution preferred ($4.50/hr)

### 16.4 Deployment & Scaling

**Cloud Deployment Options:**
- **Serverless:** AWS Lambda, Google Cloud Functions, Azure Functions
- **Container Orchestration:** Kubernetes, AWS ECS, Google GKE
- **Platform-as-a-Service:** Heroku, Render, Fly.io
- **Specialized Platforms:** Modal, Cerebrium (Pipecat hosting)

**Scaling Strategies:**
- Horizontal scaling with load balancers
- Auto-scaling based on demand
- Geographic distribution (multi-region)
- Connection pooling and resource management
- Queue-based request handling

**Infrastructure as Code:**
- Terraform for cloud resource provisioning
- Docker for containerization
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Automated testing and deployment

### 16.5 Business & Product Evolution

**Productization:**
- White-label voice agent platform
- Multi-tenant architecture
- Admin dashboard for configuration
- Usage analytics for customers
- Billing and subscription management

**Vertical-Specific Adaptations:**
- **Healthcare:** HIPAA compliance, medical terminology
- **Customer Service:** CRM integration, ticket creation
- **Education:** Tutoring, assessment, accessibility
- **Real Estate:** Property search, appointment scheduling
- **Finance:** Account inquiries, transaction support (with security)

**Mobile Applications:**
- Native iOS app (Swift/SwiftUI)
- Native Android app (Kotlin)
- React Native cross-platform app
- WebRTC mobile SDK integration

---

## Appendix A: Technology Comparisons

### A.1 STT Service Comparison

| Service | Latency | Accuracy | Pricing | Languages | Pipecat Support | Best For |
|---------|---------|----------|---------|-----------|-----------------|----------|
| **Cartesia Ink-Whisper** | Fastest TTCT (~150-250ms) | Better than Whisper V3 | **$0.13/hr** | 100+ | ✅ Built-in | **Cost + Speed** |
| AssemblyAI Universal-2 | 300-600ms | 14.5% WER (best) | $0.27/hr | 90+ | ✅ Built-in | Highest accuracy |
| Deepgram Nova-3 | ~200-260ms | 18.3% WER | ~$0.30/hr | 36 | ✅ Built-in | Balanced |
| Deepgram Flux | ~200ms | Good | ~$0.30/hr | 36 | ✅ Built-in | Conversation-aware |
| OpenAI Whisper V3 | Variable (local) | Baseline | Free (local GPU) | 99+ | ✅ Built-in | Offline/Budget |
| **ElevenLabs Scribe** | **Variable (batch)** | 96.7% accuracy | $0.22-0.48/hr | 99+ | ⚠️ Non-streaming | **NOT real-time** |

**Recommendation:** **Cartesia Ink-Whisper** for best cost/performance balance

### A.2 LLM Service Comparison

| Service | Speed | Latency (TTFB) | Pricing | Quality | Best For |
|---------|-------|----------------|---------|---------|----------|
| **Cerebras Llama 3.3-70B** | **450 tok/s** | **~240ms** | **$0.60/M** | Excellent | **Voice agents** |
| Groq Llama 3.1-70B | ~800 tok/s | ~100ms | $0.59/M | Excellent | Max speed |
| OpenAI GPT-4o | ~100 tok/s | ~500ms | $5.00/M | Best | Highest quality |
| Anthropic Claude 3.5 Sonnet | ~80 tok/s | ~600ms | $3.00/M | Excellent | Reasoning |
| OpenAI GPT-3.5 Turbo | ~150 tok/s | ~400ms | $0.50/M | Good | Budget |

**Recommendation:** **Cerebras** for best latency/cost for voice

### A.3 TTS Service Comparison

| Service | Latency | Quality | Pricing | Voices | Best For |
|---------|---------|---------|---------|--------|----------|
| **ElevenLabs Flash v2.5** | **75ms** | Excellent | Usage-based | 1,000+ | **Voice agents** |
| Cartesia Sonic | 90ms | Excellent | Usage-based | Limited | Unified stack |
| OpenAI TTS | ~250ms | Very Good | $15/M chars | 6 | Budget |
| Deepgram Aura | <250ms | Good | Bundled | Limited | Deepgram users |
| Google Cloud TTS | ~300ms | Good | $16/M chars | 200+ | Enterprise |

**Recommendation:** **ElevenLabs Flash v2.5** for lowest latency

### A.4 Transport Comparison

| Transport | Latency | Setup | Production | Cost | Best For |
|-----------|---------|-------|------------|------|----------|
| **Daily (WebRTC)** | **50-100ms** | Medium | **✅ Yes** | Free tier + paid | **Production** |
| WebSocket | 200-400ms | Easy | ⚠️ Limited | Infrastructure only | Development |
| LiveKit (WebRTC) | 50-100ms | Medium | ✅ Yes | Paid | Multi-user |
| Agora (WebRTC) | 50-100ms | Complex | ✅ Yes | Paid | Scale |

**Recommendation:** **Daily WebRTC** for production, **WebSocket** for development

### A.5 Why NOT ElevenLabs Scribe for Real-Time Voice Agents

**ElevenLabs Scribe v1 is NOT suitable for real-time voice agents because:**

1. **No Streaming Support:** Batch processing only, must wait for complete audio
2. **High Variable Latency:** Reported as "highly variable" by Pipecat maintainers
3. **Rate Limiting Issues:** 429 errors even with enterprise plans
4. **Pipecat Integration:** Uses SegmentedSTTService (non-streaming), not WebsocketSTTService
5. **Design Purpose:** Built for transcription (podcasts, meetings), not conversational AI

**ElevenLabs DOES have real-time STT**, but it's:
- **Platform-only:** Part of their Conversational AI Platform (<100ms latency)
- **Not available as standalone API:** Cannot be used with Pipecat
- **All-in-one solution:** Must use their entire platform ($0.10/min)

**When ElevenLabs Scribe IS appropriate:**
- Post-call transcription and analysis
- Batch processing of recorded conversations
- Multi-speaker diarization (up to 32 speakers)
- High-accuracy transcription of underserved languages
- Audio event detection (laughter, applause, etc.)

**Wait for:** ElevenLabs to release streaming version of Scribe before reconsidering for voice agents.

---

## Appendix B: References & Resources

### B.1 Official Documentation

**Pipecat Framework:**
- GitHub Repository: https://github.com/pipecat-ai/pipecat
- Documentation: https://docs.pipecat.ai/
- API Reference: https://reference-server.pipecat.ai/
- Examples: https://github.com/pipecat-ai/pipecat/tree/main/examples
- Discord Community: https://discord.gg/pipecat

**Cartesia:**
- Website: https://cartesia.ai/
- Documentation: https://docs.cartesia.ai/
- API Reference: https://docs.cartesia.ai/api-reference
- Ink-Whisper STT: https://docs.cartesia.ai/product/ink
- Sonic TTS: https://docs.cartesia.ai/product/sonic
- Pipecat Integration: https://docs.cartesia.ai/integrations/pipecat

**Cerebras:**
- Website: https://www.cerebras.ai/
- Cloud Platform: https://cloud.cerebras.ai/
- Documentation: https://docs.cerebras.ai/
- Inference API: https://inference-docs.cerebras.ai/
- Pricing: https://cloud.cerebras.ai/pricing

**ElevenLabs:**
- Website: https://elevenlabs.io/
- Documentation: https://elevenlabs.io/docs/
- API Reference: https://elevenlabs.io/docs/api-reference/
- Latency Optimization: https://elevenlabs.io/docs/best-practices/latency-optimization
- TTS Streaming: https://elevenlabs.io/docs/developer-guides/streaming

**Daily.co:**
- Website: https://www.daily.co/
- Documentation: https://docs.daily.co/
- Pipecat Integration: https://docs.daily.co/guides/products/ai-toolkit/pipecat
- API Reference: https://docs.daily.co/reference/rest-api

### B.2 Technical Articles & Guides

**Voice Agent Best Practices:**
- Pipecat Voice Agent Guide: https://docs.pipecat.ai/guides/voice-agents
- Real-time AI Voice Agents: https://www.daily.co/blog/real-time-ai-voice-agents/
- Building Conversational AI: https://www.assemblyai.com/blog/voice-agents-pipecat/

**Performance Optimization:**
- Reducing Voice Agent Latency: https://elevenlabs.io/docs/best-practices/latency-optimization
- WebRTC vs WebSocket: https://docs.daily.co/guides/products/ai-toolkit/transports
- Streaming Best Practices: https://docs.cartesia.ai/guides/streaming

**Architecture Patterns:**
- Voice Agent Architecture: https://docs.pipecat.ai/guides/architecture
- Pipeline Design: https://docs.pipecat.ai/guides/pipelines
- Frame Processing: https://docs.pipecat.ai/guides/frames

### B.3 Code Examples

**Pipecat Examples Repository:**
- Foundational Examples: https://github.com/pipecat-ai/pipecat/tree/main/examples/foundational
- Cartesia STT Example: `13f-cartesia-transcription.py`
- Cerebras LLM Example: `14k-function-calling-cerebras.py`
- Daily Transport Example: `04a-transports-daily.py`
- WebSocket Example: https://github.com/pipecat-ai/pipecat/tree/main/examples/websocket-server

**Pipecat Client SDKs:**
- Client Web Transports: https://github.com/pipecat-ai/pipecat-client-web-transports
- JavaScript Client: https://github.com/pipecat-ai/pipecat-client-js

### B.4 Community Resources

**Forums & Discussion:**
- Pipecat Discord: Active community for real-time help
- Daily Slack: #ai-toolkit channel
- Reddit r/LocalLLaMA: Voice agent discussions
- Stack Overflow: Tag `pipecat`

**Video Tutorials:**
- Pipecat Getting Started: https://www.youtube.com/daily
- Building Voice Agents with Pipecat: Various tutorials on YouTube
- Daily.co AI Toolkit Demos: https://www.daily.co/products/ai

### B.5 Pricing & Plans

**Service Pricing Pages:**
- Cartesia Pricing: https://cartesia.ai/pricing
- Cerebras Pricing: https://cloud.cerebras.ai/pricing
- ElevenLabs Pricing: https://elevenlabs.io/pricing
- Daily.co Pricing: https://www.daily.co/pricing

### B.6 Research Papers & Technical Reports

**Speech Recognition:**
- Whisper Paper: https://cdn.openai.com/papers/whisper.pdf
- Deep Speech Recognition: Various academic papers

**Text-to-Speech:**
- Neural TTS: Research on modern TTS approaches
- Streaming TTS: Low-latency synthesis techniques

**LLM Inference:**
- Cerebras WSE-3 Architecture: https://www.cerebras.ai/blog/
- Fast Inference Techniques: Research on optimization

### B.7 Related Tools & Technologies

**Alternative Frameworks:**
- LangChain: https://www.langchain.com/
- LlamaIndex: https://www.llamaindex.ai/
- Haystack: https://haystack.deepset.ai/

**Audio Processing:**
- Silero VAD: https://github.com/snakers4/silero-vad
- PyAudio: https://people.csail.mit.edu/hubert/pyaudio/
- SpeechBrain: https://speechbrain.github.io/

**Deployment Platforms:**
- Modal: https://modal.com/
- Fly.io: https://fly.io/
- Render: https://render.com/
- Railway: https://railway.app/

---

## Conclusion

This Product Requirements Document outlines a comprehensive approach to building a high-performance, cost-effective voice agent platform using cutting-edge technologies. The selected stack—Pipecat orchestration with Cartesia STT, Cerebras LLM, and ElevenLabs TTS—provides an optimal balance of performance, cost, and developer experience.

**Key Takeaways:**

1. **Performance-First Architecture:** Sub-1 second end-to-end latency through component selection and streaming pipelines
2. **Cost Leadership:** ~$35-178 for 100 hours testing vs $600+ for alternatives
3. **Flexible Transport:** Configurable WebRTC/WebSocket for development-to-production path
4. **Production-Ready:** Built on proven, enterprise-grade services
5. **Clear Implementation Path:** Phased approach from foundation to optimization

**Next Steps:**

1. Set up development environment (Phase 1, Week 1)
2. Obtain API keys from all providers
3. Build basic pipeline and verify end-to-end functionality
4. Iterate based on testing and feedback
5. Document learnings and optimize for production

This PRD serves as a living document and should be updated as the project evolves, new technologies emerge, and requirements change.

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Status:** Final Draft
**Next Review:** After Phase 1 completion

