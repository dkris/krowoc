from typing import Dict, List, Optional, Set, Union, AsyncGenerator, Any
import logging
import os
from pydantic import BaseModel

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)

# Supported LLM providers and models (as per LangChain wrappers)
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
        logger.info(f"LLMService initialized with {len(self.providers)} providers (LangChain)")
    
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
    
    async def execute_prompt(self, request: PromptRequest) -> Union[str, AsyncGenerator[str, None]]:
        """
        Execute a prompt with the specified model using LangChain wrappers.
        Supports streaming and non-streaming responses.
        """
        if ":" not in request.model:
            raise ValueError(f"Invalid model format: {request.model}. Expected format: provider:model")
        provider, model = request.model.split(":", 1)
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        if model not in self.providers[provider]["models"]:
            raise ValueError(f"Unsupported model for {provider}: {model}")

        # Prepare LangChain LLM instance
        if provider == "openai":
            llm = ChatOpenAI(
                model=model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                streaming=request.stream,
                openai_api_key=os.environ.get("OPENAI_API_KEY"),
            )
        elif provider == "anthropic":
            llm = ChatAnthropic(
                model=model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                streaming=request.stream,
                anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            )
        elif provider == "google":
            llm = ChatGoogleGenerativeAI(
                model=model,
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
                streaming=request.stream,
                google_api_key=os.environ.get("GOOGLE_API_KEY"),
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Prepare messages
        messages = []
        if request.system_prompt:
            messages.append(SystemMessage(content=request.system_prompt))
        messages.append(HumanMessage(content=request.prompt))

        # Streaming
        if request.stream:
            async def stream_response():
                async for chunk in llm.astream(messages):
                    if hasattr(chunk, "content"):
                        yield chunk.content
                    else:
                        yield str(chunk)
            return stream_response()
        # Non-streaming
        response = await llm.ainvoke(messages)
        if hasattr(response, "content"):
            return response.content
        return str(response)

# Create a singleton instance
llm_service = LLMService() 