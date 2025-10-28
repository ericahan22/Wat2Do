import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { useLocalStorage } from "react-use";

const SEARCH_STORAGE_KEY = "lastSearch";

export function useSearchState() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [lastSearch, setLastSearch] = useLocalStorage<string>(SEARCH_STORAGE_KEY, "");
  
  const searchParam = searchParams.get("search") || "";
  const [inputValue, setInputValue] = useState(searchParam || lastSearch || "");

  // Sync input value with URL on mount and when URL changes externally (e.g., from filters)
  useEffect(() => {
    const urlSearchParam = searchParams.get("search") || "";
    setInputValue(urlSearchParam);
  }, [searchParams]); // Sync when URL search param changes

  // Handle initial mount - restore last search if no URL param
  useEffect(() => {
    const urlSearchParam = searchParams.get("search") || "";
    if (!urlSearchParam && lastSearch && lastSearch.trim()) {
      // If URL is empty but we have a last search, redirect to it
      setInputValue(lastSearch);
      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        nextParams.set("search", lastSearch);
        return nextParams;
      });
    }
  }, [lastSearch, searchParams, setSearchParams]); 

  const handleSearch = useCallback(() => {
    const trimmedValue = inputValue.trim();
    if (trimmedValue) {
      setLastSearch(trimmedValue);
      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        nextParams.set("search", trimmedValue);
        return nextParams;
      });
    } else {
      // If input is empty, clear the search
      setLastSearch("");
      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        nextParams.delete("search");
        return nextParams;
      });
    }
  }, [inputValue, setLastSearch, setSearchParams]);

  const handleClear = useCallback(() => {
    setInputValue("");
    setLastSearch("");
    setSearchParams((prev) => {
      const nextParams = new URLSearchParams(prev);
      nextParams.delete("search");
      return nextParams;
    });
  }, [setLastSearch, setSearchParams]);

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

