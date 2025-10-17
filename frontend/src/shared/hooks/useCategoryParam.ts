import { useCallback, useState } from "react";
import { useSearchParams } from "react-router-dom";

export const useCategoryParam = () => {
  const [categoryParams, setCategoryParams] = useSearchParams();
  const [categoryParam, setCategoryParam] = useState(
    categoryParams.get("category") || ""
  );

  const handleCategoryParamChange = useCallback(
    (value: string) => {
      setCategoryParam(value);
      setCategoryParams((prev) => {
        const nextParams = new URLSearchParams(prev);
        nextParams.set("category", value);
        return nextParams;
      });
    },
    [setCategoryParam, setCategoryParams]
  );

  return { categoryParam, setCategoryParam: handleCategoryParamChange };
};
