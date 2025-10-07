import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { useLocalStorage } from "react-use";

const SEARCH_STORAGE_KEY = "lastSearch";

export function useSearchState() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [lastSearch, setLastSearch] = useLocalStorage<string>(SEARCH_STORAGE_KEY, "");
  
  const searchParam = searchParams.get("search") || "";
  const [inputValue, setInputValue] = useState(searchParam || lastSearch || "");

  // Sync input value with URL search param when it changes
  useEffect(() => {
    if (searchParam) {
      setInputValue(searchParam);
    }
  }, [searchParam]);

  const handleSearch = useCallback(() => {
    if (inputValue.trim()) {
      setLastSearch(inputValue);
      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        nextParams.set("search", inputValue);
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

