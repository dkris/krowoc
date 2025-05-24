from prefect import flow, task
from loguru import logger
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
import asyncio

@task
def prepare_prompt(prompt_id: str):
    """Prepare a prompt for execution by loading it from the database."""
    logger.info(f"Preparing prompt {prompt_id}")
    # This would typically fetch the prompt from the database
    return {
        "id": prompt_id,
        "content": "Sample prompt content"
    }

@task
async def execute_prompt(prompt: dict, model: str = "openai:gpt-4", stream: bool = False, use_memory: bool = True):
    """
    Execute a prompt using LangChain LLM wrappers, supporting chains, memory, and streaming.
    """
    logger.info(f"Executing prompt {prompt['id']} with model {model}")
    provider, model_name = model.split(":", 1) if ":" in model else ("openai", model)
    if provider == "openai":
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            streaming=stream,
        )
    elif provider == "anthropic":
        llm = ChatAnthropic(
            model=model_name,
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
            streaming=stream,
        )
    elif provider == "google":
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            streaming=stream,
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ])

    memory = ConversationBufferMemory(return_messages=True) if use_memory else None

    chain = prompt_template | llm
    result = None
    if stream:
        async def stream_result():
            async for chunk in chain.astream({"input": prompt["content"]}):
                yield chunk.content if hasattr(chunk, "content") else str(chunk)
        result = stream_result()
    else:
        if use_memory:
            # Add memory to the chain if needed
            result = await chain.ainvoke({"input": prompt["content"]}, memory=memory)
        else:
            result = await chain.ainvoke({"input": prompt["content"]})
        if hasattr(result, "content"):
            result = result.content
    return {
        "prompt_id": prompt["id"],
        "model": model,
        "result": result
    }

@task
def record_result(result: dict):
    """Record the result of a prompt execution."""
    logger.info(f"Recording result for prompt {result['prompt_id']}")
    # This would typically store the result in the database
    return result

@flow(name="Execute Prompt")
def execute_prompt_flow(prompt_id: str, model: str = "openai:gpt-4", stream: bool = False, use_memory: bool = True):
    """
    Flow to execute a prompt using an LLM with LangChain, supporting chains, memory, and streaming.
    """
    prompt = prepare_prompt(prompt_id)
    result = asyncio.run(execute_prompt(prompt, model, stream, use_memory))
    return record_result(result)

if __name__ == "__main__":
    # Example usage
    prompt_id = "sample-prompt-id"
    model = os.environ.get("DEFAULT_MODEL", "openai:gpt-4")
    execute_prompt_flow(prompt_id, model, stream=False, use_memory=True) 