import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, Map, Bell, ShieldAlert, Settings, LogOut, Wifi, WifiOff
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/map', icon: Map, label: 'Live Map' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/sos', icon: ShieldAlert, label: 'Emergency SOS' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar({ isConnected }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">🏍️</div>
        <div>
          <h1>SmartHelmetX</h1>
          <span>IoT Safety System</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <Icon size={20} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className={`conn-status ${isConnected ? 'online' : 'offline'}`}>
          <div className={`conn-dot ${isConnected ? 'online' : 'offline'}`} />
          {isConnected ? (
            <><Wifi size={14} /> Live Connected</>
          ) : (
            <><WifiOff size={14} /> Disconnected</>
          )}
        </div>
        <button className="nav-link" onClick={handleLogout} style={{ marginTop: 8 }}>
          <LogOut size={20} />
          {user?.username || 'Logout'}
        </button>
      </div>
    </aside>
  );
}
