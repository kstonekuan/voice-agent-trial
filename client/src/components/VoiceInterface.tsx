import { usePipecatClient } from '@pipecat-ai/client-react';
import { useState } from 'react';
import { getConnectionParams, getPipecatConfig } from '../config/pipecatConfig';

export function VoiceInterface() {
  const pipecatClient = usePipecatClient();
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const config = getPipecatConfig();

  const handleConnect = async () => {
    if (!pipecatClient) {
      setError('Pipecat client not initialized');
      return;
    }

    try {
      setIsConnecting(true);
      setError(null);
      const params = getConnectionParams();
      await pipecatClient.connect(params);
      setIsConnected(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect');
      console.error('Connection error:', err);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    if (!pipecatClient) {
      setError('Pipecat client not initialized');
      return;
    }

    try {
      await pipecatClient.disconnect();
      setIsConnected(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to disconnect');
      console.error('Disconnection error:', err);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center gap-8 p-8 max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-5xl font-bold text-white mb-4">Voice Agent</h1>
        <p className="text-xl text-purple-200 mb-2">
          Real-time AI assistant with ultra-low latency
        </p>
        <div className="inline-block bg-purple-800/30 backdrop-blur-sm rounded-full px-4 py-2 border border-purple-500/30">
          <p className="text-sm text-purple-300">
            Transport: <span className="font-semibold text-purple-100">{config.transportType}</span>
          </p>
        </div>
      </div>

      {/* Connection Status */}
      <div className="flex items-center gap-3 bg-slate-800/50 backdrop-blur-sm rounded-2xl px-6 py-4 border border-slate-700/50">
        <div
          className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
          }`}
        />
        <span className="text-white font-medium">{isConnected ? 'Connected' : 'Disconnected'}</span>
      </div>

      {/* Error Display */}
      {error && (
        <div className="w-full bg-red-900/30 backdrop-blur-sm border border-red-500/30 rounded-2xl px-6 py-4">
          <p className="text-red-200 text-center">
            <span className="font-semibold">Error:</span> {error}
          </p>
        </div>
      )}

      {/* Control Button */}
      <button
        type="button"
        onClick={isConnected ? handleDisconnect : handleConnect}
        disabled={isConnecting}
        className={`
          px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-200
          ${
            isConnected
              ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/50'
              : 'bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-500/50'
          }
          ${isConnecting ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}
          disabled:hover:scale-100
        `}
      >
        {isConnecting ? 'Connecting...' : isConnected ? 'Disconnect' : 'Start Conversation'}
      </button>

      {/* Instructions */}
      {isConnected && (
        <div className="text-center space-y-2 animate-fade-in">
          <p className="text-green-300 font-medium">🎤 Microphone active - Start speaking!</p>
          <p className="text-sm text-purple-300">
            The AI assistant will respond in real-time with voice
          </p>
        </div>
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mt-8">
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-slate-700/30">
          <div className="text-2xl mb-2">🎤</div>
          <h3 className="text-white font-semibold mb-1">Fast STT</h3>
          <p className="text-sm text-slate-300">Cartesia Ink-Whisper</p>
        </div>
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-slate-700/30">
          <div className="text-2xl mb-2">🧠</div>
          <h3 className="text-white font-semibold mb-1">Smart LLM</h3>
          <p className="text-sm text-slate-300">Cerebras Llama 3.3</p>
        </div>
        <div className="bg-slate-800/30 backdrop-blur-sm rounded-xl p-4 border border-slate-700/30">
          <div className="text-2xl mb-2">🔊</div>
          <h3 className="text-white font-semibold mb-1">Natural TTS</h3>
          <p className="text-sm text-slate-300">ElevenLabs Flash</p>
        </div>
      </div>

      {/* Configuration Info */}
      <div className="text-center text-xs text-slate-400 mt-4">
        {config.transportType === 'websocket' && config.wsUrl && <p>WebSocket: {config.wsUrl}</p>}
        {config.transportType === 'daily' && config.dailyRoomUrl && (
          <p>Daily Room: {config.dailyRoomUrl}</p>
        )}
      </div>
    </div>
  );
}
