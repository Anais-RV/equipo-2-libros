import React, { useState } from 'react';
import styles from './BookCard.module.css';
import EmotionBars from '../EmotionBars/EmotionBars';

function pct(v) {
  return `${Math.round(Number(v || 0) * 100)}%`;
}

function getFavs() {
  return JSON.parse(localStorage.getItem('favorites') || '[]');
}

function BookCard({ book, position }) {
  const score = Number(book.score_final ?? book.similarity ?? 0);
  const [fav, setFav] = useState(() => 
    getFavs().some(f => f.book_title === book.book_title)
  );

  function toggleFav() {
    const favs = getFavs();
    const idx = favs.findIndex(f => f.book_title === book.book_title);
    if (idx >= 0) {
      favs.splice(idx, 1);
      setFav(false);
    } else {
      favs.push({
        book_title: book.book_title,
        author: book.author,
        average_rating: book.average_rating,
        emocion_dominante_es: book.emocion_dominante_es || book.emocion_dominante,
      });
      setFav(true);
    }
    localStorage.setItem('favorites', JSON.stringify(favs));
  }

  return (
    <article className={styles.card}>
      <div className={styles.top}>
        <div className={styles.rank}>#{position}</div>

        {book.cover_image_uri && (
          <img
            src={book.cover_image_uri}
            alt={book.book_title}
            className={styles.cover}
          />
        )}

        <div className={styles.topRight}>
          <button onClick={toggleFav} style={{
            background: 'transparent', border: 'none', cursor: 'pointer',
            fontSize: '1.4rem', color: fav ? '#f472b6' : '#aaa',
            padding: '0 4px', lineHeight: 1
          }}>
            {fav ? '♥' : '♡'}
          </button>
          <div className={styles.match}>
            <span>{Math.round(score * 100)}%</span>
            match
          </div>
        </div>
      </div>

      <div className={styles.content}>
        <h3>{book.book_title || 'Título desconocido'}</h3>
        <p className={styles.author}>{book.author || 'Autor desconocido'}</p>

        <div className={styles.grid}>
          <div>
            <span>Dominante</span>
            <strong>{book.emocion_dominante_es || book.emocion_dominante || '—'}</strong>
          </div>
          <div>
            <span>Rating</span>
            <strong>{Number(book.average_rating || 0).toFixed(2)}</strong>
          </div>
          <div>
            <span>Emoción</span>
            <strong>{pct(book.emotion_similarity ?? book.similarity)}</strong>
          </div>
          <div>
            <span>Géneros</span>
            <strong>{pct(book.genre_similarity)}</strong>
          </div>
        </div>

        <EmotionBars profile={book} />

        {book.genres && (
          <p className={styles.genres}>{String(book.genres)}</p>
        )}

        {book.book_details && (
          <div className={styles.synopsisBox}>
            <span className={styles.synopsisTitle}>Sinopsis</span>
            <p className={styles.synopsis}>{String(book.book_details)}</p>
          </div>
        )}

        {book.reason && (
          <p className={styles.reason}>{book.reason}</p>
        )}
      </div>
    </article>
  );
}

export default BookCard;