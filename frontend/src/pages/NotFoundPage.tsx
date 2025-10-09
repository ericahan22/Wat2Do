import React from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import GeeveKickingRocks from "@/assets/artwork/geeve-kicking-rocks.svg?react";

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center max-w-md mx-auto px-4">
          <GeeveKickingRocks className="w-48 h-48 mb-6 mx-auto text-gray-400 dark:text-gray-600" />
        
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          404
        </h1>
        
        <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-4">
          Page Not Found
        </h2>
        
        <p className="text-gray-600 dark:text-gray-400 mb-8">
          Looks like this page decided to skip the event. Let's get you back to discovering what's happening on campus!
        </p>
        
        <div className="space-y-3">
          <Button 
            onClick={() => navigate("/")} 
            className="w-full"
          >
            Back to Events
          </Button>
          
          <Button 
            onClick={() => navigate(-1)} 
            variant="outline"
            className="w-full"
          >
            Go Back
          </Button>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
