import * as React from "react"

import { cn } from "@/shared/lib/utils"

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "flex min-h-[80px] w-full min-w-0 rounded-xl border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-450 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-900 dark:text-gray-100 dark:placeholder:text-gray-400 md:text-sm resize-vertical",
        className
      )}
      {...props}
    />
  )
}

export { Textarea }
