import { cva } from "class-variance-authority";

export const buttonVariants = cva(
  "inline-flex hover:bg-gray-100 dark:hover:bg-gray-900 cursor-pointer items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium focus:outline-none disabled:pointer-events-none disabled:opacity-50 select-none [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "text-gray-900 dark:text-gray-100 bg-[#0056D6] hover:!bg-[#0056D6]/80 text-white",
        destructive: "text-red-600 bg-red-500 hover:!bg-red-500/80 text-white",
        outline:
          "border border-gray-200 text-gray-900 hover:border-gray-300 dark:border-gray-700 dark:text-gray-100 dark:hover:border-gray-600",
        secondary: "text-gray-900 dark:text-gray-100",
        ghost:
          "hover:bg-gray-500/10 text-gray-900 dark:text-gray-100 dark:hover:bg-gray-50/10",
        link:
          "text-gray-900 underline-offset-4 hover:underline hover:bg-gray-500/10 dark:text-gray-100 dark:hover:bg-gray-50/10",
      },
      effect: {
        expandIcon: "group gap-0 relative",
        ringHover: "hover:ring-2 hover:ring-primary/90 hover:ring-offset-2",
        shine:
          "before:animate-shine relative overflow-hidden before:absolute before:inset-0 before:rounded-[inherit] before:bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.5)_50%,transparent_75%,transparent_100%)] before:bg-[length:250%_250%,100%_100%] before:bg-no-repeat",
        shineHover:
          "relative overflow-hidden before:absolute before:inset-0 before:rounded-[inherit] before:bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.5)_50%,transparent_75%,transparent_100%)] before:bg-[length:250%_250%,100%_100%] before:bg-no-repeat hover:before:bg-[position:-100%_0,0_0]",
        gooeyRight:
          "relative z-0 overflow-hidden before:absolute before:inset-0 before:-z-10 before:translate-x-[150%] before:translate-y-[150%] before:scale-[2.5] before:rounded-[100%] before:bg-gradient-to-r from-white/40 hover:before:translate-x-[0%] hover:before:translate-y-[0%]",
        gooeyLeft:
          "relative z-0 overflow-hidden after:absolute after:inset-0 after:-z-10 after:translate-x-[-150%] after:translate-y-[150%] after:scale-[2.5] after:rounded-[100%] after:bg-gradient-to-l from-white/40 hover:after:translate-x-[0%] hover:after:translate-y-[0%]",
        underline:
          "relative !no-underline after:absolute after:bg-primary after:bottom-2 after:h-[1px] after:w-2/3 after:origin-bottom-left after:scale-x-100 hover:after:origin-bottom-right hover:after:scale-x-0",
        hoverUnderline:
          "relative !no-underline after:absolute after:bg-primary after:bottom-2 after:h-[1px] after:w-2/3 after:origin-bottom-right after:scale-x-0 hover:after:origin-bottom-left hover:after:scale-x-100",
        gradientSlideShow:
          "bg-[size:400%] bg-[linear-gradient(-45deg,var(--gradient-lime),var(--gradient-ocean),var(--gradient-wine),var(--gradient-rust))] animate-gradient-flow",
      },
      size: {
        sm: "h-8 rounded-xl px-2",
        default: "h-9 rounded-xl px-3",
        lg: "h-11 rounded-xl px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);
