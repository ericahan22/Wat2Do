/**
 * User Profile Component
 * Displays user information and provides logout functionality
 */

import { useUser, useClerk } from '@clerk/clerk-react';
import { Button } from '@/shared/components/ui/button';
import { LogOut, User, Mail, Calendar } from 'lucide-react';

export const UserProfile = () => {
  const { user } = useUser();
  const { signOut } = useClerk();

  if (!user) return null;

  const primaryEmail = user.primaryEmailAddress?.emailAddress;
  const emailVerified = user.primaryEmailAddress?.verification?.status === 'verified';

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <div className="flex items-center space-x-4">
        <div className="flex-shrink-0">
          {user.imageUrl ? (
            <img
              className="h-12 w-12 rounded-full"
              src={user.imageUrl}
              alt={`${user.firstName || 'User'} profile`}
            />
          ) : (
            <div className="h-12 w-12 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
              <User className="h-6 w-6 text-gray-600 dark:text-gray-300" />
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            {user.firstName && user.lastName 
              ? `${user.firstName} ${user.lastName}`
              : user.username || 'User'
            }
          </h3>
          <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <Mail className="h-4 w-4" />
            <span>{primaryEmail}</span>
            {emailVerified ? (
              <span className="text-green-600 dark:text-green-400">✓</span>
            ) : (
              <span className="text-yellow-600 dark:text-yellow-400">!</span>
            )}
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <Calendar className="h-4 w-4" />
            <span>Joined {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}</span>
          </div>
        </div>
        <div className="flex-shrink-0">
          <Button
            variant="outline"
            size="sm"
            onClick={() => signOut()}
            className="flex items-center space-x-2"
          >
            <LogOut className="h-4 w-4" />
            <span>Sign Out</span>
          </Button>
        </div>
      </div>
    </div>
  );
};
