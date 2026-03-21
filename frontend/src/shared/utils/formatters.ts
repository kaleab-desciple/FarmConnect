/**
 * Formatting utilities for FarmConnect UI
 */

/**
 * Formats a hectare value for display (e.g., 1.5 ha)
 * Handles both number and string inputs (from API)
 */
export const formatArea = (value: number | string | undefined | null): string => {
  if (value === undefined || value === null) return '0.0 ha';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0.0 ha';
  return `${num.toFixed(1)} ha`;
};

/**
 * Formats coordinates for display (e.g., -90.0000)
 */
export const formatCoordinate = (value: number | string | undefined | null, precision: number = 4): string => {
  if (value === undefined || value === null) return '0.0000';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '0.0000';
  return num.toFixed(precision);
};

/**
 * Formats a currency value
 */
export const formatCurrency = (
  value: number | string | undefined | null, 
  currency: string = 'USD',
  precision: number = 2
): string => {
  if (value === undefined || value === null) return `$ 0.00`;
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return `$ 0.00`;
  
  const symbol = currency === 'USD' ? '$' : currency;
  return `${symbol} ${num.toLocaleString(undefined, {
    minimumFractionDigits: precision,
    maximumFractionDigits: precision
  })}`;
};

/**
 * Formats a date string for display
 */
export const formatDate = (dateStr: string | undefined | null): string => {
  if (!dateStr) return 'N/A';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  } catch (e) {
    return 'Invalid Date';
  }
};
