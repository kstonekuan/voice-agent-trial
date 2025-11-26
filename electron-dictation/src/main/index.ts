import { join } from "node:path";
import {
	app,
	BrowserWindow,
	globalShortcut,
	ipcMain,
	Menu,
	nativeImage,
	screen,
	Tray,
} from "electron";

// Extend Electron's App type to include isQuitting flag
declare module "electron" {
	interface App {
		isQuitting?: boolean;
	}
}

let mainWindow: BrowserWindow | null = null;
let overlayWindow: BrowserWindow | null = null;
let tray: Tray | null = null;

// Server configuration
const SERVER_URL = "ws://127.0.0.1:8765";

// Recording state
let isRecording = false;

function createMainWindow(): void {
	mainWindow = new BrowserWindow({
		width: 450,
		height: 350,
		show: false,
		webPreferences: {
			preload: join(__dirname, "../preload/index.js"),
			contextIsolation: true,
			nodeIntegration: false,
		},
	});

	// Load the renderer
	if (process.env.ELECTRON_RENDERER_URL) {
		mainWindow.loadURL(process.env.ELECTRON_RENDERER_URL);
	} else {
		mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
	}

	mainWindow.on("close", (event) => {
		if (!app.isQuitting) {
			event.preventDefault();
			mainWindow?.hide();
		}
	});
}

function positionOverlayBottomRight(): void {
	if (!overlayWindow) return;
	const primaryDisplay = screen.getPrimaryDisplay();
	const { width, height } = primaryDisplay.workAreaSize;
	const windowBounds = overlayWindow.getBounds();
	const x = width - windowBounds.width - 20;
	const y = height - windowBounds.height - 20;
	console.log(
		`Positioning overlay to: ${x}, ${y} (screen: ${width}x${height})`,
	);
	overlayWindow.setPosition(x, y);
}

function createOverlayWindow(): void {
	const primaryDisplay = screen.getPrimaryDisplay();
	const { width, height } = primaryDisplay.workAreaSize;

	overlayWindow = new BrowserWindow({
		width: 200,
		height: 80,
		x: width - 220,
		y: height - 100,
		frame: false,
		transparent: true,
		skipTaskbar: true,
		resizable: false,
		focusable: false, // Don't steal focus from other windows
		type: "toolbar", // Better always-on-top behavior on Linux/X11
		webPreferences: {
			preload: join(__dirname, "../preload/index.js"),
			contextIsolation: true,
			nodeIntegration: false,
		},
	});

	// Set always on top with highest level for Linux compatibility
	overlayWindow.setAlwaysOnTop(true, "screen-saver");
	overlayWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

	// Load overlay page
	if (process.env.ELECTRON_RENDERER_URL) {
		overlayWindow.loadURL(`${process.env.ELECTRON_RENDERER_URL}/overlay.html`);
	} else {
		overlayWindow.loadFile(join(__dirname, "../renderer/overlay.html"));
	}

	// Position and show after content loads
	overlayWindow.webContents.once("did-finish-load", () => {
		positionOverlayBottomRight();
		overlayWindow?.show();
		// Re-apply always on top after show (helps on some WMs)
		overlayWindow?.setAlwaysOnTop(true, "screen-saver");
	});
}

function createTray(): void {
	const icon = nativeImage.createEmpty();
	tray = new Tray(icon);

	const contextMenu = Menu.buildFromTemplate([
		{
			label: "Show Window",
			click: () => mainWindow?.show(),
		},
		{
			label: "Quit",
			click: () => {
				app.isQuitting = true;
				app.quit();
			},
		},
	]);

	tray.setToolTip("Voice Dictation");
	tray.setContextMenu(contextMenu);
	tray.on("click", () => {
		mainWindow?.isVisible() ? mainWindow.hide() : mainWindow?.show();
	});
}

function sendToOverlay(channel: string): void {
	try {
		if (overlayWindow && !overlayWindow.isDestroyed()) {
			overlayWindow.webContents.send(channel);
		}
	} catch (error) {
		console.error(`Failed to send ${channel} to overlay:`, error);
	}
}

function registerHotkeys(): void {
	// Register Ctrl+Alt+R as toggle hotkey for recording
	const registered = globalShortcut.register("CommandOrControl+Alt+R", () => {
		if (isRecording) {
			isRecording = false;
			console.log("Hotkey pressed: Stopping recording");
			sendToOverlay("stop-recording");
		} else {
			isRecording = true;
			console.log("Hotkey pressed: Starting recording");
			sendToOverlay("start-recording");
		}
	});

	if (!registered) {
		console.error(
			"Failed to register global shortcut Ctrl+Alt+R - it may be in use by another application",
		);
	} else {
		console.log("Hotkey registered: Ctrl+Alt+R to toggle recording");
	}
}

// IPC Handlers
ipcMain.on("overlay-state", (_event, state: string) => {
	try {
		if (overlayWindow && !overlayWindow.isDestroyed()) {
			overlayWindow.webContents.send("update-state", state);
			if (state === "idle") {
				setTimeout(() => {
					if (overlayWindow && !overlayWindow.isDestroyed()) {
						overlayWindow.hide();
					}
				}, 1000);
			} else if (state === "recording") {
				overlayWindow.show();
			}
		}
	} catch (error) {
		console.error("Failed to handle overlay-state:", error);
	}
});

ipcMain.handle("type-text", async (_event, text: string) => {
	try {
		const { keyboard } = await import("@nut-tree-fork/nut-js");
		await keyboard.type(text);
		return { success: true };
	} catch (error) {
		console.error("Failed to type text:", error);
		return { success: false, error: (error as Error).message };
	}
});

ipcMain.handle("get-server-url", () => SERVER_URL);

app.whenReady().then(() => {
	createMainWindow();
	createOverlayWindow();
	createTray();
	registerHotkeys();
	mainWindow?.show();
});

app.on("will-quit", () => {
	globalShortcut.unregisterAll();
});

app.on("window-all-closed", () => {
	if (process.platform !== "darwin") {
		app.quit();
	}
});

app.on("activate", () => {
	if (BrowserWindow.getAllWindows().length === 0) {
		createMainWindow();
	}
});
