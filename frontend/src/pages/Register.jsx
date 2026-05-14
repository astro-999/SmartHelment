import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '', first_name: '', last_name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.password2) { setError('Passwords do not match'); return; }
    setLoading(true);
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(' ') : 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  return (
    <div className="auth-page">
      <div className="auth-card fade-in">
        <div style={{textAlign:'center',marginBottom:24}}>
          <div style={{fontSize:48,marginBottom:8}}>🏍️</div>
          <h2>Create Account</h2>
          <p className="subtitle">Join SmartHelmetX safety platform</p>
        </div>
        {error && <div className="badge badge-danger" style={{width:'100%',justifyContent:'center',padding:'10px',marginBottom:16}}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="grid-2" style={{marginBottom:0}}>
            <div className="form-group"><label>First Name</label><input className="form-control" value={form.first_name} onChange={update('first_name')} /></div>
            <div className="form-group"><label>Last Name</label><input className="form-control" value={form.last_name} onChange={update('last_name')} /></div>
          </div>
          <div className="form-group"><label>Username</label><input className="form-control" value={form.username} onChange={update('username')} required /></div>
          <div className="form-group"><label>Email</label><input type="email" className="form-control" value={form.email} onChange={update('email')} required /></div>
          <div className="form-group"><label>Password</label><input type="password" className="form-control" value={form.password} onChange={update('password')} required minLength={6} /></div>
          <div className="form-group"><label>Confirm Password</label><input type="password" className="form-control" value={form.password2} onChange={update('password2')} required /></div>
          <button type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{width:'100%',justifyContent:'center'}}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <div className="auth-footer">Already have an account? <Link to="/login">Sign in</Link></div>
      </div>
    </div>
  );
}
