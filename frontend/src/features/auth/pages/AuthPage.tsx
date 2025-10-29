import { Navigate } from "react-router-dom";

export const AuthPage = () => {
  // Redirect to Clerk's sign-in page
  return <Navigate to="/auth/sign-in" replace />;
};