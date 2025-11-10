import { usePipecatClient, usePipecatClientTransportState } from '@pipecat-ai/client-react';
import { env } from '../env';

export function ConnectButton() {
  const client = usePipecatClient();
  const transportState = usePipecatClientTransportState();
  const isConnected = ['connected', 'ready'].includes(transportState);

  const handleClick = async () => {
    if (!client) {
      console.error('Pipecat client is not initialized');
      return;
    }

    try {
      if (isConnected) {
        await client.disconnect();
      } else {
        // Use Pipecat's runner endpoint to start bot and connect
        await client.startBotAndConnect({
          endpoint: `${env.VITE_RUNNER_ENDPOINT}/start`,
          requestData: {
            createDailyRoom: true,
          },
        });
      }
    } catch (error) {
      console.error('Connection error:', error);
    }
  };

  return (
    <div className="controls">
      <button
        type="button"
        className={isConnected ? 'disconnect-btn' : 'connect-btn'}
        onClick={handleClick}
        disabled={!client || ['connecting', 'disconnecting'].includes(transportState)}
      >
        {isConnected ? 'Disconnect' : 'Connect'}
      </button>
    </div>
  );
}
