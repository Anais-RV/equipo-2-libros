import React from 'react';
import styles from './ResultsDisplay.module.css';
import BookCard from '../BookCard/BookCard';
import EmotionRadar from '../EmotionRadar/EmotionRadar';

function ResultsDisplay({ recommendations }) {
  const baseBook = recommendations?.libro_base;
  const books = recommendations?.recomendaciones || [];

  if (!baseBook) {
    return null;
  }

  return (
    <section className={styles.results}>

      {/* LIBRO BASE - tarjeta a la izquierda, radar a la derecha */}
      <div>
        <div className={styles.sectionHeader}>
          <div>
            <span className={styles.kicker}>Punto de partida</span>
            <h2>Libro base</h2>
          </div>
        </div>

        <div className={styles.baseLayout}>
          <div className={styles.baseCard}>
            <BookCard book={baseBook} isBase={true} />
          </div>
          <div className={styles.radarPanel}>
            <EmotionRadar profile={baseBook} />
          </div>
        </div>
      </div>

      {/* RECOMENDACIONES */}
      <div className={styles.sectionHeader}>
        <div>
          <span className={styles.kicker}>Ruta de lectura</span>
          <h2>Libros recomendados</h2>
        </div>
        <p>
          {books.length} resultados ordenados por score final.
        </p>
      </div>

      {books.length === 0 ? (
        <div className={styles.emptyState}>
          <strong>No hay recomendaciones disponibles</strong>
          <p>
            Prueba con otro título o revisa que el backend esté devolviendo datos.
          </p>
        </div>
      ) : (
        <div className={styles.cards}>
          {books.map((book, index) => (
            <BookCard
              key={`${book.book_id || book.book_title}-${index}`}
              book={book}
              position={index + 1}
            />
          ))}
        </div>
      )}
    </section>
  );
}

export default ResultsDisplay;
