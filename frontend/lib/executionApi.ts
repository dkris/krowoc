import { Execution } from '../types/execution';
import { isMockMode } from './mockMode';
import apiClient from './api/apiClient';
import { trackEvent } from './analytics';

// Mock data generation for development mode
function generateMockExecutions(promptId: string, count: number): Execution[] {
  return Array.from({ length: count }).map((_, index) => ({
    id: `mock-exec-${Date.now()}-${index}`,
    prompt_id: promptId,
    user_id: 'mock-user-id',
    model: index % 2 === 0 ? 'openai:gpt-4' : 'anthropic:claude-2.1',
    provider: index % 2 === 0 ? 'openai' : 'anthropic',
    input_tokens: 100 + index * 20,
    output_tokens: 200 + index * 30,
    cost: 0.01 + index * 0.005,
    response_text: `This is mock execution response #${index + 1} for prompt ${promptId}`,
    is_successful: index !== 1, // Make one execution fail for testing
    execution_time_ms: 1000 + index * 500,
    created_at: new Date(Date.now() - index * 86400000).toISOString() // Each one a day apart
  }));
}

/**
 * Get the execution history for a prompt
 * @param promptId The ID of the prompt
 * @returns Array of executions
 */
export async function getExecutionsByPromptId(promptId: string): Promise<Execution[]> {
  try {
    // Return mock data if mock mode is enabled
    if (isMockMode()) {
      console.log('Using mock execution data');
      const mockData = generateMockExecutions(promptId, 5);
      trackEvent('get_executions', { promptId, count: mockData.length, isMock: true });
      return mockData;
    }
    
    const data = await apiClient.get<{ executions: Execution[] }>(`/prompts/${promptId}/executions`);
    trackEvent('get_executions', { promptId, count: data.executions?.length || 0 });
    return data.executions || [];
  } catch (error) {
    trackEvent('get_executions_error', { promptId, error: (error as Error).message });
    console.error('Failed to fetch execution history:', error);
    return [];
  }
}

/**
 * Save an execution to the database
 * @param execution The execution to save
 * @returns The saved execution
 */
export async function saveExecution(execution: Execution): Promise<Execution> {
  try {
    // Return mock data if mock mode is enabled
    if (isMockMode()) {
      console.log('Mock: saving execution', execution);
      const mockResult = {
        ...execution,
        id: execution.id || Date.now().toString()
      };
      trackEvent('save_execution', { 
        promptId: execution.prompt_id,
        model: execution.model,
        isMock: true
      });
      return mockResult;
    }
    
    const result = await apiClient.post<Execution>('/executions', execution);
    
    trackEvent('save_execution', {
      promptId: execution.prompt_id,
      model: execution.model,
      executionId: result.id,
      isSuccess: result.is_successful
    });
    
    return result;
  } catch (error) {
    trackEvent('save_execution_error', { 
      promptId: execution.prompt_id,
      error: (error as Error).message
    });
    console.error('Failed to save execution:', error);
    throw error;
  }
}

/**
 * Execute a prompt
 * @param promptId The ID of the prompt to execute
 * @param model The LLM model to use
 * @param options Additional options
 * @returns The execution result
 */
export async function executePrompt(
  promptId: string, 
  model: string,
  options: { temperature?: number } = {}
): Promise<Execution> {
  try {
    // Track the start of execution
    trackEvent('prompt_execution_start', { promptId, model });
    
    // Return mock data if mock mode is enabled
    if (isMockMode()) {
      console.log('Mock: executing prompt', promptId, model);
      const mockResult = {
        id: Date.now().toString(),
        prompt_id: promptId,
        user_id: 'mock-user-id',
        model: model,
        provider: model.split(':')[0],
        input_tokens: 150,
        output_tokens: 250,
        cost: 0.05,
        response_text: 'This is a mock execution response.',
        is_successful: true,
        execution_time_ms: 2500,
        created_at: new Date().toISOString()
      };
      
      // Simulate execution delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      trackEvent('prompt_execution_complete', { 
        promptId, 
        model, 
        executionId: mockResult.id,
        isSuccess: true,
        isMock: true,
        duration_ms: mockResult.execution_time_ms
      });
      
      return mockResult;
    }
    
    const startTime = Date.now();
    const result = await apiClient.post<Execution>(`/prompts/${promptId}/execute`, {
      model,
      temperature: options.temperature
    });
    
    const duration = Date.now() - startTime;
    
    trackEvent('prompt_execution_complete', {
      promptId,
      model,
      executionId: result.id,
      isSuccess: result.is_successful,
      duration_ms: duration,
      tokenCount: (result.input_tokens || 0) + (result.output_tokens || 0)
    });
    
    return result;
  } catch (error) {
    trackEvent('prompt_execution_error', { 
      promptId, 
      model, 
      error: (error as Error).message 
    });
    console.error('Failed to execute prompt:', error);
    throw error;
  }
}

/**
 * Retry a failed execution
 * @param executionId The ID of the execution to retry
 * @returns The new execution
 */
export async function retryExecution(executionId: string): Promise<Execution> {
  try {
    trackEvent('retry_execution_start', { executionId });
    
    // Return mock data if mock mode is enabled
    if (isMockMode()) {
      console.log('Mock: retrying execution', executionId);
      const mockResult = {
        id: Date.now().toString(),
        prompt_id: 'mock-prompt-id',
        user_id: 'mock-user-id',
        model: 'openai:gpt-4',
        provider: 'openai',
        input_tokens: 150,
        output_tokens: 250,
        cost: 0.05,
        response_text: 'This is a mock retry response.',
        is_successful: true,
        execution_time_ms: 2500,
        created_at: new Date().toISOString()
      };
      
      trackEvent('retry_execution_complete', { 
        executionId, 
        newExecutionId: mockResult.id,
        isSuccess: true,
        isMock: true
      });
      
      return mockResult;
    }
    
    const result = await apiClient.post<Execution>(`/executions/${executionId}/retry`, {});
    
    trackEvent('retry_execution_complete', {
      executionId,
      newExecutionId: result.id,
      isSuccess: result.is_successful
    });
    
    return result;
  } catch (error) {
    trackEvent('retry_execution_error', { 
      executionId, 
      error: (error as Error).message 
    });
    console.error('Failed to retry execution:', error);
    throw error;
  }
} 