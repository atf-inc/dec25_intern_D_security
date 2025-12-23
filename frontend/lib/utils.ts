import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a number with commas
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat("en-US").format(num);
}

/**
 * Format a percentage
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Format a date relative to now
 */
export function formatRelativeTime(date: Date | string): string {
  const now = new Date();
  const then = new Date(date);
  const diffMs = now.getTime() - then.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return then.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

/**
 * Format a date
 */
export function formatDate(date: Date | string): string {
  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format date and time
 */
export function formatDateTime(date: Date | string): string {
  return new Date(date).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Get severity color class
 */
export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case "critical":
      return "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30";
    case "high":
      return "text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30";
    case "medium":
      return "text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30";
    case "low":
      return "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30";
    default:
      return "text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-800";
  }
}

/**
 * Get action color class
 */
export function getActionColor(action: string): string {
  switch (action.toUpperCase()) {
    case "BLOCK":
      return "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30";
    case "WARN":
      return "text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30";
    case "PASS":
      return "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30";
    default:
      return "text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-800";
  }
}

/**
 * Get badge color for champion rank
 */
export function getBadgeColor(badge: string): string {
  switch (badge.toLowerCase()) {
    case "platinum":
      return "from-slate-300 to-slate-500 text-slate-900";
    case "gold":
      return "from-yellow-400 to-yellow-600 text-yellow-900";
    case "silver":
      return "from-gray-300 to-gray-500 text-gray-900";
    case "bronze":
      return "from-orange-400 to-orange-600 text-orange-900";
    default:
      return "from-gray-200 to-gray-400 text-gray-700";
  }
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + "...";
}

/**
 * Sleep utility for async operations
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * API fetch wrapper with error handling
 * For /api/* paths, uses relative URLs (goes to Next.js API routes which proxy to backend)
 * For external URLs, uses them directly
 */
export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  // For /api/* paths, use relative URL to go through Next.js API routes
  // The API routes handle proxying to the backend using BACKEND_API_URL
  let url: string;
  if (endpoint.startsWith("http")) {
    url = endpoint;
  } else if (endpoint.startsWith("/api/")) {
    // Relative URL - goes to Next.js API routes
    url = endpoint;
  } else {
    // For non-/api/ paths, try to use NEXT_PUBLIC_API_URL or fallback
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "";
    url = baseUrl ? `${baseUrl}${endpoint}` : endpoint;
  }
  
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }
  
  return response.json();
}

