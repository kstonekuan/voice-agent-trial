"""Extended Daily transport with network statistics monitoring support.

This module extends Pipecat's DailyTransport to add network statistics collection
via the on_network_stats_updated event handler that Daily's Python SDK provides.
"""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from loguru import logger
from pipecat.transports.daily.transport import (
    DailyCallbacks,
    DailyParams,
    DailyTransport,
    DailyTransportClient,
)

from utils.network_stats_writer import NetworkStatsWriter

if TYPE_CHECKING:
    pass


class ExtendedDailyTransportClient(DailyTransportClient):
    """Extended Daily transport client with network stats event handling."""

    def __init__(
        self,
        room_url: str,
        token: str | None,
        bot_name: str,
        params: DailyParams,
        callbacks: DailyCallbacks,
        transport_name: str,
        stats_writer: NetworkStatsWriter | None = None,
    ) -> None:
        """Initialize the extended Daily transport client.

        Args:
            room_url: URL of the Daily room to connect to.
            token: Optional authentication token for the room.
            bot_name: Display name for the bot in the call.
            params: Configuration parameters for the transport.
            callbacks: Event callback handlers.
            transport_name: Name identifier for the transport.
            stats_writer: Optional network stats CSV writer instance.
        """
        super().__init__(room_url, token, bot_name, params, callbacks, transport_name)
        self._stats_writer = stats_writer
        self._first_stats_logged = False  # Track if we've logged full stats once

    def on_network_stats_updated(self, stats: Mapping[str, Any]) -> None:
        """Handle network stats update events from Daily.

        This event is fired by the Daily Python SDK when network statistics change.
        It receives comprehensive network quality metrics including bitrate, packet loss,
        jitter, and round-trip time.

        Args:
            stats: Network statistics dictionary from Daily SDK.
        """
        # Queue this for async callback handling using the event queue
        self._call_event_callback(self._on_network_stats_updated_async, stats)

    async def _on_network_stats_updated_async(self, stats: Mapping[str, Any]) -> None:
        """Async handler for network stats updates.

        This is called from the event queue task handler, so it's safe to perform
        async I/O operations like writing to CSV files.

        Args:
            stats: Network statistics dictionary from Daily SDK.
        """
        # Log full stats structure once for debugging
        if not self._first_stats_logged:
            import json

            logger.info(
                f"First network stats received (full structure):\n{json.dumps(dict(stats), indent=2, default=str)}"
            )
            self._first_stats_logged = True

        # Write to CSV if writer is configured
        if self._stats_writer:
            await self._stats_writer.write_stats(stats)


class ExtendedDailyTransport(DailyTransport):
    """Extended Daily transport with network statistics monitoring.

    This transport extends the standard Pipecat DailyTransport to add support
    for collecting network statistics via Daily's on_network_stats_updated event.
    """

    def __init__(
        self,
        room_url: str,
        token: str | None,
        bot_name: str,
        params: DailyParams | None = None,
        input_name: str | None = None,
        output_name: str | None = None,
        stats_writer: NetworkStatsWriter | None = None,
    ) -> None:
        """Initialize the extended Daily transport.

        Args:
            room_url: URL of the Daily room to connect to.
            token: Optional authentication token for the room.
            bot_name: Display name for the bot in the call.
            params: Configuration parameters for the transport.
            input_name: Optional name for the input transport.
            output_name: Optional name for the output transport.
            stats_writer: Optional network stats CSV writer instance.
        """
        # Note: We need to override the client creation, so we'll do this differently
        # We can't call super().__init__() and then replace _client because it's already
        # used to create _input and _output. Instead, we need to replicate the logic.

        # Import here to match the parent class pattern
        from pipecat.transports.base_transport import BaseTransport

        # Initialize BaseTransport directly
        BaseTransport.__init__(self, input_name=input_name, output_name=output_name)

        # Import DailyCallbacks from parent
        from pipecat.transports.daily.transport import DailyCallbacks

        # Create callbacks - copy from parent class
        callbacks = DailyCallbacks(
            on_active_speaker_changed=self._on_active_speaker_changed,
            on_joined=self._on_joined,
            on_left=self._on_left,
            on_before_leave=self._on_before_leave,
            on_error=self._on_error,
            on_app_message=self._on_app_message,
            on_call_state_updated=self._on_call_state_updated,
            on_client_connected=self._on_client_connected,
            on_client_disconnected=self._on_client_disconnected,
            on_dialin_connected=self._on_dialin_connected,
            on_dialin_ready=self._on_dialin_ready,
            on_dialin_stopped=self._on_dialin_stopped,
            on_dialin_error=self._on_dialin_error,
            on_dialin_warning=self._on_dialin_warning,
            on_dialout_answered=self._on_dialout_answered,
            on_dialout_connected=self._on_dialout_connected,
            on_dialout_stopped=self._on_dialout_stopped,
            on_dialout_error=self._on_dialout_error,
            on_dialout_warning=self._on_dialout_warning,
            on_participant_joined=self._on_participant_joined,
            on_participant_left=self._on_participant_left,
            on_participant_updated=self._on_participant_updated,
            on_transcription_message=self._on_transcription_message,
            on_transcription_stopped=self._on_transcription_stopped,
            on_transcription_error=self._on_transcription_error,
            on_recording_started=self._on_recording_started,
            on_recording_stopped=self._on_recording_stopped,
            on_recording_error=self._on_recording_error,
        )

        self._params = params or DailyParams()

        # Create our extended client instead of the standard one
        self._client = ExtendedDailyTransportClient(
            room_url, token, bot_name, self._params, callbacks, self.name, stats_writer
        )

        self._input: Any | None = None
        self._output: Any | None = None

        self._other_participant_has_joined = False

        # Register supported handlers - copy from parent
        self._register_event_handler("on_active_speaker_changed")
        self._register_event_handler("on_joined")
        self._register_event_handler("on_left")
        self._register_event_handler("on_error")
        self._register_event_handler("on_app_message")
        self._register_event_handler("on_call_state_updated")
        self._register_event_handler("on_client_connected")
        self._register_event_handler("on_client_disconnected")
        self._register_event_handler("on_dialin_connected")
        self._register_event_handler("on_dialin_ready")
        self._register_event_handler("on_dialin_stopped")
        self._register_event_handler("on_dialin_error")
        self._register_event_handler("on_dialin_warning")
        self._register_event_handler("on_dialout_answered")
        self._register_event_handler("on_dialout_connected")
        self._register_event_handler("on_dialout_stopped")
        self._register_event_handler("on_dialout_error")
        self._register_event_handler("on_dialout_warning")
        self._register_event_handler("on_first_participant_joined")
        self._register_event_handler("on_participant_joined")
        self._register_event_handler("on_participant_left")
        self._register_event_handler("on_participant_updated")
        self._register_event_handler("on_transcription_message")
        self._register_event_handler("on_recording_started")
        self._register_event_handler("on_recording_stopped")
        self._register_event_handler("on_recording_error")
        self._register_event_handler("on_before_leave", sync=True)

        # Add our new network stats event handler
        self._register_event_handler("on_network_stats_updated")
