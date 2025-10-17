import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Custom color system utilities - Blue and Green ranges
export const primaryColors = [
  'var(--primary-1)', // Light Blue
  'var(--primary-2)', // Blue 300
  'var(--primary-3)', // Blue 500
  'var(--primary-4)', // Blue 700
  'var(--primary-5)', // Blue 800
  'var(--primary-6)', // Dark Blue
]

export const secondaryColors = [
  'var(--secondary-1)', // Light Green
  'var(--secondary-2)', // Green 300
  'var(--secondary-3)', // Green 500
  'var(--secondary-4)', // Green 700
  'var(--secondary-5)', // Green 800
  'var(--secondary-6)', // Dark Green
]

export function getRandomPrimaryColor(): string {
  return primaryColors[Math.floor(Math.random() * primaryColors.length)]
}

export function getRandomSecondaryColor(): string {
  return secondaryColors[Math.floor(Math.random() * secondaryColors.length)]
}

export function getColorByIndex(index: number, isPrimary: boolean = true): string {
  const colors = isPrimary ? primaryColors : secondaryColors
  return colors[index % colors.length]
}
