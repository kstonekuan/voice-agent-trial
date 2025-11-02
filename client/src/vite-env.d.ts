/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_TRANSPORT_TYPE: string;
  readonly VITE_WS_HOST: string;
  readonly VITE_WS_PORT: string;
  readonly VITE_DAILY_ROOM_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
