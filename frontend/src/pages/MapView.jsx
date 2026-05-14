import { useState, useEffect } from 'react';
import { dashboardAPI } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const helmetIcon = new L.DivIcon({
  html: '<div style="background:#6366f1;width:28px;height:28px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 15px rgba(99,102,241,0.6);display:flex;align-items:center;justify-content:center;font-size:14px;">🏍️</div>',
  iconSize: [28, 28],
  className: '',
});

const alertIcon = new L.DivIcon({
  html: '<div style="background:#ef4444;width:20px;height:20px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 10px rgba(239,68,68,0.5);"></div>',
  iconSize: [20, 20],
  className: '',
});

function MapUpdater({ center, mapRef }) {
  useEffect(() => {
    if (mapRef.current && center) {
      mapRef.current.setView(center, mapRef.current.getZoom());
    }
  }, [center, mapRef]);
  return null;
}

export default function MapView() {
  const [gps, setGps] = useState(null);
  const [trail, setTrail] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { subscribe } = useWebSocket();
  const mapRef = { current: null };

  useEffect(() => {
    Promise.all([
      dashboardAPI.gpsHistory(2),
      dashboardAPI.get(),
    ]).then(([gpsRes, dashRes]) => {
      const locations = gpsRes.data.results || gpsRes.data || [];
      if (locations.length > 0) {
        const latest = locations[locations.length - 1];
        setGps(latest);
        setTrail(locations.map(l => [l.latitude, l.longitude]));
      }
      const allAlerts = dashRes.data?.latest_alerts || [];
      setAlerts(allAlerts.filter(a => a.latitude && a.longitude));
    }).catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const unsub = subscribe('gps', (d) => {
      setGps(d);
      setTrail(prev => [...prev.slice(-200), [d.latitude, d.longitude]]);
    });
    const unsub2 = subscribe('alert', (d) => {
      if (d.latitude && d.longitude) setAlerts(prev => [d, ...prev]);
    });
    return () => { unsub(); unsub2(); };
  }, [subscribe]);

  const center = gps ? [gps.latitude, gps.longitude] : [27.7172, 85.3240];

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Live Map</h2>
        <p>Real-time GPS tracking & alert locations</p>
      </div>

      <div style={{display:'flex',gap:12,marginBottom:16,flexWrap:'wrap'}}>
        <div className="badge badge-primary">
          📍 {gps ? `${gps.latitude?.toFixed(6)}, ${gps.longitude?.toFixed(6)}` : 'Waiting for GPS...'}
        </div>
        {gps?.speed !== undefined && (
          <div className="badge badge-success">🏍️ {gps.speed?.toFixed(1)} km/h</div>
        )}
        <div className="badge badge-danger">🚨 {alerts.length} alert markers</div>
      </div>

      <div className="map-container full">
        <MapContainer
          center={center}
          zoom={15}
          style={{height:'100%',width:'100%'}}
          ref={(map) => { mapRef.current = map; }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          {trail.length > 1 && (
            <Polyline
              positions={trail}
              pathOptions={{ color: '#6366f1', weight: 3, opacity: 0.7, dashArray: '5,10' }}
            />
          )}
          {gps && (
            <Marker position={[gps.latitude, gps.longitude]} icon={helmetIcon}>
              <Popup><strong>Current Position</strong><br/>Speed: {gps.speed?.toFixed(1)} km/h</Popup>
            </Marker>
          )}
          {alerts.map((a, i) => (
            <Marker key={a.id || i} position={[a.latitude, a.longitude]} icon={alertIcon}>
              <Popup>
                <strong style={{color:'#ef4444'}}>⚠️ {a.alert_type}</strong><br/>
                {a.message}<br/>
                <small>{new Date(a.created_at).toLocaleString()}</small>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
