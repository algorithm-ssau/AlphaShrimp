import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthPage from './components/AuthPage';

function AppContent() {
    const { user, logout } = useAuth();
    if (!user) return <AuthPage />;
    return (
        <div className="p-8">
            <h1>Hello, {user.email}!</h1>
            <button onClick={logout}>Logout</button>
        </div>
    );
}

export default function App() {
    return <AuthProvider><AppContent /></AuthProvider>;
}