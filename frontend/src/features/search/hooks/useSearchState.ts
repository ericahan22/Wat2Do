import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

export function useSearchState() {
  const [searchParams, setSearchParams] = useSearchParams();

  const searchParam = searchParams.get("search") || "";
  const [inputValue, setInputValue] = useState(searchParam);

  // Sync input value with URL on mount and when URL changes externally (e.g., from filters)
  useEffect(() => {
    const urlSearchParam = searchParams.get("search") || "";
    setInputValue(urlSearchParam);
  }, [searchParams]); // Sync when URL search param changes

  const handleSearch = useCallback(() => {
    const trimmedValue = inputValue.trim();

    if (trimmedValue) {
      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        nextParams.set("search", trimmedValue);
        return nextParams;
      });
    } else {
      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        nextParams.delete("search");
        return nextParams;
      });
    }
  }, [inputValue, setSearchParams]);

  const handleClear = useCallback(() => {
    setInputValue("");
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      nextParams.delete("search");
      return nextParams;
    });
  }, [setSearchParams]);

  const handleChange = useCallback((value: string) => {
    setInputValue(value);
  }, []);

  return {
    inputValue,
    handleSearch,
    handleClear,
    handleChange,
  };
}
