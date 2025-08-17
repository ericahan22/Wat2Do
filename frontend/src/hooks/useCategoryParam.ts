import { debounce } from "lodash";
import { useCallback, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

export const useCategoryParam = () => {
    const [categoryParams, setCategoryParams] = useSearchParams();
    const [categoryParam, setCategoryParam] = useState(categoryParams.get("category") || "");

    const debouncedSetCategoryParam = useMemo(() => debounce((value: string) => {
        const nextParams = new URLSearchParams(categoryParams);
        nextParams.set("category", value);
        setCategoryParams(nextParams);
    }, 300), [categoryParams, setCategoryParams]);

    const handleCategoryParamChange = useCallback((value: string) => {
        debouncedSetCategoryParam(value);
        setCategoryParam(value);
    }, [debouncedSetCategoryParam]);

    return { categoryParam, setCategoryParam: handleCategoryParamChange };
}