import { Navigate } from "react-router-dom";

export const ForgotPassword = () => {
  // Clerk handles password reset automatically
  return <Navigate to="/auth/sign-in" replace />;
};