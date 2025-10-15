"""
Prompt templates and composers for WellNavigator chatbot.
"""
from typing import Optional, List, Dict, Tuple

# Main system prompt for the assistant
ASSISTANT_SYSTEM_PROMPT = """You are WellNavigator, an empathetic health concierge. You advise, not prescribe. You:
• Use plain, empowering language; acknowledge uncertainty; never diagnose or replace clinicians.
• Prefer verified info. If unsure, say so and suggest next steps (contact provider, second opinion).
• When using retrieval or web, cite sources inline with short labels (e.g., "[Mayo Clinic]").
• Offer actionable next steps and questions to ask a provider.
• Safety: decline harmful or out-of-scope requests; escalate emergencies; avoid definitive treatment directives.
• Tone: calm, supportive, precise; avoid jargon unless explaining it."""


def compose_chat_prompt(
    history: List[Dict],
    user_input: str,
    retrieved: Optional[List[Dict]] = None,
    web_results: Optional[List[Dict]] = None,
    settings: Optional[Dict] = None
) -> Tuple[List[Dict], List[Dict]]:
    """
    Compose a complete chat prompt for OpenAI API.
    
    Args:
        history: List of previous messages with 'role' and 'content' keys
        user_input: The current user input text
        retrieved: Optional list of retrieved documents from RAG
                  Each dict should have 'text', 'source', and 'score' keys
        web_results: Optional list of web search results
                    Each dict should have 'content', 'source', and 'url' keys
        settings: Optional settings dict (for future use)
    
    Returns:
        Tuple of (messages: List[Dict], citations: List[Dict])
        - messages: List of message dicts ready for OpenAI Chat API
        - citations: List of unique sources used in the response
    """
    messages = []
    
    # Start with system prompt
    system_content = ASSISTANT_SYSTEM_PROMPT
    
    # Augment system prompt with context if available
    context_parts = []
    citations = []
    
    if retrieved and len(retrieved) > 0:
        retrieved_context, retrieved_citations = _format_retrieved_context(retrieved)
        context_parts.append(retrieved_context)
        citations.extend(retrieved_citations)
    
    if web_results and len(web_results) > 0:
        web_context, web_citations = _format_web_context(web_results)
        context_parts.append(web_context)
        citations.extend(web_citations)
    
    if context_parts:
        system_content += "\n\n---\n\n**CONTEXT FOR THIS QUERY:**\n\n"
        system_content += "\n\n".join(context_parts)
        system_content += "\n\nRemember to cite sources inline when using this information with [Source Label] format."
    
    messages.append({
        "role": "system",
        "content": system_content
    })
    
    # Add conversation history (limit to recent messages to manage context)
    # Include only user/assistant messages, skip any with meta-only content
    max_history = 10  # Keep last 10 exchanges
    recent_history = history[-max_history:] if len(history) > max_history else history
    
    for msg in recent_history:
        if msg.get("role") in ["user", "assistant"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Add current user input
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    return messages, citations


def _format_retrieved_context(retrieved: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Format retrieved RAG documents into context string.
    
    Args:
        retrieved: List of retrieved documents with 'text', 'source', 'score'
    
    Returns:
        Tuple of (formatted context string, citations list)
    """
    context = "**Retrieved from Knowledge Base:**\n"
    citations = []
    
    for i, doc in enumerate(retrieved[:5], 1):  # Limit to top 5
        source = doc.get("source", "Unknown")
        title = doc.get("title", "")
        text = doc.get("text", "").strip()
        score = doc.get("score", 0.0)
        
        # Create source label for inline citations
        source_label = source.replace(" ", "")[:15]  # Short label for inline use
        
        context += f"\n[{i}] [{source_label}] {title}\n"
        context += f"{text}\n"
        
        # Track unique citations
        citation = {
            'label': source_label,
            'source': source,
            'title': title,
            'score': score,
            'type': 'knowledge_base'
        }
        if citation not in citations:
            citations.append(citation)
    
    return context, citations


def _format_web_context(web_results: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Format web search results into context string.
    
    Args:
        web_results: List of web results with 'content', 'source', and 'url'
    
    Returns:
        Tuple of (formatted context string, citations list)
    """
    context = "**Current Web Information:**\n"
    citations = []
    
    for i, result in enumerate(web_results[:5], 1):  # Limit to top 5
        source = result.get("source", "Web")
        url = result.get("url", "")
        content = result.get("content", "").strip()
        
        # Create source label for inline citations
        source_label = f"Web{i}"
        
        context += f"\n[{i}] [{source_label}] {source}"
        if url:
            context += f" ({url})"
        context += f"\n{content}\n"
        
        # Track unique citations
        citation = {
            'label': source_label,
            'source': source,
            'url': url,
            'type': 'web_search'
        }
        if citation not in citations:
            citations.append(citation)
    
    return context, citations


def get_suggested_prompts(context: Optional[str] = None) -> List[str]:
    """
    Generate suggested prompts for the user.
    
    Args:
        context: Optional context to tailor suggestions (e.g., diagnosis, condition)
    
    Returns:
        List of suggested prompt strings
    """
    # Actionable, specific suggestions for health navigation
    default_prompts = [
        "Help me prepare for my next doctor visit",
        "Explain this medical term or test result in plain English",
        "What questions should I ask my doctor about my diagnosis?",
        "Help me compare treatment options in plain language",
        "Find the right specialist for my symptoms",
        "What lifestyle changes can support my condition?",
        "What does this insurance EOB or bill mean?",
        "What warning signs should I watch for with my condition?"
    ]
    
    # TODO: In future, use context to provide condition-specific suggestions
    # For now, return default prompts
    return default_prompts

