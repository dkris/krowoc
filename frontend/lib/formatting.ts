/**
 * Format a number with commas as thousands separators
 * @param num Number to format
 * @returns Formatted number string
 */
export function formatNumber(num: number | undefined): string {
  if (num === undefined) return '-';
  return new Intl.NumberFormat().format(Math.round(num));
}

/**
 * Format a cost value as currency
 * @param cost Cost value to format
 * @returns Formatted cost string
 */
export function formatCost(cost: number | undefined): string {
  if (cost === undefined) return '-';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 4,
    maximumFractionDigits: 4,
  }).format(cost);
} 