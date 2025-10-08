import React from "react";
import { Button } from "@/components/ui/button";

const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
          About Wat2Do
        </h1>

        <p className="text-lg text-gray-600 dark:text-gray-300 mb-4">
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
          remote controlled car hackathon,{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Food%20and%20Drink/Fork%20And%20Knife%20With%20Plate.webp"
            alt="Fork And Knife With Plate"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          italian cooking lessons in a studio kitchen, a free 2-hr{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/People/Mechanical%20Arm.webp"
            alt="Mechanical Arm"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          curling lesson, a $20{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Travel%20and%20Places/Motor%20Boat.webp"
            alt="Motor Boat"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          harbour boat cruise, a $30 trip to the Stratford Festival to
          watch{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Activity/Performing%20Arts.webp"
            alt="Performing Arts"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          Annie,{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/Travel%20and%20Places/Roller%20Coaster.webp"
            alt="Roller Coaster"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          Canada's Wonderland, and tons of great company{" "}
          <img
            src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/People/Handshake.webp"
            alt="Handshake"
            width="25"
            height="25"
            className="inline mx-1"
          />{" "}
          networking events (
          <a
            href="/events?view=calendar&search=Atlassian"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Atlassian
          </a>
          , Patreon,{" "}
          <a
            href="/events?view=calendar&search=Point72"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Point72
          </a>
          ). We realized we were missing out on so much happening around campus
          and built this for ourselves in August 2025. After 2 months we're
          extroardinarily excited to be sharing it with the rest of you! P.S. We
          don't run ads or sponsors, everything runs out of our own pockets.
        </p>

        <p className="text-lg font-bold text-gray-600 dark:text-gray-300 mb-12">
          — Tony & Erica
        </p>

        <p className="text-lg text-gray-600 dark:text-gray-300 mb-12">
          We believe there are helpful tips to making the most out of this site,
          so we went ahead and created a little guide for you, depending on your
          goals.
        </p>

        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Networking
        </h2>
        <p className="text-gray-600 dark:text-gray-300 mb-4">
          Skip the generic LinkedIn messages. The best networking happens at
          events where people are in-person, sharing the present with you.
        </p>
        <p className="text-gray-600 dark:text-gray-300 mb-8">
          Check out events like{" "}
          <a
            href="/events?view=calendar&search=All Things Legal Panel"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            All Things Legal Panel
          </a>
          ,
          <a
            href="/events?view=calendar&search=Innovation Open House"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            {" "}
            Innovation Open House
          </a>
          , and
          <a
            href="/events?view=calendar&search=WiE x Bloomberg"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            {" "}
            WiE x Bloomberg Fall Kick Off
          </a>{" "}
          for industry connections.
        </p>

        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Finding Your Crowd
        </h2>
        <p className="text-gray-600 dark:text-gray-300 mb-4">
          Don't just join clubs that match your major. The most interesting
          people often come from completely different fields. Use our filters to
          discover niche communities you never knew existed.
        </p>
        <p className="text-gray-600 dark:text-gray-300 mb-8">
          Try events like{" "}
          <a
            href="/events?view=calendar&search=Gatka Classes"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Gatka Classes
          </a>
          ,
          <a
            href="/events?view=calendar&search=Retro Rollers"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            {" "}
            Retro Rollers
          </a>
          , and
          <a
            href="/events?view=calendar&search=Repair Club"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            {" "}
            Repair Club First Meeting
          </a>{" "}
          to find unexpected communities.
        </p>

        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Making Memories With Yourself or Your Friends
        </h2>
        <p className="text-gray-600 dark:text-gray-300 mb-4">
          The best events for groups are the ones that don't require
          registration. You can show up with friends, leave early if it's not
          fun, or split up and meet different people. Pro tip: check the "food"
          filter for events with free meals, we experience them to be more
          social and less formal.
        </p>
        <p className="text-gray-600 dark:text-gray-300 mb-8">
          Great for groups:{" "}
          <a
            href="/events?view=calendar&search=Nature Hike"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            Nature Hike
          </a>
          ,
          <a
            href="/events?view=calendar&search=Fall BBQ"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            {" "}
            Fall BBQ Smash
          </a>
          , and
          <a
            href="/events?view=calendar&search=Trivia Night"
            className="underline hover:text-gray-500 dark:hover:text-gray-200"
          >
            {" "}
            Trivia Night
          </a>
          .
        </p>

        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          Start Exploring
        </h2>
        <p className="text-gray-600 dark:text-gray-300 mb-8">
          Check Wat2Do regularly for new events. Subscribe to our newsletter for
          weekly updates. Don't be afraid to attend events alone! The best
          connections happen when you show up.
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
