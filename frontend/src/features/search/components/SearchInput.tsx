import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import { Search, X } from "lucide-react";
import { useRef, useEffect, memo } from "react";
import { useSearchState } from "@/features/search";

interface SearchInputProps {
  placeholder?: string;
  className?: string;
}

const SearchInput = memo(
  ({ placeholder = "Search...", className = "flex-1" }: SearchInputProps) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const { inputValue, handleSearch, handleClear, handleChange } = useSearchState();

    useEffect(() => {
      inputRef.current?.focus();
    }, []);

    const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        handleSearch();
      }
    };

    const onClear = () => {
      handleClear();
      inputRef.current?.focus();
    };

    const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      handleChange(e.target.value);
    };

    return (
      <div
        className={`relative ${className} border border-gray-300 h-9 dark:border-gray-700 overflow-hidden rounded-xl`}
      >
        <Input
          ref={inputRef}
          placeholder={placeholder}
          value={inputValue}
          onChange={onChange}
          onKeyDown={onKeyDown}
          className={`shadow-none text-sm border-none ${
            inputValue ? "pr-20" : "pr-12"
          }`}
        />
        {inputValue && (
          <ClearButton onClear={onClear} />
        )}
        <SearchButton onSearch={handleSearch} />
      </div>
    );
  }
);

const ClearButton = memo(({ onClear }: { onClear: () => void }) => (
  <Button
    onMouseDown={onClear}
    className="absolute right-12 top-0 w-8 h-full rounded-none border-none bg-transparent hover:bg-gray-50 dark:hover:bg-gray-900"
    size="sm"
    variant="ghost"
  >
    <X className="h-4 w-4 text-gray-500 dark:text-gray-400" />
  </Button>
));

const SearchButton = memo(({ onSearch }: { onSearch: () => void }) => (
  <Button
    onMouseDown={onSearch}
    className="absolute right-0 top-0 w-12 h-full !rounded-l-none rounded-r-md border-l-0 bg-gray-100 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-800"
    size="sm"
    variant="ghost"
  >
    <Search className="h-4 w-4" />
  </Button>
));

SearchInput.displayName = "SearchInput";
ClearButton.displayName = "ClearButton";
SearchButton.displayName = "SearchButton";

export default SearchInput;
