"""
Listening mode demo component for Streamlit.
Provides a right-side panel with live notes and coach suggestions.
"""

import streamlit as st
import time
from typing import List, Dict, Any
from core.voice import get_listening_mode


def listening_mode_panel():
    """Render the listening mode demo panel."""
    
    listening_mode = get_listening_mode()
    
    # Panel header
    st.markdown("### 🎧 Listening Mode Demo")
    st.markdown("*Capture conversation insights and get coaching suggestions*")
    
    # Session stats
    stats = listening_mode.get_session_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Duration", f"{stats['duration_minutes']:.1f} min")
    with col2:
        st.metric("Messages", stats['total_messages'])
    with col3:
        st.metric("Suggestions", stats['suggestions_count'])
    
    st.markdown("---")
    
    # Live notes section
    st.markdown("#### 📝 Live Notes")
    
    session_data = st.session_state.get("listening_mode_data", {})
    live_notes = session_data.get("live_notes", [])
    
    if live_notes:
        # Display recent notes (last 10)
        recent_notes = live_notes[-10:]
        
        for note in reversed(recent_notes):
            with st.container():
                st.markdown(f"**{note['timestamp']}** - {note['content']}")
                st.markdown("---")
    else:
        st.info("No notes captured yet. Start chatting to see live notes appear here!")
    
    # Coach suggestions section
    st.markdown("#### 💡 Coach Suggestions")
    
    coach_suggestions = session_data.get("coach_suggestions", [])
    
    if coach_suggestions:
        # Group by priority
        high_priority = [s for s in coach_suggestions if s.get('priority') == 'high']
        medium_priority = [s for s in coach_suggestions if s.get('priority') == 'medium']
        
        # Display high priority first
        for suggestion in high_priority:
            render_suggestion_card(suggestion, "high")
        
        # Display medium priority
        for suggestion in medium_priority:
            render_suggestion_card(suggestion, "medium")
    else:
        st.info("No suggestions yet. Chat about health topics to get personalized coaching!")
    
    # Control buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh", help="Update the panel with latest data"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Session", help="Clear all notes and suggestions"):
            listening_mode.clear_session()
            st.rerun()


def render_suggestion_card(suggestion: Dict[str, Any], priority: str):
    """Render a coach suggestion card."""
    
    # Priority-based styling
    if priority == "high":
        border_color = "#ff4444"
        bg_color = "#fff5f5"
        icon_color = "#ff4444"
    else:
        border_color = "#4CAF50"
        bg_color = "#f5fff5"
        icon_color = "#4CAF50"
    
    # Card HTML
    card_html = f"""
    <div style="
        border: 2px solid {border_color};
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        background-color: {bg_color};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 20px; margin-right: 8px;">{suggestion.get('icon', '💡')}</span>
            <strong style="color: {icon_color};">{suggestion.get('title', 'Suggestion')}</strong>
        </div>
        <p style="margin: 0; font-size: 14px; color: #333;">
            {suggestion.get('content', 'No content available')}
        </p>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def listening_mode_sidebar():
    """Render listening mode controls in the sidebar."""
    
    st.markdown("### 🎧 Listening Mode")
    
    # Toggle for listening mode
    listening_enabled = st.toggle(
        "Enable Listening Mode",
        value=st.session_state.get("listening_mode_enabled", False),
        help="Capture conversation insights and get coaching suggestions"
    )
    
    st.session_state["listening_mode_enabled"] = listening_enabled
    
    if listening_enabled:
        st.success("✅ Listening mode active")
        
        # Quick stats
        listening_mode = get_listening_mode()
        stats = listening_mode.get_session_stats()
        
        st.markdown(f"**Session Stats:**")
        st.markdown(f"• Duration: {stats['duration_minutes']:.1f} min")
        st.markdown(f"• Messages: {stats['total_messages']}")
        st.markdown(f"• Suggestions: {stats['suggestions_count']}")
        
        # Quick actions
        if st.button("📊 View Panel"):
            st.session_state["show_listening_panel"] = True
        
        if st.button("🗑️ Clear Session"):
            listening_mode.clear_session()
            st.rerun()
    else:
        st.info("💤 Listening mode inactive")


def mock_streaming_capture():
    """
    Mock streaming capture for demo purposes.
    Simulates real-time capture of user messages.
    """
    
    if not st.session_state.get("listening_mode_enabled", False):
        return
    
    # This would be called whenever a user message is processed
    # For now, it's integrated into the main chat flow
    
    # Simulate some additional insights
    listening_mode = get_listening_mode()
    
    # Add some mock insights based on recent activity
    current_time = time.strftime("%H:%M:%S")
    
    # Example: Add a mock insight every few messages
    session_data = st.session_state.get("listening_mode_data", {})
    total_messages = session_data.get("total_messages", 0)
    
    if total_messages > 0 and total_messages % 3 == 0:
        mock_insight = {
            "timestamp": current_time,
            "content": f"Pattern detected: {total_messages} messages about health topics",
            "type": "insight"
        }
        
        if "live_notes" not in st.session_state.get("listening_mode_data", {}):
            st.session_state["listening_mode_data"]["live_notes"] = []
        
        st.session_state["listening_mode_data"]["live_notes"].append(mock_insight)


def get_coach_suggestions_summary() -> str:
    """Get a summary of current coach suggestions for display."""
    
    session_data = st.session_state.get("listening_mode_data", {})
    suggestions = session_data.get("coach_suggestions", [])
    
    if not suggestions:
        return "No suggestions available yet."
    
    high_priority = [s for s in suggestions if s.get('priority') == 'high']
    medium_priority = [s for s in suggestions if s.get('priority') == 'medium']
    
    summary_parts = []
    
    if high_priority:
        summary_parts.append(f"🔥 {len(high_priority)} high-priority suggestions")
    
    if medium_priority:
        summary_parts.append(f"💡 {len(medium_priority)} general suggestions")
    
    return " • ".join(summary_parts) if summary_parts else "No suggestions available."
