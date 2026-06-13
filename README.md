# Isaac Newton Digital Twin (RAG Project)

A sophisticated Retrieval-Augmented Generation (RAG) system that creates a "digital twin" of Sir Isaac Newton. This project combines historical data retrieval with advanced AI reasoning, voice capabilities, and interactive physics simulations.

## Features

- **Persona-Driven AI**: Newton's responses are crafted in 17th-century formal English using Google Gemini 2.5 Flash.
- **RAG Architecture**: Knowledge is grounded in primary sources (`Principia`, `Opticks`) and detailed historical biographies.
- **Dynamic Simulations (New!)**: Newton can launch standalone **Pygame simulations** to illustrate concepts like:
    - Universal Gravitation
    - Orbital Mechanics
    - Light Decomposition (Prisms)
    - Action and Reaction (Third Law)
- **Local Voice Engine**: 
    - **Speech-to-Text**: Local Whisper "tiny" model for high-accuracy transcription.
    - **Text-to-Speech**: Edge-TTS for neural-quality voice output.
- **Hardware Optimized**: Specialized support for external microphones like the **RØDE VideoMic GO II**.
- **Interactive Rebuttals**: Engage in philosophical disputes with a Robert Hooke agent.

## Project Structure

- `data/`: Source documents for the vector store.
- `agent.py`: Core logic for Newton/Hooke personas and simulation code generation.
- `app.py`: Streamlit-based web interface with persistent chat and simulation handling.
- `voice_engine.py`: Handles local transcription (Whisper) and speech synthesis (Edge-TTS).
- `create_vector_db.py`: Script to build the Chroma vector database.
- `requirements.txt`: Project dependencies.

## Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd digitalTwin
   ```

2. **Set up the environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **System Dependencies (Linux)**:
   Ensure you have PortAudio and ffmpeg installed for voice features:
   ```bash
   sudo apt-get install libportaudio2 libasound2-dev ffmpeg
   ```

4. **Configure API Keys**:
   Create a `.env` file in the root directory:
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## Usage

### 1. Initialize Knowledge Base
Build the vector store from the historical texts in the `data/` folder:
```bash
python create_vector_db.py
```

### 2. Run the Application
Launch the Streamlit interface:
```bash
streamlit run app.py
```

## Scientific Simulations
To see an illustration, ask Newton specific questions:
- "Explain gravity with an illustration."
- "Show me how a prism works."
- "What happens in orbital mechanics?"

## Requirements
- Python 3.10+
- Google Gemini API Key
- Desktop environment (required for Pygame windows)
