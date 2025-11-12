/**
 * Custom hook for polling Daily network statistics.
 *
 * This hook polls the Daily CallObject's getNetworkStats() method at regular intervals
 * and maintains a rolling history of network statistics for visualization.
 */

import { usePipecatClient, usePipecatClientTransportState } from '@pipecat-ai/client-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import type {
  NetworkStats,
  NetworkStatsData,
  NetworkStatsDataPoint,
  NetworkStatsHistory,
  NetworkTopology,
} from '../types/network-stats';

const POLL_INTERVAL_MS = 15000; // 15 seconds (Daily.js recommended interval)
const TIME_WINDOW_MS = 10 * 60 * 1000; // 10 minutes
const MAX_DATA_POINTS = Math.ceil(TIME_WINDOW_MS / POLL_INTERVAL_MS); // ~40 points

/**
 * Hook return type containing current stats and history.
 */
export interface UseNetworkStatsReturn {
  currentStats: NetworkStats | null;
  history: NetworkStatsHistory;
  topology: NetworkTopology;
  isCollecting: boolean;
  error: string | null;
}

/**
 * Hook to collect and manage Daily network statistics.
 *
 * Automatically starts polling when connected and stops when disconnected.
 * Maintains a rolling 10-minute history of stats for visualization.
 *
 * @returns Current stats, historical data, collection state, and any errors
 */
export function useNetworkStats(): UseNetworkStatsReturn {
  const client = usePipecatClient();
  const transportState = usePipecatClientTransportState();

  const [currentStats, setCurrentStats] = useState<NetworkStats | null>(null);
  const [history, setHistory] = useState<NetworkStatsHistory>({
    dataPoints: [],
    startTime: 0,
    endTime: 0,
    maxPoints: MAX_DATA_POINTS,
  });
  const [topology, setTopology] = useState<NetworkTopology>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCollecting, setIsCollecting] = useState(false);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const extractDataPoint = useCallback((stats: NetworkStats): NetworkStatsDataPoint | null => {
    // Check if stats has data (not empty object)
    if (!stats.stats || Object.keys(stats.stats).length === 0) {
      return null;
    }

    const statsData = stats.stats as NetworkStatsData;
    const latest = statsData.latest;

    return {
      timestamp: latest.timestamp || Date.now(),
      recvBitsPerSecond: latest.recvBitsPerSecond,
      sendBitsPerSecond: latest.sendBitsPerSecond,
      videoRecvPacketLoss: latest.videoRecvPacketLoss,
      videoSendPacketLoss: latest.videoSendPacketLoss,
      audioRecvPacketLoss: latest.audioRecvPacketLoss,
      audioSendPacketLoss: latest.audioSendPacketLoss,
      totalRecvPacketLoss: latest.totalRecvPacketLoss,
      totalSendPacketLoss: latest.totalSendPacketLoss,
      networkRoundTripTime: latest.networkRoundTripTime,
      videoRecvJitter: latest.videoRecvJitter,
      videoSendJitter: latest.videoSendJitter,
      audioRecvJitter: latest.audioRecvJitter,
      audioSendJitter: latest.audioSendJitter,
    };
  }, []);

  const fetchNetworkTopology = useCallback(async () => {
    if (!client || transportState !== 'ready') {
      return;
    }

    try {
      // Access the Daily transport's dailyCallClient
      const transport = client.transport as unknown;

      // Check if this is a Daily transport with getNetworkTopology method
      if (
        !transport ||
        typeof transport !== 'object' ||
        !('dailyCallClient' in transport) ||
        typeof (transport as { dailyCallClient?: { getNetworkTopology?: unknown } }).dailyCallClient
          ?.getNetworkTopology !== 'function'
      ) {
        return;
      }

      // Get network topology from Daily
      const dailyClient = (
        transport as {
          dailyCallClient: { getNetworkTopology: () => { topology: NetworkTopology } };
        }
      ).dailyCallClient;
      const result = dailyClient.getNetworkTopology();

      setTopology(result.topology);
    } catch (err) {
      console.error('Error fetching network topology:', err);
      // Don't set error state for topology - it's not critical
    }
  }, [client, transportState]);

  const pollNetworkStats = useCallback(async () => {
    if (!client || transportState !== 'ready') {
      return;
    }

    try {
      // Access the Daily transport's dailyCallClient
      const transport = client.transport as unknown;

      // Check if this is a Daily transport with getNetworkStats method
      if (
        !transport ||
        typeof transport !== 'object' ||
        !('dailyCallClient' in transport) ||
        typeof (transport as { dailyCallClient?: { getNetworkStats?: unknown } }).dailyCallClient
          ?.getNetworkStats !== 'function'
      ) {
        setError('Network stats not available for this transport type');
        return;
      }

      // Get network stats from Daily
      const dailyClient = (
        transport as { dailyCallClient: { getNetworkStats: () => Promise<NetworkStats> } }
      ).dailyCallClient;
      const stats: NetworkStats = await dailyClient.getNetworkStats();

      setCurrentStats(stats);
      setError(null);

      // Extract data point and add to history
      const dataPoint = extractDataPoint(stats);
      if (dataPoint) {
        setHistory((prev) => {
          const newDataPoints = [...prev.dataPoints, dataPoint];

          // Remove old data points outside the time window
          const cutoffTime = Date.now() - TIME_WINDOW_MS;
          const filteredPoints = newDataPoints.filter((point) => point.timestamp >= cutoffTime);

          // Limit to max points
          const limitedPoints = filteredPoints.slice(-MAX_DATA_POINTS);

          return {
            ...prev,
            dataPoints: limitedPoints,
            startTime: limitedPoints.length > 0 ? limitedPoints[0].timestamp : 0,
            endTime: dataPoint.timestamp,
          };
        });
      }
    } catch (err) {
      console.error('Error fetching network stats:', err);
      setError(err instanceof Error ? err.message : 'Unknown error fetching network stats');
    }
  }, [client, transportState, extractDataPoint]);

  useEffect(() => {
    // Only collect stats when connected
    if (transportState === 'ready') {
      setIsCollecting(true);

      // Fetch topology immediately at connection start
      fetchNetworkTopology();

      // Fetch stats immediately
      pollNetworkStats();

      // Then poll at regular intervals
      intervalRef.current = setInterval(pollNetworkStats, POLL_INTERVAL_MS);
    } else {
      setIsCollecting(false);

      // Reset topology when disconnected
      setTopology(null);

      // Clear interval when not connected
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [transportState, pollNetworkStats, fetchNetworkTopology]);

  return {
    currentStats,
    history,
    topology,
    isCollecting,
    error,
  };
}
