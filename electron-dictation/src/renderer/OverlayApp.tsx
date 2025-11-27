import { PipecatClient, RTVIEvent } from "@pipecat-ai/client-js";
import {
	PipecatClientProvider,
	usePipecatClient,
} from "@pipecat-ai/client-react";
import { ThemeProvider, UserAudioComponent } from "@pipecat-ai/voice-ui-kit";
import { WebSocketTransport } from "@pipecat-ai/websocket-transport";
import { useCallback, useEffect, useRef, useState } from "react";
import type { ElectronAPI } from "../preload/index";
import "./app.css";

declare global {
	interface Window {
		electronAPI: ElectronAPI;
	}
}

function RecordingControl() {
	const client = usePipecatClient();
	const [isRecording, setIsRecording] = useState(false);
	const isRecordingRef = useRef(false);
	const clientRef = useRef(client);

	// Keep refs in sync
	useEffect(() => {
		isRecordingRef.current = isRecording;
	}, [isRecording]);

	useEffect(() => {
		clientRef.current = client;
	}, [client]);

	const startRecording = useCallback(async () => {
		const currentClient = clientRef.current;
		if (isRecordingRef.current || !currentClient) return;
		isRecordingRef.current = true;
		setIsRecording(true);
		try {
			const serverUrl = await window.electronAPI.getServerUrl();
			await currentClient.connect({ wsUrl: serverUrl });
		} catch (error) {
			console.error("Failed to connect:", error);
			isRecordingRef.current = false;
			setIsRecording(false);
		}
	}, []);

	const stopRecording = useCallback(async () => {
		const currentClient = clientRef.current;
		if (!isRecordingRef.current || !currentClient) return;
		isRecordingRef.current = false;
		setIsRecording(false);
		try {
			await currentClient.disconnect();
		} catch (error) {
			console.error("Failed to disconnect:", error);
		}
	}, []);

	// Hotkey events (toggle mode) from main process - register ONCE
	useEffect(() => {
		const unsubscribeStart = window.electronAPI.onStartRecording(() => {
			startRecording();
		});

		const unsubscribeStop = window.electronAPI.onStopRecording(() => {
			stopRecording();
		});

		return () => {
			unsubscribeStart?.();
			unsubscribeStop?.();
		};
	}, [startRecording, stopRecording]);

	// Click handler (toggle mode)
	const handleClick = useCallback(() => {
		if (isRecording) {
			stopRecording();
		} else {
			startRecording();
		}
	}, [isRecording, startRecording, stopRecording]);

	// Handle transcript and type text
	useEffect(() => {
		if (!client) return;

		const handleTranscript = async (data: { text?: string }) => {
			if (data.text) {
				await window.electronAPI.typeText(data.text);
				window.electronAPI.setOverlayState("idle");
			}
		};

		client.on(RTVIEvent.BotTranscript, handleTranscript);
		client.on(RTVIEvent.ServerMessage, async (message: unknown) => {
			const msg = message as { type?: string; text?: string };
			if (msg.type === "transcript" && msg.text) {
				await window.electronAPI.typeText(msg.text);
				window.electronAPI.setOverlayState("idle");
			}
		});

		return () => {
			client.off(RTVIEvent.BotTranscript, handleTranscript);
		};
	}, [client]);

	return (
		<UserAudioComponent
			onClick={handleClick}
			isMicEnabled={isRecording}
			noDevicePicker={true}
		/>
	);
}

export default function OverlayApp() {
	const [client, setClient] = useState<PipecatClient | null>(null);
	const [devicesReady, setDevicesReady] = useState(false);

	useEffect(() => {
		const transport = new WebSocketTransport();
		const pipecatClient = new PipecatClient({
			transport,
			enableMic: true,
			enableCam: false,
		});
		setClient(pipecatClient);

		// Initialize devices to request permissions and enumerate mics
		pipecatClient
			.initDevices()
			.then(() => {
				console.log("Devices initialized");
				setDevicesReady(true);
			})
			.catch((error) => {
				console.error("Failed to initialize devices:", error);
				// Still set ready so UI shows, user can try again
				setDevicesReady(true);
			});

		return () => {
			pipecatClient.disconnect();
		};
	}, []);

	if (!client || !devicesReady) return null;

	return (
		<ThemeProvider>
			<PipecatClientProvider client={client}>
				<RecordingControl />
			</PipecatClientProvider>
		</ThemeProvider>
	);
}
