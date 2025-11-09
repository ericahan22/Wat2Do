import { Button } from "@/shared/components/ui/button";
import { useClerk } from "@clerk/clerk-react";
import { PromotionsManager } from "@/features/admin/components/PromotionsManager";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export function PromotionsPage() {
  const { signOut } = useClerk();
  const navigate = useNavigate();

  const handleLogout = () => {
    signOut();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <div className="flex flex-col gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate("/admin")}
              className="flex items-center gap-2 w-fit"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Admin
            </Button>
            <h1 className="text-3xl font-bold">Event Promotions</h1>
          </div>
          <Button onClick={handleLogout} variant="destructive">
            Logout
          </Button>
        </div>

        <PromotionsManager />
      </div>
    </div>
  );
}


