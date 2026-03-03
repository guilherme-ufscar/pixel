import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import HomePage from './pages/HomePage';
import RatedMoviesPage from './pages/RatedMoviesPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import { useScrollToTop } from './hooks';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }
    return <>{children}</>;
}

export default function App() {
    const location = useLocation();
    const { isAuthenticated, logout, user } = useAuthStore();
    const { visible, scrollToTop } = useScrollToTop();

    return (
        <>
            {/* Header */}
            <header className="header">
                <div className="header-content">
                    <Link to="/" className="header-logo">
                        <span className="material-icons-round">movie</span>
                        Pixel Movies
                    </Link>
                    <nav className="header-nav">
                        <Link
                            to="/"
                            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
                        >
                            <span className="material-icons-round">search</span>
                            <span>Buscar</span>
                        </Link>
                        {isAuthenticated && (
                            <Link
                                to="/rated"
                                className={`nav-link ${location.pathname === '/rated' ? 'active' : ''}`}
                            >
                                <span className="material-icons-round">star</span>
                                <span>Avaliados</span>
                            </Link>
                        )}
                        {isAuthenticated ? (
                            <button className="nav-link" onClick={logout} title={user?.email}>
                                <span className="material-icons-round">logout</span>
                                <span>Sair</span>
                            </button>
                        ) : (
                            <Link
                                to="/login"
                                className={`nav-link ${location.pathname === '/login' ? 'active' : ''}`}
                            >
                                <span className="material-icons-round">person</span>
                                <span>Entrar</span>
                            </Link>
                        )}
                    </nav>
                </div>
            </header>

            {/* Routes */}
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route
                    path="/rated"
                    element={
                        <ProtectedRoute>
                            <RatedMoviesPage />
                        </ProtectedRoute>
                    }
                />
            </Routes>

            {/* Scroll to top */}
            {visible && (
                <button
                    className="scroll-to-top"
                    onClick={scrollToTop}
                    aria-label="Voltar ao topo"
                >
                    <span className="material-icons-round">keyboard_arrow_up</span>
                </button>
            )}
        </>
    );
}
