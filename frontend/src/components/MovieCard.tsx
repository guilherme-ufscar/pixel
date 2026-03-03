import type { Movie } from '../types';

const TMDB_IMG = 'https://image.tmdb.org/t/p/w500';

interface MovieCardProps {
    movie: Movie;
    onClick: () => void;
}

export default function MovieCard({ movie, onClick }: MovieCardProps) {
    return (
        <div
            className="movie-card"
            onClick={onClick}
            role="button"
            tabIndex={0}
            aria-label={`Ver detalhes de ${movie.title}`}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onClick();
                }
            }}
        >
            {movie.poster_path ? (
                <img
                    src={`${TMDB_IMG}${movie.poster_path}`}
                    alt={movie.title}
                    className="movie-card-poster"
                    loading="lazy"
                />
            ) : (
                <div className="movie-card-poster-fallback">
                    <span className="material-icons-round">movie</span>
                    <span style={{ fontSize: '0.75rem' }}>Sem pôster</span>
                </div>
            )}

            {movie.vote_average > 0 && (
                <div className="movie-card-rating">
                    <span className="material-icons-round">star</span>
                    {movie.vote_average.toFixed(1)}
                </div>
            )}

            <div className="movie-card-overlay">
                <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{movie.title}</span>
            </div>

            <div className="movie-card-info">
                <h3 className="movie-card-title">{movie.title}</h3>
            </div>
        </div>
    );
}
