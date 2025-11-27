"""Async CSV writer for Daily network statistics.

This module provides a writer class that asynchronously logs network statistics
from Daily transport to CSV files with daily rotation.
"""

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, TypedDict

import aiofiles
from loguru import logger


class NetworkLatestStats(TypedDict, total=False):
    """Latest network statistics from Daily Python SDK.

    See: https://reference-python.daily.co/types.html#networklateststats
    """

    timestamp: float
    receiveBitsPerSecond: float
    sendBitsPerSecond: float
    videoRecvBitsPerSecond: float
    videoSendBitsPerSecond: float
    totalRecvPacketLoss: float
    totalSendPacketLoss: float
    videoRecvPacketLoss: float
    videoSendPacketLoss: float


class NetworkDetailedStats(TypedDict, total=False):
    """Detailed network statistics from Daily Python SDK.

    See: https://reference-python.daily.co/types.html#networkdetailedstats
    """

    latest: NetworkLatestStats
    worstVideoReceivePacketLoss: float
    worstVideoSendPacketLoss: float


class NetworkStats(TypedDict, total=False):
    """Network statistics from Daily Python SDK.

    See: https://reference-python.daily.co/types.html#networkstats
    """

    quality: float
    threshold: str  # "good" | "low" | "veryLow"
    previousThreshold: str  # "good" | "low" | "veryLow"
    stats: NetworkDetailedStats


class NetworkStatsWriter:
    """Async writer for network statistics to CSV files.

    Writes network stats to daily-rotated CSV files with comprehensive metrics
    including bitrate, packet loss, jitter, and round-trip time.
    """

    # CSV column headers matching Daily Python SDK's available fields
    # Note: Python SDK provides fewer fields than JavaScript SDK
    # See: https://reference-python.daily.co/types.html#networkstats
    HEADERS: ClassVar[list[str]] = [
        "timestamp",
        "timestamp_iso",
        # Aggregate bandwidth metrics
        "recv_bits_per_second",
        "send_bits_per_second",
        # Video-specific bandwidth
        "video_recv_bits_per_second",
        "video_send_bits_per_second",
        # Packet loss metrics
        "total_recv_packet_loss",
        "total_send_packet_loss",
        "video_recv_packet_loss",
        "video_send_packet_loss",
        # Worst-case packet loss
        "worst_video_recv_packet_loss",
        "worst_video_send_packet_loss",
        # Legacy quality indicators
        "quality",
        "threshold",
    ]

    def __init__(self, output_dir: Path) -> None:
        """Initialize the network stats writer.

        Args:
            output_dir: Directory where CSV files will be written.
        """
        self._output_dir = output_dir
        self._current_date: str | None = None
        self._current_file_path: Path | None = None

        # Ensure output directory exists
        self._output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Network stats writer initialized: output_dir={output_dir}")

    def _get_file_path(self, date_str: str) -> Path:
        """Get the CSV file path for a specific date.

        Args:
            date_str: Date string in YYYY-MM-DD format.

        Returns:
            Path to the CSV file for that date.
        """
        return self._output_dir / f"network_stats_{date_str}.csv"

    async def _ensure_file_exists(self, file_path: Path) -> None:
        """Ensure the CSV file exists with headers.

        Args:
            file_path: Path to the CSV file.
        """
        if not file_path.exists():
            logger.info(f"Creating new network stats CSV file: {file_path}")
            async with aiofiles.open(file_path, mode="w", newline="") as f:
                await f.write(",".join(self.HEADERS) + "\n")

    def _extract_stats_from_daily_format(self, stats: Mapping[str, Any]) -> dict[str, Any]:
        """Extract and flatten stats from Daily's format.

        Daily Python SDK provides a subset of fields compared to the JavaScript SDK.
        This method extracts only the fields available in the Python SDK.

        Args:
            stats: Network statistics from Daily Python SDK.

        Returns:
            Flattened dictionary with available stat values.
        """
        # Get the current timestamp
        now = datetime.now()
        timestamp = now.timestamp()
        timestamp_iso = now.isoformat()

        # Extract latest stats from nested structure
        latest_stats = stats.get("stats", {}).get("latest", {})
        detailed_stats = stats.get("stats", {})

        # Build the flattened row with only fields available in Python SDK
        row = {
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
            # Aggregate bandwidth (Python SDK provides these)
            "recv_bits_per_second": latest_stats.get("receiveBitsPerSecond"),
            "send_bits_per_second": latest_stats.get("sendBitsPerSecond"),
            # Video-specific bandwidth
            "video_recv_bits_per_second": latest_stats.get("videoRecvBitsPerSecond"),
            "video_send_bits_per_second": latest_stats.get("videoSendBitsPerSecond"),
            # Packet loss metrics
            "total_recv_packet_loss": latest_stats.get("totalRecvPacketLoss"),
            "total_send_packet_loss": latest_stats.get("totalSendPacketLoss"),
            "video_recv_packet_loss": latest_stats.get("videoRecvPacketLoss"),
            "video_send_packet_loss": latest_stats.get("videoSendPacketLoss"),
            # Worst-case packet loss (only video available in Python SDK)
            "worst_video_recv_packet_loss": detailed_stats.get("worstVideoReceivePacketLoss"),
            "worst_video_send_packet_loss": detailed_stats.get("worstVideoSendPacketLoss"),
            # Legacy quality indicators
            "quality": stats.get("quality"),
            "threshold": stats.get("threshold"),
        }

        return row

    async def write_stats(self, stats: Mapping[str, Any]) -> None:
        """Write network statistics to CSV file.

        Automatically handles daily file rotation. Each day gets a new CSV file.

        Args:
            stats: Network statistics dictionary from Daily SDK.
        """
        try:
            # Get current date for file rotation
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Check if we need to rotate to a new file
            if self._current_date != current_date:
                self._current_date = current_date
                self._current_file_path = self._get_file_path(current_date)
                await self._ensure_file_exists(self._current_file_path)
                logger.info(f"Rotated to new network stats file: {self._current_file_path}")

            # Extract and flatten stats
            row = self._extract_stats_from_daily_format(stats)

            # Write the row to CSV
            async with aiofiles.open(self._current_file_path, mode="a", newline="") as f:
                # Build CSV line manually since csv.DictWriter doesn't work well with aiofiles
                values = [str(row.get(header, "")) for header in self.HEADERS]
                line = ",".join(values) + "\n"
                await f.write(line)

        except Exception as e:
            logger.error(f"Error writing network stats to CSV: {e}")
            logger.exception(e)

    async def close(self) -> None:
        """Close the writer and perform any cleanup.

        Currently a no-op but provided for future extensibility.
        """
        logger.info("Network stats writer closed")
