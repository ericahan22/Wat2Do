import { debounce } from "lodash";
import { useCallback, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

export const useSearchParam = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [searchValue, setSearchValue] = useState(searchParams.get("search") || "");

    const debouncedSetSearchValue = useMemo(() => debounce((value: string) => {
        const nextParams = new URLSearchParams(searchParams);
        nextParams.set("search", value);
        setSearchParams(nextParams);
    }, 300), [searchParams, setSearchParams]);

    const handleSearchValueChange = useCallback((value: string) => {
        debouncedSetSearchValue(value);
        setSearchValue(value);
    }, [debouncedSetSearchValue]);

    return { searchValue, setSearchValue: handleSearchValueChange };
}