/** API client with interceptors for auth token management */

import { useAuthStore } from '../store/authStore';

const API_BASE = '/api/v1';

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    private getHeaders(auth = false): HeadersInit {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };
        if (auth) {
            const token = useAuthStore.getState().accessToken;
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        return headers;
    }

    private async handleResponse<T>(response: Response): Promise<T> {
        if (response.status === 401) {
            // Try to refresh token
            const refreshToken = useAuthStore.getState().refreshToken;
            if (refreshToken) {
                try {
                    const refreshRes = await fetch(`${this.baseUrl}/auth/refresh`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${refreshToken}`,
                        },
                    });
                    if (refreshRes.ok) {
                        const data = await refreshRes.json();
                        useAuthStore.getState().setAccessToken(data.access_token);
                        // Note: the original request should be retried by the caller
                    } else {
                        useAuthStore.getState().logout();
                    }
                } catch {
                    useAuthStore.getState().logout();
                }
            }
        }

        if (!response.ok) {
            const error = await response.json().catch(() => ({
                error: 'An unexpected error occurred',
                code: 'UNKNOWN_ERROR',
            }));
            throw error;
        }

        return response.json();
    }

    async get<T>(endpoint: string, auth = false): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            headers: this.getHeaders(auth),
        });
        return this.handleResponse<T>(response);
    }

    async post<T>(endpoint: string, data: unknown, auth = false): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: this.getHeaders(auth),
            body: JSON.stringify(data),
        });
        return this.handleResponse<T>(response);
    }

    async delete<T>(endpoint: string, auth = false): Promise<T> {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'DELETE',
            headers: this.getHeaders(auth),
        });
        return this.handleResponse<T>(response);
    }
}

export const api = new ApiClient(API_BASE);
