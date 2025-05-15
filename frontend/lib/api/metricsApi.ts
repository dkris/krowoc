import { z } from 'zod';

// Types and schemas for usage metrics
export const MetricsSummarySchema = z.object({
  summary: z.object({
    total_executions: z.number(),
    total_input_tokens: z.number(),
    total_output_tokens: z.number(),
    total_cost: z.number(),
    avg_execution_time_ms: z.number(),
  }),
  by_model: z.array(
    z.object({
      model: z.string(),
      provider: z.string(),
      executions: z.number(),
      input_tokens: z.number(),
      output_tokens: z.number(),
      cost: z.number(),
    })
  ),
});

export type MetricsSummary = z.infer<typeof MetricsSummarySchema>;

export const DailyMetricsSchema = z.object({
  daily_metrics: z.array(
    z.object({
      date: z.string(),
      executions: z.number(),
      input_tokens: z.number(),
      output_tokens: z.number(),
      cost: z.number(),
    })
  ),
});

export type DailyMetrics = z.infer<typeof DailyMetricsSchema>;

export const CostBreakdownSchema = z.object({
  cost_breakdown: z.array(
    z.object({
      provider: z.string(),
      cost: z.number(),
    })
  ),
});

export type CostBreakdown = z.infer<typeof CostBreakdownSchema>;

// Function to check if we should use mock data
const shouldUseMockData = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.location.search.includes('mock=true');
};

// Mock data
const MOCK_METRICS_SUMMARY: MetricsSummary = {
  summary: {
    total_executions: 1243,
    total_input_tokens: 2654789,
    total_output_tokens: 789541,
    total_cost: 53.42,
    avg_execution_time_ms: 1892,
  },
  by_model: [
    {
      model: 'gpt-4',
      provider: 'OpenAI',
      executions: 456,
      input_tokens: 1245000,
      output_tokens: 328000,
      cost: 28.14,
    },
    {
      model: 'claude-3-opus',
      provider: 'Anthropic',
      executions: 321,
      input_tokens: 876000,
      output_tokens: 256000,
      cost: 19.87,
    },
    {
      model: 'gemini-pro',
      provider: 'Google',
      executions: 224,
      input_tokens: 365789,
      output_tokens: 123541,
      cost: 4.21,
    },
    {
      model: 'gpt-3.5-turbo',
      provider: 'OpenAI',
      executions: 242,
      input_tokens: 168000,
      output_tokens: 82000,
      cost: 1.20,
    },
  ],
};

const generateMockDailyMetrics = (days: number): DailyMetrics => {
  const today = new Date();
  const metrics: DailyMetrics = {
    daily_metrics: []
  };

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // Create some variation in the data
    const multiplier = 0.5 + Math.random();
    const dayOfWeek = date.getDay();
    // Lower values on weekends
    const weekendFactor = (dayOfWeek === 0 || dayOfWeek === 6) ? 0.6 : 1;
    
    metrics.daily_metrics.push({
      date: date.toISOString().split('T')[0],
      executions: Math.round(40 * multiplier * weekendFactor),
      input_tokens: Math.round(85000 * multiplier * weekendFactor),
      output_tokens: Math.round(25000 * multiplier * weekendFactor),
      cost: parseFloat((1.72 * multiplier * weekendFactor).toFixed(2)),
    });
  }

  return metrics;
};

const MOCK_COST_BREAKDOWN: CostBreakdown = {
  cost_breakdown: [
    {
      provider: 'OpenAI',
      cost: 29.34,
    },
    {
      provider: 'Anthropic',
      cost: 19.87,
    },
    {
      provider: 'Google',
      cost: 4.21,
    },
  ],
};

// API functions
export async function getMetricsSummary(): Promise<MetricsSummary> {
  // Check for mock mode
  if (shouldUseMockData()) {
    return new Promise(resolve => {
      setTimeout(() => resolve(MOCK_METRICS_SUMMARY), 800);
    });
  }
  
  const response = await fetch('/api/metrics/summary');
  
  if (!response.ok) {
    throw new Error(`Failed to fetch metrics summary: ${response.statusText}`);
  }
  
  const data = await response.json();
  return MetricsSummarySchema.parse(data);
}

export async function getDailyMetrics(days: number = 30): Promise<DailyMetrics> {
  // Check for mock mode
  if (shouldUseMockData()) {
    return new Promise(resolve => {
      setTimeout(() => resolve(generateMockDailyMetrics(days)), 1000);
    });
  }
  
  const response = await fetch(`/api/metrics/daily?days=${days}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch daily metrics: ${response.statusText}`);
  }
  
  const data = await response.json();
  return DailyMetricsSchema.parse(data);
}

export async function getCostBreakdown(): Promise<CostBreakdown> {
  // Check for mock mode
  if (shouldUseMockData()) {
    return new Promise(resolve => {
      setTimeout(() => resolve(MOCK_COST_BREAKDOWN), 700);
    });
  }
  
  const response = await fetch('/api/metrics/cost_breakdown');
  
  if (!response.ok) {
    throw new Error(`Failed to fetch cost breakdown: ${response.statusText}`);
  }
  
  const data = await response.json();
  return CostBreakdownSchema.parse(data);
} 