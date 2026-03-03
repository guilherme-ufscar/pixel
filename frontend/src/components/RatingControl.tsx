import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import type { Rating } from '../types';
import toast from 'react-hot-toast';

interface RatingControlProps {
    movieId: number;
    movieTitle: string;
    posterPath: string | null;
}

export default function RatingControl({ movieId, movieTitle, posterPath }: RatingControlProps) {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const queryClient = useQueryClient();
    const [hoveredStar, setHoveredStar] = useState(0);

    // Fetch existing rating
    const { data, isLoading } = useQuery({
        queryKey: ['rating', movieId],
        queryFn: () => api.get<{ rating: Rating | null }>(`/ratings/${movieId}`, true),
        enabled: isAuthenticated,
    });

    const currentRating = data?.rating;

    // Upsert mutation
    const upsertMutation = useMutation({
        mutationFn: (score: number) =>
            api.post('/ratings', {
                movie_id: movieId,
                score,
                movie_title: movieTitle,
                poster_path: posterPath,
            }, true),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['rating', movieId] });
            queryClient.invalidateQueries({ queryKey: ['rated-movies'] });
            toast.success(currentRating ? 'Avaliação atualizada!' : 'Filme avaliado com sucesso!');
        },
        onError: (err: any) => {
            toast.error(err?.error || 'Erro ao salvar avaliação');
        },
    });

    // Delete mutation
    const deleteMutation = useMutation({
        mutationFn: () => api.delete(`/ratings/${movieId}`, true),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['rating', movieId] });
            queryClient.invalidateQueries({ queryKey: ['rated-movies'] });
            toast.success('Avaliação removida');
        },
        onError: (err: any) => {
            toast.error(err?.error || 'Erro ao remover avaliação');
        },
    });

    const isSubmitting = upsertMutation.isPending || deleteMutation.isPending;

    if (!isAuthenticated) {
        return (
            <div className="rating-control">
                <p className="rating-label">
                    Faça login para avaliar este filme
                </p>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="rating-control">
                <div className="loading-spinner">
                    <div className="spinner" style={{ width: '24px', height: '24px' }} />
                </div>
            </div>
        );
    }

    const displayScore = hoveredStar || currentRating?.score || 0;

    return (
        <div className="rating-control">
            <div className="rating-stars" role="radiogroup" aria-label="Avaliação do filme">
                {[1, 2, 3, 4, 5].map((star) => (
                    <span
                        key={star}
                        className={`material-icons-round rating-star ${star <= displayScore ? 'active' : ''}`}
                        onClick={() => {
                            if (!isSubmitting) upsertMutation.mutate(star);
                        }}
                        onMouseEnter={() => setHoveredStar(star)}
                        onMouseLeave={() => setHoveredStar(0)}
                        role="radio"
                        aria-checked={star === currentRating?.score}
                        aria-label={`${star} estrela${star > 1 ? 's' : ''}`}
                        tabIndex={0}
                        onKeyDown={(e) => {
                            if ((e.key === 'Enter' || e.key === ' ') && !isSubmitting) {
                                e.preventDefault();
                                upsertMutation.mutate(star);
                            }
                        }}
                    >
                        {star <= displayScore ? 'star' : 'star_border'}
                    </span>
                ))}
            </div>

            <p className="rating-label">
                {currentRating
                    ? `Sua nota: ${currentRating.score}/5`
                    : hoveredStar
                        ? `${hoveredStar}/5`
                        : 'Clique para avaliar'}
            </p>

            {currentRating && (
                <div className="rating-actions">
                    <button
                        className="btn btn-danger btn-sm"
                        onClick={() => {
                            if (!isSubmitting) deleteMutation.mutate();
                        }}
                        disabled={isSubmitting}
                    >
                        <span className="material-icons-round" style={{ fontSize: '16px' }}>delete</span>
                        Remover
                    </button>
                </div>
            )}
        </div>
    );
}
