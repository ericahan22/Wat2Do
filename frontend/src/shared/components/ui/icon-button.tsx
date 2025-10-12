import * as React from 'react';
import { Button, ButtonProps } from './button';
import { cn } from '@/shared/lib/utils';

export interface IconButtonProps extends Omit<ButtonProps, 'children'> {
  icon: React.ElementType;
  children?: never;
  'aria-label': string;
}

const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant = 'ghost', size = 'icon', icon: Icon, ...props }, ref) => {
    return (
      <Button
        className={cn(className)}
        variant={variant}
        size={size}
        ref={ref}
        {...props}
      >
        <Icon className="h-4 w-4" />
      </Button>
    );
  }
);
IconButton.displayName = 'IconButton';

export { IconButton };
