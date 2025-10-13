import React, { useEffect, useState } from "react";
import { Github } from "lucide-react";
import { Button } from "@/shared/components/ui/button";

const GITHUB_OWNER = "ericahan22";
const GITHUB_REPO = "bug-free-octo-spork";

function GitHubLink() {
  const [starCount, setStarCount] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStarCount = async () => {
      try {
        const response = await fetch(
          `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}`
        );
        if (response.ok) {
          const data = await response.json();
          setStarCount(data.stargazers_count);
        }
      } catch (error) {
        console.error("Error fetching GitHub star count:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStarCount();
  }, []);

  return (
    <a
      href={`https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center text-gray-600 dark:text-gray-300 transition-colors"
      title="View on GitHub"
    >
      <Button variant="ghost">
        <Github className="h-4 w-4 text-gray-700 dark:text-gray-300" />
        {!isLoading && starCount !== null && (
          <span className="text-sm font-medium">{starCount}</span>
        )}
      </Button>
    </a>
  );
}

export default React.memo(GitHubLink);
