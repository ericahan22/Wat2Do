import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search } from 'lucide-react'
import { useRef, useEffect, memo, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'

interface SearchInputProps {
  placeholder?: string
  className?: string
}

const SearchInput = memo(({   placeholder = "Search...", className = "flex-1" }: SearchInputProps) => {
  const [, setSearchParams] = useSearchParams();
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-focus on search input when component mounts
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const handleSearch = useCallback(() => {
    setSearchParams({ search: inputRef.current?.value || "" })
  }, [setSearchParams])

  const handleKeyPress = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }, [handleSearch])

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchParams({ search: e.target.value })
  }, [])

  return (
    <div className={`relative ${className} border border-gray-300 dark:border-gray-700 rounded-md`}>
      <Input
        ref={inputRef}
        placeholder={placeholder}
        // onChange={handleInputChange}
        onKeyDown={handleKeyPress}
        className="pr-12 shadow-none border-none"
      />
      <Button 
        onMouseDown={handleSearch}
        className="absolute right-0 top-0 h-full w-12 !rounded-l-none rounded-r-md border-l-0 bg-gray-100 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-800"
        size="sm"
        variant="ghost"
      >
        <Search className="h-4 w-4" />
      </Button>
    </div>
  )
})

SearchInput.displayName = 'SearchInput'

export default SearchInput 