# Contributing Network Stats Support to Pipecat DailyTransport

This guide documents how to contribute comprehensive network statistics support to the Pipecat Daily transport wrapper, exposing both event-based and polling access methods.

## Background

The Daily Python SDK provides network statistics via two complementary approaches:
- `CallClient.get_network_stats()` - Synchronous method for on-demand polling
- `EventHandler.on_network_stats_updated(stats)` - Event fired when conditions change (~every 2 seconds)

However, Pipecat's `DailyTransport` wrapper does not currently expose these capabilities. This guide explains how to add comprehensive network stats support upstream by implementing **both** approaches.

## Why This Feature is Valuable

Network statistics monitoring enables:
1. **Quality Monitoring** - Real-time visibility into call quality
2. **Debugging** - Identify bandwidth, latency, or packet loss issues
3. **Analytics** - Collect data for performance analysis and optimization
4. **User Experience** - Proactively detect and respond to network degradation
5. **Adaptive Behavior** - Adjust bot behavior based on network conditions

## Implementation Approach

Provide **two complementary access patterns** for maximum flexibility:

### 1. Event-Based (Push) - Recommended for Most Use Cases
- Automatic updates every ~2 seconds
- Ideal for logging, monitoring, real-time dashboards
- Zero polling overhead
- Async-friendly for I/O operations

### 2. Polling-Based (Pull) - For On-Demand Access
- Manual calls when needed
- Ideal for conditional checks before operations
- Simpler for quick one-off queries
- Synchronous access pattern

Both methods return identical data structures from the Daily SDK.

---

## Implementation Details

### 1. Add Event Handler to DailyTransportClient

**File:** `pipecat/transports/daily/transport.py`
**Location:** After line 1483 (after `on_recording_error`)

```python
def on_network_stats_updated(self, stats: Mapping[str, Any]) -> None:
    """Handle network stats update events from Daily.

    This event is fired by the Daily Python SDK when network statistics change,
    typically every 2 seconds. It provides comprehensive network quality metrics
    including bitrate, packet loss, jitter, and round-trip time.

    Args:
        stats: Network statistics dictionary from Daily SDK containing:
            - networkState: Overall quality ("good" | "warning" | "bad" | "unknown")
            - networkStateReasons: List of specific issues (e.g., ["sendPacketLoss"])
            - stats: Detailed metrics (bitrate, packet loss, RTT, jitter)

    Example:
        The stats parameter structure:
        {
            "networkState": "good",
            "networkStateReasons": [],
            "stats": {
                "latest": {
                    "timestamp": 1234567890,
                    "recvBitsPerSecond": 1500000,
                    "sendBitsPerSecond": 800000,
                    "networkRoundTripTime": 45,
                    "totalRecvPacketLoss": 0.01,
                    ...
                },
                "worstVideoRecvPacketLoss": 0.05,
                "averageNetworkRoundTripTime": 52,
                ...
            }
        }
    """
    logger.debug(f"Network stats updated: {stats}")
    self._call_event_callback(self._callbacks.on_network_stats_updated, stats)
```

**Rationale:**
- Follows the same pattern as all other Daily event handlers
- Uses existing `_call_event_callback` infrastructure
- Provides debug logging for troubleshooting
- Enables async I/O operations in user handlers

### 2. Add Polling Method to DailyTransportClient

**File:** `pipecat/transports/daily/transport.py`
**Location:** After line 893 (after `participant_counts()`)

```python
def get_network_stats(self) -> Mapping[str, Any]:
    """Get current network statistics from Daily.

    Returns network quality metrics including bitrate, packet loss, jitter,
    and round-trip time. This method provides on-demand access to stats,
    complementing the event-based on_network_stats_updated handler.

    Returns:
        Dictionary containing network statistics with the same structure as
        on_network_stats_updated events. Returns empty dict if client not
        available or on error.

    Example:
        ```python
        stats = transport._client.get_network_stats()
        latest = stats.get("stats", {}).get("latest", {})
        rtt = latest.get("networkRoundTripTime")
        packet_loss = latest.get("totalRecvPacketLoss")

        print(f"Current RTT: {rtt}ms")
        print(f"Packet Loss: {packet_loss*100:.2f}%")
        ```

    Note:
        This is a synchronous call that queries the current state. For
        automatic continuous monitoring, use the on_network_stats_updated
        event handler instead.
    """
    if not self._client:
        logger.warning("Cannot get network stats: CallClient not initialized")
        return {}

    try:
        stats = self._client.get_network_stats()
        logger.debug(f"Retrieved network stats: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error getting network stats: {e}")
        return {}
```

**Rationale:**
- Provides on-demand access without events
- Useful for conditional logic and one-off checks
- Graceful error handling with empty dict return
- Synchronous for simple use cases

### 3. Add Callback to DailyCallbacks Type

**File:** `pipecat/transports/daily/transport.py`
**Location:** After line 381 (in `DailyCallbacks` class)

```python
on_network_stats_updated: Callable[[Mapping[str, Any]], Awaitable[None]]
```

**Rationale:**
- Consistent with other callback type definitions
- Async callback allows for I/O operations (database writes, file logging)
- Type hints match Daily SDK's signature

### 4. Register Event Handler in DailyTransport

**File:** `pipecat/transports/daily/transport.py`
**Location:** After line 2123 (in `DailyTransport.__init__`)

```python
self._register_event_handler("on_network_stats_updated")
```

**Rationale:**
- Makes the handler discoverable by Pipecat users
- Follows the pattern for all other event handlers
- Required for `@transport.event_handler()` decorator to work

### 5. Wire Up Callback in Constructor

**File:** `pipecat/transports/daily/transport.py`
**Location:** Around line 2055-2084 (in `DailyTransport.__init__` callbacks section)

```python
callbacks = DailyCallbacks(
    # ... existing callbacks ...
    on_network_stats_updated=self._on_network_stats_updated,
    # ... other callbacks ...
)
```

**Location:** After line 2695 (add the handler method)

```python
async def _on_network_stats_updated(self, stats: Mapping[str, Any]) -> None:
    """Handle network stats update events.

    Args:
        stats: Network statistics dictionary from Daily SDK.
    """
    await self._call_event_handler("on_network_stats_updated", stats)
```

**Rationale:**
- Connects Daily SDK events to Pipecat's event system
- Allows users to register custom handlers via decorator
- Consistent with architecture of other event handlers

### 6. Expose Polling Method on DailyTransport

**File:** `pipecat/transports/daily/transport.py`
**Location:** After line 2219 (after `participant_counts()`)

```python
def get_network_stats(self) -> Mapping[str, Any]:
    """Get current network statistics.

    Provides on-demand access to network quality metrics. Returns the same
    data structure as on_network_stats_updated events.

    Returns:
        Dictionary containing network statistics including:
        - networkState: Overall quality assessment
        - networkStateReasons: Specific quality issues
        - stats: Detailed metrics (bitrate, packet loss, RTT, jitter)

    Example:
        ```python
        # Check network quality before critical operation
        stats = transport.get_network_stats()
        if stats.get("networkState") == "bad":
            logger.warning("Poor network quality, delaying operation")
            await asyncio.sleep(5)
        ```
    """
    return self._client.get_network_stats()
```

**Rationale:**
- Public API exposure for easy access
- Delegates to client implementation
- Same return type as event handler for consistency

---

## Network Stats Structure

Both methods return the same comprehensive metrics:

```python
{
  "stats": {
    "latest": {
      "timestamp": 1234567890,              # Unix timestamp
      "recvBitsPerSecond": 1500000,         # Total receive bitrate
      "sendBitsPerSecond": 800000,          # Total send bitrate
      "availableOutgoingBitrate": 2000000,  # Available bandwidth
      "networkRoundTripTime": 45,           # RTT in milliseconds
      "videoRecvBitsPerSecond": 1200000,
      "videoSendBitsPerSecond": 600000,
      "audioRecvBitsPerSecond": 300000,
      "audioSendBitsPerSecond": 200000,
      "videoRecvPacketLoss": 0.01,          # Packet loss as decimal (0.01 = 1%)
      "videoSendPacketLoss": 0.005,
      "audioRecvPacketLoss": 0.001,
      "audioSendPacketLoss": 0.0,
      "totalSendPacketLoss": 0.003,
      "totalRecvPacketLoss": 0.008,
      "videoRecvJitter": 12,                # Jitter in milliseconds
      "videoSendJitter": 8,
      "audioRecvJitter": 5,
      "audioSendJitter": 3
    },
    # Historical worst-case values
    "worstVideoRecvPacketLoss": 0.05,
    "worstVideoSendPacketLoss": 0.02,
    "worstAudioRecvPacketLoss": 0.01,
    "worstAudioSendPacketLoss": 0.005,
    "worstVideoRecvJitter": 25,
    "worstVideoSendJitter": 15,
    "worstAudioRecvJitter": 10,
    "worstAudioSendJitter": 7,
    # Average values
    "averageNetworkRoundTripTime": 52
  },
  # Quality assessment
  "networkState": "good",  # "good" | "warning" | "bad" | "unknown"
  "networkStateReasons": []  # e.g., ["sendPacketLoss", "roundTripTime"]
}
```

---

## Usage Examples

### Example 1: Event-Based Monitoring (Recommended for Logging)

```python
from pipecat.transports.daily import DailyTransport, DailyParams
import csv
from datetime import datetime

transport = DailyTransport(
    room_url="https://example.daily.co/room",
    token="your_token",
    bot_name="Network Monitor Bot",
    params=DailyParams()
)

@transport.event_handler("on_network_stats_updated")
async def log_network_stats(stats):
    """Automatically log all network stats updates to CSV."""
    latest = stats.get("stats", {}).get("latest", {})

    # Log to CSV file
    with open(f"network_stats_{datetime.now().date()}.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            stats.get("networkState"),
            latest.get("networkRoundTripTime"),
            latest.get("totalRecvPacketLoss"),
            latest.get("recvBitsPerSecond"),
            latest.get("sendBitsPerSecond"),
        ])

    # Alert on poor quality
    if stats.get("networkState") == "bad":
        logger.warning(f"Network degraded: {stats.get('networkStateReasons')}")
```

### Example 2: Polling-Based On-Demand Checks

```python
from pipecat.transports.daily import DailyTransport, DailyParams

transport = DailyTransport(
    room_url="https://example.daily.co/room",
    token="your_token",
    bot_name="Smart Bot",
    params=DailyParams()
)

async def check_network_before_operation():
    """Check network quality before performing bandwidth-intensive operation."""
    stats = transport.get_network_stats()

    network_state = stats.get("networkState", "unknown")
    latest = stats.get("stats", {}).get("latest", {})
    rtt = latest.get("networkRoundTripTime", 999)

    if network_state in ["bad", "warning"] or rtt > 200:
        logger.info("Network quality suboptimal, waiting...")
        await asyncio.sleep(5)
        return await check_network_before_operation()  # Retry

    logger.info(f"Network good (RTT: {rtt}ms), proceeding with operation")
    await perform_bandwidth_intensive_operation()
```

### Example 3: Hybrid Approach (Events + Polling)

```python
from pipecat.transports.daily import DailyTransport, DailyParams
import asyncio

transport = DailyTransport(
    room_url="https://example.daily.co/room",
    token="your_token",
    bot_name="Hybrid Monitor Bot",
    params=DailyParams()
)

# Event handler for continuous monitoring
@transport.event_handler("on_network_stats_updated")
async def monitor_quality(stats):
    """Continuously monitor and log network quality."""
    network_state = stats.get("networkState")
    logger.info(f"Network state: {network_state}")

    # Could send to monitoring service, database, etc.
    await send_to_metrics_service(stats)

# Polling for conditional logic
async def adaptive_quality_mode():
    """Adjust bot behavior based on current network conditions."""
    while True:
        stats = transport.get_network_stats()
        latest = stats.get("stats", {}).get("latest", {})

        bitrate = latest.get("recvBitsPerSecond", 0)
        packet_loss = latest.get("totalRecvPacketLoss", 0)

        # Adjust quality based on conditions
        if packet_loss > 0.05 or bitrate < 500000:  # Poor quality
            await set_low_quality_mode()
        elif bitrate > 2000000:  # Excellent quality
            await set_high_quality_mode()
        else:  # Normal quality
            await set_medium_quality_mode()

        await asyncio.sleep(10)  # Check every 10 seconds

# Run alongside bot
asyncio.create_task(adaptive_quality_mode())
```

### Example 4: Periodic Stats Summary

```python
from pipecat.transports.daily import DailyTransport
import asyncio

transport = DailyTransport(...)

async def periodic_stats_summary():
    """Poll stats every 30 seconds and log summary."""
    while True:
        await asyncio.sleep(30)

        stats = transport.get_network_stats()
        if not stats:
            continue

        latest = stats.get("stats", {}).get("latest", {})
        worst = stats.get("stats", {})

        logger.info(f"""
        Network Stats Summary:
        - State: {stats.get('networkState')}
        - Current RTT: {latest.get('networkRoundTripTime')}ms
        - Average RTT: {worst.get('averageNetworkRoundTripTime')}ms
        - Current Packet Loss: {latest.get('totalRecvPacketLoss', 0)*100:.2f}%
        - Worst Packet Loss: {worst.get('worstVideoRecvPacketLoss', 0)*100:.2f}%
        - Bandwidth: {latest.get('recvBitsPerSecond', 0)/1_000_000:.2f} Mbps
        """)
```

---

## When to Use Each Approach

### Use Event Handler When:
- ✓ Logging all stats to database/file
- ✓ Building real-time monitoring dashboards
- ✓ Sending alerts on quality changes
- ✓ Need comprehensive historical data
- ✓ Want zero polling overhead
- ✓ Prefer async/event-driven architecture

### Use Polling Method When:
- ✓ One-off quality checks before operations
- ✓ Conditional logic based on current state
- ✓ Custom polling intervals (not every 2s)
- ✓ Simpler synchronous code preferred
- ✓ Testing/debugging specific scenarios

### Use Both When:
- ✓ Event handler for comprehensive logging
- ✓ Polling for pre-operation validation
- ✓ Maximum flexibility needed
- ✓ Different parts of codebase have different needs

---

## Testing Plan

### Unit Tests

**File:** `tests/transports/daily/test_network_stats.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

def test_network_stats_event_handler_registered():
    """Verify on_network_stats_updated is registered."""
    transport = DailyTransport(...)
    assert "on_network_stats_updated" in transport._event_handlers

def test_network_stats_event_handler_invoked():
    """Verify event handler callback is invoked."""
    transport = DailyTransport(...)
    handler = AsyncMock()
    transport.event_handler("on_network_stats_updated")(handler)

    # Simulate stats update from Daily SDK
    stats = {"networkState": "good", "stats": {...}}
    transport._client.on_network_stats_updated(stats)

    handler.assert_called_once_with(stats)

def test_get_network_stats_returns_data():
    """Verify get_network_stats returns stats dictionary."""
    transport = DailyTransport(...)

    with patch.object(transport._client._client, 'get_network_stats') as mock:
        mock.return_value = {"networkState": "good", "stats": {...}}
        stats = transport.get_network_stats()

    assert stats["networkState"] == "good"
    assert "stats" in stats
    mock.assert_called_once()

def test_get_network_stats_handles_no_client():
    """Verify graceful handling when client not initialized."""
    transport = DailyTransport(...)
    transport._client._client = None

    stats = transport.get_network_stats()
    assert stats == {}  # Empty dict, no exception

def test_get_network_stats_handles_exception():
    """Verify error handling in get_network_stats."""
    transport = DailyTransport(...)

    with patch.object(transport._client._client, 'get_network_stats') as mock:
        mock.side_effect = Exception("Network error")
        stats = transport.get_network_stats()

    assert stats == {}  # Graceful degradation
```

### Integration Tests

1. **Create Daily room** via API
2. **Connect bot** with DailyTransport
3. **Register event handler** and verify it receives updates within 5 seconds
4. **Call `get_network_stats()`** and verify non-empty response
5. **Validate structure** - Both methods return same schema
6. **Check timestamps** - Event and polling return current data
7. **Test error cases** - Disconnected, no client, etc.

### Manual Testing Checklist

- [ ] Event handler receives updates every ~2 seconds when connected
- [ ] `get_network_stats()` returns current stats matching events
- [ ] Stats structure matches Daily SDK documentation exactly
- [ ] Both methods return identical data when sampled simultaneously
- [ ] Error handling works: no client, no connection, mid-disconnect
- [ ] No performance issues: no memory leaks, no blocking
- [ ] Works under various network conditions (good/warning/bad)
- [ ] Stats values are realistic and accurate

---

## Documentation Updates

### 1. API Reference

Add to `docs/api/transports/daily.md`:

#### Event Handlers

##### `on_network_stats_updated`

```python
@transport.event_handler("on_network_stats_updated")
async def handler(stats: dict):
    """Handle automatic network stats updates."""
    pass
```

**Description:** Called automatically when network statistics change (approximately every 2 seconds during an active call).

**Parameters:**
- `stats` (dict): Network statistics dictionary containing:
  - `networkState` (str): Quality assessment ("good", "warning", "bad", "unknown")
  - `networkStateReasons` (list): Specific issues affecting quality
  - `stats` (dict): Detailed metrics (bitrate, packet loss, RTT, jitter)

**Use Cases:**
- Continuous monitoring and logging
- Real-time dashboards
- Automatic alerts on quality degradation
- Analytics and historical data collection

---

#### Methods

##### `get_network_stats() -> dict`

Get current network statistics on-demand.

**Returns:**
- `dict`: Network statistics (same structure as `on_network_stats_updated` events)
- Returns empty dict `{}` if stats unavailable

**Example:**
```python
stats = transport.get_network_stats()
if stats.get("networkState") == "bad":
    logger.warning("Poor network quality detected")
```

**Use Cases:**
- Pre-operation quality checks
- Conditional logic based on current state
- One-off debugging queries

---

### 2. User Guide

Create `docs/guides/network-quality-monitoring.md`:

```markdown
# Network Quality Monitoring

## Overview

Pipecat provides comprehensive network quality monitoring for Daily calls through two complementary approaches:

1. **Event-Based Monitoring** - Automatic updates via `on_network_stats_updated`
2. **Polling-Based Access** - On-demand queries via `get_network_stats()`

## Quick Start

### Event-Based (Recommended)

[Include Example 1 from above]

### Polling-Based

[Include Example 2 from above]

## Network Stats Structure

[Include stats structure documentation]

## Best Practices

1. **Use events for continuous monitoring** - More efficient than polling
2. **Use polling for conditional checks** - Before bandwidth-intensive operations
3. **Handle empty responses** - Stats may be unavailable before connection
4. **Log responsibly** - Avoid logging every update to disk (use aggregation)
5. **Set thresholds** - Define what "bad" means for your use case

## Metrics Explained

- **RTT (Round-Trip Time)**: Network latency in milliseconds. Lower is better.
  - Good: < 100ms
  - Warning: 100-200ms
  - Bad: > 200ms

- **Packet Loss**: Percentage of lost packets (0.01 = 1%)
  - Good: < 1%
  - Warning: 1-5%
  - Bad: > 5%

[etc.]
```

---

### 3. Changelog

```markdown
## [Unreleased]

### Added
- **Network statistics support for DailyTransport**
  - `on_network_stats_updated` event handler for automatic push updates
  - `get_network_stats()` method for on-demand polling
  - Comprehensive metrics: bitrate, packet loss, RTT, jitter
  - Quality assessment: networkState and networkStateReasons
  - Both approaches return identical data structures
  - Includes documentation and usage examples
  - Fully tested with unit and integration tests
  - Zero breaking changes (purely additive feature)
```

---

## Pull Request Checklist

- [ ] Add `on_network_stats_updated` event handler to `DailyTransportClient`
- [ ] Add `get_network_stats()` method to `DailyTransportClient`
- [ ] Add `on_network_stats_updated` callback to `DailyCallbacks` type
- [ ] Register event handler in `DailyTransport.__init__`
- [ ] Wire up event callback in constructor
- [ ] Expose `get_network_stats()` on public `DailyTransport` API
- [ ] Add comprehensive unit tests for both approaches
- [ ] Add integration tests with real Daily rooms
- [ ] Update API reference documentation
- [ ] Add user guide with examples
- [ ] Add usage examples for both approaches
- [ ] Update changelog
- [ ] Verify zero breaking changes (backward compatibility)

---

## Why This Should Be Accepted

### 1. Native Daily SDK Features
Both `get_network_stats()` and `on_network_stats_updated` are official Daily SDK features. Wrappers should expose the underlying capabilities.

### 2. Zero Breaking Changes
Purely additive - no modifications to existing APIs or behavior. Fully backward compatible.

### 3. Follows Existing Patterns
- Event handler uses same architecture as all other Daily events
- Polling method matches pattern of `participants()` and `participant_counts()`
- Consistent naming and structure

### 4. High Value
Enables critical use cases:
- Production monitoring
- Quality assurance
- User experience optimization
- Debugging and troubleshooting
- Adaptive behavior (bitrate, quality adjustments)

### 5. Dual Approach Benefits
Provides flexibility for different use cases:
- Events for efficiency (continuous monitoring)
- Polling for simplicity (one-off checks)
- Users choose what works best for them

### 6. Low Maintenance
Once implemented, requires no ongoing maintenance. No new dependencies or external services.

### 7. Well Tested
Includes:
- Unit tests for both methods
- Integration tests with real Daily calls
- Error handling tests
- Manual testing procedures

### 8. Comprehensive Documentation
- API reference with examples
- User guide with best practices
- Multiple real-world usage examples
- Inline docstrings with examples

---

## Alternative Approaches (Why They're Inferior)

### If PR is Not Accepted

Users could access stats via private attributes:

```python
# NOT RECOMMENDED - Accessing private attributes
transport = DailyTransport(...)
daily_client = transport._client._client  # Private access
stats = daily_client.get_network_stats()
```

**Problems with this approach:**
- ❌ Requires accessing private/internal attributes
- ❌ Not officially supported by Pipecat
- ❌ May break in future versions without warning
- ❌ Not event-driven (no push updates)
- ❌ Not discoverable in documentation
- ❌ Poor developer experience

### Only Implementing Event Handler

Some might suggest only implementing the event handler:

**Limitations:**
- Users who need on-demand checks must set up complex event state tracking
- Adds overhead for simple one-off queries
- Less flexible for conditional logic patterns
- Doesn't match Daily.js API (which has both)

### Only Implementing Polling Method

Some might suggest only implementing polling:

**Limitations:**
- Inefficient for continuous monitoring (polling overhead)
- Users must implement their own polling loops
- No push notifications on quality changes
- Higher CPU usage for background polling
- Doesn't leverage Daily SDK's built-in event system

**The dual approach is superior and matches Daily.js precedent.**

---

## Daily SDK References

- **Daily Python SDK:** https://reference-python.daily.co/
  - `CallClient.get_network_stats()`: https://reference-python.daily.co/api_reference.html#daily.CallClient.get_network_stats
  - `EventHandler.on_network_stats_updated()`: https://reference-python.daily.co/api_reference.html#daily.EventHandler.on_network_stats_updated

- **Daily.js Network Stats:** https://docs.daily.co/reference/daily-js/instance-methods/get-network-stats
  - Note: Daily.js also provides `getNetworkStats()` method AND `'network-quality-change'` event

- **Network Quality Guide:** https://docs.daily.co/guides/products/network-quality

---

## Contact

For questions or discussions:

- **Pipecat GitHub:** https://github.com/pipecat-ai/pipecat
- **Pipecat Discord:** https://discord.gg/pipecat
- **Daily Support:** https://www.daily.co/contact

---

## License

This contribution guide is released under the same license as Pipecat (BSD 2-Clause).
