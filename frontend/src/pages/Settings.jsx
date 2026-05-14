import { useState, useEffect } from 'react';
import { contactsAPI, devicesAPI } from '../services/api';
import { Settings as SettingsIcon, Plus, Trash2, User, Phone, Heart, Cpu } from 'lucide-react';

export default function Settings() {
  const [contacts, setContacts] = useState([]);
  const [device, setDevice] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', phone: '', relationship: '', is_primary: false });

  useEffect(() => {
    contactsAPI.list().then(res => setContacts(res.data.results || res.data || [])).catch(() => {});
    devicesAPI.list().then(res => {
      const devices = res.data.results || res.data || [];
      if (devices.length > 0) setDevice(devices[0]);
    }).catch(() => {});
  }, []);

  const handleAddContact = async (e) => {
    e.preventDefault();
    try {
      await contactsAPI.create(form);
      const res = await contactsAPI.list();
      setContacts(res.data.results || res.data || []);
      setForm({ name: '', phone: '', relationship: '', is_primary: false });
      setShowForm(false);
    } catch (err) {
      alert('Error: ' + JSON.stringify(err.response?.data));
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this contact?')) return;
    await contactsAPI.delete(id);
    setContacts(contacts.filter(c => c.id !== id));
  };

  const handleDeviceUpdate = async (field, value) => {
    if (!device) return;
    try {
      const res = await devicesAPI.update(device.id, { [field]: value });
      setDevice(res.data);
    } catch {}
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Settings</h2>
        <p>Manage your emergency contacts and device configuration</p>
      </div>

      {/* Emergency Contacts */}
      <div className="settings-section">
        <h3><Phone size={20} style={{color:'var(--primary)'}} /> Emergency Contacts</h3>
        <div className="card">
          {contacts.map(c => (
            <div key={c.id} className="contact-card">
              <div style={{display:'flex',alignItems:'center',gap:12}}>
                <div className="stat-icon primary" style={{width:40,height:40}}>
                  <User size={18} />
                </div>
                <div>
                  <div style={{fontWeight:600,display:'flex',alignItems:'center',gap:8}}>
                    {c.name}
                    {c.is_primary && <span className="badge badge-primary" style={{fontSize:10}}>Primary</span>}
                  </div>
                  <div style={{fontSize:13,color:'var(--text-secondary)'}}>{c.phone} {c.relationship && `· ${c.relationship}`}</div>
                </div>
              </div>
              <button className="btn btn-sm btn-outline" onClick={() => handleDelete(c.id)}>
                <Trash2 size={14} />
              </button>
            </div>
          ))}

          {showForm ? (
            <form onSubmit={handleAddContact} style={{padding:16,background:'var(--bg-secondary)',borderRadius:'var(--radius-sm)',marginTop:12}}>
              <div className="grid-2" style={{marginBottom:0}}>
                <div className="form-group">
                  <label>Name</label>
                  <input className="form-control" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input className="form-control" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} required placeholder="+977..." />
                </div>
              </div>
              <div className="grid-2" style={{marginBottom:0}}>
                <div className="form-group">
                  <label>Relationship</label>
                  <input className="form-control" value={form.relationship} onChange={e => setForm({...form, relationship: e.target.value})} placeholder="e.g. Parent" />
                </div>
                <div className="form-group" style={{display:'flex',alignItems:'flex-end',paddingBottom:20}}>
                  <label style={{display:'flex',alignItems:'center',gap:8,cursor:'pointer'}}>
                    <input type="checkbox" checked={form.is_primary} onChange={e => setForm({...form, is_primary: e.target.checked})} />
                    Primary contact
                  </label>
                </div>
              </div>
              <div style={{display:'flex',gap:8}}>
                <button type="submit" className="btn btn-primary"><Plus size={16} /> Add Contact</button>
                <button type="button" className="btn btn-outline" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          ) : (
            <button className="btn btn-outline" style={{marginTop:12}} onClick={() => setShowForm(true)}>
              <Plus size={16} /> Add Emergency Contact
            </button>
          )}
        </div>
      </div>

      {/* Device Config */}
      {device && (
        <div className="settings-section">
          <h3><Cpu size={20} style={{color:'var(--success)'}} /> Device Configuration</h3>
          <div className="card">
            <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:20}}>
              <div>
                <div style={{fontSize:13,color:'var(--text-secondary)',marginBottom:4}}>Device ID</div>
                <div style={{fontWeight:600}}>{device.device_id}</div>
              </div>
              <div>
                <div style={{fontSize:13,color:'var(--text-secondary)',marginBottom:4}}>Firmware</div>
                <div style={{fontWeight:600}}>{device.firmware_version}</div>
              </div>
              <div>
                <div style={{fontSize:13,color:'var(--text-secondary)',marginBottom:4}}>BLE MAC</div>
                <div style={{fontWeight:600}}>{device.ble_mac || 'Not configured'}</div>
              </div>
              <div>
                <div style={{fontSize:13,color:'var(--text-secondary)',marginBottom:4}}>Status</div>
                <div className={`badge ${device.status === 'online' ? 'badge-success' : 'badge-danger'}`}>{device.status}</div>
              </div>
            </div>

            <div style={{marginTop:24,borderTop:'1px solid var(--border)',paddingTop:20}}>
              <label style={{fontSize:13,color:'var(--text-secondary)',display:'block',marginBottom:8}}>
                Fall Detection Threshold: <strong style={{color:'var(--text-primary)'}}>{device.fall_threshold}g</strong>
              </label>
              <div className="slider-group">
                <span style={{fontSize:12,color:'var(--text-muted)'}}>1.0g</span>
                <input type="range" min="1.0" max="4.0" step="0.1"
                  value={device.fall_threshold}
                  onChange={e => handleDeviceUpdate('fall_threshold', parseFloat(e.target.value))} />
                <span style={{fontSize:12,color:'var(--text-muted)'}}>4.0g</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
