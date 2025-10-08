import { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { useLocalStorage } from "react-use";

const SEARCH_STORAGE_KEY = "lastSearch";

export function useSearchState() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [lastSearch, setLastSearch] = useLocalStorage<string>(SEARCH_STORAGE_KEY, "");
  
  const searchParam = searchParams.get("search") || "";
  const [inputValue, setInputValue] = useState(searchParam || lastSearch || "");
  const isInitialMount = useRef(true);

  // Sync input value with URL search param when it changes
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      // On initial mount, only sync if there's an actual search param
      if (searchParam) {
        setInputValue(searchParam);
      } else if (lastSearch && lastSearch.trim()) {
        // If URL is empty but we have a last search, redirect to it
        setInputValue(lastSearch);
        setSearchParams((prev) => {
          const nextParams = new URLSearchParams(prev);
          nextParams.set("search", lastSearch);
          return nextParams;
        });
      }
    } else {
      // On subsequent updates, always sync with URL
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
    } else {
      // If input is empty, clear the search
      setInputValue("");
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

