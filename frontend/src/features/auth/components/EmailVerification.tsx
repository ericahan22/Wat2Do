import { Navigate } from "react-router-dom";

export const EmailVerification = () => {
  // Clerk handles email verification automatically
  return <Navigate to="/dashboard" replace />;
};