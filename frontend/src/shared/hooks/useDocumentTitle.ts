import { useEffect } from "react";

/**
 * Custom hook to manage document title
 * @param title - The title to set for the document
 * @param dependencies - Optional array of dependencies to trigger title update
 */
export const useDocumentTitle = (title: string) => {
  useEffect(() => {
    document.title = title;
  }, [title]);
};
