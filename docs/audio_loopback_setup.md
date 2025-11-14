# Audio Loopback Setup for System Audio Transcription

This guide explains how to configure audio loopback to transcribe system audio (browser videos, music, etc.) on WSL2.

## Overview

By default, the transcription tool captures audio from your microphone. To transcribe system audio (like YouTube videos or online meetings), you need to set up audio loopback that routes your computer's audio output back as an input source.

## Architecture

```
Windows Audio Output (browser/videos)
    → Virtual Audio Cable (VB-Cable)
    → PulseAudio in WSL2
    → Transcription Tool
```

## Setup Steps

### 1. Install Virtual Audio Cable (Windows Side)

**Option A: VB-CABLE (Free)**
1. Download from: https://vb-audio.com/Cable/
2. Extract and run `VBCABLE_Setup_x64.exe` as Administrator
3. Restart Windows after installation

**Option B: VoiceMeeter (Free, more features)**
1. Download from: https://vb-audio.com/Voicemeeter/
2. Install and restart Windows

### 2. Configure Windows Audio

1. **Right-click the speaker icon** in Windows taskbar
2. **Select "Open Sound settings"**
3. **Output device**: Set to "CABLE Input (VB-Audio Virtual Cable)"
   - This routes all Windows audio through the virtual cable
4. **Input device**: Should show "CABLE Output (VB-Audio Virtual Cable)"
   - This makes the looped audio available as an input

**To hear audio while transcribing:**
- Open VoiceMeeter (if using VoiceMeeter option)
- Or use "Listen to this device" feature:
  1. Right-click speaker icon → Sounds
  2. Recording tab → CABLE Output → Properties
  3. Listen tab → Check "Listen to this device"
  4. Select your actual speakers

### 3. Configure WSL2 Audio (PulseAudio)

```bash
# Install PulseAudio
sudo apt-get update
sudo apt-get install -y pulseaudio portaudio19-dev python3-pyaudio

# Start PulseAudio (if not running)
pulseaudio --start

# Verify audio devices are visible
pactl list sources short
```

### 4. Configure Windows → WSL2 Audio Bridge

Edit or create `~/.config/pulse/default.pa` in WSL2:

```bash
# Create config directory
mkdir -p ~/.config/pulse

# Create configuration
cat > ~/.config/pulse/default.pa << 'EOF'
# Load PulseAudio modules
.include /etc/pulse/default.pa

# Load Windows audio bridge (if using PulseAudio server on Windows)
# This connects to Windows PulseAudio server
load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1

# Or use Windows WASAPI loopback (alternative method)
# load-module module-waveout sink_name=output source_name=input
EOF

# Restart PulseAudio
pulseaudio --kill
pulseaudio --start
```

### 5. Install Python Audio Dependencies

```bash
# System libraries
sudo apt-get install -y portaudio19-dev

# Python packages (handled by uv)
uv sync
```

### 6. Test Audio Loopback

```bash
# List available audio devices
uv run transcribe --list-devices

# You should see the virtual cable or loopback device
# Example output:
#   Device 0: default
#   Device 1: CABLE Output (VB-Audio Virtual Cable)
#   Device 2: pulse
```

### 7. Run Transcription

```bash
# Use default device (usually picks up loopback automatically)
uv run transcribe

# Or specify device explicitly
uv run transcribe --device 1
```

## Troubleshooting

### No Audio Devices Found

```bash
# Check if PulseAudio is running
pulseaudio --check
echo $?  # Should return 0 if running

# If not running, start it
pulseaudio --start

# Check system audio
aplay -l
arecord -l
```

### Audio Not Routing to WSL2

**Method 1: Use PulseAudio Network**
1. Install PulseAudio on Windows: https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/
2. Configure Windows PulseAudio to accept network connections
3. Point WSL2 to Windows PulseAudio server

**Method 2: Use WSLg Audio (Simpler)**
- Ensure you're using WSL2 with WSLg (Windows 11 or updated Windows 10)
- WSLg automatically bridges audio
- Just install portaudio and it should work

```bash
# Check WSLg
echo $DISPLAY  # Should show something like :0

# If WSLg is active, audio should work automatically
```

### Low Audio Quality or Latency

Adjust PulseAudio buffer settings in `~/.config/pulse/daemon.conf`:

```ini
default-fragments = 4
default-fragment-size-msec = 5
```

Then restart PulseAudio:
```bash
pulseaudio --kill && pulseaudio --start
```

### Device Index Changes

Device indices can change. Use the device name instead:

```python
# In transcribe_cli.py, you could add name-based device selection
# For now, run --list-devices each time to check current indices
```

## Alternative: Run on Native Windows

If WSL2 audio is problematic, run Python natively on Windows:

1. Install Python on Windows
2. Clone repo to Windows filesystem
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python tools/transcribe_cli.py`

Windows Python will directly access the virtual cable without WSL2 complexity.

## Testing

### Test with Browser Video

1. Start transcription: `uv run transcribe`
2. Open YouTube in your browser
3. Play a video with clear speech
4. You should see transcriptions appear in real-time

### Test with Microphone (Fallback)

If system audio doesn't work, test with microphone first:

```bash
# List devices
uv run transcribe --list-devices

# Use microphone device (usually device 0 or "default")
uv run transcribe --device 0

# Speak into microphone - you should see transcriptions
```

## Performance Tips

1. **Use wired connection**: WiFi can add latency
2. **Close unnecessary apps**: Reduce CPU load for real-time processing
3. **Adjust sample rate**: 16kHz is optimal for speech (already configured)
4. **Monitor CPU usage**: Transcription is CPU-intensive

## References

- VB-Cable Documentation: https://vb-audio.com/Cable/
- PulseAudio Documentation: https://www.freedesktop.org/wiki/Software/PulseAudio/
- WSLg Audio: https://github.com/microsoft/wslg
- Pipecat LocalAudioTransport: https://docs.pipecat.ai/

## Need Help?

If you encounter issues:

1. Check PulseAudio logs: `journalctl --user -u pulseaudio`
2. Test system audio: `arecord -d 5 test.wav && aplay test.wav`
3. Verify virtual cable in Windows Sound settings
4. Try native Windows Python as fallback
