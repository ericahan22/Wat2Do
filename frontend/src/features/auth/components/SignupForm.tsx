import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/shared/components/ui/button';
import { Input } from '@/shared/components/ui/input';
import { Label } from '@/shared/components/ui/label';
import { signupSchema, type SignupFormData } from '@/features/auth/schemas/authSchemas';
import { AUTH_FORM_LABELS, AUTH_FORM_PLACEHOLDERS } from '@/features/auth/constants/auth';
import type { AuthError, AuthMutationOptions, SignupRequest } from '@/features/auth/types/auth';

interface SignupFormProps {
  onSubmit: (data: SignupRequest, options?: AuthMutationOptions) => void;
  isLoading?: boolean;
  error?: AuthError | null;
  onSuccess?: () => void;
}

export const SignupForm = ({ onSubmit, isLoading = false, error, onSuccess }: SignupFormProps) => {
  const form = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const handleSubmit = (data: SignupFormData) => {
    const { confirmPassword, ...signupData } = data;
    onSubmit({
      ...signupData,
      password_confirm: confirmPassword
    }, {
      onSuccess: () => {
        form.reset();
        onSuccess?.();
      }
    });
  };

  return (
    <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="signup-email" className="text-gray-700 dark:text-gray-200">
          {AUTH_FORM_LABELS.EMAIL}
        </Label>
        <Input
          id="signup-email"
          type="email"
          placeholder={AUTH_FORM_PLACEHOLDERS.EMAIL}
          {...form.register('email')}
        />
        {form.formState.errors.email && (
          <p className="text-sm text-red-600 dark:text-red-400">{form.formState.errors.email.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="signup-password" className="text-gray-700 dark:text-gray-200">
          {AUTH_FORM_LABELS.PASSWORD}
        </Label>
        <Input
          id="signup-password"
          type="password"
          placeholder={AUTH_FORM_PLACEHOLDERS.PASSWORD}
          {...form.register('password')}
        />
        {form.formState.errors.password && (
          <p className="text-sm text-red-600 dark:text-red-400">{form.formState.errors.password.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="signup-confirm-password" className="text-gray-700 dark:text-gray-200">
          {AUTH_FORM_LABELS.CONFIRM_PASSWORD}
        </Label>
        <Input
          id="signup-confirm-password"
          type="password"
          placeholder={AUTH_FORM_PLACEHOLDERS.CONFIRM_PASSWORD}
          {...form.register('confirmPassword')}
        />
        {form.formState.errors.confirmPassword && (
          <p className="text-sm text-red-600 dark:text-red-400">{form.formState.errors.confirmPassword.message}</p>
        )}
      </div>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error.message}</p>
      )}

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? AUTH_FORM_LABELS.CREATING_ACCOUNT : AUTH_FORM_LABELS.CREATE_ACCOUNT}
      </Button>
    </form>
  );
};
