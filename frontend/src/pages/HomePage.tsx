import { useState, useCallback, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { useDebounce, useInfiniteScroll } from '../hooks';
import MovieCard from '../components/MovieCard';
import MovieDetailsModal from '../components/MovieDetailsModal';
import type { SearchResult, Genre, Movie } from '../types';

const TMDB_IMG = 'https://image.tmdb.org/t/p/w500';

export default function HomePage() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [selectedMovieId, setSelectedMovieId] = useState<number | null>(null);

    // Read filters from URL
    const query = searchParams.get('q') || '';
    const genre = searchParams.get('genre') || '';
    const year = searchParams.get('year') || '';

    const [inputValue, setInputValue] = useState(query);
    const debouncedQuery = useDebounce(inputValue, 400);

    // Sync debounced query to URL
    useEffect(() => {
        const params = new URLSearchParams(searchParams);
        if (debouncedQuery) {
            params.set('q', debouncedQuery);
        } else {
            params.delete('q');
        }
        setSearchParams(params, { replace: true });
    }, [debouncedQuery]);

    // Fetch genres
    const { data: genresData } = useQuery({
        queryKey: ['genres'],
        queryFn: () => api.get<{ genres: Genre[] }>('/movies/genres'),
        staleTime: 86400000,
    });

    // Build search params string
    const buildSearchUrl = (page: number) => {
        const params = new URLSearchParams();
        if (query) params.set('query', query);
        if (genre) params.set('genre', genre);
        if (year) params.set('year', year);
        params.set('page', String(page));
        return `/movies/search?${params.toString()}`;
    };

    // Infinite query for movie search
    const {
        data,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage,
        isLoading,
        isError,
        error,
        refetch,
    } = useInfiniteQuery({
        queryKey: ['movies', query, genre, year],
        queryFn: async ({ pageParam = 1 }) => {
            const result = await api.get<SearchResult>(buildSearchUrl(pageParam));
            return result;
        },
        getNextPageParam: (lastPage) => {
            if (lastPage.page < lastPage.total_pages) {
                return lastPage.page + 1;
            }
            return undefined;
        },
        initialPageParam: 1,
        enabled: true,
    });

    // Deduplicate movies across pages
    const allMovies = (() => {
        if (!data?.pages) return [];
        const seen = new Set<number>();
        const movies: Movie[] = [];
        for (const page of data.pages) {
            for (const movie of page.results) {
                if (!seen.has(movie.id)) {
                    seen.add(movie.id);
                    movies.push(movie);
                }
            }
        }
        return movies;
    })();

    const totalResults = data?.pages?.[0]?.total_results ?? 0;

    // Infinite scroll sentinel
    const loadMore = useCallback(() => {
        if (hasNextPage && !isFetchingNextPage) {
            fetchNextPage();
        }
    }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

    const sentinelRef = useInfiniteScroll(loadMore, {
        enabled: hasNextPage && !isFetchingNextPage,
    });

    // Filter handlers
    const updateFilter = (key: string, value: string) => {
        const params = new URLSearchParams(searchParams);
        if (value) {
            params.set(key, value);
        } else {
            params.delete(key);
        }
        setSearchParams(params, { replace: true });
    };

    return (
        <main className="app-container">
            {/* Hero */}
            <section className="hero">
                <h1 className="hero-title">Descubra Filmes Incríveis</h1>
                <p className="hero-subtitle">
                    Pesquise, explore e avalie seus filmes favoritos
                </p>

                {/* Search */}
                <div className="search-container">
                    <div className="search-input-wrapper">
                        <span className="material-icons-round">search</span>
                        <input
                            type="text"
                            className="search-input"
                            placeholder="Pesquisar filmes..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            aria-label="Pesquisar filmes"
                            id="search-input"
                        />
                    </div>

                    {/* Filters */}
                    <div className="filters-bar">
                        <span className="filter-label">
                            <span className="material-icons-round">filter_list</span>
                            Filtros:
                        </span>
                        <select
                            className="filter-select"
                            value={genre}
                            onChange={(e) => updateFilter('genre', e.target.value)}
                            aria-label="Filtrar por gênero"
                            id="filter-genre"
                        >
                            <option value="">Todos os gêneros</option>
                            {genresData?.genres.map((g) => (
                                <option key={g.id} value={g.id}>{g.name}</option>
                            ))}
                        </select>
                        <input
                            type="number"
                            className="filter-input"
                            placeholder="Ano"
                            value={year}
                            onChange={(e) => updateFilter('year', e.target.value)}
                            min="1888"
                            max="2030"
                            aria-label="Filtrar por ano"
                            id="filter-year"
                        />
                    </div>
                </div>
            </section>

            {/* Results count */}
            {!isLoading && allMovies.length > 0 && (
                <p className="page-title">
                    {totalResults.toLocaleString('pt-BR')} resultados encontrados
                </p>
            )}

            {/* Loading (first load) */}
            {isLoading && (
                <div className="movie-grid">
                    {Array.from({ length: 12 }).map((_, i) => (
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
                        {(error as any)?.error || 'Ocorreu um erro ao buscar filmes. Tente novamente.'}
                    </p>
                    <button className="btn btn-primary" onClick={() => refetch()}>
                        <span className="material-icons-round">refresh</span>
                        Tentar novamente
                    </button>
                </div>
            )}

            {/* Empty state */}
            {!isLoading && !isError && allMovies.length === 0 && query && (
                <div className="empty-state">
                    <span className="material-icons-round">movie_filter</span>
                    <h3 className="empty-state-title">Nenhum filme encontrado</h3>
                    <p className="empty-state-message">
                        Tente uma busca diferente ou ajuste os filtros
                    </p>
                </div>
            )}

            {/* Welcome state (no query) */}
            {!isLoading && !isError && !query && allMovies.length > 0 && (
                <p className="page-title">Filmes populares</p>
            )}

            {/* Movie Grid */}
            {!isError && allMovies.length > 0 && (
                <div className="movie-grid">
                    {allMovies.map((movie) => (
                        <MovieCard
                            key={movie.id}
                            movie={movie}
                            onClick={() => setSelectedMovieId(movie.id)}
                        />
                    ))}
                </div>
            )}

            {/* Infinite scroll sentinel */}
            {hasNextPage && (
                <div ref={sentinelRef} className="loading-spinner">
                    <div className="spinner" />
                </div>
            )}

            {/* Loading more */}
            {isFetchingNextPage && (
                <div className="loading-spinner">
                    <div className="spinner" />
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
