/**
 * Network statistics graph component using recharts for time-series visualization.
 *
 * Displays rolling 10-minute graphs of network metrics including:
 * - Bitrate (send/receive)
 * - Packet loss
 * - Round-trip time (latency)
 * - Jitter
 */

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useNetworkStats } from '../hooks/useNetworkStats';

/**
 * Format timestamp for X-axis display (MM:SS format).
 */
function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    minute: '2-digit',
    second: '2-digit',
  });
}

/**
 * Convert bps to Mbps for graph display.
 */
function bpsToMbps(bps: number | null): number | null {
  return bps !== null ? bps / 1000000 : null;
}

/**
 * Convert packet loss to percentage for graph display.
 */
function toPercentage(value: number | null): number | null {
  return value !== null ? value * 100 : null;
}

/**
 * Negate value for mirrored graph display (send as negative).
 */
function negateValue(value: number | null): number | null {
  return value !== null ? -value : null;
}

/**
 * Component displaying network statistics graphs.
 */
export function NetworkStatsGraph() {
  const { history, isCollecting, error } = useNetworkStats();

  if (error) {
    return (
      <div className="border border-red-300 rounded-lg p-4 bg-red-50">
        <h3 className="text-sm font-semibold text-red-800 mb-2">Network Stats Graph Error</h3>
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }

  if (!isCollecting || history.dataPoints.length === 0) {
    return (
      <div className="border border-gray-300 rounded-lg p-4 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Network Statistics (10min)</h3>
        <p className="text-sm text-gray-500">
          {isCollecting ? 'Collecting data...' : 'Not connected'}
        </p>
      </div>
    );
  }

  // Prepare data for recharts (convert to appropriate units)
  // Send values are negated for mirrored display
  const chartData = history.dataPoints.map((point) => ({
    timestamp: point.timestamp,
    timeLabel: formatTime(point.timestamp),
    // Bitrate in Mbps (send as negative for mirrored display)
    sendBitrate: negateValue(bpsToMbps(point.sendBitsPerSecond)),
    recvBitrate: bpsToMbps(point.recvBitsPerSecond),
    // Packet loss in percentage (send as negative for mirrored display)
    sendPacketLoss: negateValue(toPercentage(point.totalSendPacketLoss)),
    recvPacketLoss: toPercentage(point.totalRecvPacketLoss),
    // Latency in ms
    rtt: point.networkRoundTripTime,
    // Jitter in ms
    audioJitter: point.audioRecvJitter,
    videoJitter: point.videoRecvJitter,
  }));

  return (
    <div className="border border-gray-300 rounded-lg p-4 bg-white shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">
        Network Statistics (Last 10 Minutes)
      </h3>

      <div className="space-y-6">
        {/* Bitrate Graph */}
        <div>
          <h4 className="text-xs font-semibold text-gray-600 mb-2">
            Bandwidth (Mbps) - Mirrored: Send ↓ / Receive ↑
          </h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="timeLabel"
                tick={{ fontSize: 10 }}
                interval="preserveStartEnd"
                minTickGap={50}
              />
              <YAxis tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{ fontSize: 12 }}
                formatter={(value: unknown, name: string) => {
                  if (value === null || value === undefined) return ['N/A', name];
                  const numValue = typeof value === 'number' ? value : Number(value);
                  return [`${Math.abs(numValue).toFixed(2)} Mbps`, name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
              <Line
                type="monotone"
                dataKey="sendBitrate"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="Send"
              />
              <Line
                type="monotone"
                dataKey="recvBitrate"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                name="Receive"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Packet Loss Graph */}
        <div>
          <h4 className="text-xs font-semibold text-gray-600 mb-2">
            Packet Loss (%) - Mirrored: Send ↓ / Receive ↑
          </h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="timeLabel"
                tick={{ fontSize: 10 }}
                interval="preserveStartEnd"
                minTickGap={50}
              />
              <YAxis tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{ fontSize: 12 }}
                formatter={(value: unknown, name: string) => {
                  if (value === null || value === undefined) return ['N/A', name];
                  const numValue = typeof value === 'number' ? value : Number(value);
                  return [`${Math.abs(numValue).toFixed(2)}%`, name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
              <Line
                type="monotone"
                dataKey="sendPacketLoss"
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
                name="Send"
              />
              <Line
                type="monotone"
                dataKey="recvPacketLoss"
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
                name="Receive"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Latency (RTT) Graph */}
        <div>
          <h4 className="text-xs font-semibold text-gray-600 mb-2">Round-Trip Time (ms)</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="timeLabel"
                tick={{ fontSize: 10 }}
                interval="preserveStartEnd"
                minTickGap={50}
              />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ fontSize: 12 }}
                formatter={(value: unknown, name: string) => {
                  if (value === null || value === undefined) return ['N/A', name];
                  const numValue = typeof value === 'number' ? value : Number(value);
                  return [`${numValue.toFixed(0)} ms`, name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line
                type="monotone"
                dataKey="rtt"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={false}
                name="Latency"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Jitter Graph */}
        <div>
          <h4 className="text-xs font-semibold text-gray-600 mb-2">Jitter (ms)</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="timeLabel"
                tick={{ fontSize: 10 }}
                interval="preserveStartEnd"
                minTickGap={50}
              />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{ fontSize: 12 }}
                formatter={(value: unknown, name: string) => {
                  if (value === null || value === undefined) return ['N/A', name];
                  const numValue = typeof value === 'number' ? value : Number(value);
                  return [`${numValue.toFixed(2)} ms`, name];
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Line
                type="monotone"
                dataKey="audioJitter"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={false}
                name="Audio"
              />
              <Line
                type="monotone"
                dataKey="videoJitter"
                stroke="#ec4899"
                strokeWidth={2}
                dot={false}
                name="Video"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Data Point Count */}
      <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-400">
        {history.dataPoints.length} data points / {history.maxPoints} max
      </div>
    </div>
  );
}
