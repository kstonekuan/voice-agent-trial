# Voice Agent Client

React-based web client for the Voice Agent platform, built with:
- **React 19** + **TypeScript**
- **Vite** for fast development and builds
- **Tailwind CSS v4** for modern styling
- **Pipecat React SDK** for voice interaction
- **Biome** for linting and formatting

## Features

- 🎤 Real-time voice conversations with AI
- 🔄 Dual transport support (WebSocket + Daily WebRTC)
- 🎨 Modern, responsive UI with Tailwind CSS v4
- ⚙️ Shared configuration with backend (single .env file)
- 📦 Production-ready build with code splitting

## Quick Start

### 1. Prerequisites

Make sure the parent `.env` file is configured (see `../README.md`).

The client automatically reads from `../env` for configuration.

### 2. Install Dependencies

```bash
pnpm install
```

### 3. Start Development Server

```bash
pnpm dev
```

The client will start on `http://localhost:5173` and automatically use the transport configuration from the parent `.env` file.

### 4. Connect to Voice Agent

1. Start the Python backend:
   ```bash
   cd ..
   uv run voice-agent start
   ```

2. Open the client in your browser: `http://localhost:5173`

3. Click "Start Conversation" to connect

4. Speak into your microphone to interact with the AI!

## Configuration

The client reads configuration from the parent `.env` file:

- `TRANSPORT_TYPE` - Transport type: `websocket` or `daily`
- `WS_HOST` - WebSocket host (for websocket transport)
- `WS_PORT` - WebSocket port (for websocket transport)
- `DAILY_ROOM_URL` - Daily room URL (for daily transport)

**No separate client configuration needed!** Just update `../env` and both the server and client will use the same settings.

## Development

### Available Scripts

```bash
# Start development server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Type checking
pnpm typecheck

# Linting
pnpm lint

# Auto-fix linting issues
pnpm lint:fix

# Format code
pnpm format
```

### Project Structure

```
client/
├── src/
│   ├── components/
│   │   └── VoiceInterface.tsx    # Main voice UI component
│   ├── config/
│   │   └── pipecatConfig.ts      # Transport configuration (reads from .env)
│   ├── App.tsx                   # Root component
│   ├── main.tsx                  # Entry point
│   ├── index.css                 # Global styles + Tailwind
│   └── vite-env.d.ts             # TypeScript declarations
├── public/                       # Static assets
├── biome.json                    # Biome configuration
├── vite.config.ts                # Vite config + parent .env loading
├── tsconfig.json                 # TypeScript configuration
└── package.json
```

## Transport Configuration

### WebSocket Transport (Development)

Best for local development. Configure in `../env`:

```env
TRANSPORT_TYPE=websocket
WS_HOST=localhost
WS_PORT=8765
```

Client connects to: `ws://localhost:8765/ws`

### Daily WebRTC Transport (Production)

Best for production with ultra-low latency. Configure in `../env`:

```env
TRANSPORT_TYPE=daily
DAILY_ROOM_URL=https://your-domain.daily.co/your-room
DAILY_TOKEN=your_meeting_token
```

## Building for Production

```bash
# Build optimized production bundle
pnpm build

# Preview the production build
pnpm preview
```

The build output will be in `dist/` directory.

## Deployment

### Static Hosting (Netlify, Vercel, etc.)

1. Build the project:
   ```bash
   pnpm build
   ```

2. Deploy the `dist/` directory to your hosting provider

3. Ensure environment variables are set in your hosting platform:
   - `TRANSPORT_TYPE`
   - `DAILY_ROOM_URL` (if using Daily transport)

### Important Notes

- For WebSocket transport in production, ensure your backend is accessible
- For Daily transport, create rooms dynamically via Daily API
- Configure CORS properly on your backend for cross-origin requests

## Troubleshooting

### Client can't connect to backend

**WebSocket Transport:**
- Ensure backend is running: `cd .. && uv run voice-agent start`
- Check `WS_HOST` and `WS_PORT` in `../env`
- If using WSL, you may need to use the WSL IP instead of `localhost`

**Daily Transport:**
- Verify `DAILY_ROOM_URL` is set in `../env`
- Ensure the Daily room exists and is active
- Check that backend is connected to the same room

### Microphone not working

- Grant microphone permissions in your browser
- Check browser console for errors
- Ensure you're using HTTPS (required for microphone access in production)
- For localhost development, HTTP is fine

### Build errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Clear Vite cache
rm -rf dist node_modules/.vite
pnpm build
```

## Code Quality

This project uses:
- **Biome** for fast linting and formatting
- **TypeScript** with strict mode
- **Tailwind CSS v4** with proper CSS imports

Run quality checks before committing:

```bash
pnpm lint && pnpm typecheck && pnpm build
```

## License

MIT
