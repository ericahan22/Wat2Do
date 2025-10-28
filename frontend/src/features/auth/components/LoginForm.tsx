import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/shared/components/ui/button';
import { Input } from '@/shared/components/ui/input';
import { Label } from '@/shared/components/ui/label';
import { loginSchema, type LoginFormData } from '@/features/auth/schemas/authSchemas';
import { AUTH_FORM_LABELS, AUTH_FORM_PLACEHOLDERS } from '@/features/auth/constants/auth';
import type { AuthError } from '@/features/auth/types/auth';

interface LoginFormProps {
  onSubmit: (data: LoginFormData) => void;
  isLoading?: boolean;
  error?: AuthError | null;
}

export const LoginForm = ({ onSubmit, isLoading = false, error }: LoginFormProps) => {
  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const handleSubmit = (data: LoginFormData) => {
    onSubmit(data);
  };

  return (
    <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="login-email">{AUTH_FORM_LABELS.EMAIL}</Label>
        <Input
          id="login-email"
          type="email"
          placeholder={AUTH_FORM_PLACEHOLDERS.EMAIL}
          {...form.register('email')}
        />
        {form.formState.errors.email && (
          <p className="text-sm text-red-600">{form.formState.errors.email.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="login-password">{AUTH_FORM_LABELS.PASSWORD}</Label>
        <Input
          id="login-password"
          type="password"
          placeholder={AUTH_FORM_PLACEHOLDERS.PASSWORD}
          {...form.register('password')}
        />
        {form.formState.errors.password && (
          <p className="text-sm text-red-600">{form.formState.errors.password.message}</p>
        )}
      </div>

      {error && (
        <p className="text-sm text-red-600">{error.message}</p>
      )}

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? AUTH_FORM_LABELS.SIGNING_IN : AUTH_FORM_LABELS.SIGN_IN}
      </Button>
    </form>
  );
};
