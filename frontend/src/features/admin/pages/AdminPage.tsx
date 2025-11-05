import { useState } from "react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { useClerk } from "@clerk/clerk-react";
import { PromotionsManager } from "@/features/admin/components/PromotionsManager";
import { SubmissionsReview } from "@/features/admin/components/SubmissionsReview";

/**
 * Admin page for managing event promotions
 * Requires admin authentication
 */
function AdminPage() {
  const { signOut } = useClerk();
  const [error, setError] = useState<string | null>(null);

  const handleLogout = () => {
    signOut();
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold ">Admin Dashboard</h1>
          <Button onClick={handleLogout} variant="destructive">
            Logout
          </Button>
        </div>

        {error && (
          <Card className="mb-6 border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
            <CardContent className="pt-6 flex items-center justify-between">
              <div className="text-sm text-red-700 dark:text-red-300">{error}</div>
              <Button onClick={() => setError(null)} variant="ghost" size="sm" className="text-red-500">
                ×
              </Button>
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="promotions" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="promotions">Event Promotions</TabsTrigger>
            <TabsTrigger value="submissions">Event Submissions</TabsTrigger>
          </TabsList>

          <TabsContent value="promotions" className="mt-6">
            <PromotionsManager />
          </TabsContent>

          <TabsContent value="submissions" className="mt-6">
            <SubmissionsReview />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default AdminPage;
