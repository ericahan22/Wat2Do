import { toast } from "sonner";

export function handleError(error: unknown) {
  if (error instanceof Error) {
    toast.error(error.message);
  } else {
    toast.error("Something went wrong.");
  }
  console.error(error);
}

