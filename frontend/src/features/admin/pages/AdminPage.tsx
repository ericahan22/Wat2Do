import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { useClerk } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { Sparkles, FileText } from "lucide-react";

function AdminPage() {
  const { signOut } = useClerk();
  const navigate = useNavigate();

  const handleLogout = () => {
    signOut();
  };

  const adminCards = [
    {
      title: "Event Promotions",
      description: "Manage event promotions and featured events",
      icon: Sparkles,
      route: "/admin/promotions",
      color: "text-purple-600 dark:text-purple-400",
    },
    {
      title: "Event Submissions",
      description: "Review and manage user-submitted events",
      icon: FileText,
      route: "/admin/submissions",
      color: "text-blue-600 dark:text-blue-400",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <Button onClick={handleLogout} variant="destructive">
            Logout
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {adminCards.map((card) => {
            const Icon = card.icon;
            return (
              <Card
                key={card.route}
                className="cursor-pointer transition-all hover:shadow-lg hover:scale-105"
                onClick={() => navigate(card.route)}
              >
                <CardHeader>
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-lg bg-gray-100 dark:bg-gray-800 ${card.color}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                    <CardTitle className="text-xl">{card.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{card.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default AdminPage;
