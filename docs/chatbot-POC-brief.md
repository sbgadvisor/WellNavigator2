# WellNavigator Chatbot — POC Brief

## Mission
Patient-first, empathetic health concierge that advises (doesn't prescribe) and helps users act on next steps.

## Technology Stack
- **Frontend**: Streamlit (chat UI)
- **LLM**: OpenAI GPT-4
- **RAG**: Local vector store + Google Search connector
- **Scope**: No Supabase/OAuth/Dashboard integration in this phase (those are Wave 2)

## Must-have POC Capabilities

### 1. Chat UI
- Streaming responses for real-time interaction
- Persistent session state management
- Clean, intuitive chat interface

### 2. System Prompt & Guardrails
- Clear advice-not-prescribe stance
- Empathetic tone and communication style
- Source citation requirements
- Safety guardrails and refusal patterns

### 3. Suggested Prompts
- Tiles seeded by diagnosis/intent
- User-clickable prompt injection
- Context-aware suggestions

### 4. Minimal RAG Implementation
- Ingest small curated corpus (2-3 conditions)
- Embed and store in local vector database
- Retrieve relevant context for responses
- Cite sources in answers

### 5. Google Search Connector
- Fallback/validation mechanism
- Enable/disable via toggle
- Real-time information retrieval when needed

### 6. Voice Input & Listening Mode
- Push-to-talk (PTT) microphone functionality
- "Listening Mode" demo interface
- Mock realtime coach UI experience

### 7. Observability & Cost Management
- Token usage logging
- Latency measurement and tracking
- Per-turn and per-session metrics
- Cost monitoring and optimization

### 8. Safety & Compliance
- Non-diagnostic stance enforcement
- Clear disclaimers and limitations
- Escalation paths ("talk to your clinician")
- Refusal patterns for risky requests
- Compliance with health information guidelines

## Out of Scope (Wave 2)
- Supabase authentication/profile management
- Gated personalization features
- Dashboard write-backs
- Appointment scheduling integration
- Advanced user management

## Deliverables Structure

```
app.py
/core/
├── llm.py          # LLM interface and configuration
├── prompts.py      # System prompts and templates
├── rag.py          # RAG implementation and vector store
├── search.py       # Google Search integration
├── safety.py       # Safety checks and compliance
├── observe.py      # Logging and metrics
└── state.py        # Session state management
/data/corpus/       # Curated health content
├── condition1.md
├── condition2.md
└── condition3.md
ingest.py           # Data ingestion script
.env.example        # Environment variables template
/docs/
├── chatbot-POC-brief.md
└── acceptance.md   # Implementation checklist
```

## Success Criteria
- Functional chat interface with streaming responses
- Working RAG system with source citations
- Voice input capability
- Safety guardrails preventing medical advice
- Comprehensive logging and observability
- Google Search integration for real-time information
- Clean, maintainable codebase ready for Wave 2 expansion

## Next Steps
1. Review and approve this brief
2. Create detailed acceptance criteria in `/docs/acceptance.md`
3. Begin implementation following the deliverables structure
4. Regular check-ins against acceptance criteria
5. Prepare for Wave 2 planning upon POC completion
