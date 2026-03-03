import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import type { AuthResponse, ApiError } from '../types';
import toast from 'react-hot-toast';

export default function RegisterPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const setAuth = useAuthStore((s) => s.setAuth);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (isSubmitting) return;

        setError('');

        if (password !== confirmPassword) {
            setError('As senhas não coincidem');
            return;
        }

        if (password.length < 6) {
            setError('A senha deve ter no mínimo 6 caracteres');
            return;
        }

        setIsSubmitting(true);

        try {
            const data = await api.post<AuthResponse>('/auth/register', { email, password });
            setAuth(data.user, data.access_token, data.refresh_token);
            toast.success('Conta criada com sucesso!');
            navigate('/');
        } catch (err) {
            const apiError = err as ApiError;
            if (apiError.details) {
                setError(apiError.details.map((d) => d.message).join('. '));
            } else {
                setError(apiError.error || 'Erro ao criar conta');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1 className="auth-title">Criar Conta</h1>
                <p className="auth-subtitle">Junte-se para avaliar seus filmes favoritos</p>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="register-email" className="form-label">E-mail</label>
                        <input
                            id="register-email"
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
                        <label htmlFor="register-password" className="form-label">Senha</label>
                        <input
                            id="register-password"
                            type="password"
                            className="form-input"
                            placeholder="Mínimo 6 caracteres"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength={6}
                            autoComplete="new-password"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="register-confirm" className="form-label">Confirmar Senha</label>
                        <input
                            id="register-confirm"
                            type="password"
                            className="form-input"
                            placeholder="Repita a senha"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            autoComplete="new-password"
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
                                Criando...
                            </>
                        ) : (
                            <>
                                <span className="material-icons-round">person_add</span>
                                Criar Conta
                            </>
                        )}
                    </button>
                </form>

                <p className="auth-link">
                    Já tem conta? <Link to="/login">Entrar</Link>
                </p>
            </div>
        </div>
    );
}
