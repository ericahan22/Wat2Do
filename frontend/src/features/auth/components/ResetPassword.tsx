import { Navigate } from "react-router-dom";

export const ResetPassword = () => {
  // Clerk handles password reset automatically
  return <Navigate to="/auth/sign-in" replace />;
};