import { contextBridge, ipcRenderer } from "electron";

export type OverlayState = "idle" | "recording";

export interface TypeTextResult {
	success: boolean;
	error?: string;
}

export interface ElectronAPI {
	setOverlayState: (state: OverlayState) => void;
	onStartRecording: (callback: () => void) => () => void;
	onStopRecording: (callback: () => void) => () => void;
	typeText: (text: string) => Promise<TypeTextResult>;
	getServerUrl: () => Promise<string>;
}

const electronAPI: ElectronAPI = {
	setOverlayState: (state) => ipcRenderer.send("overlay-state", state),

	onStartRecording: (callback) => {
		ipcRenderer.on("start-recording", callback);
		return () => {
			ipcRenderer.removeListener("start-recording", callback);
		};
	},

	onStopRecording: (callback) => {
		ipcRenderer.on("stop-recording", callback);
		return () => {
			ipcRenderer.removeListener("stop-recording", callback);
		};
	},

	typeText: (text) => ipcRenderer.invoke("type-text", text),

	getServerUrl: () => ipcRenderer.invoke("get-server-url"),
};

contextBridge.exposeInMainWorld("electronAPI", electronAPI);
