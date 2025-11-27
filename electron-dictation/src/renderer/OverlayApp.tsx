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
	const [isWaitingForResponse, setIsWaitingForResponse] = useState(false);
	const isRecordingRef = useRef(false);
	const isWaitingForResponseRef = useRef(false);
	const responseTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const clientRef = useRef(client);

	// Keep refs in sync
	useEffect(() => {
		isRecordingRef.current = isRecording;
	}, [isRecording]);

	useEffect(() => {
		isWaitingForResponseRef.current = isWaitingForResponse;
	}, [isWaitingForResponse]);

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

	const stopRecording = useCallback(() => {
		const currentClient = clientRef.current;
		if (!isRecordingRef.current || !currentClient) return;
		isRecordingRef.current = false;
		setIsRecording(false);
		setIsWaitingForResponse(true);

		// Tell server to flush the transcription buffer
		try {
			currentClient.sendClientMessage("stop-recording", {});
		} catch (error) {
			console.error("Failed to send stop-recording message:", error);
		}

		// Clear any existing timeout
		if (responseTimeoutRef.current) {
			clearTimeout(responseTimeoutRef.current);
		}

		// Set a timeout to disconnect if no response in 10 seconds
		responseTimeoutRef.current = setTimeout(() => {
			if (isWaitingForResponseRef.current) {
				console.log("Response timeout - disconnecting");
				setIsWaitingForResponse(false);
				currentClient.disconnect().catch((error) => {
					console.error("Failed to disconnect on timeout:", error);
				});
			}
		}, 10000);
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

	// Handle transcript and type text, then disconnect
	useEffect(() => {
		if (!client) return;

		const handleResponseReceived = async (text: string) => {
			// Clear the timeout since we got a response
			if (responseTimeoutRef.current) {
				clearTimeout(responseTimeoutRef.current);
				responseTimeoutRef.current = null;
			}

			await window.electronAPI.typeText(text);
			window.electronAPI.setOverlayState("idle");

			// Disconnect after receiving response
			setIsWaitingForResponse(false);
			const currentClient = clientRef.current;
			if (currentClient) {
				try {
					await currentClient.disconnect();
				} catch (error) {
					console.error("Failed to disconnect after response:", error);
				}
			}
		};

		const handleBotTranscript = async (data: { text?: string }) => {
			if (data.text) {
				await handleResponseReceived(data.text);
			}
		};

		const handleServerMessage = async (message: unknown) => {
			const msg = message as { type?: string; text?: string };
			if (msg.type === "transcript" && msg.text) {
				await handleResponseReceived(msg.text);
			}
		};

		client.on(RTVIEvent.BotTranscript, handleBotTranscript);
		client.on(RTVIEvent.ServerMessage, handleServerMessage);

		return () => {
			client.off(RTVIEvent.BotTranscript, handleBotTranscript);
			client.off(RTVIEvent.ServerMessage, handleServerMessage);
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
