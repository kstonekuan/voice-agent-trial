import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  // Load env file from parent directory (shared with Python backend)
  const env = loadEnv(mode, '../', '');

  return {
    plugins: [react(), tailwindcss()],
    envDir: '../', // Load .env from parent directory
    server: {
      port: 5173,
      strictPort: false,
      host: true,
    },
    define: {
      // Make env variables available to the app
      'import.meta.env.VITE_TRANSPORT_TYPE': JSON.stringify(env.TRANSPORT_TYPE || 'websocket'),
      'import.meta.env.VITE_WS_HOST': JSON.stringify(env.WS_HOST || 'localhost'),
      'import.meta.env.VITE_WS_PORT': JSON.stringify(env.WS_PORT || '8765'),
      'import.meta.env.VITE_DAILY_ROOM_URL': JSON.stringify(env.DAILY_ROOM_URL || ''),
    },
  };
});
