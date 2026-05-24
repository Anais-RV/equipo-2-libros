import { useState } from 'react';
import styles from './FeedbackForm.module.css';

export default function FeedbackForm({ token, onFeedbackSent }) {
  const [bookTitle, setBookTitle] = useState('');
  const [reviewText, setReviewText] = useState('');
  const [rating, setRating] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/user/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          book_title: bookTitle,
          review_text: reviewText,
          rating: parseInt(rating)
        })
      });

      if (!response.ok) {
        setError('Error al guardar la review');
        return;
      }

      setSuccess('Review guardada exitosamente');
      setBookTitle('');
      setReviewText('');
      setRating(5);

      if (onFeedbackSent) onFeedbackSent();
    } catch (err) {
      setError('Error de conexión: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles['feedback-form']}>
      <h3 className={styles['feedback-title']}>Dejar una Review</h3>

      {error && <p className={styles['feedback-error']}>{error}</p>}
      {success && <p className={styles['feedback-success']}>{success}</p>}

      <div className={styles['feedback-field']}>
        <label className={styles['feedback-label']}>Título del Libro</label>
        <input
          type="text"
          value={bookTitle}
          onChange={(e) => setBookTitle(e.target.value)}
          placeholder="Ej: The Midnight Library"
          className={styles['feedback-input']}
          disabled={loading}
          required
        />
      </div>

      <div className={styles['feedback-field']}>
        <label className={styles['feedback-label']}>Tu Review</label>
        <textarea
          value={reviewText}
          onChange={(e) => setReviewText(e.target.value)}
          placeholder="Qué te pareció el libro..."
          className={styles['feedback-textarea']}
          disabled={loading}
          required
        />
      </div>

      <div className={styles['feedback-field']}>
        <label className={styles['feedback-label']}>Rating</label>
        <select
          value={rating}
          onChange={(e) => setRating(e.target.value)}
          className={styles['feedback-select']}
          disabled={loading}
        >
          <option value={1}>1 - Muy malo</option>
          <option value={2}>2 - Malo</option>
          <option value={3}>3 - Normal</option>
          <option value={4}>4 - Bueno</option>
          <option value={5}>5 - Excelente</option>
        </select>
      </div>

      <button
        type="submit"
        className={styles['feedback-button']}
        disabled={loading}
      >
        {loading ? 'Guardando...' : 'Guardar Review'}
      </button>
    </form>
  );
}
