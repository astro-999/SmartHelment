import { useState, useEffect } from 'react';
import { alertsAPI } from '../services/api';
import { Bell, CheckCircle, XCircle, Filter } from 'lucide-react';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  const fetchAlerts = () => {
    const params = filter !== 'all' ? { status: filter } : {};
    alertsAPI.list(params)
      .then(res => setAlerts(res.data.results || res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchAlerts(); }, [filter]);

  const handleResolve = async (id) => {
    await alertsAPI.resolve(id);
    fetchAlerts();
  };

  const handleCancel = async (id) => {
    await alertsAPI.cancel(id);
    fetchAlerts();
  };

  const severityColor = { critical: 'danger', high: 'warning', medium: 'info', low: 'success' };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Alerts</h2>
        <p>View and manage all safety alerts</p>
      </div>

      <div style={{display:'flex',gap:8,marginBottom:20,flexWrap:'wrap'}}>
        <Filter size={18} style={{color:'var(--text-muted)',marginTop:6}} />
        {['all','active','resolved','cancelled'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-outline'}`}>
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      <div className="card">
        {loading ? (
          <div style={{padding:32,textAlign:'center',color:'var(--text-muted)'}}>Loading alerts...</div>
        ) : alerts.length === 0 ? (
          <div style={{padding:48,textAlign:'center',color:'var(--text-muted)'}}>
            <Bell size={48} style={{opacity:0.3,marginBottom:12}} /><br/>
            No alerts found
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th></th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Message</th>
                  <th>Location</th>
                  <th>Time</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map(alert => (
                  <tr key={alert.id}>
                    <td><div className={`alert-dot ${alert.severity}`} /></td>
                    <td style={{fontWeight:600}}>{alert.type_display || alert.alert_type}</td>
                    <td><span className={`badge badge-${severityColor[alert.severity]}`}>{alert.severity}</span></td>
                    <td style={{maxWidth:200,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{alert.message}</td>
                    <td style={{fontSize:12,color:'var(--text-muted)'}}>
                      {alert.latitude ? `${alert.latitude.toFixed(4)}, ${alert.longitude.toFixed(4)}` : '—'}
                    </td>
                    <td style={{fontSize:12,whiteSpace:'nowrap'}}>{new Date(alert.created_at).toLocaleString()}</td>
                    <td>
                      <span className={`badge ${alert.status === 'active' ? 'badge-danger' : alert.status === 'resolved' ? 'badge-success' : 'badge-info'}`}>
                        {alert.status}
                      </span>
                    </td>
                    <td>
                      {alert.status === 'active' && (
                        <div style={{display:'flex',gap:4}}>
                          <button className="btn btn-sm btn-success" onClick={() => handleResolve(alert.id)} title="Resolve">
                            <CheckCircle size={14} />
                          </button>
                          <button className="btn btn-sm btn-outline" onClick={() => handleCancel(alert.id)} title="Cancel">
                            <XCircle size={14} />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
