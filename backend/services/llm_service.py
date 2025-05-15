from typing import Dict, List, Optional, Set, Union, AsyncGenerator, Any
import logging
import os
from aisuite import AsyncClient, CompletionOptions, LLMResponse, ResponseFormat
from aisuite.streaming import ChunkResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Supported LLM providers and models
# This should be expanded with actual models and providers from aisuite
SUPPORTED_PROVIDERS = {
    "openai": {
        "models": {
            "gpt-3.5-turbo", 
            "gpt-4", 
            "gpt-4-turbo",
            "gpt-4o",
        }
    },
    "anthropic": {
        "models": {
            "claude-2", 
            "claude-3-opus", 
            "claude-3-sonnet",
            "claude-3-haiku",
        }
    },
    "google": {
        "models": {
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-ultra",
        }
    }
}

class PromptRequest(BaseModel):
    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    stream: bool = False
    system_prompt: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None

class LLMService:
    def __init__(self):
        self.providers = SUPPORTED_PROVIDERS
        self.client = AsyncClient(
            api_key=os.environ.get("AISUITE_API_KEY"),
            organization_id=os.environ.get("AISUITE_ORG_ID", None)
        )
        logger.info(f"LLMService initialized with {len(self.providers)} providers")
    
    def get_supported_providers(self) -> List[str]:
        """Get list of supported LLM providers"""
        return list(self.providers.keys())
    
    def get_supported_models(self, provider: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get supported models, optionally filtered by provider
        
        Args:
            provider: Optional provider to filter by
            
        Returns:
            Dictionary of provider -> list of models
        """
        if provider:
            if provider not in self.providers:
                raise ValueError(f"Unsupported provider: {provider}")
            return {provider: list(self.providers[provider]["models"])}
        
        # Return all models by provider
        return {
            provider: list(models["models"]) 
            for provider, models in self.providers.items()
        }
    
    def validate_model_whitelist(self, model_whitelist: List[str]) -> List[str]:
        """
        Validate a list of models against supported providers/models
        
        Args:
            model_whitelist: List of model identifiers (e.g., "openai:gpt-4")
            
        Returns:
            List of valid model identifiers
            
        Raises:
            ValueError if any models are invalid
        """
        if not model_whitelist:
            return []
            
        valid_models = []
        invalid_models = []
        
        for model_id in model_whitelist:
            # Format should be provider:model
            if ":" not in model_id:
                invalid_models.append(model_id)
                continue
                
            provider, model = model_id.split(":", 1)
            
            # Check if provider is supported
            if provider not in self.providers:
                invalid_models.append(model_id)
                continue
                
            # Check if model is supported for this provider
            if model not in self.providers[provider]["models"]:
                invalid_models.append(model_id)
                continue
                
            valid_models.append(model_id)
            
        if invalid_models:
            raise ValueError(f"Invalid models in whitelist: {', '.join(invalid_models)}")
            
        return valid_models
    
    async def execute_prompt(self, request: PromptRequest) -> Union[LLMResponse, AsyncGenerator[ChunkResponse, None]]:
        """
        Execute a prompt with the specified model
        
        Args:
            request: The prompt request containing prompt text and parameters
            
        Returns:
            The LLM response or a stream of chunks if streaming is enabled
        """
        # Extract provider and model name
        if ":" not in request.model:
            raise ValueError(f"Invalid model format: {request.model}. Expected format: provider:model")
        
        provider, model = request.model.split(":", 1)
        
        # Validate provider and model
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if model not in self.providers[provider]["models"]:
            raise ValueError(f"Unsupported model for {provider}: {model}")
        
        # Prepare completion options
        options = CompletionOptions(
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream,
            provider=provider,
        )
        
        # Execute prompt
        if request.stream:
            return self.client.complete_streaming(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                tools=request.tools,
                options=options
            )
        else:
            return await self.client.complete(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                tools=request.tools,
                options=options
            )

# Create a singleton instance
llm_service = LLMService() 