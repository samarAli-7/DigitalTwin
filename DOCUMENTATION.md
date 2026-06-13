# Technical Documentation: The Newton Digital Twin 2.0

## 1. System Architecture
The application is built on a modular architecture that combines high-level LLM orchestration with robust local services for voice and data persistence.

### Core Architecture Components:
- Reasoning Engine (Brain): Google Gemini 2.5 Flash (via `langchain-google-genai`). Replaced local inference to provide higher-tier reasoning, better 17th-century linguistic nuances, and reliable output formatting.
- Retrieval-Augmented Generation (RAG): 
  - Vector Store: ChromaDB stores embeddings for Newton's historical works (Principia, Opticks) and user-specific facts.
  - Embeddings: `sentence-transformers/all-MiniLM-L6-v2` provides efficient local embedding generation.
- Voice Processing Suite:
  - STT (Ears): Local OpenAI Whisper (Tiny) for private, robust speech transcription.
  - TTS (Voice): `edge-tts` (en-GB-ThomasNeural) providing a professional British persona.
- Frontend: Streamlit provides a clean, professional web interface designed for scientific discourse.

## 2. Technical Novelties

### Interactive Dispute Engine (Newton vs. Hooke)
The project implements a Multi-Agent Discourse Pattern.
- Antagonistic Reasoning: The system simulates the historical rivalry by passing Newton's claims to a specialized Hooke agent. Hooke is programmed to challenge abstractions with "physical observations," forcing the LLM to defend its reasoning.
- Session Continuity: The outcome of these disputes is summarized by the LLM and injected back into the long-term vector memory, allowing Newton to refer to past disagreements in future chats.

### Automated Milestone Discovery
Instead of manual checklists, the system uses Keyword-Driven State Management to track scientific progress.
- The `update_milestones` logic scans LLM responses for semantic triggers related to Newton's major discoveries (e.g., "prism" for Optics, "fluxion" for Calculus).
- This creates a gamified yet professional sense of exploration through Newton's scientific legacy.

### Manuscript Synthesis
A unique feature that transforms transient chat history into a structured Markdown manuscript.
- The `generate_manuscript` method uses a specialized system prompt to rewrite the conversation in the style of 17th-century scientific papers.
- It includes Latin-style headings and formal vocabulary, suitable for the Philosophical Transactions of the Royal Society.

## 3. Data Flow & Memory
The system uses a Hybrid Memory Strategy:
1. Short-Term Context: Managed via `ChatMessageHistory` for the current conversation loop.
2. Long-Term Vector Memory: ChromaDB handles RAG, ensuring Newton has a "knowledge base" of the user.
3. Long-Term JSON Persistence: `long_term_memory.json` provides a human-readable and UI-friendly mirror of the facts Newton has learned.

## 4. UI/UX Refinements
The interface has been stripped of informal elements (emojis, "local" branding) to provide a "Digital Twin" experience that feels like a professional research tool. The custom CSS provides "Mobile-style" chat bubbles for readability while maintaining a "Manuscript-style" aesthetic for the document viewer.

## 5. Graceful State Management
The "End Conversation" feature performs an automated post-session cleanup:
- It extracts new facts from the current session.
- It persists them to both the Vector DB and JSON store.
- It shuts down the server, ensuring all resources are properly released.
