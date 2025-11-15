export function getEmojiUrl([emojiCategory, emoji]: [string, string]): string {
  return `https://raw.githubusercontent.com/Tarikul-Islam-Anik/Telegram-Animated-Emojis/main/${emojiCategory}/${emoji}.webp`;
}