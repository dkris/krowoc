# LLM Integration Guide

This guide explains how to use the LLM integration features in Krowoc.

## Overview

Krowoc provides a unified API for interacting with multiple LLM providers through the `aisuite` library. This allows you to:

1. Execute prompts with any supported model
2. Stream responses in real-time
3. Use system prompts and tool specifications
4. Apply model whitelisting for specific prompts

## API Endpoints

### Execute an Arbitrary Prompt

```http
POST /api/prompts/execute
Content-Type: application/json

{
  "prompt": "What is the capital of France?",
  "model": "openai:gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false,
  "system_prompt": "You are a helpful assistant."
}
```

### Execute a Stored Prompt

```http
POST /api/prompts/{prompt_id}/execute
Content-Type: application/json

{
  "model": "anthropic:claude-3-opus",
  "temperature": 0.5,
  "max_tokens": 2000,
  "stream": true
}
```

## Streaming Responses

To receive streaming responses, set `stream: true` in your request. The response will be delivered as Server-Sent Events (SSE):

```javascript
// Frontend example (React)
import { useState, useEffect } from 'react';

function StreamingPromptDemo() {
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const executePrompt = async () => {
    setIsLoading(true);
    setResponse('');
    setError(null);
    
    try {
      const eventSource = new EventSource('/api/prompts/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: "Explain quantum computing in simple terms",
          model: "openai:gpt-4",
          stream: true
        })
      });
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.text) {
          setResponse(prev => prev + data.text);
        }
      };
      
      eventSource.onerror = (error) => {
        setError("An error occurred while streaming the response");
        eventSource.close();
        setIsLoading(false);
      };
      
      eventSource.addEventListener('done', () => {
        eventSource.close();
        setIsLoading(false);
      });
      
      eventSource.addEventListener('error', (event) => {
        const data = JSON.parse(event.data);
        setError(data.error);
        eventSource.close();
        setIsLoading(false);
      });
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  return (
    <div>
      <button onClick={executePrompt} disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Execute Prompt'}
      </button>
      {error && <div className="error">{error}</div>}
      <div className="response">
        {response || 'Response will appear here'}
      </div>
    </div>
  );
}
```

## Tools Support

You can provide tool specifications for models that support function calling:

```http
POST /api/prompts/execute
Content-Type: application/json

{
  "prompt": "What's the weather in New York?",
  "model": "openai:gpt-4",
  "system_prompt": "You are a helpful assistant with access to tools.",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get the current weather in a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "The temperature unit"
            }
          },
          "required": ["location"]
        }
      }
    }
  ]
}
```

## Environment Setup

To use the LLM integration, you need to set up API keys for your chosen providers:

1. Copy `_env.example` to `.env`
2. Add your API keys for supported providers:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GOOGLE_AI_API_KEY=your_google_ai_api_key
   AISUITE_API_KEY=your_aisuite_api_key
   AISUITE_ORG_ID=your_aisuite_org_id
   ```

## Supported Models

The following models are currently supported:

### OpenAI
- gpt-3.5-turbo
- gpt-4
- gpt-4-turbo
- gpt-4o

### Anthropic
- claude-2
- claude-3-opus
- claude-3-sonnet
- claude-3-haiku

### Google
- gemini-pro
- gemini-pro-vision
- gemini-ultra 