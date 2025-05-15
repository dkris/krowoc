import React from 'react';
import { DailyMetrics } from '../../lib/api/metricsApi';

interface DailyMetricsChartProps {
  data: DailyMetrics;
  height?: number;
}

export const DailyMetricsChart: React.FC<DailyMetricsChartProps> = ({ 
  data,
  height = 300
}) => {
  if (!data || !data.daily_metrics || data.daily_metrics.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-md p-4">
        <p>No daily usage data available for the selected period</p>
      </div>
    );
  }

  // Find the maximum execution and token values to scale bars properly
  const maxExecutions = Math.max(...data.daily_metrics.map(item => item.executions));
  const maxTokens = Math.max(...data.daily_metrics.map(item => item.input_tokens + item.output_tokens));
  const maxCost = Math.max(...data.daily_metrics.map(item => item.cost));

  // Format number with thousands separator
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(Math.round(num));
  };

  // Format cost with currency
  const formatCost = (cost: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(cost);
  };

  return (
    <div className="w-full" style={{ height: `${height}px`, overflowX: 'auto', overflowY: 'hidden' }}>
      <h3 className="text-lg font-medium mb-4">Daily Usage Trends</h3>
      
      <div className="flex justify-between mb-3">
        <div>
          <span className="inline-block w-3 h-3 bg-blue-500 mr-1"></span>
          <span className="text-xs text-gray-500">Executions</span>
        </div>
        <div>
          <span className="inline-block w-3 h-3 bg-green-500 mr-1"></span>
          <span className="text-xs text-gray-500">Tokens (scaled)</span>
        </div>
        <div>
          <span className="inline-block w-3 h-3 bg-amber-500 mr-1"></span>
          <span className="text-xs text-gray-500">Cost</span>
        </div>
      </div>
      
      <div className="flex items-end space-x-2" style={{ height: `${height - 70}px` }}>
        {data.daily_metrics.map((item, index) => {
          const executionHeight = maxExecutions ? (item.executions / maxExecutions) * 100 : 0;
          const tokenHeight = maxTokens ? ((item.input_tokens + item.output_tokens) / maxTokens) * 100 : 0;
          const costHeight = maxCost ? (item.cost / maxCost) * 100 : 0;
          
          return (
            <div key={`${item.date}-${index}`} className="flex-1 min-w-8 flex flex-col items-center">
              <div className="w-full flex justify-center space-x-1">
                <div 
                  className="w-2 bg-blue-500 rounded-t" 
                  style={{ height: `${executionHeight}%` }}
                  title={`Executions: ${formatNumber(item.executions)}`}
                ></div>
                <div 
                  className="w-2 bg-green-500 rounded-t" 
                  style={{ height: `${tokenHeight}%` }}
                  title={`Tokens: ${formatNumber(item.input_tokens + item.output_tokens)}`}
                ></div>
                <div 
                  className="w-2 bg-amber-500 rounded-t" 
                  style={{ height: `${costHeight}%` }}
                  title={`Cost: ${formatCost(item.cost)}`}
                ></div>
              </div>
              <div className="text-xs text-gray-500 mt-1 transform -rotate-45 origin-top-left">
                {new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}; 