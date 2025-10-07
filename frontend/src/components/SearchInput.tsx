import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { useRef, useEffect, memo, useCallback, useState } from "react";
import { useSearchParams } from "react-router-dom";

interface SearchInputProps {
  placeholder?: string;
  className?: string;
}

const SearchInput = memo(
  ({ placeholder = "Search...", className = "flex-1" }: SearchInputProps) => {
    const [searchParams, setSearchParams] = useSearchParams();
    const inputRef = useRef<HTMLInputElement>(null);
    const searchParam = searchParams.get("search") || "";
    const [inputValue, setInputValue] = useState(searchParam);

    // Sync input value with URL search param
    useEffect(() => {
      setInputValue(searchParam);
    }, [searchParam]);

    // Auto-focus on search input when component mounts
    useEffect(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, []);

    const handleSearch = useCallback(() => {
      setSearchParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        nextParams.set("search", inputValue);
        return nextParams;
      });
    }, [setSearchParams, inputValue]);

    const handleKeyPress = useCallback(
      (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
          handleSearch();
        }
      },
      [handleSearch]
    );

    const handleChange = useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value);
      },
      []
    );

    return (
      <div
        className={`relative ${className} border border-gray-300 h-9 dark:border-gray-700 overflow-hidden rounded-md`}
      >
        <Input
          ref={inputRef}
          placeholder={placeholder}
          value={inputValue}
          onChange={handleChange}
          onKeyDown={handleKeyPress}
          className="pr-12 shadow-none border-none h-8"
        />
        <Button
          onMouseDown={handleSearch}
          className="absolute right-0 top-0 w-12 h-full !rounded-l-none rounded-r-md border-l-0 bg-gray-100 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-800"
          size="sm"
          variant="ghost"
        >
          <Search className="h-4 w-4" />
        </Button>
      </div>
    );
  }
);

SearchInput.displayName = "SearchInput";

export default SearchInput;
