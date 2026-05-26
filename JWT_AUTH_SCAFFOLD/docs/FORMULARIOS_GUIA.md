# 📝 Formularios en React: Guía para Data Analysts

**Para:** Gente sin experiencia en frontend  
**Objetivo:** Entiendas cómo funciona un formulario login → backend

---

## El Patrón Básico (Sin React Complicado)

Un formulario hace 4 cosas:

```
1. Usuario escribe email + password
   ↓
2. Nosotros guardamos eso en "memoria" (estado)
   ↓
3. Usuario clickea "Login"
   ↓
4. Enviamos al backend, guardamos respuesta
```

---

## Código Mínimo: Un Formulario

```jsx
import { useState } from 'react';

export default function Login() {
  // 1. MEMORIA: dónde guardamos lo que el usuario escribe
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // 2. ENVIAR: qué pasa cuando clickean "Login"
  const handleSubmit = async (e) => {
    e.preventDefault(); // No recarga la página
    
    // Enviar al backend
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    // Guardar token
    localStorage.setItem('token', data.access_token);
    
    // Limpiar
    setEmail('');
    setPassword('');
  };

  // 3. HTML: El formulario
  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="tu@email.com"
        required
      />
      
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Contraseña"
        required
      />
      
      <button type="submit">Login</button>
    </form>
  );
}
```

**Eso es todo.** 20 líneas de código. Así funciona.

---

## ¿Qué Es Cada Cosa?

### `useState`
```jsx
const [email, setEmail] = useState('');
```
**Memoria:** Guardamos "email" en una caja mental.
- `email` = valor actual (""inicialmente)
- `setEmail()` = función para cambiar el valor
- Cuando cambias `setEmail('test@test.com')`, React redibuja el componente

### `onChange`
```jsx
<input onChange={(e) => setEmail(e.target.value)} />
```
**Sincronización:** Cada vez que el usuario escribe, actualizamos memoria.
- `e.target.value` = lo que está escrito en el input

### `onSubmit`
```jsx
<form onSubmit={handleSubmit}>
```
**Envío:** Cuando clickean botón, llamamos a `handleSubmit`

### `fetch()`
```jsx
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  body: JSON.stringify({ email, password })
});
```
**Comunica con backend:**
- URL: dónde está el backend
- `method: 'POST'`: enviar datos
- `body`: qué datos enviamos (email + password)

### `localStorage`
```jsx
localStorage.setItem('token', data.access_token);
```
**Guardar para después:** El navegador recuerda el token. Próximas peticiones lo usan.

---

## Paso a Paso: Cómo Construirlo

### 1. Crear archivo vacío
```bash
touch frontend/src/components/Login.jsx
```

### 2. Imports (siempre primero)
```jsx
import { useState } from 'react';
```

### 3. Crear componente
```jsx
export default function Login() {
  // Aquí va el código
  return <form>...</form>;
}
```

### 4. Agregar memoria (useState)
```jsx
const [email, setEmail] = useState('');
const [password, setPassword] = useState('');
```

### 5. Función para enviar
```jsx
const handleSubmit = async (e) => {
  e.preventDefault();
  // XXX TODO: fetch al backend
};
```

### 6. HTML del formulario
```jsx
<form onSubmit={handleSubmit}>
  <input ... />
  <button type="submit">Login</button>
</form>
```

---

## Ejemplo Completo: Login + Register

```jsx
import { useState } from 'react';

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true); // Toggle login/register
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
        setError('Error: ' + response.statusText);
        return;
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      
      // Avisar al padre (App.jsx) que el usuario logueó
      onLoginSuccess(email, data.access_token);
    } catch (err) {
      setError('Error de conexión: ' + err.message);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto' }}>
      <form onSubmit={handleSubmit}>
        <h2>{isLogin ? 'Login' : 'Registrarse'}</h2>
        
        {error && <p style={{ color: 'red' }}>{error}</p>}
        
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Contraseña"
          required
        />
        
        <button type="submit">
          {isLogin ? 'Login' : 'Registrarse'}
        </button>

        <button
          type="button"
          onClick={() => setIsLogin(!isLogin)}
          style={{ marginTop: '10px', width: '100%' }}
        >
          {isLogin
            ? '¿No tienes cuenta? Registrarse'
            : '¿Ya tienes cuenta? Login'}
        </button>
      </form>
    </div>
  );
}
```

---

## Integrar en App.jsx

Tu `App.jsx` debe hacer esto:

```jsx
import { useState } from 'react';
import Login from './components/Login';
import BookSearch from './components/BookSearch'; // Tu componente existente

export default function App() {
  // Recuperar token del navegador (si existe)
  const [token, setToken] = useState(() => 
    localStorage.getItem('token')
  );
  
  // Si NO hay token, mostrar login
  if (!token) {
    return (
      <Login 
        onLoginSuccess={(email, accessToken) => {
          setToken(accessToken);
        }}
      />
    );
  }

  // Si hay token, mostrar app normal
  return (
    <div>
      <h1>Bienvenido</h1>
      <button onClick={() => {
        localStorage.removeItem('token');
        setToken(null);
      }}>
        Logout
      </button>
      
      {/* Tu componente de búsqueda, etc. */}
      <BookSearch token={token} />
    </div>
  );
}
```
