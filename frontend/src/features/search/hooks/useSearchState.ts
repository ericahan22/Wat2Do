import { useState, useEffect, useCallback } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useLocalStorage } from "react-use";
import { toast } from "sonner";
import { useApi } from "@/shared/hooks/useApi";

const SEARCH_STORAGE_KEY = "lastSearch";

export function useSearchState() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [lastSearch, setLastSearch] = useLocalStorage<string>(SEARCH_STORAGE_KEY, "");
  const navigate = useNavigate();
  const { eventsAPIClient } = useApi();

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

  const handleSearch = useCallback(async () => {
    const trimmedValue = inputValue.trim();

    // Easter egg: typing "random" navigates to a random event
    if (trimmedValue.toLowerCase() === "random") {
      try {
        // Fetch all events and pick a random one
        const response = await eventsAPIClient.getEvents({ all: true });
        if (response.results.length > 0) {
          const randomEvent = response.results[Math.floor(Math.random() * response.results.length)];
          toast.success(`Taking you to: ${randomEvent.title}`);
          navigate(`/events/${randomEvent.id}`);
          setInputValue("");
        } else {
          toast.error("No events found to randomize!");
        }
      } catch (error) {
        toast.error("Failed to find a random event");
        console.error(error);
      }
      return;
    }

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
  }, [inputValue, setLastSearch, setSearchParams, eventsAPIClient, navigate]);

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
