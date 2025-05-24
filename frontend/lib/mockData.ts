import { Execution } from '../types/execution';
import { Prompt } from '../types/prompt';

/**
 * Generate a mock prompt
 * @param id Optional ID for the prompt
 * @returns A mock prompt object
 */
export function generateMockPrompt(id?: string): Prompt {
  return {
    id: id || `mock-${Date.now()}`,
    title: 'Mock Prompt',
    content: 'This is a mock prompt for testing purposes. It can be used to demonstrate the UI without backend connection.',
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    updatedAt: new Date().toISOString(),
    userId: 'mock-user-1',
    tags: ['mock', 'test', 'development'],
    isPublic: true,
    name: 'Mock Prompt',
    description: 'This is a mock prompt for testing purposes. It can be used to demonstrate the UI without backend connection.'
  };
}

/**
 * Generate a single mock execution
 * @param promptId The prompt ID
 * @param isSuccessful Whether the execution was successful
 * @returns A mock execution object
 */
export function generateMockExecution(promptId: string, isSuccessful: boolean = true): Execution {
  const randomDate = new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 3600 * 1000));
  const executionTime = Math.floor(Math.random() * 5000) + 1000; // 1-6 seconds
  const inputTokens = Math.floor(Math.random() * 400) + 100; // 100-500 tokens
  const outputTokens = Math.floor(Math.random() * 800) + 200; // 200-1000 tokens
  const cost = (inputTokens * 0.00003 + outputTokens * 0.00006).toFixed(5);
  
  const models = [
    'openai:gpt-4',
    'openai:gpt-3.5-turbo',
    'anthropic:claude-3-opus',
    'anthropic:claude-3-sonnet',
    'google:gemini-pro'
  ];
  
  const model = models[Math.floor(Math.random() * models.length)];
  const provider = model.split(':')[0];
  
  const successResponses = [
    "The capital of France is Paris, which is known as the City of Light. Paris is famous for its art, culture, fashion, and gastronomy.",
    "A recursive function is a function that calls itself during its execution. This enables solving complex problems by breaking them down into simpler subproblems of the same type.",
    "The Pythagorean theorem states that in a right-angled triangle, the square of the length of the hypotenuse equals the sum of the squares of the other two sides.",
    "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
    "The Great Barrier Reef is the world's largest coral reef system, composed of over 2,900 individual reefs and 900 islands stretching for over 2,300 kilometers."
  ];
  
  const errorMessages = [
    "Connection timeout after 30000ms",
    "Rate limit exceeded. Please try again in a few seconds.",
    "The model is currently overloaded. Please try again later.",
    "Internal server error occurred while processing request.",
    "The requested model is not available or doesn't exist."
  ];
  
  return {
    id: `mock-execution-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
    prompt_id: promptId,
    user_id: 'mock-user-1',
    model,
    provider,
    input_tokens: isSuccessful ? inputTokens : undefined,
    output_tokens: isSuccessful ? outputTokens : undefined,
    cost: isSuccessful ? parseFloat(cost) : undefined,
    response_text: isSuccessful ? 
      successResponses[Math.floor(Math.random() * successResponses.length)] : 
      undefined,
    is_successful: isSuccessful,
    error_message: !isSuccessful ? 
      errorMessages[Math.floor(Math.random() * errorMessages.length)] : 
      undefined,
    execution_time_ms: executionTime,
    created_at: randomDate.toISOString()
  };
}

/**
 * Generate multiple mock executions
 * @param promptId The prompt ID
 * @param count Number of executions to generate
 * @returns Array of mock execution objects
 */
export function generateMockExecutions(promptId: string, count: number): Execution[] {
  const executions: Execution[] = [];
  
  for (let i = 0; i < count; i++) {
    // Make 20% of executions fail
    const isSuccessful = Math.random() > 0.2;
    executions.push(generateMockExecution(promptId, isSuccessful));
  }
  
  // Sort by created_at, newest first
  return executions.sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

/**
 * Simulate an API delay
 * @param minMs Minimum delay in milliseconds
 * @param maxMs Maximum delay in milliseconds
 * @returns A promise that resolves after the delay
 */
export function mockDelay(minMs: number = 200, maxMs: number = 1000): Promise<void> {
  const delay = Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  return new Promise(resolve => setTimeout(resolve, delay));
} 