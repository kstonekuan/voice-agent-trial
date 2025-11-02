import { PipecatClient } from '@pipecat-ai/client-js';
import { DailyTransport } from '@pipecat-ai/daily-transport';
import { ProtobufFrameSerializer, WebSocketTransport } from '@pipecat-ai/websocket-transport';

// Get transport type from environment (same as Python backend)
const transportType = import.meta.env.VITE_TRANSPORT_TYPE || 'websocket';
const wsHost = import.meta.env.VITE_WS_HOST || 'localhost';
const wsPort = import.meta.env.VITE_WS_PORT || '8765';
const dailyRoomUrl = import.meta.env.VITE_DAILY_ROOM_URL || '';

export interface PipecatConfig {
  transportType: 'websocket' | 'daily';
  wsUrl?: string;
  dailyRoomUrl?: string;
}

/**
 * Get Pipecat configuration from shared .env file
 */
export function getPipecatConfig(): PipecatConfig {
  const config: PipecatConfig = {
    transportType: transportType as 'websocket' | 'daily',
  };

  if (transportType === 'websocket') {
    config.wsUrl = `ws://${wsHost}:${wsPort}/ws`;
  } else if (transportType === 'daily') {
    config.dailyRoomUrl = dailyRoomUrl;
  }

  return config;
}

/**
 * Create Pipecat client with transport based on shared configuration
 */
export function createPipecatClient(): PipecatClient {
  const config = getPipecatConfig();

  let transport: WebSocketTransport | DailyTransport;

  if (config.transportType === 'websocket') {
    transport = new WebSocketTransport({
      serializer: new ProtobufFrameSerializer(),
      recorderSampleRate: 16000,
      playerSampleRate: 24000,
    });
  } else if (config.transportType === 'daily') {
    transport = new DailyTransport();
  } else {
    throw new Error(`Invalid transport type: ${config.transportType}`);
  }

  return new PipecatClient({
    transport,
    enableMic: true,
    enableCam: false,
    callbacks: {
      onConnected: () => console.log('[Pipecat] Connected'),
      onDisconnected: () => console.log('[Pipecat] Disconnected'),
      onBotReady: () => console.log('[Pipecat] Bot ready'),
      onTransportStateChanged: (state) => console.log('[Pipecat] Transport state:', state),
    },
  });
}

/**
 * Get connection parameters based on transport type
 */
export function getConnectionParams(): Record<string, string> {
  const config = getPipecatConfig();

  if (config.transportType === 'websocket' && config.wsUrl) {
    return { wsUrl: config.wsUrl };
  }

  if (config.transportType === 'daily' && config.dailyRoomUrl) {
    return { url: config.dailyRoomUrl };
  }

  throw new Error('Missing connection configuration');
}
