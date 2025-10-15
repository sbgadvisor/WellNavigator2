"""
LLM integration module for WellNavigator.
Handles OpenAI API calls with streaming support.
"""

import os
import time
from typing import List, Dict, Tuple, Iterator, Optional

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# Token pricing per 1K tokens (USD) - updated as of late 2024
MODEL_PRICING = {
    "gpt-4o": {
        "input": 0.0025,
        "output": 0.01
    },
    "gpt-4o-mini": {
        "input": 0.00015,
        "output": 0.0006
    },
    "gpt-4-turbo": {
        "input": 0.01,
        "output": 0.03
    },
    "gpt-4-turbo-preview": {
        "input": 0.01,
        "output": 0.03
    },
    "gpt-3.5-turbo": {
        "input": 0.0005,
        "output": 0.0015
    },
    "gpt-3.5-turbo-0125": {
        "input": 0.0005,
        "output": 0.0015
    }
}


def get_openai_client() -> Optional[OpenAI]:
    """
    Initialize and return OpenAI client.
    
    Returns:
        OpenAI client instance or None if API key not found
    """
    if OpenAI is None:
        if st:
            st.error("❌ OpenAI library not installed. Run: `pip install openai`")
        return None
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        if st:
            st.error("❌ OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")
        return None
    
    return OpenAI(api_key=api_key)


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count from text.
    More accurate would use tiktoken, but this is a reasonable approximation.
    
    Args:
        text: Input text to estimate
    
    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters for English text
    return len(text) // 4


def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """
    Calculate cost based on token usage and model pricing.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
    
    Returns:
        Total cost in USD
    """
    # Get pricing for the model (default to gpt-4o-mini if not found)
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
    
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]
    
    return input_cost + output_cost


def stream_chat(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> Tuple[str, Dict[str, any]]:
    """
    Stream a chat completion from OpenAI and yield tokens to Streamlit.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        model: OpenAI model to use
        temperature: Sampling temperature (0.0 - 2.0)
        max_tokens: Maximum tokens to generate (None = no limit)
    
    Returns:
        Tuple of (full_response: str, metadata: dict)
        metadata contains: tokens_in, tokens_out, cost, latency, model
    
    Yields:
        Tokens as they arrive from the API
    """
    client = get_openai_client()
    if client is None:
        # Return error message if client couldn't be initialized
        error_msg = "⚠️ OpenAI client not available. Check API key configuration."
        return error_msg, {
            "tokens_in": 0,
            "tokens_out": 0,
            "cost": 0.0,
            "latency": 0.0,
            "model": model,
            "error": True
        }
    
    start_time = time.time()
    full_response = ""
    
    try:
        # Create streaming completion
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        # Stream tokens
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                token = chunk.choices[0].delta.content
                full_response += token
                yield token
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Estimate token counts (more accurate would be to use tiktoken)
        # Calculate input tokens from all messages
        input_text = " ".join([msg["content"] for msg in messages])
        tokens_in = estimate_tokens(input_text)
        tokens_out = estimate_tokens(full_response)
        
        # Calculate cost
        cost = calculate_cost(tokens_in, tokens_out, model)
        
        metadata = {
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost,
            "latency": latency,
            "model": model,
            "error": False
        }
        
        return full_response, metadata
        
    except Exception as e:
        end_time = time.time()
        latency = end_time - start_time
        
        error_msg = f"❌ Error calling OpenAI API: {str(e)}"
        st.error(error_msg)
        
        return error_msg, {
            "tokens_in": 0,
            "tokens_out": 0,
            "cost": 0.0,
            "latency": latency,
            "model": model,
            "error": True,
            "error_message": str(e)
        }


def stream_chat_to_streamlit(
    messages: List[Dict[str, str]],
    placeholder,  # st.delta_generator.DeltaGenerator
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> Tuple[str, Dict[str, any]]:
    """
    Stream chat completion directly to a Streamlit placeholder.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        placeholder: Streamlit empty() placeholder to stream into
        model: OpenAI model to use
        temperature: Sampling temperature (0.0 - 2.0)
        max_tokens: Maximum tokens to generate (None = no limit)
    
    Returns:
        Tuple of (full_response: str, metadata: dict)
    """
    client = get_openai_client()
    if client is None:
        error_msg = "⚠️ OpenAI client not available. Check API key configuration."
        placeholder.markdown(error_msg)
        return error_msg, {
            "tokens_in": 0,
            "tokens_out": 0,
            "cost": 0.0,
            "latency": 0.0,
            "model": model,
            "error": True
        }
    
    start_time = time.time()
    full_response = ""
    
    try:
        # Create streaming completion
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        # Stream tokens to placeholder
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                token = chunk.choices[0].delta.content
                full_response += token
                # Update placeholder with accumulated response
                placeholder.markdown(full_response + "▌")
        
        # Final update without cursor
        placeholder.markdown(full_response)
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Estimate token counts
        input_text = " ".join([msg["content"] for msg in messages])
        tokens_in = estimate_tokens(input_text)
        tokens_out = estimate_tokens(full_response)
        
        # Calculate cost
        cost = calculate_cost(tokens_in, tokens_out, model)
        
        metadata = {
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost,
            "latency": latency,
            "model": model,
            "error": False
        }
        
        return full_response, metadata
        
    except Exception as e:
        end_time = time.time()
        latency = end_time - start_time
        
        error_msg = f"❌ Error calling OpenAI API: {str(e)}\n\n"
        error_msg += "Please check:\n"
        error_msg += "1. Your OPENAI_API_KEY is set correctly\n"
        error_msg += "2. Your API key has available credits\n"
        error_msg += "3. You have access to the selected model"
        
        placeholder.markdown(error_msg)
        
        return error_msg, {
            "tokens_in": 0,
            "tokens_out": 0,
            "cost": 0.0,
            "latency": latency,
            "model": model,
            "error": True,
            "error_message": str(e)
        }


def get_available_models() -> List[str]:
    """
    Get list of available OpenAI models.
    
    Returns:
        List of model names
    """
    return list(MODEL_PRICING.keys())

