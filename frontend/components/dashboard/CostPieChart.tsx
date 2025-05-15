import React from 'react';
import { CostBreakdown } from '../../lib/api/metricsApi';

interface CostPieChartProps {
  data: CostBreakdown;
}

export const CostPieChart: React.FC<CostPieChartProps> = ({ data }) => {
  if (!data || !data.cost_breakdown || data.cost_breakdown.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-md p-4">
        <p>No cost breakdown data available</p>
      </div>
    );
  }

  // Calculate total cost
  const totalCost = data.cost_breakdown.reduce((sum, item) => sum + item.cost, 0);

  // Format cost with currency
  const formatCost = (cost: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(cost);
  };

  // Define colors for providers
  const getProviderColor = (provider: string, index: number) => {
    const colors = {
      'OpenAI': 'bg-green-500',
      'Anthropic': 'bg-purple-500',
      'Google': 'bg-blue-500',
      'Amazon': 'bg-orange-500',
      'Microsoft': 'bg-blue-700',
      'Cohere': 'bg-indigo-500',
    };
    
    return colors[provider as keyof typeof colors] || `bg-gray-${300 + (index * 100)}`;
  };

  return (
    <div className="w-full">
      <h3 className="text-lg font-medium mb-4">Cost Breakdown</h3>
      
      <div className="flex flex-col md:flex-row items-center gap-8">
        {/* Visualization */}
        <div className="relative w-48 h-48">
          {data.cost_breakdown.map((item, index, array) => {
            // Calculate the percentage of this slice
            const percentage = (item.cost / totalCost) * 100;
            
            // Calculate angles for CSS conic gradient
            let startAngle = 0;
            for (let i = 0; i < index; i++) {
              startAngle += (array[i].cost / totalCost) * 360;
            }
            const endAngle = startAngle + (percentage * 3.6);
            
            return (
              <div 
                key={`${item.provider}-${index}`}
                className="absolute inset-0 rounded-full"
                style={{ 
                  clipPath: `conic-gradient(from ${startAngle}deg, transparent ${startAngle}deg, 
                              currentColor ${startAngle}deg, currentColor ${endAngle}deg, 
                              transparent ${endAngle}deg)`,
                  color: getProviderColor(item.provider, index).replace('bg-', '')
                }}
              >
                <div className={`w-full h-full rounded-full ${getProviderColor(item.provider, index)}`}></div>
              </div>
            );
          })}
          <div className="absolute inset-0 flex items-center justify-center bg-white rounded-full m-12">
            <span className="font-bold text-lg">{formatCost(totalCost)}</span>
          </div>
        </div>
        
        {/* Legend */}
        <div className="flex flex-col gap-2">
          {data.cost_breakdown.map((item, index) => {
            const percentage = (item.cost / totalCost) * 100;
            
            return (
              <div key={`legend-${item.provider}-${index}`} className="flex items-center space-x-2">
                <div className={`w-4 h-4 ${getProviderColor(item.provider, index)} rounded-sm`}></div>
                <div className="flex justify-between items-center w-full">
                  <span>{item.provider}</span>
                  <span className="ml-4 font-medium">
                    {formatCost(item.cost)} ({percentage.toFixed(1)}%)
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}; 