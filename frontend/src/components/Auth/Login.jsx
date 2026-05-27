import { useState } from 'react';

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const endpoint = isLogin ? '/auth/login' : '/auth/register';

    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || 'Error al conectar');
        return;
      }

      const data = await response.json();
      onLoginSuccess(email, data.access_token);
    } catch (err) {
      setError('Error de conexión con el backend');
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '100px auto', padding: '2rem',
      background: '#f4ece0', borderRadius: '12px', color: '#3a2c20',
      border: '1px solid rgba(120,85,60,.20)',
      boxShadow: '0 8px 30px rgba(90,60,40,.18)' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
        🦄 {isLogin ? 'Iniciar sesión' : 'Registrarse'}
      </h2>

      {error && (
        <p style={{
          color: '#8a4a32', background: '#f0dcd0',
          border: '1px solid #dcc0ad', borderRadius: '6px',
          padding: '10px', marginBottom: '1rem', fontSize: '0.9rem'
        }}>{error}</p>
      )}

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
          style={{ width: '100%', padding: '12px', marginBottom: '1rem',
            borderRadius: '6px', border: '1px solid rgba(120,85,60,.28)',
            background: '#ffffff', color: '#3a2c20', boxSizing: 'border-box' }}
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Contraseña"
          required
          style={{ width: '100%', padding: '12px', marginBottom: '1rem',
            borderRadius: '6px', border: '1px solid rgba(120,85,60,.28)',
            background: '#ffffff', color: '#3a2c20', boxSizing: 'border-box' }}
        />
        <button type="submit"
          style={{ width: '100%', padding: '12px', background: '#a98467',
            color: '#ffffff', border: 'none', borderRadius: '6px', cursor: 'pointer',
            fontWeight: 'bold', fontSize: '1rem' }}>
          {isLogin ? 'Entrar' : 'Crear cuenta'}
        </button>
      </form>

      <button onClick={() => setIsLogin(!isLogin)}
        style={{ width: '100%', marginTop: '1rem', padding: '10px',
          background: 'transparent', color: '#6b5947',
          border: '1px solid rgba(120,85,60,.28)',
          borderRadius: '6px', cursor: 'pointer' }}>
        {isLogin ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Entra'}
      </button>
    </div>
  );
}
