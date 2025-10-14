import { useNavigate, useLocation } from 'react-router-dom';
import { LoginForm } from '../components/LoginForm';

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleAuthSuccess = () => {
    // Redirect to the original URL the user was trying to access, or home page
    const from = location.state?.from?.pathname || '/';
    navigate(from, { replace: true });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Welcome to Wat2Do
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to submit events and clubs
          </p>
        </div>
        <LoginForm onSuccess={handleAuthSuccess} />
      </div>
    </div>
  );
}
