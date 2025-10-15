import streamlit as st
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import core modules
from core import (
    ASSISTANT_SYSTEM_PROMPT,
    compose_chat_prompt,
    get_suggested_prompts,
    should_refuse,
    redact_pi,
    medical_disclaimer,
    retrieve_documents,
    is_rag_available,
    get_rag_stats,
    web_search,
    is_search_available,
    reformulate_query_for_search,
    is_voice_available,
    add_to_listening_mode,
    log_turn,
    get_session_metrics,
    check_token_limit,
    should_allow_streaming,
    get_token_usage_summary,
    MAX_TOKENS_PER_SESSION
)
from core.llm import stream_chat_to_streamlit
from components.voice_input import simple_voice_button
from components.listening_mode import listening_mode_sidebar, listening_mode_panel

# Page configuration
st.set_page_config(
    page_title="WellNavigator - Health Support Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables if they don't exist"""
    
    # Messages list: each message has role, content, and meta
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Settings
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "model": "gpt-4o-mini",
            "temperature": 0.7,
        "search_on": False,
        "rag_on": False,
        "voice_on": False
        }
    
    # Metrics
    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "token_in": 0,
            "token_out": 0,
            "cost": 0.0,
            "latency": 0.0
        }

initialize_session_state()

# Disclaimer Banner
st.markdown("""
<div style="background-color: #FFF3CD; padding: 15px; border-radius: 5px; border-left: 5px solid #FFC107; margin-bottom: 20px;">
    <strong>⚠️ Important Disclaimer:</strong> This is an educational support tool, not medical advice. 
    In emergencies, call 911 or visit your nearest emergency room immediately.
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    st.markdown("---")
    
    # Model selection
    st.subheader("Model Configuration")
    model_options = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo"
    ]
    st.session_state.settings["model"] = st.selectbox(
        "Select Model",
        options=model_options,
        index=model_options.index(st.session_state.settings["model"])
    )
    
    # Temperature slider
    st.session_state.settings["temperature"] = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.settings["temperature"],
        step=0.1,
        help="Higher values make output more random, lower values more focused"
    )
    
    st.markdown("---")
    
    # Feature toggles
    st.subheader("Features")
    search_available = is_search_available()
    search_status = "✅ Available" if search_available else "❌ Not configured"
    
    st.session_state.settings["search_on"] = st.toggle(
        f"Use Google Search in answers - {search_status}",
        value=st.session_state.settings["search_on"] and search_available,
        disabled=not search_available,
        help="Enable web search to provide up-to-date information" if search_available else "Set GOOGLE_API_KEY and GOOGLE_CSE_ID in .env file"
    )
    
    rag_available = is_rag_available()
    rag_status = "✅ Available" if rag_available else "❌ Not available"
    
    st.session_state.settings["rag_on"] = st.toggle(
        f"Use RAG (vector store) - {rag_status}",
        value=st.session_state.settings["rag_on"] and rag_available,
        disabled=not rag_available,
        help="Enable retrieval from knowledge base" if rag_available else "Run 'python ingest.py' to create the RAG index"
    )
    
    # Voice input toggle
    voice_available = is_voice_available()
    voice_status = "✅ Available" if voice_available else "❌ Not configured"
    
    st.session_state.settings["voice_on"] = st.toggle(
        f"Enable Voice Input - {voice_status}",
        value=st.session_state.settings.get("voice_on", False) and voice_available,
        disabled=not voice_available,
        help="Enable voice recording and transcription" if voice_available else "OpenAI API key required for Whisper"
    )
    
    # Listening mode toggle
    listening_mode_sidebar()
    
    st.markdown("---")
    
    # Session Metrics expander with comprehensive stats
    st.subheader("📊 Session Metrics")
    
    with st.expander("Detailed Session Stats", expanded=True):
        session_metrics = get_session_metrics()
        limit_status = check_token_limit()
        
        # Token usage with limit indicator
        st.markdown("**Token Usage:**")
        st.markdown(get_token_usage_summary())
        
        # Progress bar for token usage
        progress_value = min(limit_status["percentage"], 1.0)
        st.progress(progress_value)
        
        # Show warning or limit message if needed
        if limit_status["message"]:
            if limit_status["exceeded"]:
                st.error(limit_status["message"])
            elif limit_status["warning"]:
                st.warning(limit_status["message"])
        
        st.markdown("---")
        
        # Request metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Requests", session_metrics["total_requests"])
        with col2:
            st.metric("Avg Latency", f"{session_metrics['avg_latency']:.2f}s")
        with col3:
            st.metric("Total Cost", f"${session_metrics['total_cost']:.4f}")
        
        # Token breakdown
        st.markdown("**Token Breakdown:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Input", f"{session_metrics['total_tokens_in']:,}")
        with col2:
            st.metric("Output", f"{session_metrics['total_tokens_out']:,}")
        with col3:
            st.metric("Total", f"{session_metrics['total_tokens']:,}")
        
        # Feature usage
        st.markdown("**Feature Usage:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("RAG Requests", session_metrics["rag_requests"])
        with col2:
            st.metric("Search Requests", session_metrics["search_requests"])
        with col3:
            st.metric("Refusals", session_metrics["refused_requests"])
    
    st.markdown("---")
    
    # Safety & Limits section
    st.subheader("🛡️ Safety & Limits")
    
    with st.expander("Our Safety Stance", expanded=False):
        st.markdown("""
        **What We Do:**
        - ✅ Provide general health information
        - ✅ Help prepare for doctor visits
        - ✅ Explain medical concepts
        - ✅ Assist with healthcare navigation
        
        **What We Don't Do:**
        - ❌ **Diagnose** medical conditions
        - ❌ **Prescribe** medications or treatments
        - ❌ **Replace** your healthcare provider
        - ❌ **Handle** medical emergencies
        
        **Emergency?** Call 911 immediately.
        
        **Crisis Support:**
        - 988 - Suicide & Crisis Lifeline
        - 741741 - Crisis Text Line
        """)
    
    with st.expander("Privacy & Data", expanded=False):
        st.markdown("""
        **POC Privacy Notice:**
        
        This is a **proof-of-concept** system:
        - 🔒 Conversations are session-only
        - 🔒 No data stored after you close tab
        - 🔒 PI automatically redacted (SSN, cards, etc.)
        - 🔒 No PHI stored in this POC
        
        **For Production:**
        - Would require HIPAA compliance
        - Encrypted data storage
        - Audit logging
        - Access controls
        
        **Never share:**
        - Social Security Numbers
        - Credit card information
        - Full medical records
        - Identifiable health information
        """)
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.metrics = {
            "token_in": 0,
            "token_out": 0,
            "cost": 0.0,
            "latency": 0.0
        }
        st.rerun()

# Main chat interface
st.title("🏥 WellNavigator")
st.markdown("*Your AI-powered health information assistant*")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display metadata if present
        if "meta" in message and message["meta"]:
            with st.expander("ℹ️ Message Details", expanded=False):
                st.json(message["meta"])

# Suggested Prompts Panel - Always visible above chat input
st.markdown("---")
with st.expander("💡 **Suggested Questions** - Click to use", expanded=(len(st.session_state.messages) == 0)):
    st.markdown("*Quick-start prompts to help you navigate your health journey*")
    
    suggested_prompts = get_suggested_prompts()
    
    # Display in a 2-column grid for better visibility
    cols = st.columns(2)
    for idx, prompt in enumerate(suggested_prompts):
        with cols[idx % 2]:
            # Create compact, clickable buttons
            if st.button(
                prompt, 
                key=f"suggested_prompt_{idx}",
                use_container_width=True,
                type="secondary"
            ):
                # Inject the prompt as user input and process immediately
                st.session_state._suggested_prompt = prompt
                st.rerun()

# Voice input section
voice_transcript = None
if st.session_state.settings.get("voice_on", False) and is_voice_available():
    st.markdown("#### 🎤 Voice Input")
    voice_transcript = simple_voice_button("main_voice")
    if voice_transcript:
        st.session_state.voice_input = voice_transcript

# Chat input (check if a suggested prompt was clicked)
user_input = None
if "_suggested_prompt" in st.session_state:
    user_input = st.session_state._suggested_prompt
    del st.session_state._suggested_prompt
elif voice_transcript:
    user_input = voice_transcript
    # Clear voice input after use
    if "voice_input" in st.session_state:
        del st.session_state.voice_input
else:
    chat_placeholder = "Ask me about health topics..."
    if voice_transcript:
        chat_placeholder = f"Voice input: {voice_transcript}"
    user_input = st.chat_input(chat_placeholder)

if user_input:
    # Check for PI and redact if necessary
    original_input = user_input
    user_input = redact_pi(user_input)
    
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "meta": {
            "timestamp": datetime.now().isoformat(),
            "settings": st.session_state.settings.copy(),
            "redacted": original_input != user_input
        }
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Safety check
    should_refuse_request, refusal_message = should_refuse(user_input)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if should_refuse_request:
            # Show refusal message (no API call needed)
            response = refusal_message
            message_placeholder.markdown(response)
            
            # Add medical disclaimer
            st.markdown("---")
            st.info(medical_disclaimer())
            
            # Minimal metrics for refusal
            token_in = len(user_input) // 4
            token_out = len(response) // 4
            cost = 0.0  # No API cost for refusals
            latency = 0.0
            
        else:
            # Check token limit before processing
            limit_status = check_token_limit()
            
            if limit_status["exceeded"]:
                # Token limit exceeded - show gentle nudge
                response = (
                    f"⚠️ **Session token limit reached ({MAX_TOKENS_PER_SESSION:,} tokens).**\n\n"
                    f"You've reached the session token limit to help maintain optimal performance "
                    f"and cost efficiency. Please clear your chat history to continue.\n\n"
                    f"Click the **🗑️ Clear Chat** button in the sidebar to start fresh."
                )
                message_placeholder.markdown(response)
                
                # Minimal metrics
                token_in = len(user_input) // 4
                token_out = len(response) // 4
                cost = 0.0
                latency = 0.0
                retrieved_docs = []
                web_results = []
                citations = []
                
            else:
                # Retrieve RAG context if enabled
                retrieved_docs = []
                if st.session_state.settings["rag_on"] and is_rag_available():
                    try:
                        retrieved_docs = retrieve_documents(user_input, k=5)
                    except Exception as e:
                        st.warning(f"RAG retrieval failed: {e}")
                        retrieved_docs = []
                
                # Perform web search if enabled
                web_results = []
                if st.session_state.settings["search_on"] and is_search_available():
                    try:
                        # Reformulate query for better search results
                        search_query = reformulate_query_for_search(user_input)
                        web_results = web_search(search_query, k=3)
                    except Exception as e:
                        st.warning(f"Web search failed: {e}")
                        web_results = []
                
                # Build messages for OpenAI API
                messages, citations = compose_chat_prompt(
                    history=st.session_state.messages[:-1],  # Exclude current user message
                    user_input=user_input,
                    retrieved=retrieved_docs if st.session_state.settings["rag_on"] else None,
                    web_results=web_results if st.session_state.settings["search_on"] else None,
                    settings=st.session_state.settings
                )
                
                # Stream response from LLM
                response, metadata = stream_chat_to_streamlit(
                    messages=messages,
                    placeholder=message_placeholder,
                    model=st.session_state.settings["model"],
                    temperature=st.session_state.settings["temperature"]
                )
            
            # Extract metrics from metadata
            token_in = metadata.get("tokens_in", 0)
            token_out = metadata.get("tokens_out", 0)
            cost = metadata.get("cost", 0.0)
            latency = metadata.get("latency", 0.0)
            
            # Display citations if RAG was used
            if citations and st.session_state.settings["rag_on"]:
                st.markdown("---")
                st.markdown("### 📚 Sources")
                for citation in citations:
                    if citation['type'] == 'knowledge_base':
                        st.markdown(f"**{citation['source']}** - {citation['title']}")
                    else:
                        st.markdown(f"**{citation['source']}** - {citation.get('url', 'Web source')}")
        
        # Update metrics
        st.session_state.metrics["token_in"] += token_in
        st.session_state.metrics["token_out"] += token_out
        st.session_state.metrics["cost"] += cost
        st.session_state.metrics["latency"] = latency
    
    # Add assistant message to chat
    meta = {
        "timestamp": time.time(),
        "model": st.session_state.settings["model"],
        "temperature": st.session_state.settings["temperature"],
        "token_in": token_in,
        "token_out": token_out,
        "cost": cost,
        "latency": latency,
        "search_used": st.session_state.settings["search_on"],
        "rag_used": st.session_state.settings["rag_on"],
        "rag_docs_retrieved": len(retrieved_docs) if 'retrieved_docs' in locals() else 0,
        "search_results": len(web_results) if 'web_results' in locals() else 0,
        "citations": citations if 'citations' in locals() else [],
        "refused": should_refuse_request,
        "voice_used": st.session_state.settings.get("voice_on", False),
        "listening_mode": st.session_state.get("listening_mode_enabled", False),
    }
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "meta": meta
    })
    
    # Log turn to JSON lines
    log_turn(meta)
    
    # Add to listening mode if enabled
    if st.session_state.get("listening_mode_enabled", False):
        add_to_listening_mode(user_input)
    
    st.rerun()

# Listening mode panel
if st.session_state.get("show_listening_panel", False):
    st.markdown("---")
    listening_mode_panel()
    
    if st.button("Close Panel"):
        st.session_state["show_listening_panel"] = False
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; padding: 20px;">
    <p><strong>Privacy Note:</strong> Your conversations are stored in session state and are not persisted after you close this tab.</p>
    <p><strong>Citations:</strong> When references are provided, they will appear inline with responses for your verification.</p>
    <p style="margin-top: 10px;">© 2025 WellNavigator | Educational Use Only</p>
</div>
""", unsafe_allow_html=True)

