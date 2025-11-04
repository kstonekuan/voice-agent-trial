import { PipecatClient } from '@pipecat-ai/client-js';
import { PipecatClientProvider } from '@pipecat-ai/client-react';
import { DailyTransport } from '@pipecat-ai/daily-transport';
import type { PropsWithChildren } from 'react';

const client = new PipecatClient({
  transport: new DailyTransport(),
  enableMic: true,
  enableCam: false,
});

export function DailyProvider({ children }: PropsWithChildren) {
  return <PipecatClientProvider client={client}>{children}</PipecatClientProvider>;
}
