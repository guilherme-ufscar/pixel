import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import type { AuthResponse, ApiError } from '../types';
import toast from 'react-hot-toast';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const setAuth = useAuthStore((s) => s.setAuth);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (isSubmitting) return;

        setError('');
        setIsSubmitting(true);

        try {
            const data = await api.post<AuthResponse>('/auth/login', { email, password });
            setAuth(data.user, data.access_token, data.refresh_token);
            toast.success('Login realizado com sucesso!');
            navigate('/');
        } catch (err) {
            const apiError = err as ApiError;
            setError(apiError.error || 'Erro ao fazer login');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1 className="auth-title">Bem-vindo de volta</h1>
                <p className="auth-subtitle">Entre para avaliar seus filmes favoritos</p>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="login-email" className="form-label">E-mail</label>
                        <input
                            id="login-email"
                            type="email"
                            className="form-input"
                            placeholder="seu@email.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            autoComplete="email"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="login-password" className="form-label">Senha</label>
                        <input
                            id="login-password"
                            type="password"
                            className="form-input"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            autoComplete="current-password"
                        />
                    </div>

                    {error && <p className="form-error">{error}</p>}

                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ width: '100%', marginTop: '0.5rem' }}
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? (
                            <>
                                <div className="spinner" style={{ width: '18px', height: '18px', borderWidth: '2px' }} />
                                Entrando...
                            </>
                        ) : (
                            <>
                                <span className="material-icons-round">login</span>
                                Entrar
                            </>
                        )}
                    </button>
                </form>

                <p className="auth-link">
                    Não tem conta? <Link to="/register">Criar conta</Link>
                </p>
            </div>
        </div>
    );
}
