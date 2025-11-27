import { join } from "node:path";
import {
	app,
	BrowserWindow,
	clipboard,
	globalShortcut,
	ipcMain,
	Menu,
	nativeImage,
	screen,
	Tray,
} from "electron";

// Helper for delays (like VoiceTypr's 50ms timing)
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

let mainWindow: BrowserWindow | null = null;
let overlayWindow: BrowserWindow | null = null;
let tray: Tray | null = null;

// Server configuration
const SERVER_URL = "ws://127.0.0.1:8765";

// App state
let isQuitting = false;
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
		if (!isQuitting) {
			event.preventDefault();
			mainWindow?.hide();
		}
	});
}

function positionOverlayBottomRight(): void {
	if (!overlayWindow) return;
	const primaryDisplay = screen.getPrimaryDisplay();
	// Use bounds instead of workAreaSize to ignore dock/taskbar inset
	const { width, height } = primaryDisplay.bounds;

	// Use fixed window size since content may not be rendered yet
	const windowWidth = 200;
	const windowHeight = 80;

	// Position with minimal margin (10px) to ensure it's truly at bottom-right
	const x = width - windowWidth - 10;
	const y = height - windowHeight - 10;

	console.log(
		`Positioning overlay to: ${x}, ${y} (bounds: ${width}x${height})`,
	);
	overlayWindow.setPosition(x, y);
}

function createOverlayWindow(): void {
	const primaryDisplay = screen.getPrimaryDisplay();
	const { width, height } = primaryDisplay.bounds;

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
		hasShadow: false, // Cleaner overlay appearance
		thickFrame: false, // Prevents Windows taskbar issues
		type: "notification", // Better always-on-top behavior on Linux/X11
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

	// Enable mouse event pass-through by default (prevents focus stealing)
	overlayWindow.setIgnoreMouseEvents(true, { forward: true });

	// Poll cursor position to toggle mouse events when hovering over overlay
	// This is more reliable than renderer-based detection
	let lastIgnoreState = true;
	const cursorCheckInterval = setInterval(() => {
		if (!overlayWindow || overlayWindow.isDestroyed()) {
			clearInterval(cursorCheckInterval);
			return;
		}

		const cursorPoint = screen.getCursorScreenPoint();
		const windowBounds = overlayWindow.getBounds();

		const isOverOverlay =
			cursorPoint.x >= windowBounds.x &&
			cursorPoint.x <= windowBounds.x + windowBounds.width &&
			cursorPoint.y >= windowBounds.y &&
			cursorPoint.y <= windowBounds.y + windowBounds.height;

		// Only update if state changed to avoid unnecessary calls
		if (isOverOverlay && lastIgnoreState) {
			overlayWindow.setIgnoreMouseEvents(false);
			lastIgnoreState = false;
		} else if (!isOverOverlay && !lastIgnoreState) {
			overlayWindow.setIgnoreMouseEvents(true, { forward: true });
			lastIgnoreState = true;
		}
	}, 50); // Check every 50ms

	overlayWindow.on("closed", () => {
		clearInterval(cursorCheckInterval);
	});

	// Position and show after content loads
	overlayWindow.webContents.once("did-finish-load", () => {
		// Small delay to ensure content is rendered before positioning
		setTimeout(() => {
			positionOverlayBottomRight();
			overlayWindow?.show();
			// Re-apply always on top after show (helps on some WMs)
			overlayWindow?.setAlwaysOnTop(true, "screen-saver");
		}, 100);
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
				isQuitting = true;
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
	console.log("=== Attempting to register hotkeys ===");
	console.log("Platform:", process.platform);
	console.log("Display:", process.env.DISPLAY);

	// Register Ctrl+Alt+Space as toggle hotkey for recording
	const shortcut = "CommandOrControl+Alt+Space";
	const registered = globalShortcut.register(shortcut, () => {
		console.log("=== HOTKEY CALLBACK TRIGGERED ===");
		if (isRecording) {
			isRecording = false;
			console.log("Hotkey pressed: Stopping recording");
			sendToOverlay("stop-recording");
		} else {
			isRecording = true;
			console.log("Hotkey pressed: Starting recording");
			// Show overlay and re-apply always-on-top
			if (overlayWindow && !overlayWindow.isDestroyed()) {
				overlayWindow.show();
				overlayWindow.setAlwaysOnTop(true, "screen-saver");
			}
			sendToOverlay("start-recording");
		}
	});

	console.log("Registration result:", registered);
	console.log("isRegistered check:", globalShortcut.isRegistered(shortcut));

	if (!registered) {
		console.error(
			"Failed to register global shortcut Ctrl+Alt+Space - it may be in use by another application",
		);
	} else {
		console.log("Hotkey registered: Ctrl+Alt+Space to toggle recording");
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
				// Re-apply always-on-top after showing
				overlayWindow.setAlwaysOnTop(true, "screen-saver");
			}
		}
	} catch (error) {
		console.error("Failed to handle overlay-state:", error);
	}
});

ipcMain.handle("type-text", async (_event, text: string) => {
	try {
		const { keyboard, Key } = await import("@nut-tree-fork/nut-js");

		// 1. Save existing clipboard content (Wispr Flow approach)
		let previousClipboard: string | undefined;
		try {
			previousClipboard = clipboard.readText();
		} catch {
			// Clipboard may be empty or contain non-text
		}

		// 2. Copy transcribed text to clipboard
		clipboard.writeText(text);

		// 3. Small delay to ensure clipboard is set
		await delay(50);

		// 4. Simulate paste based on platform
		const isMac = process.platform === "darwin";
		const modifier = isMac ? Key.LeftCmd : Key.LeftControl;

		// Press modifier + V with timing like VoiceTypr
		await keyboard.pressKey(modifier);
		await delay(50);
		await keyboard.pressKey(Key.V);
		await delay(50);
		await keyboard.releaseKey(Key.V);
		await delay(50);
		await keyboard.releaseKey(modifier);

		// 5. Restore previous clipboard after paste completes (Wispr Flow approach)
		if (previousClipboard !== undefined) {
			setTimeout(() => {
				try {
					clipboard.writeText(previousClipboard);
				} catch {
					// Ignore errors restoring clipboard
				}
			}, 100);
		}

		return { success: true };
	} catch (error) {
		console.error("Failed to paste text:", error);
		// Graceful degradation: text is still in clipboard for manual paste
		return { success: false, error: (error as Error).message };
	}
});

ipcMain.handle("get-server-url", () => SERVER_URL);

// Handle mouse event toggling for overlay (prevents focus stealing)
ipcMain.on("set-ignore-mouse-events", (_event, ignore: boolean) => {
	if (overlayWindow && !overlayWindow.isDestroyed()) {
		overlayWindow.setIgnoreMouseEvents(ignore, { forward: true });
	}
});

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

// Handle SIGINT/SIGTERM for clean shutdown (fixes zombie processes on Ctrl+C)
process.on("SIGINT", () => {
	console.log("Received SIGINT, quitting...");
	isQuitting = true;
	app.quit();
});

process.on("SIGTERM", () => {
	console.log("Received SIGTERM, quitting...");
	isQuitting = true;
	app.quit();
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
