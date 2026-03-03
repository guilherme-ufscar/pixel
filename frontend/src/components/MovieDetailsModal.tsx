import { useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import RatingControl from './RatingControl';
import type { MovieDetails, CastMember } from '../types';

const TMDB_IMG = 'https://image.tmdb.org/t/p/w500';
const TMDB_IMG_ORIGINAL = 'https://image.tmdb.org/t/p/original';

interface MovieDetailsModalProps {
    movieId: number;
    onClose: () => void;
}

export default function MovieDetailsModal({ movieId, onClose }: MovieDetailsModalProps) {
    // Movie details
    const {
        data: movie,
        isLoading: movieLoading,
        isError: movieError,
        refetch: refetchMovie,
    } = useQuery({
        queryKey: ['movie', movieId],
        queryFn: () => api.get<MovieDetails>(`/movies/${movieId}`),
    });

    // Cast
    const {
        data: creditsData,
        isLoading: creditsLoading,
    } = useQuery({
        queryKey: ['credits', movieId],
        queryFn: () => api.get<{ cast: CastMember[] }>(`/movies/${movieId}/credits`),
    });

    const cast = creditsData?.cast ?? [];

    // Close on Escape
    const handleKeyDown = useCallback(
        (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        },
        [onClose]
    );

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        document.body.style.overflow = 'hidden';
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.body.style.overflow = '';
        };
    }, [handleKeyDown]);

    // Close on backdrop click
    const handleBackdropClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) onClose();
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return 'Data não informada';
        const date = new Date(dateStr + 'T00:00:00');
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
        });
    };

    return (
        <div
            className="modal-backdrop"
            onClick={handleBackdropClick}
            role="dialog"
            aria-modal="true"
            aria-label={movie?.title || 'Detalhes do filme'}
        >
            <div className="modal-content">
                <button
                    className="modal-close"
                    onClick={onClose}
                    aria-label="Fechar modal"
                >
                    <span className="material-icons-round">close</span>
                </button>

                {/* Loading */}
                {movieLoading && (
                    <div style={{ padding: '4rem' }}>
                        <div className="loading-spinner">
                            <div className="spinner" />
                        </div>
                    </div>
                )}

                {/* Error */}
                {movieError && (
                    <div className="error-state" style={{ minHeight: '300px' }}>
                        <span className="material-icons-round">error_outline</span>
                        <p className="error-state-message">Erro ao carregar detalhes do filme</p>
                        <button className="btn btn-primary" onClick={() => refetchMovie()}>
                            <span className="material-icons-round">refresh</span>
                            Tentar novamente
                        </button>
                    </div>
                )}

                {/* Movie Content */}
                {movie && !movieLoading && !movieError && (
                    <>
                        {/* Backdrop */}
                        {movie.backdrop_path ? (
                            <img
                                src={`${TMDB_IMG_ORIGINAL}${movie.backdrop_path}`}
                                alt=""
                                className="modal-backdrop-image"
                            />
                        ) : (
                            <div
                                className="modal-backdrop-image"
                                style={{ background: 'linear-gradient(135deg, var(--color-bg-card), var(--color-primary))' }}
                            />
                        )}

                        <div className="modal-body">
                            <h2 className="modal-title">{movie.title}</h2>

                            {/* Meta */}
                            <div className="modal-meta">
                                <span className="modal-meta-item">
                                    <span className="material-icons-round">calendar_today</span>
                                    {formatDate(movie.release_date)}
                                </span>
                                {movie.runtime && (
                                    <span className="modal-meta-item">
                                        <span className="material-icons-round">schedule</span>
                                        {movie.runtime} min
                                    </span>
                                )}
                                {movie.vote_average > 0 && (
                                    <span className="modal-meta-item">
                                        <span className="material-icons-round">star</span>
                                        {movie.vote_average.toFixed(1)}/10
                                    </span>
                                )}
                                {movie.genres?.map((g) => (
                                    <span key={g.id} className="modal-meta-item" style={{ background: 'var(--color-bg-card)', padding: '2px 10px', borderRadius: '20px', fontSize: '0.8rem' }}>
                                        {g.name}
                                    </span>
                                ))}
                            </div>

                            {/* Synopsis */}
                            <div className="modal-section">
                                <h3 className="modal-section-title">
                                    <span className="material-icons-round">description</span>
                                    Sinopse
                                </h3>
                                <p className="modal-overview">
                                    {movie.overview || 'Sinopse não disponível para este filme.'}
                                </p>
                            </div>

                            {/* Cast */}
                            <div className="modal-section">
                                <h3 className="modal-section-title">
                                    <span className="material-icons-round">people</span>
                                    Elenco
                                </h3>
                                {creditsLoading ? (
                                    <div className="loading-spinner">
                                        <div className="spinner" />
                                    </div>
                                ) : cast.length > 0 ? (
                                    <div className="cast-grid">
                                        {cast.map((member) => (
                                            <div key={member.id} className="cast-card">
                                                {member.profile_path ? (
                                                    <img
                                                        src={`${TMDB_IMG}${member.profile_path}`}
                                                        alt={member.name}
                                                        className="cast-photo"
                                                        loading="lazy"
                                                    />
                                                ) : (
                                                    <div className="cast-photo-fallback">
                                                        <span className="material-icons-round">person</span>
                                                    </div>
                                                )}
                                                <p className="cast-name">{member.name}</p>
                                                <p className="cast-character">{member.character}</p>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p style={{ color: 'var(--color-text-muted)' }}>Elenco não disponível</p>
                                )}
                            </div>

                            {/* Rating */}
                            <div className="modal-section">
                                <h3 className="modal-section-title">
                                    <span className="material-icons-round">rate_review</span>
                                    Sua Avaliação
                                </h3>
                                <RatingControl
                                    movieId={movieId}
                                    movieTitle={movie.title}
                                    posterPath={movie.poster_path}
                                />
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
