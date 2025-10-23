import React from "react";
import { SEOHead } from "@/shared/components/SEOHead";

const ContactPage: React.FC = () => {
  return (
    <div className="min-h-[60vh]">
      <SEOHead 
        title="Contact Wat2Do - Get in Touch"
        description="Have questions, ideas, or feedback about Wat2Do? Contact us to help improve the University of Waterloo event discovery platform."
        url="/contact"
        keywords={[
          'contact Wat2Do',
          'feedback',
          'support',
          'University of Waterloo events',
          'help',
          'suggestions'
        ]}
      />
      <h1 className="text-3xl font-bold mb-4">
        Contact
      </h1>
      <p className="mb-8">
        Questions, ideas, or feedback? We'd love to hear from you.
      </p>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-5 bg-white dark:bg-gray-900">
          <h2 className="text-lg font-semibold mb-2">
            Email
          </h2>
          <p>
            Reach us at {" "}
            <a
              href="mailto:tqiu@uwaterloo.ca"
              className="underline hover:text-gray-900 dark:hover:text-gray-100"
            >
              tqiu@uwaterloo.ca
            </a>{" "}
            and {" "}
            <a
              href="mailto:e22han@uwaterloo.ca"
              className="underline hover:text-gray-900 dark:hover:text-gray-100"
            >
              e22han@uwaterloo.ca
            </a>
            .
          </p>
        </div>

        <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-5 bg-white dark:bg-gray-900">
          <h2 className="text-lg font-semibold mb-2">
            GitHub Issues
          </h2>
          <p>
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

export default ContactPage;


