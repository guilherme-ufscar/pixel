import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import MovieCard from '../components/MovieCard';
import MovieDetailsModal from '../components/MovieDetailsModal';
import type { Rating } from '../types';

export default function RatedMoviesPage() {
    const [selectedMovieId, setSelectedMovieId] = useState<number | null>(null);
    const [sortBy, setSortBy] = useState('updated_at');
    const [order, setOrder] = useState('desc');

    const { data, isLoading, isError, error, refetch } = useQuery({
        queryKey: ['rated-movies', sortBy, order],
        queryFn: () =>
            api.get<{ ratings: Rating[] }>(
                `/ratings?sort_by=${sortBy}&order=${order}`,
                true
            ),
    });

    const ratings = data?.ratings ?? [];

    return (
        <main className="app-container">
            <div className="rated-header">
                <h1 className="rated-title">
                    <span className="material-icons-round">star</span>
                    Filmes Avaliados
                </h1>

                {ratings.length > 0 && (
                    <div className="rated-sort">
                        <span className="rated-sort-label">Ordenar por:</span>
                        <select
                            className="filter-select"
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value)}
                            aria-label="Ordenar por"
                            id="sort-by"
                        >
                            <option value="updated_at">Data de avaliação</option>
                            <option value="score">Nota</option>
                            <option value="created_at">Data de criação</option>
                        </select>
                        <select
                            className="filter-select"
                            value={order}
                            onChange={(e) => setOrder(e.target.value)}
                            aria-label="Ordem"
                            id="sort-order"
                        >
                            <option value="desc">Mais recente</option>
                            <option value="asc">Mais antigo</option>
                        </select>
                    </div>
                )}
            </div>

            {/* Loading */}
            {isLoading && (
                <div className="movie-grid">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <div key={i}>
                            <div className="skeleton skeleton-card" />
                            <div className="skeleton skeleton-text" />
                        </div>
                    ))}
                </div>
            )}

            {/* Error */}
            {isError && (
                <div className="error-state">
                    <span className="material-icons-round">error_outline</span>
                    <p className="error-state-message">
                        {(error as any)?.error || 'Erro ao carregar filmes avaliados.'}
                    </p>
                    <button className="btn btn-primary" onClick={() => refetch()}>
                        <span className="material-icons-round">refresh</span>
                        Tentar novamente
                    </button>
                </div>
            )}

            {/* Empty */}
            {!isLoading && !isError && ratings.length === 0 && (
                <div className="empty-state">
                    <span className="material-icons-round">star_border</span>
                    <h3 className="empty-state-title">Nenhum filme avaliado</h3>
                    <p className="empty-state-message">
                        Pesquise filmes e comece a avaliá-los!
                    </p>
                </div>
            )}

            {/* Rated Movies Grid */}
            {!isError && ratings.length > 0 && (
                <div className="movie-grid">
                    {ratings.map((rating) => (
                        <div
                            key={rating.id}
                            className="movie-card"
                            onClick={() => setSelectedMovieId(rating.movie_id)}
                            role="button"
                            tabIndex={0}
                            aria-label={`Ver detalhes de ${rating.movie_title}`}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    setSelectedMovieId(rating.movie_id);
                                }
                            }}
                        >
                            {rating.poster_path ? (
                                <img
                                    src={`https://image.tmdb.org/t/p/w500${rating.poster_path}`}
                                    alt={rating.movie_title}
                                    className="movie-card-poster"
                                    loading="lazy"
                                />
                            ) : (
                                <div className="movie-card-poster-fallback">
                                    <span className="material-icons-round">movie</span>
                                    <span style={{ fontSize: '0.75rem' }}>Sem pôster</span>
                                </div>
                            )}
                            <div className="rated-movie-score">
                                <span className="material-icons-round">star</span>
                                {rating.score}/5
                            </div>
                            <div className="movie-card-info">
                                <h3 className="movie-card-title">{rating.movie_title}</h3>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Movie Details Modal */}
            {selectedMovieId && (
                <MovieDetailsModal
                    movieId={selectedMovieId}
                    onClose={() => setSelectedMovieId(null)}
                />
            )}
        </main>
    );
}
