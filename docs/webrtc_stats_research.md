# WebRTC Statistics Research: Daily.co REST API & Network-Layer Monitoring

This document provides comprehensive research on accessing detailed WebRTC statistics beyond what the Daily Python SDK provides through `get_network_stats()`.

## Current Limitations

The Daily Python SDK (`daily-python` v0.21.0) provides limited network statistics via `get_network_stats()`:

**Available Metrics:**
- Bitrate (receive/send, total and video-specific)
- Packet loss percentages (total and video-specific)
- Quality score (0-100) and threshold (good/low/veryLow)

**Missing Critical WebRTC Metrics:**
- RTT (Round Trip Time)
- Jitter (per track)
- Frame rate / Resolution details
- Codec information
- Individual SSRC/track-level statistics
- ICE candidate pair statistics
- Audio level, energy, echo return loss

---

## Option 2: Daily.co REST API for Analytics

### Overview
Daily.co provides POST-CALL analytics through their REST API `/logs` endpoint. This allows you to retrieve detailed call quality metrics after a session completes.

### Available Metrics via `/logs` Endpoint

The `/logs` endpoint provides comprehensive WebRTC statistics including:

**Network & Transport:**
- RTT (Round Trip Time) averages ✅
- Packet loss percentages (videoRecvPacketLoss)
- Bitrate measurements (average, maximum, minimum for sent/received)

**Audio Metrics:**
- Jitter measurements (average and maximum) ✅
- Packet loss percentages
- Bits received per second
- Jitter buffer delay per emitted count average

**Video Metrics:**
- Packets lost percentage and reception rates
- Decode/encode time per frame
- QP sum per frame (quality metrics)
- Jitter buffer delay
- Frames encoded per second (framesEncodedPerSec)

**Call Context:**
- Discrete events during the session
- Per-participant connection information
- Transport layer data
- Track-level statistics

### API Access Details

**Authentication:**
```bash
Authorization: Bearer YOUR_API_KEY
```

**Endpoint:**
```
GET https://api.daily.co/v1/logs
```

**Query Parameters:**
- `mtgSessionId` (string, required if userSessionId not present): Filter by session ID
- `userSessionId` (string, required if mtgSessionId not present): Filter by participant ID
- `includeMetrics` (boolean, default: false): Include metrics array in response
- `includeLogs` (boolean, default: true): Include logs array in response
- `logLevel` (string): Filter by log level (ERROR, INFO, DEBUG)
- `order` (string): ASC or DESC (default: DESC)

**Example cURL Request:**
```bash
curl --request GET \
  --header 'Authorization: Bearer $YOUR_API_KEY' \
  --url 'https://api.daily.co/v1/logs?mtgSessionId=7a99abff-0047-4b27-c6c1-49b4ec46f1de&userSessionId=4fde3659-71f6-4c28-9a90-e4c3f08ca611&includeMetrics=1'
```

### Additional Endpoints

**GET /meetings**
- Fetches up to 100 meeting session objects with pagination
- Provides: domain name, room name, start/end times, participant list
- Participant data includes: join_time, duration, participant_id, user_id, user_name
- Timestamps are Unix format with ~15-second granularity

**GET /meetings/:meeting/participants**
- Get detailed participant information for a specific meeting session

### Limitations

**POST-CALL ONLY:** The REST API provides historical data after the call completes, not real-time statistics during the call.

**Dashboard Access:** For real-time visualization, Daily provides dashboard analytics at `dashboard.daily.co` with packet loss, bitrate charts, and more.

**Advanced Analytics:** Enterprise customers can access Looker-based custom reporting with advanced visualizations.

### Implementation Approach

To use this option, you would need to:

1. Track meeting session IDs and participant IDs during calls
2. After call completion, query the `/logs` endpoint
3. Parse the metrics data to extract desired statistics
4. Store/analyze the data for quality monitoring

**Python Example:**
```python
import requests
from typing import Dict, Any

def get_call_metrics(
    api_key: str,
    mtg_session_id: str,
    user_session_id: str | None = None
) -> Dict[str, Any]:
    """Retrieve call quality metrics from Daily REST API.

    Args:
        api_key: Daily.co API key
        mtg_session_id: Meeting session ID
        user_session_id: Optional participant ID

    Returns:
        Dictionary containing logs and metrics data
    """
    url = "https://api.daily.co/v1/logs"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "mtgSessionId": mtg_session_id,
        "includeMetrics": 1
    }

    if user_session_id:
        params["userSessionId"] = user_session_id

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()
```

---

## Option 4: Network-Layer Monitoring

### Overview
Capture and analyze RTP/RTCP packets at the network layer to calculate WebRTC statistics independently of Daily's SDK.

### Challenges

**WebRTC Encryption:**
- RTP is encrypted using SRTP (mandatory in WebRTC)
- RTCP is also encrypted via DTLS/SRTP
- Direct packet analysis cannot decrypt encrypted payload without keys

**Solutions:**
1. **Capture decrypted packets** - Some browsers support dumping decrypted RTP/RTCP
2. **Analyze RTCP sender/receiver reports** - Extract RTT from unencrypted RTCP headers
3. **Use transport-layer metrics** - Calculate jitter/RTT from packet timing patterns

### Approach 1: Packet Capture with Wireshark/tcpdump

**Tools:**
- `tcpdump`: Command-line packet capture
- `Wireshark`: GUI-based protocol analyzer with RTP statistics

**Wireshark RTP Statistics:**
- Delay, jitter, bandwidth per stream
- Packet loss, maximum delay, sequence errors
- Jitter calculated per RFC3550 (RTP)
- Graph visualization of jitter and packet intervals

**Decryption Methods:**
- Firefox: Supports dumping decrypted RTP/RTCP to log files
- Chrome: No built-in support for decrypted packet dumps
- Server-side: Capture before encryption / after decryption

**Process:**
```bash
# Capture packets on network interface
sudo tcpdump -i any -w webrtc_capture.pcap 'udp'

# Analyze with Wireshark
wireshark webrtc_capture.pcap

# Or use tshark (CLI Wireshark)
tshark -r webrtc_capture.pcap -Y rtp -T fields -e rtp.ssrc -e rtp.timestamp
```

### Approach 2: Python-Based Real-Time Analysis

**Python Libraries:**

1. **PyShark** - Python wrapper for Wireshark/tshark
   - Leverages Wireshark's protocol dissectors
   - Good for complex protocol parsing
   - Example: `smpte2110-analyzer` uses PyShark for RTP analysis

2. **Scapy** - Packet manipulation and analysis
   - Built-in RTP layer support
   - Can calculate RTT from packet timestamps
   - Real-time capture and processing
   - Example: RTT = `pkts[1].time - pkts[0].time`

3. **dpkt** - Fast, lightweight packet parsing
   - Lower-level than PyShark
   - Excellent for custom metric calculations
   - Examples show jitter calculation implementations

4. **rtpcap** (Facebook/Meta)
   - tshark wrapper + Python aggregation code
   - Designed for RTP/RTCP stream analysis
   - Provides network-time, audio-packet, video-frame analysis
   - GitHub: `facebookexperimental/rtpcap`

5. **rtclite** - Lightweight RTC protocol implementations
   - Pure Python RTP/RTCP implementation (RFC 3550)
   - Can encode/decode RTP packets
   - GitHub: `theintencity/rtclite`

6. **PyRTP** - Simple RTP library
   - Handles RTP packet encoding/decoding
   - Basic packet parsing

**Jitter Calculation Example:**
```python
import dpkt
from statistics import mean, stdev

def calculate_jitter(packets):
    """Calculate instantaneous packet delay variation (jitter)."""
    delays = []
    prev_arrival = None
    prev_timestamp = None

    for packet in packets:
        arrival_time = packet.timestamp
        rtp_timestamp = packet.rtp.timestamp

        if prev_arrival is not None:
            # Inter-arrival time
            arrival_delta = arrival_time - prev_arrival
            # RTP timestamp delta
            timestamp_delta = rtp_timestamp - prev_timestamp
            # Delay variation
            delay = arrival_delta - timestamp_delta
            delays.append(delay)

        prev_arrival = arrival_time
        prev_timestamp = rtp_timestamp

    return {
        'mean_jitter': mean(delays),
        'jitter_stdev': stdev(delays)
    }
```

**RTT from RTCP Sender/Receiver Reports:**
```python
def calculate_rtt_from_rtcp(rtcp_packet):
    """
    Calculate RTT from RTCP sender/receiver reports.

    The sender sends its timestamp to receiver,
    receiver reflects it back, allowing RTT calculation.
    """
    # Extract sender report timestamp
    sender_ts = rtcp_packet.sender_info.ntp_timestamp

    # Extract receiver report delay since last SR
    dlsr = rtcp_packet.receiver_report.delay_since_last_sr

    # Calculate RTT
    rtt = current_ntp_time - sender_ts - dlsr
    return rtt
```

### Approach 3: eBPF-Based Monitoring

**eBPF (Extended Berkeley Packet Filter)** - Kernel-level network monitoring

**Tools:**
- **BCC (BPF Compiler Collection)** - Python front-end for eBPF programs
  - `tcprtt.py`: TCP RTT monitoring tool
  - Can be adapted for UDP/RTP monitoring
  - Zero packet capture overhead

**Advantages:**
- Extremely low overhead
- Real-time statistics
- No packet capture files needed
- Direct kernel-level metrics

**Limitations:**
- Primarily for TCP (RTT built-in)
- UDP/RTP requires custom eBPF programs
- More complex to implement

### Approach 4: Server-Side Packet Interception

Since you're running a voice agent server, you can intercept packets at the application layer:

**Method 1: Socket-level capture**
```python
import socket
import struct
from datetime import datetime

class RTPMonitor:
    def __init__(self, interface='any'):
        # Create raw socket
        self.sock = socket.socket(
            socket.AF_PACKET,
            socket.SOCK_RAW,
            socket.ntohs(0x0800)
        )
        self.sock.bind((interface, 0))

    def capture_rtp_packets(self):
        while True:
            packet = self.sock.recvfrom(65565)
            timestamp = datetime.now()
            # Parse UDP payload for RTP
            self.parse_rtp(packet[0], timestamp)

    def parse_rtp(self, data, timestamp):
        # RTP header parsing
        # Calculate jitter, packet loss, etc.
        pass
```

**Method 2: Network namespace monitoring**
```bash
# Create network namespace
ip netns add webrtc_monitor

# Run packet capture in namespace
ip netns exec webrtc_monitor tcpdump -i any -w capture.pcap

# Mirror traffic to namespace
tc filter add dev eth0 parent ffff: protocol ip u32 \
  match ip protocol 17 0xff \
  action mirred egress mirror dev veth_monitor
```

### Implementation Recommendation

**Best Approach for Your Use Case:**

1. **Real-time statistics during call:** Network-layer monitoring with PyShark or Scapy
2. **Post-call analysis:** Daily REST API `/logs` endpoint
3. **Hybrid approach:** Combine both for comprehensive monitoring

**Hybrid Implementation:**
```python
class ComprehensiveWebRTCMonitor:
    """
    Combines real-time packet analysis with post-call API retrieval.
    """

    def __init__(self, daily_api_key: str):
        self.api_key = daily_api_key
        self.packet_analyzer = RealTimeRTPAnalyzer()
        self.session_metrics = {}

    async def monitor_call(self, session_id: str):
        # Start real-time packet capture
        self.packet_analyzer.start_capture()

        # During call: collect real-time metrics
        while call_active:
            metrics = self.packet_analyzer.get_current_metrics()
            self.session_metrics[datetime.now()] = metrics
            await asyncio.sleep(1)

        # After call: retrieve Daily API metrics
        api_metrics = await self.get_daily_metrics(session_id)

        # Combine and analyze
        return self.merge_metrics(self.session_metrics, api_metrics)

    async def get_daily_metrics(self, session_id: str):
        # Use REST API to get comprehensive post-call data
        url = f"https://api.daily.co/v1/logs?mtgSessionId={session_id}&includeMetrics=1"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        # ... fetch and return
```

### Comparison Matrix

| Feature | Daily REST API | PyShark/Scapy | eBPF | Wireshark |
|---------|----------------|---------------|------|-----------|
| Real-time | ❌ | ✅ | ✅ | ✅ |
| Post-call | ✅ | ✅ | ❌ | ✅ |
| RTT | ✅ | ✅* | ✅ | ✅* |
| Jitter | ✅ | ✅ | ⚠️ | ✅ |
| Setup complexity | Low | Medium | High | Low |
| Encryption issue | N/A | ⚠️ | ⚠️ | ⚠️ |
| CPU overhead | None | Medium | Very Low | Medium |
| Code integration | Easy | Medium | Hard | Manual |

*Requires RTCP analysis or packet timing correlation

---

## Recommendations

### For Immediate Implementation

**Use Daily REST API `/logs` endpoint:**
- Easiest to implement
- Provides RTT, jitter, and comprehensive metrics
- No encryption concerns
- Perfect for post-call analysis and quality monitoring

### For Real-Time Monitoring

**Use PyShark or rtpcap:**
- Captures packets during call
- Can calculate basic metrics from packet timing
- Good balance of ease-of-use and capability
- Combine with Daily API for complete picture

### For Production Deployment

**Hybrid Approach:**
1. Real-time: Simple packet timing analysis (arrival patterns)
2. Post-call: Daily REST API for authoritative metrics
3. Alerting: Combine both for comprehensive monitoring

### Next Steps

1. **Get Daily API key** from dashboard.daily.co
2. **Implement `/logs` endpoint integration** for post-call metrics
3. **Optional: Add PyShark** for real-time monitoring if needed
4. **Store metrics** in time-series database (InfluxDB, Prometheus)
5. **Create dashboards** using Grafana or similar tools

---

## Code Examples

See the following files for implementation examples:
- `tools/daily_metrics_fetcher.py` - Daily REST API integration
- `tools/rtp_packet_analyzer.py` - Real-time packet analysis with PyShark
- `tools/webrtc_monitor.py` - Hybrid monitoring implementation

## References

- Daily.co REST API: https://docs.daily.co/reference/rest-api
- Daily.co Logging & Metrics: https://docs.daily.co/guides/architecture-and-monitoring/logging-and-metrics
- WebRTC Statistics API: https://www.w3.org/TR/webrtc-stats/
- RFC 3550 (RTP): https://datatracker.ietf.org/doc/html/rfc3550
- PyShark Documentation: https://github.com/KimiNewt/pyshark
- Scapy RTP Layer: https://scapy.readthedocs.io/en/latest/api/scapy.layers.rtp.html
- Facebook rtpcap: https://github.com/facebookexperimental/rtpcap
