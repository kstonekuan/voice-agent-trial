/**
 * Network statistics display component showing current network quality metrics.
 *
 * Displays real-time network statistics including:
 * - Overall network quality status
 * - Bitrate (send/receive)
 * - Packet loss
 * - Round-trip time (latency)
 * - Jitter
 */

import { useNetworkStats } from '../hooks/useNetworkStats';
import type { NetworkStatsData } from '../types/network-stats';

/**
 * Format bitrate value for display (converts to Mbps if > 1000000 bps).
 */
function formatBitrate(bps: number | null): string {
  if (bps === null) return 'N/A';
  if (bps >= 1000000) {
    return `${(bps / 1000000).toFixed(2)} Mbps`;
  }
  return `${(bps / 1000).toFixed(0)} Kbps`;
}

/**
 * Format percentage value for display.
 */
function formatPercentage(value: number | null): string {
  if (value === null) return 'N/A';
  return `${(value * 100).toFixed(2)}%`;
}

/**
 * Format milliseconds value for display.
 */
function formatMilliseconds(ms: number | null): string {
  if (ms === null) return 'N/A';
  return `${ms.toFixed(0)} ms`;
}

/**
 * Get color class based on network quality state.
 */
function getNetworkStateColor(state: string): string {
  switch (state) {
    case 'good':
      return 'text-green-600';
    case 'warning':
      return 'text-yellow-600';
    case 'bad':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
}

/**
 * Get status emoji based on network quality state.
 */
function getNetworkStateEmoji(state: string): string {
  switch (state) {
    case 'good':
      return '✓';
    case 'warning':
      return '⚠';
    case 'bad':
      return '✗';
    default:
      return '?';
  }
}

/**
 * Format topology value for display.
 */
function formatTopology(topology: string | null): string {
  if (!topology) return 'Unknown';
  switch (topology) {
    case 'peer':
      return 'Peer-to-Peer';
    case 'sfu':
      return 'SFU (Server)';
    default:
      return topology;
  }
}

/**
 * Component displaying current network statistics.
 */
export function NetworkStats() {
  const { currentStats, topology, isCollecting, error } = useNetworkStats();

  if (error) {
    return (
      <div className="border border-red-300 rounded-lg p-4 bg-red-50">
        <h3 className="text-sm font-semibold text-red-800 mb-2">Network Stats Error</h3>
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  if (!isCollecting || !currentStats) {
    return (
      <div className="border border-gray-300 rounded-lg p-4 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Network Statistics</h3>
        <p className="text-sm text-gray-500">Not connected</p>
      </div>
    );
  }

  const hasStats = currentStats.stats && Object.keys(currentStats.stats).length > 0;
  const statsData = hasStats ? (currentStats.stats as NetworkStatsData) : null;
  const latest = statsData?.latest;

  const networkStateColor = getNetworkStateColor(currentStats.networkState);
  const networkStateEmoji = getNetworkStateEmoji(currentStats.networkState);

  return (
    <div className="border border-gray-300 rounded-lg p-4 bg-white shadow-sm">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Network Statistics</h3>

        {/* Network Quality Status */}
        <div className="flex items-center gap-2 mb-3">
          <span className={`text-lg font-bold ${networkStateColor}`}>
            {networkStateEmoji} {currentStats.networkState.toUpperCase()}
          </span>
          {(currentStats.networkState === 'warning' || currentStats.networkState === 'bad') &&
            currentStats.networkStateReasons.length > 0 && (
              <span className="text-xs text-gray-500">
                ({currentStats.networkStateReasons.join(', ')})
              </span>
            )}
        </div>

        {/* Connection Topology */}
        <div className="text-xs text-gray-600 mb-2">
          <span className="font-semibold">Connection Type:</span>{' '}
          <span className="font-mono">{formatTopology(topology)}</span>
        </div>
      </div>

      {statsData && latest ? (
        <div className="grid grid-cols-2 gap-4 text-sm">
          {/* Bitrate Section */}
          <div className="col-span-2">
            <h4 className="font-semibold text-gray-600 mb-2">Bandwidth</h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-500">Send:</span>
                <span className="ml-2 font-mono">{formatBitrate(latest.sendBitsPerSecond)}</span>
              </div>
              <div>
                <span className="text-gray-500">Receive:</span>
                <span className="ml-2 font-mono">{formatBitrate(latest.recvBitsPerSecond)}</span>
              </div>
            </div>
          </div>

          {/* Packet Loss Section */}
          <div className="col-span-2">
            <h4 className="font-semibold text-gray-600 mb-2">Packet Loss</h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-500">Send:</span>
                <span className="ml-2 font-mono">
                  {formatPercentage(latest.totalSendPacketLoss)}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Receive:</span>
                <span className="ml-2 font-mono">
                  {formatPercentage(latest.totalRecvPacketLoss)}
                </span>
              </div>
            </div>
          </div>

          {/* Latency Section */}
          <div>
            <h4 className="font-semibold text-gray-600 mb-2">Latency (RTT)</h4>
            <div className="text-xs">
              <span className="font-mono">{formatMilliseconds(latest.networkRoundTripTime)}</span>
            </div>
          </div>

          {/* Jitter Section */}
          <div>
            <h4 className="font-semibold text-gray-600 mb-2">Jitter</h4>
            <div className="text-xs space-y-1">
              <div>
                <span className="text-gray-500">Audio:</span>
                <span className="ml-2 font-mono">{formatMilliseconds(latest.audioRecvJitter)}</span>
              </div>
              <div>
                <span className="text-gray-500">Video:</span>
                <span className="ml-2 font-mono">{formatMilliseconds(latest.videoRecvJitter)}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-500">Waiting for statistics...</p>
      )}

      {/* Last Update Time */}
      {latest?.timestamp && (
        <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-400">
          Last updated: {new Date(latest.timestamp).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}
