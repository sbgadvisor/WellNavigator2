"""
Observability and session management for WellNavigator.
Handles logging, metrics tracking, and token limits.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import streamlit as st


# Configuration
LOGS_DIR = Path("logs")
MAX_TOKENS_PER_SESSION = 50000  # Soft cap for POC
TOKEN_WARNING_THRESHOLD = 0.8  # Warn at 80% of max


class SessionObserver:
    """Observes and logs session interactions."""
    
    def __init__(self, logs_dir: Path = LOGS_DIR):
        self.logs_dir = logs_dir
        self._ensure_logs_dir()
    
    def _ensure_logs_dir(self):
        """Create logs directory if it doesn't exist."""
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create a .gitignore in logs directory
        gitignore_path = self.logs_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("# Ignore all log files\n*.jsonl\n*.log\n")
    
    def log_turn(self, meta: Dict[str, Any]):
        """
        Log a conversation turn to JSON lines file.
        
        Args:
            meta: Metadata dictionary containing:
                - timestamp: Turn timestamp
                - tokens_in: Input tokens
                - tokens_out: Output tokens
                - latency: Response latency in seconds
                - model: Model used
                - rag_used: Whether RAG was used
                - search_used: Whether search was used
                - cost: Turn cost in USD
                - refused: Whether request was refused
        """
        # Create log entry
        log_entry = {
            "timestamp": meta.get("timestamp", time.time()),
            "datetime": datetime.fromtimestamp(meta.get("timestamp", time.time())).isoformat(),
            "tokens_in": meta.get("token_in", 0),
            "tokens_out": meta.get("token_out", 0),
            "total_tokens": meta.get("token_in", 0) + meta.get("token_out", 0),
            "latency": meta.get("latency", 0.0),
            "model": meta.get("model", "unknown"),
            "temperature": meta.get("temperature", 0.7),
            "rag_used": meta.get("rag_used", False),
            "rag_docs_retrieved": meta.get("rag_docs_retrieved", 0),
            "search_used": meta.get("search_used", False),
            "search_results": meta.get("search_results", 0),
            "voice_used": meta.get("voice_used", False),
            "listening_mode": meta.get("listening_mode", False),
            "cost": meta.get("cost", 0.0),
            "refused": meta.get("refused", False),
            "citations_count": len(meta.get("citations", [])),
        }
        
        # Determine log file (one per day)
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"turns_{log_date}.jsonl"
        
        # Append to log file
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"❌ Error writing to log file: {e}")
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """
        Calculate session metrics from session state.
        
        Returns:
            Dictionary with session statistics
        """
        if "messages" not in st.session_state or "metrics" not in st.session_state:
            return {
                "total_requests": 0,
                "total_tokens_in": 0,
                "total_tokens_out": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency": 0.0,
                "requests_count": 0,
                "rag_requests": 0,
                "search_requests": 0,
                "refused_requests": 0,
            }
        
        # Count different types of messages
        assistant_messages = [
            msg for msg in st.session_state.messages 
            if msg.get("role") == "assistant"
        ]
        
        if not assistant_messages:
            return {
                "total_requests": 0,
                "total_tokens_in": 0,
                "total_tokens_out": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency": 0.0,
                "requests_count": 0,
                "rag_requests": 0,
                "search_requests": 0,
                "refused_requests": 0,
            }
        
        # Calculate metrics from messages
        latencies = []
        rag_count = 0
        search_count = 0
        refused_count = 0
        
        for msg in assistant_messages:
            meta = msg.get("meta", {})
            
            if meta.get("latency", 0) > 0:
                latencies.append(meta.get("latency", 0))
            
            if meta.get("rag_used", False):
                rag_count += 1
            
            if meta.get("search_used", False):
                search_count += 1
            
            if meta.get("refused", False):
                refused_count += 1
        
        # Get totals from session state metrics
        metrics = st.session_state.metrics
        
        return {
            "total_requests": len(assistant_messages),
            "total_tokens_in": metrics.get("token_in", 0),
            "total_tokens_out": metrics.get("token_out", 0),
            "total_tokens": metrics.get("token_in", 0) + metrics.get("token_out", 0),
            "total_cost": metrics.get("cost", 0.0),
            "avg_latency": sum(latencies) / len(latencies) if latencies else 0.0,
            "requests_count": len(assistant_messages),
            "rag_requests": rag_count,
            "search_requests": search_count,
            "refused_requests": refused_count,
        }
    
    def check_token_limit(self) -> Dict[str, Any]:
        """
        Check if session is approaching or exceeding token limit.
        
        Returns:
            Dictionary with:
                - exceeded: bool
                - warning: bool
                - remaining: int
                - percentage: float
                - message: str
        """
        metrics = self.get_session_metrics()
        total_tokens = metrics["total_tokens"]
        
        percentage = total_tokens / MAX_TOKENS_PER_SESSION
        remaining = MAX_TOKENS_PER_SESSION - total_tokens
        
        exceeded = total_tokens >= MAX_TOKENS_PER_SESSION
        warning = percentage >= TOKEN_WARNING_THRESHOLD and not exceeded
        
        # Generate appropriate message
        if exceeded:
            message = (
                f"⚠️ **Session token limit reached ({MAX_TOKENS_PER_SESSION:,} tokens).**\n\n"
                f"To continue, please clear your chat history or start a new session. "
                f"This helps maintain optimal performance and cost efficiency."
            )
        elif warning:
            percentage_str = f"{percentage * 100:.0f}%"
            message = (
                f"ℹ️ You've used {percentage_str} of your session token limit "
                f"({total_tokens:,} / {MAX_TOKENS_PER_SESSION:,} tokens). "
                f"Consider clearing chat if needed."
            )
        else:
            message = ""
        
        return {
            "exceeded": exceeded,
            "warning": warning,
            "remaining": remaining,
            "percentage": percentage,
            "message": message,
            "total_tokens": total_tokens,
        }


# Global observer instance
_observer = None

def get_observer() -> SessionObserver:
    """Get or create global observer instance."""
    global _observer
    if _observer is None:
        _observer = SessionObserver()
    return _observer

def log_turn(meta: Dict[str, Any]):
    """Convenience function to log a turn."""
    observer = get_observer()
    observer.log_turn(meta)

def get_session_metrics() -> Dict[str, Any]:
    """Convenience function to get session metrics."""
    observer = get_observer()
    return observer.get_session_metrics()

def check_token_limit() -> Dict[str, Any]:
    """Convenience function to check token limit."""
    observer = get_observer()
    return observer.check_token_limit()

def should_allow_streaming() -> bool:
    """Check if streaming should be allowed based on token limit."""
    limit_status = check_token_limit()
    return not limit_status["exceeded"]

def get_token_usage_summary() -> str:
    """Get a human-readable token usage summary."""
    metrics = get_session_metrics()
    limit_status = check_token_limit()
    
    total = metrics["total_tokens"]
    percentage = limit_status["percentage"] * 100
    
    if limit_status["exceeded"]:
        return f"🔴 {total:,} / {MAX_TOKENS_PER_SESSION:,} ({percentage:.0f}%) - Limit reached"
    elif limit_status["warning"]:
        return f"🟡 {total:,} / {MAX_TOKENS_PER_SESSION:,} ({percentage:.0f}%) - Approaching limit"
    else:
        return f"🟢 {total:,} / {MAX_TOKENS_PER_SESSION:,} ({percentage:.0f}%)"


def export_session_logs(start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """
    Export session logs for a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (default: today)
        end_date: End date in YYYY-MM-DD format (default: today)
    
    Returns:
        Path to exported file or error message
    """
    observer = get_observer()
    
    # Default to today if no dates provided
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")
    if not end_date:
        end_date = start_date
    
    # Read all matching log files
    all_logs = []
    
    try:
        for log_file in observer.logs_dir.glob(f"turns_*.jsonl"):
            # Extract date from filename
            file_date = log_file.stem.replace("turns_", "")
            
            if start_date <= file_date <= end_date:
                with open(log_file, "r") as f:
                    for line in f:
                        try:
                            all_logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        
        if not all_logs:
            return f"No logs found for date range {start_date} to {end_date}"
        
        # Create summary
        summary = {
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "total_turns": len(all_logs),
            "total_tokens": sum(log.get("total_tokens", 0) for log in all_logs),
            "total_cost": sum(log.get("cost", 0) for log in all_logs),
            "avg_latency": sum(log.get("latency", 0) for log in all_logs) / len(all_logs),
            "models_used": list(set(log.get("model", "unknown") for log in all_logs)),
            "rag_usage": sum(1 for log in all_logs if log.get("rag_used", False)),
            "search_usage": sum(1 for log in all_logs if log.get("search_used", False)),
            "refusals": sum(1 for log in all_logs if log.get("refused", False)),
            "turns": all_logs
        }
        
        # Export to file
        export_file = observer.logs_dir / f"export_{start_date}_to_{end_date}.json"
        with open(export_file, "w") as f:
            json.dumps(summary, f, indent=2)
        
        return str(export_file)
    
    except Exception as e:
        return f"Error exporting logs: {e}"


def get_logs_summary() -> Dict[str, Any]:
    """Get summary statistics from all logs."""
    observer = get_observer()
    
    all_logs = []
    
    try:
        for log_file in observer.logs_dir.glob("turns_*.jsonl"):
            with open(log_file, "r") as f:
                for line in f:
                    try:
                        all_logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        if not all_logs:
            return {
                "total_turns": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency": 0.0,
            }
        
        return {
            "total_turns": len(all_logs),
            "total_tokens": sum(log.get("total_tokens", 0) for log in all_logs),
            "total_cost": sum(log.get("cost", 0) for log in all_logs),
            "avg_latency": sum(log.get("latency", 0) for log in all_logs) / len(all_logs),
            "unique_days": len(list(observer.logs_dir.glob("turns_*.jsonl"))),
        }
    
    except Exception as e:
        print(f"Error reading logs: {e}")
        return {
            "total_turns": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_latency": 0.0,
        }

