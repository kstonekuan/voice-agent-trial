import { resolve } from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "electron-vite";

export default defineConfig({
	main: {
		build: {
			rollupOptions: {
				external: ["uiohook-napi", "@nut-tree-fork/nut-js"],
			},
		},
	},
	preload: {},
	renderer: {
		plugins: [react(), tailwindcss()],
		build: {
			rollupOptions: {
				input: {
					index: resolve(__dirname, "src/renderer/index.html"),
					overlay: resolve(__dirname, "src/renderer/overlay.html"),
				},
			},
		},
	},
});
