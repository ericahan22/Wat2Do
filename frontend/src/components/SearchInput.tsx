import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search } from 'lucide-react'
import { useRef, useEffect, memo, useState } from 'react'

interface SearchInputProps {
  onSearch: (value: string) => void
  placeholder?: string
  className?: string
}

const SearchInput = memo(({ onSearch, placeholder = "Search...", className = "flex-1" }: SearchInputProps) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const [localSearchTerm, setLocalSearchTerm] = useState("")

  // Auto-focus on search input when component mounts
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const handleSearch = () => {
    onSearch(localSearchTerm)
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className={`relative ${className} border border-gray-300 dark:border-gray-700 rounded-md`}>
      <Input
        ref={inputRef}
        placeholder={placeholder}
        value={localSearchTerm}
        onChange={(e) => setLocalSearchTerm(e.target.value)}
        onKeyPress={handleKeyPress}
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