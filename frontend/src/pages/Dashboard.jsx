import { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import { Activity, MapPin, Bell, ShieldCheck, Zap, Gauge } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix leaflet default icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const helmetIcon = new L.DivIcon({
  html: '<div style="background:#6366f1;width:24px;height:24px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 10px rgba(99,102,241,0.5);"></div>',
  iconSize: [24, 24],
  className: '',
});

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [sensorData, setSensorData] = useState([]);
  const [gps, setGps] = useState(null);
  const [loading, setLoading] = useState(true);
  const { subscribe } = useWebSocket();

  useEffect(() => {
    dashboardAPI.get()
      .then(res => {
        setData(res.data);
        setSensorData(res.data.sensor_data || []);
        if (res.data.latest_gps) setGps(res.data.latest_gps);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const unsub1 = subscribe('sensor', (d) => {
      setSensorData(prev => [...prev.slice(-49), {
        timestamp: d.timestamp,
        acc_x: d.acc_x, acc_y: d.acc_y, acc_z: d.acc_z,
      }]);
    });
    const unsub2 = subscribe('gps', (d) => setGps(d));
    const unsub3 = subscribe('alert', (d) => {
      setData(prev => prev ? {
        ...prev,
        active_alerts: prev.active_alerts + 1,
        alerts_today: prev.alerts_today + 1,
        latest_alerts: [d, ...prev.latest_alerts.slice(0, 9)],
      } : prev);
    });
    return () => { unsub1(); unsub2(); unsub3(); };
  }, [subscribe]);

  if (loading) return <div className="fade-in" style={{padding:40,textAlign:'center',color:'var(--text-secondary)'}}>Loading dashboard...</div>;

  const chartData = sensorData.map((s, i) => ({
    name: i,
    X: parseFloat(s.acc_x?.toFixed(3)),
    Y: parseFloat(s.acc_y?.toFixed(3)),
    Z: parseFloat(s.acc_z?.toFixed(3)),
  }));

  const device = data?.device;
  const mapCenter = gps ? [gps.latitude, gps.longitude] : [27.7172, 85.3240];

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Real-time helmet monitoring & safety overview</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon primary"><Activity size={24} /></div>
          <div>
            <div className="stat-value">{device?.status === 'online' ? '🟢' : '🔴'}</div>
            <div className="stat-label">Device {device?.status || 'offline'}</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon success"><Gauge size={24} /></div>
          <div>
            <div className="stat-value">{device?.battery_level || 0}%</div>
            <div className="stat-label">Battery Level</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon danger"><Bell size={24} /></div>
          <div>
            <div className="stat-value">{data?.active_alerts || 0}</div>
            <div className="stat-label">Active Alerts</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon warning"><Zap size={24} /></div>
          <div>
            <div className="stat-value">{data?.alerts_today || 0}</div>
            <div className="stat-label">Alerts Today</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* Sensor Chart */}
        <div className="card">
          <h3 style={{marginBottom:16,fontSize:16,fontWeight:600,display:'flex',alignItems:'center',gap:8}}>
            <Activity size={18} style={{color:'var(--primary)'}} /> Accelerometer (Live)
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="name" tick={false} stroke="var(--text-muted)" />
              <YAxis stroke="var(--text-muted)" domain={[-3, 3]} />
              <Tooltip
                contentStyle={{ background:'var(--bg-card)', border:'1px solid var(--border)', borderRadius:8, color:'var(--text-primary)' }}
              />
              <Legend />
              <Line type="monotone" dataKey="X" stroke="#6366f1" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="Y" stroke="#10b981" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="Z" stroke="#f59e0b" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Mini Map */}
        <div className="card">
          <h3 style={{marginBottom:16,fontSize:16,fontWeight:600,display:'flex',alignItems:'center',gap:8}}>
            <MapPin size={18} style={{color:'var(--success)'}} /> Last Known Location
          </h3>
          <div className="map-container" style={{height:250}}>
            <MapContainer center={mapCenter} zoom={14} style={{height:'100%',width:'100%'}} scrollWheelZoom={false}>
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              />
              {gps && (
                <Marker position={[gps.latitude, gps.longitude]} icon={helmetIcon}>
                  <Popup>
                    <strong>SmartHelmetX</strong><br/>
                    Speed: {gps.speed?.toFixed(1)} km/h<br/>
                    {gps.latitude?.toFixed(6)}, {gps.longitude?.toFixed(6)}
                  </Popup>
                </Marker>
              )}
            </MapContainer>
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="card" style={{marginTop:4}}>
        <h3 style={{marginBottom:16,fontSize:16,fontWeight:600,display:'flex',alignItems:'center',gap:8}}>
          <ShieldCheck size={18} style={{color:'var(--danger)'}} /> Recent Alerts
        </h3>
        {data?.latest_alerts?.length > 0 ? (
          data.latest_alerts.map((alert, i) => (
            <div key={alert.id || i} className="alert-item">
              <div className={`alert-dot ${alert.severity}`} />
              <div style={{flex:1}}>
                <div style={{fontWeight:600,fontSize:14}}>{alert.type_display || alert.alert_type}</div>
                <div style={{fontSize:12,color:'var(--text-secondary)'}}>{alert.message}</div>
              </div>
              <span className={`badge badge-${alert.severity === 'critical' ? 'danger' : alert.severity === 'high' ? 'warning' : 'info'}`}>
                {alert.severity}
              </span>
              <span style={{fontSize:12,color:'var(--text-muted)',minWidth:80}}>
                {new Date(alert.created_at).toLocaleTimeString()}
              </span>
            </div>
          ))
        ) : (
          <div style={{textAlign:'center',padding:32,color:'var(--text-muted)'}}>
            <ShieldCheck size={32} style={{marginBottom:8,opacity:0.5}} /><br/>
            No alerts — all clear! 🎉
          </div>
        )}
      </div>
    </div>
  );
}
