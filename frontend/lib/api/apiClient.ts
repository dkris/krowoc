import { addCorrelationIdToRequest, trackApiRequest } from '../analytics';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1';

type RequestOptions = {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  credentials?: RequestCredentials;
};

/**
 * Custom API client that adds correlation IDs to all requests
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  // Create headers with defaults
  const headers = new Headers(options.headers || {});
  
  // Set default content type if not provided and we have a body
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  
  // Add correlation ID to request headers and track the request
  const correlationId = addCorrelationIdToRequest(headers);
  trackApiRequest(endpoint, options.method || 'GET', correlationId);
  
  // Prepare request URL
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  
  // Prepare final request options
  const requestOptions: RequestInit = {
    method: options.method || 'GET',
    headers,
    credentials: options.credentials || 'include',
  };
  
  // Add body if provided
  if (options.body) {
    requestOptions.body = typeof options.body === 'string' 
      ? options.body 
      : JSON.stringify(options.body);
  }
  
  try {
    const response = await fetch(url, requestOptions);
    
    // Store correlation ID from response if available
    const responseCorrelationId = response.headers.get('X-Correlation-ID');
    
    // Handle API errors
    if (!response.ok) {
      // Try to parse error response
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { message: 'Unknown error occurred' };
      }
      
      const error = new Error(errorData.message || `API error: ${response.status}`);
      (error as any).status = response.status;
      (error as any).data = errorData;
      (error as any).correlationId = responseCorrelationId || correlationId;
      throw error;
    }
    
    // Check if response is expected to be JSON
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      return data as T;
    }
    
    // Return raw response for non-JSON responses
    return response as unknown as T;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Convenience methods
export const get = <T>(endpoint: string, options?: RequestOptions) => 
  apiRequest<T>(endpoint, { ...options, method: 'GET' });

export const post = <T>(endpoint: string, body: any, options?: RequestOptions) => 
  apiRequest<T>(endpoint, { ...options, method: 'POST', body });

export const put = <T>(endpoint: string, body: any, options?: RequestOptions) => 
  apiRequest<T>(endpoint, { ...options, method: 'PUT', body });

export const del = <T>(endpoint: string, options?: RequestOptions) => 
  apiRequest<T>(endpoint, { ...options, method: 'DELETE' });

export default {
  get,
  post,
  put,
  delete: del,
  request: apiRequest
}; 