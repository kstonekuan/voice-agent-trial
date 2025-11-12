#!/usr/bin/env python3
"""
Network Statistics CSV Viewer

A Streamlit-based live dashboard for viewing network statistics CSV files
with auto-refresh, live graphs, statistics summary, and file selection.

Usage:
    streamlit run tools/network_stats_viewer.py
"""

import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Network Stats Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Constants
STATS_DIR = Path("data/network_stats")
DEFAULT_REFRESH_INTERVAL = 2  # seconds


def find_latest_csv_file() -> Path | None:
    """Find the most recent network stats CSV file.

    Returns:
        Path to the latest CSV file, or None if no files found.
    """
    if not STATS_DIR.exists():
        return None

    csv_files = sorted(STATS_DIR.glob("network_stats_*.csv"))
    return csv_files[-1] if csv_files else None


def list_csv_files() -> list[Path]:
    """List all network stats CSV files in reverse chronological order.

    Returns:
        List of Path objects for CSV files.
    """
    if not STATS_DIR.exists():
        return []

    return sorted(STATS_DIR.glob("network_stats_*.csv"), reverse=True)


@st.cache_data(ttl=1)
def load_csv_data(csv_file: Path) -> pd.DataFrame | None:
    """Load and parse CSV file with network statistics.

    Args:
        csv_file: Path to the CSV file.

    Returns:
        DataFrame with parsed data, or None if error.
    """
    try:
        df = pd.read_csv(csv_file)

        # Convert timestamp_iso to datetime
        if "timestamp_iso" in df.columns:
            df["timestamp_iso"] = pd.to_datetime(df["timestamp_iso"])

        # Convert timestamp to datetime if numeric
        if "timestamp" in df.columns and pd.api.types.is_numeric_dtype(df["timestamp"]):
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
        else:
            df["datetime"] = df["timestamp_iso"]

        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None


def calculate_statistics(df: pd.DataFrame, column: str) -> dict:
    """Calculate statistics for a given column.

    Args:
        df: DataFrame containing the data.
        column: Column name to calculate stats for.

    Returns:
        Dictionary with current, min, max, avg, std, median values.
    """
    if column not in df.columns or df[column].isna().all():
        return {
            "current": None,
            "min": None,
            "max": None,
            "avg": None,
            "std": None,
            "median": None,
        }

    series = df[column].dropna()
    if len(series) == 0:
        return {
            "current": None,
            "min": None,
            "max": None,
            "avg": None,
            "std": None,
            "median": None,
        }

    return {
        "current": df[column].iloc[-1] if len(df) > 0 else None,
        "min": series.min(),
        "max": series.max(),
        "avg": series.mean(),
        "std": series.std(),
        "median": series.median(),
    }


def format_bitrate(bps: float | None) -> str:
    """Format bitrate in human-readable format.

    Args:
        bps: Bitrate in bits per second.

    Returns:
        Formatted string (e.g., "1.5 Mbps").
    """
    if bps is None or pd.isna(bps):
        return "N/A"
    return f"{bps / 1_000_000:.2f} Mbps"


def format_percentage(value: float | None) -> str:
    """Format value as percentage.

    Args:
        value: Decimal value (0.01 = 1%).

    Returns:
        Formatted string (e.g., "1.5%").
    """
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value * 100:.2f}%"


def format_milliseconds(ms: float | None) -> str:
    """Format milliseconds value.

    Args:
        ms: Milliseconds value.

    Returns:
        Formatted string (e.g., "45 ms").
    """
    if ms is None or pd.isna(ms):
        return "N/A"
    return f"{ms:.1f} ms"


def get_quality_color(metric_type: str, value: float | None) -> str:
    """Get color based on metric quality thresholds.

    Args:
        metric_type: Type of metric ('rtt', 'packet_loss', 'bitrate').
        value: Metric value.

    Returns:
        Color string ('green', 'yellow', 'red', 'gray').
    """
    if value is None or pd.isna(value):
        return "gray"

    if metric_type == "rtt":
        if value < 100:
            return "green"
        if value < 200:
            return "yellow"
        return "red"
    if metric_type == "packet_loss":
        if value < 0.01:  # < 1%
            return "green"
        if value < 0.05:  # < 5%
            return "yellow"
        return "red"
    if metric_type == "bitrate":
        if value > 1_000_000:  # > 1 Mbps
            return "green"
        if value > 500_000:  # > 0.5 Mbps
            return "yellow"
        return "red"

    return "gray"


def create_bandwidth_graph(df: pd.DataFrame) -> go.Figure:
    """Create bandwidth over time graph.

    Args:
        df: DataFrame with network stats.

    Returns:
        Plotly figure object.
    """
    fig = go.Figure()

    # Send bitrate (negative values for mirrored display)
    if "send_bits_per_second" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=-df["send_bits_per_second"] / 1_000_000,
                mode="lines",
                name="Send",
                line={"color": "#3b82f6", "width": 2},
            )
        )

    # Receive bitrate (positive values)
    if "recv_bits_per_second" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["recv_bits_per_second"] / 1_000_000,
                mode="lines",
                name="Receive",
                line={"color": "#10b981", "width": 2},
            )
        )

    # Add zero reference line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title="Network Bandwidth (Mirrored: Send ↓ / Receive ↑)",
        xaxis_title="Time",
        yaxis_title="Mbps",
        hovermode="x unified",
        height=400,
    )

    return fig


def create_packet_loss_graph(df: pd.DataFrame) -> go.Figure:
    """Create packet loss over time graph.

    Args:
        df: DataFrame with network stats.

    Returns:
        Plotly figure object.
    """
    fig = go.Figure()

    # Send packet loss (negative values for mirrored display)
    if "total_send_packet_loss" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=-df["total_send_packet_loss"] * 100,
                mode="lines",
                name="Send",
                line={"color": "#ef4444", "width": 2},
            )
        )

    # Receive packet loss (positive values)
    if "total_recv_packet_loss" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["total_recv_packet_loss"] * 100,
                mode="lines",
                name="Receive",
                line={"color": "#f97316", "width": 2},
            )
        )

    # Add zero reference line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title="Packet Loss (Mirrored: Send ↓ / Receive ↑)",
        xaxis_title="Time",
        yaxis_title="Percentage (%)",
        hovermode="x unified",
        height=400,
    )

    return fig


def create_latency_graph(df: pd.DataFrame) -> go.Figure:
    """Create RTT (latency) over time graph.

    Args:
        df: DataFrame with network stats.

    Returns:
        Plotly figure object.
    """
    fig = go.Figure()

    # Current RTT
    if "network_round_trip_time" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["network_round_trip_time"],
                mode="lines",
                name="Current RTT",
                line={"color": "#8b5cf6", "width": 2},
            )
        )

    # Average RTT
    if "average_network_round_trip_time" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["average_network_round_trip_time"],
                mode="lines",
                name="Average RTT",
                line={"color": "#8b5cf6", "width": 2, "dash": "dash"},
            )
        )

    fig.update_layout(
        title="Round-Trip Time (Latency)",
        xaxis_title="Time",
        yaxis_title="Milliseconds",
        hovermode="x unified",
        height=300,
    )

    return fig


def create_jitter_graph(df: pd.DataFrame) -> go.Figure:
    """Create jitter over time graph.

    Args:
        df: DataFrame with network stats.

    Returns:
        Plotly figure object.
    """
    fig = go.Figure()

    # Audio jitter
    if "audio_recv_jitter" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["audio_recv_jitter"],
                mode="lines",
                name="Audio",
                line={"color": "#06b6d4", "width": 2},
            )
        )

    # Video jitter
    if "video_recv_jitter" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["video_recv_jitter"],
                mode="lines",
                name="Video",
                line={"color": "#ec4899", "width": 2},
            )
        )

    fig.update_layout(
        title="Jitter",
        xaxis_title="Time",
        yaxis_title="Milliseconds",
        hovermode="x unified",
        height=300,
    )

    return fig


def main() -> None:
    """Main Streamlit application."""
    # Initialize session state
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = True
    if "refresh_interval" not in st.session_state:
        st.session_state.refresh_interval = DEFAULT_REFRESH_INTERVAL
    if "last_mtime" not in st.session_state:
        st.session_state.last_mtime = 0

    # Sidebar
    st.sidebar.title("📊 Network Stats Viewer")

    # Check if stats directory exists
    csv_files = list_csv_files()

    if not csv_files:
        st.error(f"No network stats files found in {STATS_DIR}/")
        st.info("Start the voice agent bot to generate network statistics.")
        return

    # File selector
    file_options = [f.name for f in csv_files]
    selected_file_name = st.sidebar.selectbox(
        "Select CSV file:",
        file_options,
        index=0,  # Latest first
    )
    selected_file = STATS_DIR / selected_file_name

    # Auto-refresh toggle
    st.session_state.auto_refresh = st.sidebar.toggle(
        "Auto-refresh", value=st.session_state.auto_refresh
    )

    # Refresh interval
    if st.session_state.auto_refresh:
        st.session_state.refresh_interval = st.sidebar.slider(
            "Refresh interval (seconds)", min_value=1, max_value=10, value=DEFAULT_REFRESH_INTERVAL
        )

    # File info
    st.sidebar.divider()
    st.sidebar.caption(f"**File:** {selected_file.name}")

    if selected_file.exists():
        mtime = selected_file.stat().st_mtime
        st.sidebar.caption(
            f"**Modified:** {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Check if file changed
        if mtime > st.session_state.last_mtime:
            st.session_state.last_mtime = mtime
            load_csv_data.clear()  # Clear cache to reload data

    # Load data
    df = load_csv_data(selected_file)

    if df is None or len(df) == 0:
        st.warning("CSV file is empty or couldn't be loaded. Waiting for data...")
        return

    # Main content
    st.title("Network Statistics Dashboard")

    # Summary statistics (top row)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Quality/threshold (available in Python SDK)
        quality = df["quality"].iloc[-1] if "quality" in df.columns and len(df) > 0 else None
        threshold = df["threshold"].iloc[-1] if "threshold" in df.columns and len(df) > 0 else "N/A"
        st.metric(
            "Network Quality",
            f"{quality:.0f}/100" if quality is not None else "N/A",
            delta=f"Status: {threshold}",
        )

    with col2:
        loss_stats = calculate_statistics(df, "total_recv_packet_loss")
        st.metric(
            "Packet Loss (Recv)",
            format_percentage(loss_stats["current"]),
            delta=f"Avg: {format_percentage(loss_stats['avg'])}",
        )

    with col3:
        recv_stats = calculate_statistics(df, "recv_bits_per_second")
        st.metric(
            "Receive Bitrate",
            format_bitrate(recv_stats["current"]),
            delta=f"Avg: {format_bitrate(recv_stats['avg'])}",
        )

    with col4:
        send_stats = calculate_statistics(df, "send_bits_per_second")
        st.metric(
            "Send Bitrate",
            format_bitrate(send_stats["current"]),
            delta=f"Avg: {format_bitrate(send_stats['avg'])}",
        )

    st.divider()

    # Graphs - Only show available metrics from Python SDK
    st.plotly_chart(create_bandwidth_graph(df), width="stretch")
    st.plotly_chart(create_packet_loss_graph(df), width="stretch")

    # Note: Latency (RTT) and Jitter are NOT available in Daily Python SDK
    st.info(
        "📝 **Note:** Audio metrics, jitter, and round-trip time (RTT) are not available in the "
        "Daily Python SDK. These metrics are only available in the frontend (Daily JavaScript SDK)."
    )

    st.divider()

    # Detailed statistics (expandable) - Only show fields available in Python SDK
    with st.expander("📈 Detailed Statistics", expanded=False):
        stat_col1, stat_col2 = st.columns(2)

        with stat_col1:
            st.subheader("Bitrate Statistics")
            # Only fields available in Daily Python SDK
            for col in [
                "recv_bits_per_second",
                "send_bits_per_second",
                "video_recv_bits_per_second",
                "video_send_bits_per_second",
            ]:
                if col in df.columns:
                    stats = calculate_statistics(df, col)
                    st.markdown(
                        f"**{col.replace('_', ' ').title()}**  \n"
                        f"Current: {format_bitrate(stats['current'])} | "
                        f"Avg: {format_bitrate(stats['avg'])} | "
                        f"Min: {format_bitrate(stats['min'])} | "
                        f"Max: {format_bitrate(stats['max'])}"
                    )

        with stat_col2:
            st.subheader("Packet Loss Statistics")
            # Only fields available in Daily Python SDK
            for col in [
                "total_recv_packet_loss",
                "total_send_packet_loss",
                "video_recv_packet_loss",
                "video_send_packet_loss",
                "worst_video_recv_packet_loss",
                "worst_video_send_packet_loss",
            ]:
                if col in df.columns:
                    stats = calculate_statistics(df, col)
                    st.markdown(
                        f"**{col.replace('_', ' ').title()}**  \n"
                        f"Current: {format_percentage(stats['current'])} | "
                        f"Avg: {format_percentage(stats['avg'])} | "
                        f"Min: {format_percentage(stats['min'])} | "
                        f"Max: {format_percentage(stats['max'])}"
                    )

    # Raw data table
    with st.expander("📋 Raw Data Table", expanded=False):
        st.dataframe(df, width="stretch", height=400)

        # Download button
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"network_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time.sleep(st.session_state.refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
