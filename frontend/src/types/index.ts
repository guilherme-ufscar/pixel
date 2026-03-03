/** TMDB and application TypeScript types */

export interface Movie {
    id: number;
    title: string;
    overview: string;
    poster_path: string | null;
    backdrop_path: string | null;
    release_date: string;
    vote_average: number;
    vote_count: number;
    genre_ids: number[];
    popularity: number;
}

export interface MovieDetails extends Movie {
    runtime: number | null;
    genres: Genre[];
    tagline: string;
    status: string;
    budget: number;
    revenue: number;
}

export interface CastMember {
    id: number;
    name: string;
    character: string;
    profile_path: string | null;
    order: number;
}

export interface Genre {
    id: number;
    name: string;
}

export interface SearchResult {
    page: number;
    results: Movie[];
    total_pages: number;
    total_results: number;
}

export interface Rating {
    id: number;
    user_id: number;
    movie_id: number;
    score: number;
    movie_title: string;
    poster_path: string | null;
    created_at: string;
    updated_at: string;
}

export interface User {
    id: number;
    email: string;
    created_at: string;
}

export interface AuthResponse {
    user: User;
    access_token: string;
    refresh_token: string;
}

export interface ApiError {
    error: string;
    code: string;
    details?: { field: string; message: string }[];
}
