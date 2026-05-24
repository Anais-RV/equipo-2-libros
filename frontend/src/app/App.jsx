import React, { useState } from 'react';
import '../styles/global.css';
import styles from './App.module.css';
import RecommendationForm from '../components/RecommendationForm/RecommendationForm';
import ResultsDisplay from '../components/ResultsDisplay/ResultsDisplay';
import LoadingSpinner from '../components/LoadingSpinner/LoadingSpinner';
import Login from '../components/Auth/Login';
import { getEmotionalRecommendations } from '../services/api';

function App() {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));

  if (!token) {
    return <Login onLoginSuccess={(email, t) => {
      setToken(t);
      localStorage.setItem('token', t);
    }} />;
  }

  async function handleSubmit(payload) {
    setLoading(true);
    setError(null);
    setRecommendations(null);
    try {
      const data = await getEmotionalRecommendations({
        title: payload.bookTitle,
        topN: payload.topN,
        minReviews: payload.minReviews,
        excluirMismoAutor: payload.excluirMismoAutor
      });
      setRecommendations(data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'object' ? detail?.error : detail || 'No he podido conectar con FastAPI. Revisa http://localhost:8000');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.shell}>
      <div className={styles.orbA}/>
      <div className={styles.orbB}/>
      <header className={styles.hero}>
        <div className={styles.badge}><span/>Recomendador emocional inteligente</div>
        <h1>Encuentra libros por la <em>huella emocional</em> que dejan.</h1>
        <p>Un dashboard que compara alegría, tristeza, miedo, sorpresa, ira y asco, y además mezcla géneros y rating para que las recomendaciones tengan más sentido.</p>
      </header>
      <main className={styles.main}>
        <RecommendationForm disabled={loading} onSubmit={handleSubmit}/>
        {loading && <LoadingSpinner/>}
        {error && <div className={styles.error}><strong>No se pudo generar la recomendación</strong><p>{error}</p></div>}
        {recommendations && <ResultsDisplay recommendations={recommendations}/>}
      </main>
    </div>
  );
}

export default App;