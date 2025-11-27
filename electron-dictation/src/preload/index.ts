import { contextBridge, ipcRenderer } from "electron";

export type OverlayState = "idle" | "recording" | "processing";

export interface TypeTextResult {
	success: boolean;
	error?: string;
}

export interface ElectronAPI {
	setOverlayState: (state: OverlayState) => void;
	onStartRecording: (callback: () => void) => () => void;
	onStopRecording: (callback: () => void) => () => void;
	onUpdateState: (callback: (state: OverlayState) => void) => () => void;
	typeText: (text: string) => Promise<TypeTextResult>;
	getServerUrl: () => Promise<string>;
	setIgnoreMouseEvents: (ignore: boolean) => void;
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

	onUpdateState: (callback) => {
		const handler = (_event: Electron.IpcRendererEvent, state: OverlayState) =>
			callback(state);
		ipcRenderer.on("update-state", handler);
		return () => {
			ipcRenderer.removeListener("update-state", handler);
		};
	},

	typeText: (text) => ipcRenderer.invoke("type-text", text),

	getServerUrl: () => ipcRenderer.invoke("get-server-url"),

	setIgnoreMouseEvents: (ignore) =>
		ipcRenderer.send("set-ignore-mouse-events", ignore),
};

contextBridge.exposeInMainWorld("electronAPI", electronAPI);
