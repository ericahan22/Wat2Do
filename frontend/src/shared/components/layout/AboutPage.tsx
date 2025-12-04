import React from "react";
import { Button } from "@/shared/components/ui/button";
import { SEOHead } from "@/shared/components/SEOHead";

const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <SEOHead
        title="About Wat2Do - Discover University of Waterloo Events"
        description="Learn about Wat2Do, the platform helping University of Waterloo students discover exciting club events and campus activities. Built by students, for students."
        url="/about"
        keywords={[
          "Waterloo events",
          "UW events",
          "UWaterloo events",
          "about Wat2Do",
          "University of Waterloo events platform",
          "campus event discovery",
          "student event platform",
          "UW event aggregator",
          "campus activities",
          "student life",
        ]}
      />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold mb-8">About Wat2Do</h1>

        <p className="text-lg mb-4">
          Welcome to Wat2Do! We created this platform after stumbling upon way
          too many underrated events by sheer coincidence. We found ourselves at{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/People/Man%20Dancing.webp"
            alt="Man Dancing"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          hip-hop dance tutorials, a{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Activity/Video%20Game.webp"
            alt="Video Game"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          remote-controlled car hackathon,{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Food%20and%20Drink/Fork%20And%20Knife%20With%20Plate.webp"
            alt="Fork And Knife With Plate"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          Italian cooking lessons at a culinary school, a free two-hour{" "}
          <a
            href="/events/2588"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            curling lesson
          </a>
          , a $20{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Travel%20and%20Places/Motor%20Boat.webp"
            alt="Motor Boat"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          harbour boat cruise, a $30{" "}
          <a
            href="/events/2463"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            trip to the Stratford Festival
          </a>
          {" "}to watch{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Activity/Performing%20Arts.webp"
            alt="Performing Arts"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          <i>Annie</i>,{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Travel%20and%20Places/Roller%20Coaster.webp"
            alt="Roller Coaster"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          visiting Canada's Wonderland (then missing the bus back to Waterloo), and meeting tons of great company at{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/People/Handshake.webp"
            alt="Handshake"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          networking events. We didn't want to miss other cool things happening on campus, so we built this for ourselves in{" "}
          <a
            href="https://bug-free-octo-spork.s3.us-east-2.amazonaws.com/Screenshot+2025-10-08+at+4.20.42%E2%80%AFAM.png"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            August 2025
          </a>
          . Two months later, and we're extroardinarily excited to be sharing it with
          the rest of you! All art is done by Erica. P.S. We don't run ads,
          everything runs out of our own pockets.
        </p>

        <p className="text-lg font-bold mb-12">— Tony & Erica</p>

        <p className="text-lg mb-12">
          To make the most out of this site, here are some of our helpful tips, depending on your goals.
        </p>

        <h2 className="text-2xl font-bold mb-6">Expanding Your Professional Network</h2>
        <p className="mb-4">
          A lot of company-sponsored events might fly under your radar, making it easy to miss out on crucial networking opportunities. We've met recruiters from{" "}
          <a
            href="/events/1823"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Atlassian
          </a>
          ,{" "}
          <a
            href="/events/2657"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Bloomberg
          </a>
          , and{" "}
          <a
            href="/events/1694"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Point72
          </a>{" "}
          from events we just found out about the day before.
        </p>
        <p className="mb-8">
          Check out similar events like{" "}
          <a
            href="/events/2406"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Navigating Co-op
          </a>
          ,{" "}
          <a
            href="/events/3169"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Explore ActSci at Equitable
          </a>
          , and{" "}
          <a
            href="/events/2753"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Ctrl+Alt+Innovate
          </a>
          .
        </p>

        <h2 className="text-2xl font-bold mb-6">Random Events You Didn't Know Existed</h2>
        <p className="mb-4">
          Honestly, the best part about building this project was discovering clubs we had
          no idea were on campus. There's a{" "}
          <a
            href="/events/2278"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Repair Club
          </a>{" "}
          where you can fix your broken electronics, the Iranian Students' Association's{" "}
          <a
            href="/events/934"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Persian Zumba
          </a>{" "}
          class, and Strength Club's{" "}
          <a
            href="/events/1358"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Battle of the Barbells
          </a>
          .
        </p>
        <p className="mb-8">
        </p>

        <h2 className="text-2xl font-bold mb-6">Search Tips</h2>
        <p className="mb-4">
          Category filters can help you find events that you are interested in. "Food," "Price," and "Registration Required" tags let you know what to expect. Try searching for what you are looking for, and see what comes up!
        </p>
        <p className="mb-8">
          If you're with your friends, try{" "}
          <a
            href="/events/1636"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Pho Night
          </a>
          ,{" "}
          <a
            href="/events/2304"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Campfire Jam
          </a>
          , or{" "}
          <a
            href="/events/2212"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Global Games Night
          </a>{" "}
          .
        </p>

        <h2 className="text-2xl font-bold  mb-6">Start Exploring</h2>
        <p className=" mb-4">
          Check Wat2Do regularly for new events as events are added (almost) live! Or, subscribe to our newsletter for
          daily updates. Don't be afraid to attend events alone! The best
          connections happen when you just show up.
        </p>
        <p className="mb-8">
          (P.S. You can enter "random" in the search bar to generate a random upcoming event!)
        </p>

        <div className="flex gap-4">
          <Button variant="link">
            <a href="/events">Browse Events</a>
          </Button>
          <Button variant="link">
            <a href="/clubs">Explore Clubs</a>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
