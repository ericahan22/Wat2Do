import * as React from "react";
import { useFormContext } from "react-hook-form";

const FormFieldContext = React.createContext<{ name: string }>({} as { name: string });
const FormItemContext = React.createContext<{ id: string }>({} as { id: string });

export { FormFieldContext, FormItemContext };

export const useFormField = () => {
  const fieldContext = React.useContext(FormFieldContext);
  const itemContext = React.useContext(FormItemContext);
  const { getFieldState, formState } = useFormContext();

  const fieldState = getFieldState(fieldContext.name, formState);

  if (!fieldContext) {
    throw new Error("useFormField should be used within <FormField>");
  }

  const { id } = itemContext;

  return {
    id,
    name: fieldContext.name,
    formItemId: `${id}-form-item`,
    formDescriptionId: `${id}-form-item-description`,
    formMessageId: `${id}-form-item-message`,
    ...fieldState,
  };
};
