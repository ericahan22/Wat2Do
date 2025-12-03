import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import {
  Loader2,
  CheckCircle,
  AlertCircle,
  Check,
} from "lucide-react";
import { useWaitlist } from "@/features/waitlist/hooks/useWaitlist";

// Words to animate through
const ANIMATED_WORDS = ["events", "workshops", "socials", "hackathons", "conferences"];

// Pixel scramble animation component
const PixelText: React.FC<{ words: string[] }> = ({ words }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [displayText, setDisplayText] = useState(words[0]);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsAnimating(true);
      const nextIndex = (currentIndex + 1) % words.length;
      const targetWord = words[nextIndex];
      const chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`0123456789";

      let iterations = 0;
      const maxIterations = 10;

      const scrambleInterval = setInterval(() => {
        if (iterations >= maxIterations) {
          setDisplayText(targetWord);
          setCurrentIndex(nextIndex);
          setIsAnimating(false);
          clearInterval(scrambleInterval);
          return;
        }

        // Generate scrambled text that progressively reveals the target
        const progress = iterations / maxIterations;
        const revealedLength = Math.floor(targetWord.length * progress);

        let scrambled = "";
        for (let i = 0; i < targetWord.length; i++) {
          if (i < revealedLength) {
            scrambled += targetWord[i];
          } else {
            scrambled += chars[Math.floor(Math.random() * chars.length)];
          }
        }
        setDisplayText(scrambled);
        iterations++;
      }, 50);

    }, 3000);

    return () => clearInterval(interval);
  }, [currentIndex, words]);

  return (
    <span className={`inline-block min-w-[140px] ${isAnimating ? "opacity-90" : ""}`}>
      {displayText}
    </span>
  );
};

// Event thumbnail URLs for social proof
const EVENT_THUMBNAILS = [
  "https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/events/27c1433e-e1ad-4b15-9b82-52b4d2f6d3b0.jpg",
  "https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/events/c98fd4db-5622-43bc-8221-6d91266317e1.jpg",
  "https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/events/c7f13d84-c35f-4420-8582-c841f17fad1c.jpg",
  "https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/events/bb69dc4d-38e5-4c42-9f48-ee41ccc5de2b.jpg",
  "https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/events/c18494d1-1917-475f-bdf4-5b0212963d0c.png",
  "https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/events/8457eef5-7e7b-4b1f-bf23-47cb4372a1df.webp",
];

// Value propositions
const VALUE_PROPS = [
  "Always up-to-date",
  "Curated by humans",
  "Actively maintained",
];

const WaitlistPage: React.FC = () => {
  const { schoolSlug } = useParams<{ schoolSlug: string }>();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");

  const {
    schoolInfo,
    isLoading,
    isSubmitting,
    isSubmitSuccess,
    submitData,
    isFetchError,
    isReady,
    joinWaitlist,
    errorMessage,
    resetSubmit,
  } = useWaitlist(schoolSlug);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim()) {
      joinWaitlist(email.trim());
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-600" />
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // School not found
  if (isFetchError || !schoolSlug) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 text-center flex flex-col gap-4">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
          <h1 className="text-xl font-bold">School Not Found</h1>
          <p className="text-gray-600 dark:text-gray-400">
            This school is not currently on our waitlist.
          </p>
          <Button onClick={() => navigate("/")} variant="outline">
            Go to events
          </Button>
        </Card>
      </div>
    );
  }

  // Success state
  if (isSubmitSuccess && submitData) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md w-full p-6 text-center flex flex-col gap-4">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto" />
          <h1 className="text-xl font-bold">You're on the waitlist!</h1>
          <p className="text-gray-600 dark:text-gray-400">
            We'll notify you when {submitData.school} launches on Wat2Do.
          </p>
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
            <code className="text-sm text-blue-600 dark:text-blue-400">
              {submitData.email}
            </code>
          </div>
          <Button onClick={() => navigate("/")} variant="outline">
            Explore Waterloo events
          </Button>
        </Card>
      </div>
    );
  }

  // Main waitlist page with new design system
  if (isReady && schoolInfo) {
    const isAlreadyOnList = submitData?.message?.includes("already");

    const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setEmail(e.target.value);
      if (errorMessage) {
        resetSubmit();
      }
    };

    return (
      <div className="min-h-[60vh] relative">
        {/* Dotted background pattern */}
        <div
          className="absolute inset-0 -z-10"
          style={{
            backgroundImage: `radial-gradient(circle, #e5e7eb 1px, transparent 1px)`,
            backgroundSize: "24px 24px",
            opacity: 0.5,
          }}
        />

        {/* Hero Section */}
        <div className="flex flex-col items-center text-center pt-8 pb-12 px-4">
          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4 leading-tight sm:leading-snug">
            Discover
            <br />
            <span className="text-blue-500">{schoolInfo.name}</span>
            <br />
            <PixelText words={ANIMATED_WORDS} /> with Wat2Do
          </h1>

          {/* Sub-headline */}
          <p className="text-gray-600 dark:text-gray-400 text-lg max-w-xl mb-8">
            We're building the ultimate event discovery platform for {schoolInfo.name} students.
            Club events, socials, workshops, and more, all in one place.
          </p>

          {/* Value Props */}
          <div className="flex flex-wrap justify-center gap-6 mb-8">
            {VALUE_PROPS.map((prop) => (
              <div key={prop} className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                  <Check className="w-3 h-3 text-white" />
                </div>
                <span className="text-gray-700 dark:text-gray-300">{prop}</span>
              </div>
            ))}
          </div>

          {/* Social Proof - Event Thumbnails */}
          <div className="flex flex-col items-center mb-8">
            <div className="flex gap-2 mb-3">
              {EVENT_THUMBNAILS.map((thumbnail, index) => (
                <img
                  key={index}
                  src={thumbnail}
                  alt={`Event ${index + 1}`}
                  className="w-[100px] h-[100px] rounded-lg border-2 border-white dark:border-gray-800 object-cover shadow-md"
                />
              ))}
            </div>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Used by 80 UWaterloo students everyday, 2 months after launch
            </p>
          </div>

          {/* Email Form */}
          <form onSubmit={handleSubmit} className="w-full max-w-md mb-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <Input
                id="email"
                type="email"
                placeholder={`your.name@${schoolInfo.domains[0]}`}
                value={email}
                onChange={handleEmailChange}
                disabled={isSubmitting}
                className={`flex-1 ${
                  errorMessage ? "border-red-500 focus:border-red-500 focus:ring-red-500" : ""
                }`}
              />
              <Button
                type="submit"
                disabled={isSubmitting || !email.trim()}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Joining...
                  </>
                ) : (
                  "Get early access"
                )}
              </Button>
            </div>

            {/* Error/Success messages */}
            {errorMessage && (
              <div className="flex items-center justify-center gap-2 mt-3">
                <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                <p className="text-sm text-red-500">{errorMessage}</p>
              </div>
            )}
            {isAlreadyOnList && (
              <div className="flex items-center justify-center gap-2 mt-3">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                <p className="text-sm text-green-600">You're already on the waitlist!</p>
              </div>
            )}
          </form>

          {/* Micro-copy */}
          <p className="text-gray-500 dark:text-gray-400 text-sm">
            It's free, no spam. We'll only notify you when we launch.
          </p>
        </div>

        {/* Product Showcase Screenshot */}
        <div className="px-4 pb-12">
          <div className="max-w-4xl mx-auto">
            <div className="relative rounded-xl border border-gray-200 dark:border-gray-700 shadow-2xl overflow-hidden bg-white dark:bg-gray-800">
              <img
                src="https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/Screenshot+2025-11-28+at+10.06.44%E2%80%AFPM.png"
                alt="Wat2Do Events Platform Preview"
                className="w-full h-auto"
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Fallback loading state
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
        <p>Loading...</p>
      </div>
    </div>
  );
};

export default WaitlistPage;
