# Feedback Component

## FeedbackForm.jsx

Formulario para dejar reviews de libros.

**Props:**
- `token` - JWT token para autenticación
- `onFeedbackSent()` - Callback cuando review se guarda

**Comportamiento:**
- Formulario para libro, review y rating
- Envía a `/user/feedback` endpoint
- Estados de carga, error y éxito

**Uso:**
```jsx
import FeedbackForm from './Feedback/FeedbackForm';

<FeedbackForm 
  token={token}
  onFeedbackSent={() => {
    console.log('Review guardada');
  }}
/>
```

## FeedbackForm.module.css

Estilos BEM para el componente.

Reutiliza el patrón de colores y espacios de Auth.

