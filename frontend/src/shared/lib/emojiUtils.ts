/**
 * Utility functions for handling emoji URLs and rendering
 */

export function getEmojiUrl(filterItem: FilterWithEmoji): string {
  const [category, emojiString] = filterItem;
  return `https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/${category}/${emojiString}.webp`;
}

export type FilterWithEmoji = [string, string, string]; // [category, emojiString, filterName]
