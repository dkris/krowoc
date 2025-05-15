import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMetricsSummary, MetricsSummary as MetricsSummaryType } from '../../lib/api/metricsApi';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  isLoading: boolean;
}

const StatCard = ({ title, value, description, isLoading }: StatCardProps) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <div className="mt-1">
        {isLoading ? (
          <div className="h-8 bg-gray-200 animate-pulse rounded"></div>
        ) : (
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        )}
      </div>
      {description && (
        <p className="mt-1 text-sm text-gray-500">{description}</p>
      )}
    </div>
  );
};

export const MetricsSummary = () => {
  const { data, isLoading, error } = useQuery<MetricsSummaryType>({
    queryKey: ['metricsSummary'],
    queryFn: getMetricsSummary,
  });

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(Math.round(num));
  };

  const formatCost = (cost: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(cost);
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4">
        <p>Failed to load metrics summary</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-900">Usage Summary</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Executions"
          value={isLoading || !data ? '...' : formatNumber(data.summary.total_executions)}
          isLoading={isLoading}
        />
        <StatCard
          title="Total Tokens"
          value={
            isLoading || !data
              ? '...'
              : formatNumber(
                  data.summary.total_input_tokens + data.summary.total_output_tokens
                )
          }
          description="Input + Output tokens"
          isLoading={isLoading}
        />
        <StatCard
          title="Total Cost"
          value={isLoading || !data ? '...' : formatCost(data.summary.total_cost)}
          isLoading={isLoading}
        />
        <StatCard
          title="Avg Response Time"
          value={
            isLoading || !data
              ? '...'
              : `${formatNumber(data.summary.avg_execution_time_ms)} ms`
          }
          isLoading={isLoading}
        />
      </div>

      {!isLoading && data?.by_model && data.by_model.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Usage by Model</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Model
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Provider
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Executions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Input Tokens
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Output Tokens
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.by_model.map((item, index) => (
                  <tr key={`${item.provider}-${item.model}-${index}`}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.model}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.provider}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(item.executions)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(item.input_tokens)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(item.output_tokens)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCost(item.cost)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}; 