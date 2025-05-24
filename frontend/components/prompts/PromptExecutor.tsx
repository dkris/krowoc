import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { Prompt } from '../../types/prompt';
import { Execution } from '../../types/execution';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCircleNotch, faExclamationTriangle, faRedo, faCopy } from '@fortawesome/free-solid-svg-icons';
import { formatNumber, formatCost } from '../../lib/formatting';
import { mockDelay } from '../../lib/mockData';
import { isMockMode, MockModeBanner } from '../../lib/mockMode';

interface PromptExecutorProps {
  prompt: Prompt;
  onExecutionComplete?: (execution: Execution) => void;
}

export default function PromptExecutor({ prompt, onExecutionComplete }: PromptExecutorProps) {
  const [model, setModel] = useState('openai:gpt-4');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);
  const [streaming, setStreaming] = useState(true);
  const [response, setResponse] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [executionTime, setExecutionTime] = useState<number | null>(null);
  const [currentExecution, setCurrentExecution] = useState<Execution | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [retryDelay, setRetryDelay] = useState(2000); // 2 seconds initial retry delay
  const maxRetries = 3;
  const eventSourceRef = useRef<EventSource | null>(null);
  const responseRef = useRef<HTMLDivElement>(null);
  
  // Automatically scroll to bottom of response area when new content arrives
  useEffect(() => {
    if (responseRef.current && isExecuting) {
      responseRef.current.scrollTop = responseRef.current.scrollHeight;
    }
  }, [response, isExecuting]);
  
  // Cleanup event source on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);
  
  const executePrompt = async () => {
    if (isExecuting) return;
    
    // Reset state
    setIsExecuting(true);
    setResponse('');
    setError(null);
    setExecutionTime(null);
    setCurrentExecution(null);
    
    const startTime = Date.now();
    
    try {
      if (isMockMode()) {
        // Use mock execution
        await executeMockPrompt(startTime);
      } else if (streaming) {
        // Handle streaming response
        await executeStreamingPrompt(startTime);
      } else {
        // Handle regular response
        await executeRegularPrompt(startTime);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      handleExecutionError(errorMessage, startTime);
    }
  };
  
  const executeMockPrompt = async (startTime: number) => {
    try {
      // Simulate streaming text if streaming is enabled
      if (streaming) {
        const mockResponses = [
          "I'm analyzing your question...",
          "\n\nBased on the information provided, ",
          "I can explain that ",
          "prompt execution flows typically involve ",
          "several steps:\n\n",
          "1. The prompt is processed and validated\n",
          "2. The appropriate LLM model is selected\n",
          "3. The request is sent to the model provider\n",
          "4. The response is processed and returned\n",
          "5. Execution metrics are recorded for analytics\n\n",
          "This helps maintain a consistent and reliable process ",
          "for working with language models while providing ",
          "valuable feedback and monitoring capabilities."
        ];
        
        for (const chunk of mockResponses) {
          await mockDelay(200, 500);
          setResponse(prev => prev + chunk);
        }
        
        await mockDelay(500, 1000);
      } else {
        // For non-streaming, just wait and return full response
        await mockDelay(1500, 3000);
        setResponse("Prompt execution flows typically involve several steps:\n\n1. The prompt is processed and validated\n2. The appropriate LLM model is selected\n3. The request is sent to the model provider\n4. The response is processed and returned\n5. Execution metrics are recorded for analytics\n\nThis helps maintain a consistent and reliable process for working with language models while providing valuable feedback and monitoring capabilities.");
      }
      
      // Mock execution completion
      const endTime = Date.now();
      setExecutionTime(endTime - startTime);
      
      // Create execution record
      const execution: Execution = {
        id: Date.now().toString(),
        prompt_id: prompt.id,
        user_id: '1',
        model,
        provider: model.split(':')[0],
        input_tokens: 120,
        output_tokens: 256,
        cost: 0.0354,
        response_text: response,
        is_successful: true,
        execution_time_ms: endTime - startTime,
        created_at: new Date().toISOString()
      };
      
      setCurrentExecution(execution);
      
      if (onExecutionComplete) {
        onExecutionComplete(execution);
      }
      
      // Reset retry count on successful completion
      setRetryCount(0);
      setRetryDelay(2000);
    } catch (err) {
      handleExecutionError(err instanceof Error ? err.message : 'An unknown error occurred', startTime);
    } finally {
      setIsExecuting(false);
    }
  };
  
  const executeStreamingPrompt = async (startTime: number) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    
    try {
      const requestBody = JSON.stringify({
        model,
        temperature,
        max_tokens: maxTokens,
        stream: true,
        system_prompt: systemPrompt || undefined
      });
      
      const eventSource = new EventSource(`/api/prompts/${prompt.id}/execute?body=${encodeURIComponent(requestBody)}`, { 
        withCredentials: true 
      });
      
      eventSourceRef.current = eventSource;
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.text) {
            setResponse(prev => prev + data.text);
          }
          
          // If we get usage information, store it
          if (data.usage) {
            const endTime = Date.now();
            setExecutionTime(endTime - startTime);
            
            // Create execution record
            const execution: Execution = {
              id: data.execution_id || Date.now().toString(),
              prompt_id: prompt.id,
              user_id: '1', // Replace with actual user ID
              model,
              provider: model.split(':')[0],
              input_tokens: data.usage.prompt_tokens,
              output_tokens: data.usage.completion_tokens,
              cost: data.usage.total_cost,
              response_text: response + (data.text || ''),
              is_successful: true,
              execution_time_ms: endTime - startTime,
              created_at: new Date().toISOString()
            };
            
            setCurrentExecution(execution);
            
            if (onExecutionComplete) {
              onExecutionComplete(execution);
            }
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };
      
      eventSource.onerror = (err) => {
        handleStreamError(err, startTime);
      };
      
      eventSource.addEventListener('done', () => {
        eventSource.close();
        setIsExecuting(false);
        // Reset retry count on successful completion
        setRetryCount(0);
        setRetryDelay(2000);
      });
      
      eventSource.addEventListener('error', (event) => {
        try {
          // Cast event to any to access data property
          const data = JSON.parse((event as any).data);
          handleExecutionError(data.error || 'An error occurred during streaming', startTime);
        } catch (error) {
          handleExecutionError('Failed to parse error data', startTime);
        }
        eventSource.close();
      });
    } catch (err) {
      handleExecutionError(err instanceof Error ? err.message : 'Failed to start streaming', startTime);
    }
  };
  
  const executeRegularPrompt = async (startTime: number) => {
    try {
      const response = await fetch(`/api/prompts/${prompt.id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model,
          temperature,
          max_tokens: maxTokens,
          stream: false,
          system_prompt: systemPrompt || undefined
        })
      });
      
      const endTime = Date.now();
      setExecutionTime(endTime - startTime);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error: ${response.status}`);
      }
      
      const data = await response.json();
      setResponse(data.response);
      
      // Create execution record
      const execution: Execution = {
        id: data.execution_id || Date.now().toString(),
        prompt_id: prompt.id,
        user_id: '1', // Replace with actual user ID
        model,
        provider: model.split(':')[0],
        input_tokens: data.usage?.prompt_tokens,
        output_tokens: data.usage?.completion_tokens,
        cost: data.usage?.total_cost,
        response_text: data.response,
        is_successful: true,
        execution_time_ms: endTime - startTime,
        created_at: new Date().toISOString()
      };
      
      setCurrentExecution(execution);
      
      if (onExecutionComplete) {
        onExecutionComplete(execution);
      }
      
      // Reset retry count on successful completion
      setRetryCount(0);
      setRetryDelay(2000);
    } catch (err) {
      handleExecutionError(err instanceof Error ? err.message : 'An unknown error occurred', startTime);
    } finally {
      setIsExecuting(false);
    }
  };
  
  const handleStreamError = (err: Event, startTime: number) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    const errorMessage = 'Connection error during streaming';
    handleExecutionError(errorMessage, startTime);
  };
  
  const handleExecutionError = (errorMessage: string, startTime: number) => {
    setError(errorMessage);
    setIsExecuting(false);
    
    const endTime = Date.now();
    
    // Create failed execution record
    const failedExecution: Execution = {
      id: Date.now().toString(),
      prompt_id: prompt.id,
      user_id: '1', // Replace with actual user ID
      model,
      provider: model.split(':')[0],
      input_tokens: 0,
      output_tokens: 0,
      cost: 0,
      response_text: '',
      is_successful: false,
      error_message: errorMessage,
      execution_time_ms: endTime - startTime,
      created_at: new Date().toISOString()
    };
    
    setCurrentExecution(failedExecution);
    
    if (onExecutionComplete) {
      onExecutionComplete(failedExecution);
    }
    
    // Handle retry logic
    if (retryCount < maxRetries) {
      const nextRetryDelay = retryDelay * 1.5; // Exponential backoff
      setTimeout(() => {
        retry();
      }, retryDelay);
      
      setRetryDelay(nextRetryDelay);
    }
  };
  
  const retry = () => {
    setRetryCount(prevCount => prevCount + 1);
    setError(null);
    executePrompt();
  };
  
  const copyToClipboard = () => {
    if (response) {
      navigator.clipboard.writeText(response)
        .then(() => {
          alert('Response copied to clipboard');
        })
        .catch(err => {
          console.error('Failed to copy text: ', err);
        });
    }
  };
  
  const getModelOptions = () => {
    // Powered by LangChain: update this list to match backend SUPPORTED_PROVIDERS
    return [
      { value: 'openai:gpt-4', label: 'OpenAI: GPT-4' },
      { value: 'openai:gpt-3.5-turbo', label: 'OpenAI: GPT-3.5 Turbo' },
      { value: 'openai:gpt-4-turbo', label: 'OpenAI: GPT-4 Turbo' },
      { value: 'openai:gpt-4o', label: 'OpenAI: GPT-4o' },
      { value: 'anthropic:claude-3-opus', label: 'Anthropic: Claude 3 Opus' },
      { value: 'anthropic:claude-3-sonnet', label: 'Anthropic: Claude 3 Sonnet' },
      { value: 'anthropic:claude-3-haiku', label: 'Anthropic: Claude 3 Haiku' },
      { value: 'google:gemini-pro', label: 'Google: Gemini Pro' },
      { value: 'google:gemini-pro-vision', label: 'Google: Gemini Pro Vision' },
      { value: 'google:gemini-ultra', label: 'Google: Gemini Ultra' },
    ];
  };
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      {/* Show mock mode banner if in mock mode */}
      <MockModeBanner />
      
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Execution Parameters</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
              Model <span className="text-xs text-gray-400">(Powered by LangChain)</span>
            </label>
            <select
              id="model"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full rounded-md border border-gray-300 shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              disabled={isExecuting}
            >
              {getModelOptions().map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="temperature" className="block text-sm font-medium text-gray-700 mb-1">
              Temperature: {temperature}
            </label>
            <input
              id="temperature"
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full"
              disabled={isExecuting}
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="maxTokens" className="block text-sm font-medium text-gray-700 mb-1">
              Max Tokens
            </label>
            <input
              id="maxTokens"
              type="number"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              className="w-full rounded-md border border-gray-300 shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              disabled={isExecuting}
            />
          </div>
          
          <div className="flex items-center">
            <input
              id="streaming"
              type="checkbox"
              checked={streaming}
              onChange={(e) => setStreaming(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              disabled={isExecuting}
            />
            <label htmlFor="streaming" className="ml-2 block text-sm text-gray-700">
              Enable streaming
            </label>
          </div>
        </div>
        
        <div className="mb-4">
          <label htmlFor="systemPrompt" className="block text-sm font-medium text-gray-700 mb-1">
            System Prompt (optional)
          </label>
          <textarea
            id="systemPrompt"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={3}
            className="w-full rounded-md border border-gray-300 shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Instructions for the LLM..."
            disabled={isExecuting}
          />
        </div>
        
        <div className="text-right">
          <button
            type="button"
            onClick={executePrompt}
            disabled={isExecuting}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isExecuting ? (
              <>
                <FontAwesomeIcon icon={faCircleNotch} spin className="mr-2" />
                Executing...
              </>
            ) : retryCount > 0 ? (
              <>
                <FontAwesomeIcon icon={faRedo} className="mr-2" />
                Retry ({retryCount}/{maxRetries})
              </>
            ) : (
              'Execute Prompt'
            )}
          </button>
        </div>
      </div>
      
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-medium text-gray-900">Response</h3>
          {response && (
            <button
              onClick={copyToClipboard}
              className="text-sm text-gray-500 hover:text-gray-700"
              title="Copy to clipboard"
            >
              <FontAwesomeIcon icon={faCopy} />
            </button>
          )}
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
            <div className="flex">
              <FontAwesomeIcon icon={faExclamationTriangle} className="text-red-400 mr-3 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-1 text-sm text-red-700">{error}</div>
                {retryCount < maxRetries && (
                  <button
                    onClick={retry}
                    className="mt-2 text-sm font-medium text-red-600 hover:text-red-500"
                  >
                    Retry Now
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
        
        <div
          ref={responseRef}
          className="bg-gray-50 rounded-md p-4 min-h-[200px] max-h-[500px] overflow-y-auto font-mono text-sm whitespace-pre-wrap"
        >
          {isExecuting && !response && (
            <div className="flex justify-center items-center h-full">
              <FontAwesomeIcon icon={faCircleNotch} spin size="2x" className="text-gray-400" />
            </div>
          )}
          {!isExecuting && !response && !error && (
            <div className="text-gray-400 italic">Response will appear here</div>
          )}
          {response}
        </div>
      </div>
      
      {currentExecution && (
        <div className="border-t border-gray-200 pt-4 mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Execution Details</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="block text-gray-500">Status</span>
              <span className={`font-medium ${currentExecution.is_successful ? 'text-green-600' : 'text-red-600'}`}>
                {currentExecution.is_successful ? 'Success' : 'Failed'}
              </span>
            </div>
            
            {currentExecution.execution_time_ms && (
              <div>
                <span className="block text-gray-500">Time</span>
                <span className="font-medium">{(currentExecution.execution_time_ms / 1000).toFixed(2)}s</span>
              </div>
            )}
            
            {currentExecution.input_tokens !== undefined && currentExecution.input_tokens > 0 && (
              <div>
                <span className="block text-gray-500">Input Tokens</span>
                <span className="font-medium">{formatNumber(currentExecution.input_tokens)}</span>
              </div>
            )}
            
            {currentExecution.output_tokens !== undefined && currentExecution.output_tokens > 0 && (
              <div>
                <span className="block text-gray-500">Output Tokens</span>
                <span className="font-medium">{formatNumber(currentExecution.output_tokens)}</span>
              </div>
            )}
            
            {currentExecution.cost !== undefined && (
              <div>
                <span className="block text-gray-500">Cost</span>
                <span className="font-medium">{formatCost(currentExecution.cost)}</span>
              </div>
            )}
          </div>
        </div>
      )}
      
      <div className="text-xs text-gray-500 mt-1">
        Supported providers: OpenAI, Anthropic, Google. Model options are kept in sync with backend LangChain support.
      </div>
    </div>
  );
} 