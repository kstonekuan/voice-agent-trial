import { PipecatClient } from '@pipecat-ai/client-js';
import { PipecatClientProvider } from '@pipecat-ai/client-react';
import { SmallWebRTCTransport } from '@pipecat-ai/small-webrtc-transport';
import type { PropsWithChildren } from 'react';

const client = new PipecatClient({
  transport: new SmallWebRTCTransport(),
  enableMic: true,
  enableCam: false,
});

export function SmallWebRTCProvider({ children }: PropsWithChildren) {
  return <PipecatClientProvider client={client}>{children}</PipecatClientProvider>;
}
