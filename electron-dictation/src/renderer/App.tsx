import "./styles.css";

export default function App() {
	return (
		<div className="app">
			<h1>Voice Dictation</h1>

			<div className="instructions">
				<h3>How to use:</h3>
				<p>
					Press <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Space</kbd> to toggle
					recording
				</p>
				<p>Or click the overlay to toggle recording</p>
			</div>

			<div className="info">
				<p>The overlay appears in the bottom-right corner of your screen.</p>
				<p>Speak clearly, and your text will be typed where your cursor is.</p>
			</div>
		</div>
	);
}
