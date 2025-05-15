import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useQuery } from '@tanstack/react-query';
import { getMetricsSummary, getDailyMetrics, getCostBreakdown } from '../lib/api/metricsApi';
import { useRouter } from 'next/router';
import { DailyMetricsChart } from '../components/dashboard/DailyMetricsChart';
import { CostPieChart } from '../components/dashboard/CostPieChart';

// Create a client
const queryClient = new QueryClient();

const Dashboard = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardContent />
    </QueryClientProvider>
  );
};

const DashboardContent = () => {
  const [timeRange, setTimeRange] = useState<number>(30);
  const router = useRouter();
  const [isMockMode, setIsMockMode] = useState<boolean>(false);

  useEffect(() => {
    // Check if we're in mock mode
    setIsMockMode(window.location.search.includes('mock=true'));
  }, []);

  // Function to toggle mock mode
  const toggleMockMode = () => {
    if (isMockMode) {
      router.push('/dashboard');
    } else {
      router.push('/dashboard?mock=true');
    }
  };
  
  // Fetch the metrics data
  const summaryQuery = useQuery({
    queryKey: ['metricsSummary', isMockMode],
    queryFn: getMetricsSummary,
  });
  
  const dailyQuery = useQuery({
    queryKey: ['dailyMetrics', timeRange, isMockMode],
    queryFn: () => getDailyMetrics(timeRange),
  });
  
  const costQuery = useQuery({
    queryKey: ['costBreakdown', isMockMode],
    queryFn: getCostBreakdown,
  });

  const formatNumber = (num: number | undefined) => {
    if (num === undefined) return '-';
    return new Intl.NumberFormat().format(Math.round(num));
  };

  const formatCost = (cost: number | undefined) => {
    if (cost === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(cost);
  };

  // Calculate total tokens safely
  const calculateTotalTokens = () => {
    const inputTokens = summaryQuery.data?.summary.total_input_tokens || 0;
    const outputTokens = summaryQuery.data?.summary.total_output_tokens || 0;
    return inputTokens + outputTokens;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">User Dashboard</h1>
        <button 
          onClick={toggleMockMode} 
          className={`px-4 py-2 rounded-md font-medium ${
            isMockMode ? 'bg-amber-100 text-amber-800 hover:bg-amber-200' : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
          }`}
        >
          {isMockMode ? 'Disable Mock Data' : 'Enable Mock Data'}
        </button>
      </div>
      
      {isMockMode && (
        <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-amber-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-amber-700">
                You are viewing mock data. This is for demonstration purposes only.
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Usage Summary */}
      <div className="bg-white rounded-lg shadow mb-8 p-6">
        <h2 className="text-xl font-semibold mb-4">Usage Summary</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="text-sm font-medium text-gray-500">Total Executions</h3>
            {summaryQuery.isLoading ? (
              <div className="h-8 bg-gray-200 animate-pulse rounded mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold mt-1">
                {formatNumber(summaryQuery.data?.summary.total_executions)}
              </p>
            )}
          </div>
          
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="text-sm font-medium text-gray-500">Total Tokens</h3>
            {summaryQuery.isLoading ? (
              <div className="h-8 bg-gray-200 animate-pulse rounded mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold mt-1">
                {formatNumber(calculateTotalTokens())}
              </p>
            )}
            <p className="text-xs text-gray-500 mt-1">Input + Output tokens</p>
          </div>
          
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="text-sm font-medium text-gray-500">Total Cost</h3>
            {summaryQuery.isLoading ? (
              <div className="h-8 bg-gray-200 animate-pulse rounded mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold mt-1">
                {formatCost(summaryQuery.data?.summary.total_cost)}
              </p>
            )}
          </div>
          
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="text-sm font-medium text-gray-500">Avg Response Time</h3>
            {summaryQuery.isLoading ? (
              <div className="h-8 bg-gray-200 animate-pulse rounded mt-1"></div>
            ) : (
              <p className="text-2xl font-semibold mt-1">
                {formatNumber(summaryQuery.data?.summary.avg_execution_time_ms)} ms
              </p>
            )}
          </div>
        </div>
      </div>
      
      {/* Usage by Model */}
      {!summaryQuery.isLoading && summaryQuery.data?.by_model && summaryQuery.data.by_model.length > 0 && (
        <div className="bg-white rounded-lg shadow mb-8 p-6">
          <h2 className="text-xl font-semibold mb-4">Usage by Model</h2>
          
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
                {summaryQuery.data.by_model.map((item, index) => (
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
      
      {/* Daily Usage Metrics */}
      <div className="bg-white rounded-lg shadow mb-8 p-6">
        <h2 className="text-xl font-semibold mb-4">Daily Usage</h2>
        
        <div className="flex justify-end mb-4 space-x-2">
          <button 
            className={`px-3 py-1 text-sm rounded ${timeRange === 7 ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
            onClick={() => setTimeRange(7)}
          >
            7 Days
          </button>
          <button 
            className={`px-3 py-1 text-sm rounded ${timeRange === 30 ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
            onClick={() => setTimeRange(30)}
          >
            30 Days
          </button>
          <button 
            className={`px-3 py-1 text-sm rounded ${timeRange === 90 ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'}`}
            onClick={() => setTimeRange(90)}
          >
            90 Days
          </button>
        </div>
        
        {dailyQuery.isLoading ? (
          <div className="h-80 bg-gray-100 animate-pulse rounded"></div>
        ) : dailyQuery.error ? (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4">
            <p>Failed to load daily metrics</p>
          </div>
        ) : !dailyQuery.data || !dailyQuery.data.daily_metrics || dailyQuery.data.daily_metrics.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-md p-4">
            <p>No daily usage data available for the selected period</p>
          </div>
        ) : (
          <div className="h-80">
            <DailyMetricsChart data={dailyQuery.data} height={300} />
          </div>
        )}
      </div>
      
      {/* Cost Breakdown */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Cost Breakdown</h2>
        
        {costQuery.isLoading ? (
          <div className="h-60 bg-gray-100 animate-pulse rounded"></div>
        ) : costQuery.error ? (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4">
            <p>Failed to load cost breakdown</p>
          </div>
        ) : !costQuery.data || !costQuery.data.cost_breakdown || costQuery.data.cost_breakdown.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-md p-4">
            <p>No cost breakdown data available</p>
          </div>
        ) : (
          <CostPieChart data={costQuery.data} />
        )}
      </div>
    </div>
  );
};

export default Dashboard; 