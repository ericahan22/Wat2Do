import { FormEvent, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import {
  sendOtp,
  useAuthState,
  verifyOtp,
} from "@/features/auth/hooks/useAuthState";

export function SignInPage() {
  const navigate = useNavigate();
  const { isSignedIn } = useAuthState();
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [emailSent, setEmailSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isSignedIn) return <Navigate to="/events" replace />;

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const normalizedEmail = email.trim().toLowerCase();
      if (!emailSent) {
        await sendOtp(normalizedEmail);
        setEmail(normalizedEmail);
        setEmailSent(true);
      } else {
        await verifyOtp(normalizedEmail, otp.trim());
        navigate("/events", { replace: true });
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : emailSent
            ? "That code could not be verified."
            : "The login code could not be sent.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-sm flex-col justify-center">
      <h1 className="mb-2 text-2xl font-bold">Sign in</h1>
      <p className="mb-6 text-sm text-gray-600 dark:text-gray-400">
        {emailSent
          ? `Enter the login code sent to ${email}.`
          : "Use your existing email to access your saved V1 events."}
      </p>
      <form onSubmit={handleSubmit} className="space-y-3">
        {emailSent ? (
          <Input
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            placeholder="Login code"
            value={otp}
            onChange={(event) => setOtp(event.target.value)}
            required
          />
        ) : (
          <Input
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        )}
        {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting
            ? emailSent
              ? "Verifying..."
              : "Sending..."
            : emailSent
              ? "Verify and sign in"
              : "Send login code"}
        </Button>
      </form>
      {emailSent && (
        <Button
          type="button"
          variant="ghost"
          className="mt-3"
          onClick={() => {
            setEmailSent(false);
            setOtp("");
            setError(null);
          }}
        >
          Use a different email
        </Button>
      )}
    </div>
  );
}
