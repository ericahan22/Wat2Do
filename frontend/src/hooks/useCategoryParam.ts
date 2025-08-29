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
      const nextParams = new URLSearchParams(categoryParams);
      nextParams.set("category", value);
      setCategoryParams(nextParams);
    },
    [setCategoryParam]
  );

  return { categoryParam, setCategoryParam: handleCategoryParamChange };
};
