import '@pipecat-ai/voice-ui-kit/styles';
import { PipecatClientAudio, PipecatClientProvider } from '@pipecat-ai/client-react';
import { ThemeProvider } from '@pipecat-ai/voice-ui-kit';
import { VoiceInterface } from './components/VoiceInterface';
import { createPipecatClient } from './config/pipecatConfig';
import './index.css';

// Create client instance (outside component to persist across re-renders)
const pipecatClient = createPipecatClient();

export default function App() {
  return (
    <ThemeProvider>
      <PipecatClientProvider client={pipecatClient}>
        <div className="w-full h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
          <VoiceInterface />
          <PipecatClientAudio />
        </div>
      </PipecatClientProvider>
    </ThemeProvider>
  );
}
