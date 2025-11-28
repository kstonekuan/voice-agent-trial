# Voice Dictation

A desktop voice dictation tool with global hotkeys. Speak and your words are typed wherever your cursor is.

Built with Electron, React, Pipecat, and Tailwind CSS.

## Features

- Global hotkey activation
- Real-time speech-to-text transcription
- Automatic text typing at cursor position
- System tray integration with overlay UI

## Development

```bash
pnpm install
pnpm dev
```

## Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start development server |
| `pnpm build` | Build for production |
| `pnpm lint` | Lint and format code |
| `pnpm typecheck` | Run TypeScript type checking |
| `pnpm check` | Run lint + typecheck |

## Building

### Windows

```bash
pnpm build:win
```

### macOS

```bash
pnpm build:mac
```

### Linux

```bash
pnpm build:linux
```

### Cross-compile Windows build from Linux/macOS

```bash
docker run --rm -ti \
 --env-file <(env | grep -iE 'DEBUG|NODE_|ELECTRON_|YARN_|NPM_|CI|CIRCLE|TRAVIS_TAG|TRAVIS|TRAVIS_REPO_|TRAVIS_BUILD_|TRAVIS_BRANCH|TRAVIS_PULL_REQUEST_|APPVEYOR_|CSC_|GH_|GITHUB_|BT_|AWS_|STRIP|BUILD_') \
 --env ELECTRON_CACHE="/root/.cache/electron" \
 --env ELECTRON_BUILDER_CACHE="/root/.cache/electron-builder" \
 -v ${PWD}:/project \
 -v ${PWD##*/}-node-modules:/project/node_modules \
 -v ~/.cache/electron:/root/.cache/electron \
 -v ~/.cache/electron-builder:/root/.cache/electron-builder \
 electronuserland/builder:wine \
 /bin/bash -c "npm install && npm run build:win"
```