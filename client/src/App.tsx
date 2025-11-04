import { Link, Route, Routes, useLocation } from 'react-router-dom';
import { DailyPage } from './pages/DailyPage';
import { WebRTCPage } from './pages/WebRTCPage';
import './App.css';

function Navigation() {
  const location = useLocation();

  return (
    <nav
      style={{
        padding: '1rem',
        borderBottom: '1px solid #333',
        display: 'flex',
        gap: '1rem',
        backgroundColor: '#1a1a1a',
      }}
    >
      <Link
        to="/daily"
        style={{
          padding: '0.5rem 1rem',
          borderRadius: '4px',
          textDecoration: 'none',
          color: 'white',
          backgroundColor: location.pathname === '/daily' ? '#4a4a4a' : '#2a2a2a',
        }}
      >
        Daily Transport
      </Link>
      <Link
        to="/webrtc"
        style={{
          padding: '0.5rem 1rem',
          borderRadius: '4px',
          textDecoration: 'none',
          color: 'white',
          backgroundColor: location.pathname === '/webrtc' ? '#4a4a4a' : '#2a2a2a',
        }}
      >
        WebRTC Transport
      </Link>
    </nav>
  );
}

function App() {
  return (
    <div>
      <Navigation />
      <Routes>
        <Route path="/" element={<DailyPage />} />
        <Route path="/daily" element={<DailyPage />} />
        <Route path="/webrtc" element={<WebRTCPage />} />
      </Routes>
    </div>
  );
}

export default App;
