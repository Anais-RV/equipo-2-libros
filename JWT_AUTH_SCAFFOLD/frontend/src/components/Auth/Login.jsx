import { useState } from 'react';
import styles from './Login.module.css';

// Componente de Login/Register
// Patrón: Estado (memoria) → Envío (fetch) → Respuesta (token)
// Ver docs/FORMULARIOS_GUIA.md para entender cómo funciona

export default function Login({ onLoginSuccess }) {
  // MEMORIA: Guardamos lo que escribe el usuario
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // ENVÍO: Qué pasa cuando clickean login/register
  const handleSubmit = async (e) => {
    e.preventDefault(); // No recarga la página
    setError('');
    setLoading(true); // Mostrar "Cargando..."

    const endpoint = isLogin ? '/auth/login' : '/auth/register';

    try {
      // Enviar email + password al backend
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        setError('Email o contraseña incorrectos');
        return;
      }

      // Recibir token del backend
      const data = await response.json();
      // GUARDAR token para próximas peticiones (persistencia)
      localStorage.setItem('token', data.access_token);
      // Avisar al componente padre que logueó exitosamente
      onLoginSuccess(email, data.access_token);
    } catch (err) {
      setError('Error de conexión. Intenta de nuevo.');
    } finally {
      setLoading(false); // Esconder "Cargando..."
    }
  };

  // HTML: El formulario
  return (
    <div className={styles['auth-container']}>
      <form onSubmit={handleSubmit} className={styles['auth-form']}>
        <h2 className={styles['auth-title']}>
          {isLogin ? 'Iniciar Sesión' : 'Registrarse'}
        </h2>

        {error && <p className={styles['auth-error']}>{error}</p>}

        {/* SINCRONIZACIÓN: value + onChange conectan el input con la memoria */}
        <div className={styles['auth-field']}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tu@email.com"
            className={styles['auth-input']}
            disabled={loading}
            required
          />
        </div>

        <div className={styles['auth-field']}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Contraseña"
      