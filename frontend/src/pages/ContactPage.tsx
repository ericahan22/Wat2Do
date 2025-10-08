import React from "react";

const ContactPage: React.FC = () => {
  return (
    <div className="min-h-[60vh]">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
        Contact
      </h1>
      <p className="text-gray-600 dark:text-gray-300 mb-8">
        Questions, ideas, or feedback? We'd love to hear from you.
      </p>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-5 bg-white dark:bg-gray-900">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Email
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            Reach us at {" "}
            <a
              href="mailto:tqiu@uwaterloo.ca"
              className="underline hover:text-gray-900 dark:hover:text-gray-100"
            >
              tqiu@uwaterloo.ca
            </a>{" "}
            and {" "}
            <a
              href="mailto:ericahan.38@gmail.com"
              className="underline hover:text-gray-900 dark:hover:text-gray-100"
            >
              ericahan.38@gmail.com
            </a>
            .
          </p>
        </div>

        <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-5 bg-white dark:bg-gray-900">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            GitHub Issues
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            Found a bug or want a feature? Open an issue {" "}
            <a
              href="https://github.com/ericahan22/bug-free-octo-spork/issues"
              target="_blank"
              rel="noopener noreferrer"
              className="underline hover:text-gray-900 dark:hover:text-gray-100"
            >
              on GitHub
            </a>
            .
          </p>
        </div>
      </div>
    </div>
  );
};

export default React.memo(ContactPage);


