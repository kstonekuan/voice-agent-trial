import {
  PipecatClientAudio,
  PipecatClientVideo,
  usePipecatClientTransportState,
} from '@pipecat-ai/client-react';
import { ConnectButton } from '../components/ConnectButton';
import { DebugDisplay } from '../components/DebugDisplay';
import { StatusDisplay } from '../components/StatusDisplay';
import { SmallWebRTCProvider } from '../providers/SmallWebRTCProvider';
import '../App.css';

function BotVideo() {
  const transportState = usePipecatClientTransportState();
  const isConnected = transportState !== 'disconnected';

  return (
    <div className="bot-container">
      <div className="video-container">
        {isConnected && <PipecatClientVideo participant="bot" fit="cover" />}
      </div>
    </div>
  );
}

function WebRTCPageContent() {
  return (
    <div className="app">
      <div className="status-bar">
        <StatusDisplay />
        <ConnectButton />
      </div>

      <div className="main-content">
        <BotVideo />
      </div>

      <DebugDisplay />
      <PipecatClientAudio />
    </div>
  );
}

export function WebRTCPage() {
  return (
    <SmallWebRTCProvider>
      <WebRTCPageContent />
    </SmallWebRTCProvider>
  );
}
