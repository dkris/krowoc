import React, { useState } from 'react';
import { Execution } from '../../types/execution';
import { formatNumber, formatCost } from '../../lib/formatting';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheckCircle, faTimesCircle, faAngleDown, faAngleUp } from '@fortawesome/free-solid-svg-icons';

interface ExecutionHistoryProps {
  executions: Execution[];
  onSelectExecution?: (execution: Execution) => void;
}

export default function ExecutionHistory({ executions, onSelectExecution }: ExecutionHistoryProps) {
  const [expandedExecutionId, setExpandedExecutionId] = useState<string | null>(null);
  
  if (!executions || executions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Execution History</h3>
        <p className="text-gray-500 text-sm">No execution history available for this prompt.</p>
      </div>
    );
  }
  
  // Sort executions by date, newest first
  const sortedExecutions = [...executions].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  
  const toggleExpand = (executionId: string) => {
    setExpandedExecutionId(expandedExecutionId === executionId ? null : executionId);
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Execution History</h3>
      
      <div className="overflow-hidden border border-gray-200 rounded-md">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Model
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tokens
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cost
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedExecutions.map((execution) => (
              <React.Fragment key={execution.id}>
                <tr 
                  className={`hover:bg-gray-50 cursor-pointer ${expandedExecutionId === execution.id ? 'bg-blue-50' : ''}`}
                  onClick={() => toggleExpand(execution.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    {execution.is_successful ? (
                      <FontAwesomeIcon icon={faCheckCircle} className="text-green-500" />
                    ) : (
                      <FontAwesomeIcon icon={faTimesCircle} className="text-red-500" />
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {execution.model}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {execution.execution_time_ms ? `${(execution.execution_time_ms / 1000).toFixed(2)}s` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {execution.input_tokens && execution.output_tokens ? 
                      `${formatNumber(execution.input_tokens)} / ${formatNumber(execution.output_tokens)}` : 
                      '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {execution.cost ? formatCost(execution.cost) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(execution.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      className="text-gray-500 hover:text-gray-700"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onSelectExecution) onSelectExecution(execution);
                      }}
                    >
                      View
                    </button>
                    <button className="ml-4 text-gray-500 hover:text-gray-700">
                      {expandedExecutionId === execution.id ? (
                        <FontAwesomeIcon icon={faAngleUp} />
                      ) : (
                        <FontAwesomeIcon icon={faAngleDown} />
                      )}
                    </button>
                  </td>
                </tr>
                
                {expandedExecutionId === execution.id && (
                  <tr>
                    <td colSpan={7} className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                      <div className="text-sm text-gray-500">
                        {execution.is_successful ? (
                          <div>
                            <h4 className="font-medium text-gray-900 mb-2">Response:</h4>
                            <div className="bg-white p-3 rounded border border-gray-200 max-h-48 overflow-y-auto whitespace-pre-wrap font-mono">
                              {execution.response_text || 'No response text available'}
                            </div>
                          </div>
                        ) : (
                          <div>
                            <h4 className="font-medium text-red-700 mb-2">Error:</h4>
                            <div className="bg-red-50 p-3 rounded border border-red-200 text-red-700">
                              {execution.error_message || 'Unknown error'}
                            </div>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 