import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/shared/components/ui/select";
import { SCHOOLS } from "@/features/events/constants/events";

interface SchoolSelectProps {
  value: string;
  onChange: (next: string) => void;
  className?: string;
}

const SchoolSelect: React.FC<SchoolSelectProps> = ({
  value,
  onChange,
  className,
}) => {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className={className} aria-label="Select school">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {SCHOOLS.map((school) => (
          <SelectItem key={school.value} value={school.value}>
            {school.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

export default SchoolSelect;
