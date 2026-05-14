import { useState } from 'react';
import { sosAPI } from '../services/api';
import { ShieldAlert, Phone, MapPin } from 'lucide-react';

export default function SOSPage() {
  const [triggered, setTriggered] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSOS = async () => {
    if (triggered) return;
    setLoading(true);
    try {
      const res = await sosAPI.trigger();
      setResult(res.data);
      setTriggered(true);
    } catch (err) {
      alert('Failed to trigger SOS: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setTriggered(false);
    setResult(null);
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Emergency SOS</h2>
        <p>Trigger an emergency alert to notify your contacts</p>
      </div>

      <div className="sos-container">
        <button
          className={`sos-btn ${triggered ? 'active' : ''}`}
          onClick={handleSOS}
          disabled={loading || triggered}
        >
          {loading ? '...' : 'SOS'}
        </button>

        <p className="sos-subtitle">
          {triggered
            ? '🚨 Emergency alert has been sent! Your emergency contacts have been notified.'
            : 'Press the SOS button to immediately alert your emergency contacts with your current location.'}
        </p>

        {triggered && result && (
          <div className="card" style={{width:'100%',maxWidth:500,textAlign:'left'}}>
            <h3 style={{marginBottom:16,display:'flex',alignItems:'center',gap:8}}>
              <ShieldAlert size={20} style={{color:'var(--danger)'}} /> Alert Sent
            </h3>

            {result.alert && (
              <div style={{marginBottom:16}}>
                <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:8}}>
                  <MapPin size={16} style={{color:'var(--primary)'}} />
                  <span style={{fontSize:14}}>
                    {result.alert.latitude
                      ? `${result.alert.latitude.toFixed(6)}, ${result.alert.longitude.toFixed(6)}`
                      : 'Location unavailable'}
                  </span>
                </div>
                <div className="badge badge-danger">Critical SOS Alert</div>
              </div>
            )}

            {result.contacts_notified?.length > 0 && (
              <div>
                <h4 style={{fontSize:14,color:'var(--text-secondary)',marginBottom:8}}>Contacts Notified:</h4>
                {result.contacts_notified.map((c, i) => (
                  <div key={i} style={{display:'flex',alignItems:'center',gap:8,padding:'8px 0',borderTop:'1px solid var(--border)'}}>
                    <Phone size={14} style={{color:'var(--success)'}} />
                    <span>{c.name}</span>
                    <span style={{color:'var(--text-muted)',marginLeft:'auto',fontSize:13}}>{c.phone}</span>
                  </div>
                ))}
              </div>
            )}

            <button className="btn btn-outline" style={{marginTop:20,width:'100%',justifyContent:'center'}} onClick={handleReset}>
              Reset SOS
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
