"""
WellNavigator Core Module
Contains LLM, RAG, safety, and utility components.
"""

from .prompts import ASSISTANT_SYSTEM_PROMPT, compose_chat_prompt, get_suggested_prompts
from .safety import (
    should_refuse,
    redact_pi,
    medical_disclaimer,
    escalation_message,
    is_safe_query,
    REFUSAL_TEMPLATES
)
from .llm import stream_chat, stream_chat_to_streamlit, get_available_models
from .rag import retrieve_documents, is_rag_available, get_rag_stats
from .search import web_search, is_search_available, get_search_status, reformulate_query_for_search
from .voice import is_voice_available, transcribe_audio_file, add_to_listening_mode
from .observe import (
    log_turn, 
    get_session_metrics, 
    check_token_limit, 
    should_allow_streaming,
    get_token_usage_summary,
    MAX_TOKENS_PER_SESSION
)

__all__ = [
    "ASSISTANT_SYSTEM_PROMPT",
    "compose_chat_prompt",
    "get_suggested_prompts",
    "should_refuse",
    "redact_pi",
    "medical_disclaimer",
    "escalation_message",
    "is_safe_query",
    "REFUSAL_TEMPLATES",
    "stream_chat",
    "stream_chat_to_streamlit",
    "get_available_models",
    "retrieve_documents",
    "is_rag_available",
    "get_rag_stats",
    "web_search",
    "is_search_available",
    "get_search_status",
    "reformulate_query_for_search",
    "is_voice_available",
    "transcribe_audio_file",
    "add_to_listening_mode",
    "log_turn",
    "get_session_metrics",
    "check_token_limit",
    "should_allow_streaming",
    "get_token_usage_summary",
    "MAX_TOKENS_PER_SESSION",
]

