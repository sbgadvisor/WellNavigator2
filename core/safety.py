"""
Safety checks and compliance helpers for WellNavigator.
Implements guardrails, refusal patterns, and privacy protections.
"""

import re
from typing import Tuple, Optional


# Refusal templates for different scenarios
REFUSAL_TEMPLATES = {
    "emergency": (
        "🚨 **This sounds like a medical emergency.**\n\n"
        "**Please call 911 or go to your nearest emergency room immediately.**\n\n"
        "I'm designed to provide general health information, not emergency medical care. "
        "Your safety is the absolute priority, and you need immediate professional medical attention."
    ),
    "diagnosis": (
        "I cannot provide diagnoses or determine what condition you have. This requires "
        "a trained healthcare provider who can:\n"
        "• Examine you in person\n"
        "• Review your complete medical history\n"
        "• Order and interpret appropriate tests\n"
        "• Consider your unique circumstances\n\n"
        "**What I can do:** Help you understand general health information and prepare "
        "questions to ask your doctor."
    ),
    "prescription": (
        "I cannot prescribe medications or recommend specific treatments. These critical decisions "
        "must be made by your healthcare provider who:\n"
        "• Knows your complete medical history\n"
        "• Can assess drug interactions\n"
        "• Can monitor for side effects\n"
        "• Can adjust treatment as needed\n\n"
        "**What I can do:** Help you understand general information about conditions and "
        "treatment options to discuss with your doctor."
    ),
    "harmful": (
        "🆘 **I'm concerned about your safety.**\n\n"
        "If you're experiencing thoughts of self-harm, please reach out for immediate support:\n"
        "• **988 Suicide & Crisis Lifeline** - Call or text 988\n"
        "• **Crisis Text Line** - Text HOME to 741741\n"
        "• **911** - For immediate emergency help\n\n"
        "You deserve support, and trained professionals are available 24/7 to help you through this."
    ),
    "illicit": (
        "I cannot provide information about illegal activities, substance abuse, or harmful practices. "
        "If you're struggling with substance use, please reach out to:\n"
        "• **SAMHSA National Helpline** - 1-800-662-4357 (free, confidential, 24/7)\n"
        "• Your healthcare provider for treatment referrals\n\n"
        "Help is available, and recovery is possible."
    ),
    "out_of_scope": (
        "This request is outside my capabilities as a health information assistant. "
        "I'm designed to help you:\n"
        "• Understand general health information\n"
        "• Prepare for doctor appointments\n"
        "• Navigate healthcare systems\n"
        "• Learn about common conditions\n\n"
        "I cannot assist with this particular request."
    ),
    "no_medical_records": (
        "I cannot interpret or analyze personal medical records, test results, lab values, or images. "
        "This requires your healthcare provider who can:\n"
        "• Review your complete medical context\n"
        "• Compare with baseline values\n"
        "• Consider your symptoms and history\n"
        "• Provide personalized guidance\n\n"
        "**What I can do:** Help you prepare questions to ask your doctor about your results."
    )
}


# Emergency keywords that trigger immediate escalation
EMERGENCY_KEYWORDS = [
    # Cardiac emergencies
    "heart attack", "chest pain", "chest pressure", "crushing chest",
    # Stroke symptoms
    "stroke", "can't move", "face drooping", "slurred speech", "arm weakness",
    # Respiratory emergencies
    "can't breathe", "difficulty breathing", "trouble breathing", "choking",
    "not breathing", "gasping for air",
    # Mental health emergencies
    "suicidal", "suicide", "kill myself", "end my life", "want to die",
    "harm myself", "hurt myself",
    # Severe bleeding/trauma
    "severe bleeding", "bleeding won't stop", "heavy bleeding", "trauma",
    # Consciousness issues
    "unconscious", "unresponsive", "passed out", "losing consciousness",
    # Poisoning/overdose
    "overdose", "poisoning", "poisoned", "took too many pills",
    # Allergic reactions
    "anaphylaxis", "severe allergic reaction", "throat closing", "can't swallow",
    # Seizures
    "seizure", "convulsing", "shaking uncontrollably",
    # Severe pain
    "worst pain of my life", "unbearable pain", "excruciating pain"
]


# Diagnostic/prescriptive keywords that trigger refusal
DIAGNOSTIC_KEYWORDS = [
    # Direct diagnostic requests
    "do i have", "diagnose me", "what disease", "what condition do i have",
    "tell me what i have", "what's wrong with me", "what illness",
    # Specific condition queries
    "is this cancer", "is this diabetes", "is this heart disease",
    "do you think i have", "could this be", "is it possible i have",
    # Symptom diagnosis
    "what causes these symptoms", "what disease causes",
    "diagnose my symptoms", "what condition causes"
]


PRESCRIPTION_KEYWORDS = [
    # Medication requests
    "should i take", "prescribe", "what medication", "what drug should",
    "recommend medication", "which medicine",
    # Dosage questions
    "how much should i take", "what dose", "medication dosage",
    "how many pills", "dosage for",
    # Medication changes
    "can i stop taking", "stop my medication", "quit my medication",
    "change my dose", "increase my dose", "decrease my dose",
    # Treatment directives
    "tell me what treatment", "what should i do for", "how do i treat",
    "cure for", "best treatment for"
]


# Illicit/harmful request keywords
ILLICIT_KEYWORDS = [
    # Drug-related
    "get high", "recreational drugs", "illegal drugs", "drug abuse",
    "how to use drugs", "where to buy drugs",
    # Prescription abuse
    "fake prescription", "doctor shopping", "forge prescription",
    # Other harmful
    "hurt someone", "harm others", "poison someone",
    # Inappropriate medical
    "perform surgery", "diy surgery", "home surgery"
]


# Out-of-scope medical requests
OUT_OF_SCOPE_KEYWORDS = [
    # Legal/insurance fraud
    "fake medical note", "disability fraud", "fake sick note",
    "lie to doctor", "trick doctor",
    # Veterinary
    "my dog", "my cat", "my pet", "animal health",
    # Alternative medicine fraud
    "miracle cure", "cure cancer naturally", "secret cure"
]


# Patterns to detect potential personal information
PI_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
}


def should_refuse(user_input: str) -> Tuple[bool, Optional[str]]:
    """
    Check if the user input should be refused based on safety rules.
    
    Args:
        user_input: The user's message
    
    Returns:
        Tuple of (should_refuse: bool, refusal_message: str | None)
        If should_refuse is True, refusal_message contains the appropriate response
    """
    user_input_lower = user_input.lower()
    
    # Check for emergencies (highest priority)
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in user_input_lower:
            return True, REFUSAL_TEMPLATES["emergency"]
    
    # Check for illicit/harmful requests
    for keyword in ILLICIT_KEYWORDS:
        if keyword in user_input_lower:
            return True, REFUSAL_TEMPLATES["illicit"]
    
    # Check for self-harm keywords (redundant with emergency but more specific)
    harm_keywords = ["harm myself", "hurt myself", "kill myself", "end my life", 
                     "want to die", "commit suicide"]
    if any(keyword in user_input_lower for keyword in harm_keywords):
        return True, REFUSAL_TEMPLATES["harmful"]
    
    # Check for diagnostic requests
    if any(keyword in user_input_lower for keyword in DIAGNOSTIC_KEYWORDS):
        return True, REFUSAL_TEMPLATES["diagnosis"]
    
    # Check for prescription/medication advice
    if any(keyword in user_input_lower for keyword in PRESCRIPTION_KEYWORDS):
        return True, REFUSAL_TEMPLATES["prescription"]
    
    # Check for medical record interpretation requests
    record_keywords = ["analyze my results", "look at my test", "interpret my labs",
                       "read my mri", "analyze this image", "what does my x-ray",
                       "what do my labs mean", "interpret my bloodwork"]
    if any(keyword in user_input_lower for keyword in record_keywords):
        return True, REFUSAL_TEMPLATES["no_medical_records"]
    
    # Check for out-of-scope requests
    for keyword in OUT_OF_SCOPE_KEYWORDS:
        if keyword in user_input_lower:
            return True, REFUSAL_TEMPLATES["out_of_scope"]
    
    # No refusal needed
    return False, None


def redact_pi(user_input: str) -> str:
    """
    Redact potential personal information from user input.
    
    Args:
        user_input: The user's message
    
    Returns:
        Text with PI redacted (replaced with [REDACTED])
    """
    redacted = user_input
    
    # Redact SSN
    redacted = re.sub(PI_PATTERNS["ssn"], "[SSN_REDACTED]", redacted)
    
    # Redact credit card numbers
    redacted = re.sub(PI_PATTERNS["credit_card"], "[CARD_REDACTED]", redacted)
    
    # Redact phone numbers (be conservative - some medical contexts need numbers)
    # Only redact if it looks like a standalone phone number
    redacted = re.sub(r'\b(\d{3}[-.]?\d{3}[-.]?\d{4})\b', "[PHONE_REDACTED]", redacted)
    
    # Redact email addresses
    redacted = re.sub(PI_PATTERNS["email"], "[EMAIL_REDACTED]", redacted)
    
    return redacted


def medical_disclaimer() -> str:
    """
    Returns the standard medical disclaimer text.
    
    Returns:
        Disclaimer string
    """
    return (
        "**Important:** This information is for educational purposes only and does not "
        "constitute medical advice. Always consult with a qualified healthcare provider "
        "about your specific health concerns."
    )


def escalation_message(reason: str = "general") -> str:
    """
    Generate an appropriate escalation message.
    
    Args:
        reason: The reason for escalation ('urgent', 'complex', 'general')
    
    Returns:
        Escalation message string
    """
    if reason == "urgent":
        return (
            "⚕️ This situation may need prompt medical attention. Please contact your "
            "healthcare provider or visit an urgent care clinic soon."
        )
    elif reason == "complex":
        return (
            "This is a complex medical question that's best addressed by your healthcare "
            "team. I recommend scheduling an appointment to discuss this thoroughly with "
            "your doctor."
        )
    else:
        return (
            "For personalized medical guidance, please consult with your healthcare provider "
            "who can review your complete medical history and current situation."
        )


def get_safe_response_prefix(has_rag: bool = False, has_web: bool = False) -> str:
    """
    Generate a response prefix that sets appropriate expectations.
    
    Args:
        has_rag: Whether RAG context is being used
        has_web: Whether web search is being used
    
    Returns:
        Prefix string for assistant response
    """
    prefixes = []
    
    if has_rag:
        prefixes.append("Based on our knowledge base")
    if has_web:
        prefixes.append("current information")
    
    if prefixes:
        context = " and ".join(prefixes)
        return f"I'll help you understand this using {context}. Remember, this is general information, not personal medical advice.\n\n"
    else:
        return "I'll help you understand this. Remember, this is general information, not personal medical advice.\n\n"


def is_safe_query(user_input: str) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive safety check combining multiple safety checks.
    Alias for should_refuse for clearer API.
    
    Args:
        user_input: The user's message
    
    Returns:
        Tuple of (is_safe: bool, issue_message: str | None)
        If is_safe is False, issue_message explains why
    """
    should_refuse_result, refusal_msg = should_refuse(user_input)
    # Invert the logic: should_refuse returns (True, msg) for unsafe queries
    # is_safe_query returns (False, msg) for unsafe queries
    return (not should_refuse_result, refusal_msg)

