export const inferCurrencyFromTicker = (ticker?: string | null): 'INR' | 'USD' => {
  if (!ticker) {
    return 'USD';
  }

  return ticker.endsWith('.NS') || ticker.endsWith('.BO') ? 'INR' : 'USD';
};

export const formatCurrency = (
  value: number | null | undefined,
  currency: string = 'USD',
  options: Intl.NumberFormatOptions = {},
) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return 'N/A';
  }

  const locale = currency === 'INR' ? 'en-IN' : 'en-US';

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
    ...options,
  }).format(value);
};

export const formatCompactCurrency = (value: number | null | undefined, currency: string = 'USD') =>
  formatCurrency(value, currency, {
    notation: 'compact',
    maximumFractionDigits: 2,
  });

export const formatLargeNumber = (
  value: number | null | undefined,
  locale: string = 'en-US',
  maximumFractionDigits = 2,
) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return 'N/A';
  }

  return new Intl.NumberFormat(locale, {
    notation: 'compact',
    maximumFractionDigits,
  }).format(value);
};

export const formatPercent = (value: number | null | undefined, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return 'N/A';
  }

  return `${value.toFixed(digits)}%`;
};

export const formatNumber = (value: number | null | undefined, locale: string = 'en-US') => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return 'N/A';
  }

  return new Intl.NumberFormat(locale).format(value);
};

export const formatDateTime = (value: string, intraday = false) => {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('en-US', intraday
    ? { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }
    : { month: 'short', day: 'numeric', year: 'numeric' }).format(date);
};
