/**
 * Represents an execution of a prompt against a language model
 */
export interface Execution {
  id: string;
  prompt_id: string;
  user_id: string;
  model: string;
  provider: string;
  input_tokens?: number;
  output_tokens?: number;
  cost?: number;
  response_text?: string;
  is_successful: boolean;
  error_message?: string;
  execution_time_ms: number;
  created_at: string;
} 