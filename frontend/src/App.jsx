import { BrowserRouter, Routes, Route, Outlet } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { useWebSocket } from './hooks/useWebSocket';
import ProtectedRoute from './components/ProtectedRoute';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import MapView from './pages/MapView';
import Alerts from './pages/Alerts';
import SOSPage from './pages/SOSPage';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';

function AppLayout() {
  const { isConnected } = useWebSocket();
  return (
    <div className="app-layout">
      <Sidebar isConnected={isConnected} />
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/map" element={<MapView />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/sos" element={<SOSPage />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
