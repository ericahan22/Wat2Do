import { CheckCircle } from 'lucide-react';

interface SuccessMessageProps {
  message: string;
}

export const SuccessMessage = ({ message }: SuccessMessageProps) => {
  return (
    <div className="p-4 bg-green-50 border border-green-200 rounded-md dark:bg-green-900 dark:border-green-700">
      <div className="flex items-center gap-2">
        <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
        <p className="text-sm text-green-800 dark:text-green-200">
          {message}
        </p>
      </div>
    </div>
  );
};
