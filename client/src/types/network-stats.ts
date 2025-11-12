/**
 * Network statistics types matching Daily.js getNetworkStats() return value.
 *
 * Note: Daily JavaScript SDK provides MORE fields than the Python SDK.
 * The JS SDK includes: audio metrics, jitter, RTT, networkState/networkStateReasons.
 * The Python SDK only provides: bandwidth, packet loss, quality/threshold.
 *
 * @see https://docs.daily.co/reference/daily-js/instance-methods/get-network-stats
 * @see https://reference-python.daily.co/types.html#networkstats
 */

/**
 * Latest network statistics snapshot from Daily.
 * Values are updated approximately every 2 seconds.
 */
export interface NetworkStatsLatest {
  timestamp: number;
  recvBitsPerSecond: number | null;
  sendBitsPerSecond: number | null;
  availableOutgoingBitrate: number | null;
  networkRoundTripTime: number | null;
  videoRecvBitsPerSecond: number | null;
  videoSendBitsPerSecond: number | null;
  audioRecvBitsPerSecond: number | null;
  audioSendBitsPerSecond: number | null;
  videoRecvPacketLoss: number | null;
  videoSendPacketLoss: number | null;
  audioRecvPacketLoss: number | null;
  audioSendPacketLoss: number | null;
  totalSendPacketLoss: number | null;
  totalRecvPacketLoss: number | null;
  videoRecvJitter: number | null;
  videoSendJitter: number | null;
  audioRecvJitter: number | null;
  audioSendJitter: number | null;
}

/**
 * Complete network statistics data including latest, worst-case, and average values.
 */
export interface NetworkStatsData {
  latest: NetworkStatsLatest;
  worstVideoRecvPacketLoss: number;
  worstVideoSendPacketLoss: number;
  worstAudioRecvPacketLoss: number;
  worstAudioSendPacketLoss: number;
  worstVideoRecvJitter: number;
  worstVideoSendJitter: number;
  worstAudioRecvJitter: number;
  worstAudioSendJitter: number;
  averageNetworkRoundTripTime: number;
}

/**
 * Network quality state reasons indicating specific issues.
 */
export type NetworkStateReason =
  | 'sendPacketLoss'
  | 'recvPacketLoss'
  | 'roundTripTime'
  | 'availableOutgoingBitrate';

/**
 * Discriminated union for network state and reasons.
 * When state is 'good' or 'unknown', reasons will be empty array.
 * When state is 'warning' or 'bad', reasons may contain specific issues.
 */
export type NetworkState =
  | {
      /** Network quality is good or unknown */
      networkState: 'good' | 'unknown';
    }
  | {
      /** Network quality has issues */
      networkState: 'warning' | 'bad';
      /** Specific reasons for network quality degradation */
      networkStateReasons: NetworkStateReason[];
    };

/**
 * Complete network statistics object returned by Daily.js getNetworkStats().
 */
export type NetworkStats = NetworkState & {
  /** Detailed statistics or empty object if not available */
  stats: Record<string, never> | NetworkStatsData;
  /** @deprecated Use networkState instead */
  threshold?: 'good' | 'low' | 'very-low';
  /** @deprecated Use networkStateReasons instead */
  quality?: number;
};

/**
 * Time-series data point for network stats history.
 */
export interface NetworkStatsDataPoint {
  timestamp: number;
  recvBitsPerSecond: number | null;
  sendBitsPerSecond: number | null;
  videoRecvPacketLoss: number | null;
  videoSendPacketLoss: number | null;
  audioRecvPacketLoss: number | null;
  audioSendPacketLoss: number | null;
  totalRecvPacketLoss: number | null;
  totalSendPacketLoss: number | null;
  networkRoundTripTime: number | null;
  videoRecvJitter: number | null;
  videoSendJitter: number | null;
  audioRecvJitter: number | null;
  audioSendJitter: number | null;
}

/**
 * History of network stats for time-series visualization.
 */
export interface NetworkStatsHistory {
  dataPoints: NetworkStatsDataPoint[];
  startTime: number;
  endTime: number;
  maxPoints: number;
}

/**
 * Network topology type returned by Daily.js getNetworkTopology().
 * - 'peer': Peer-to-peer direct connection
 * - 'sfu': Connection through Selective Forwarding Unit (Daily's media server)
 */
export type NetworkTopology = 'peer' | 'sfu' | null;
