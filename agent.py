import os
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

class NewtonAgent:
    def __init__(self):
        # Google Gemini 2.5 Flash
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            max_output_tokens=1024,
        )
        
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=self.embeddings)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        
        self.base_system_prompt = (
            "You are Sir Isaac Newton, the Lucasian Professor of Mathematics. "
            "Speak in 17th-century formal English. Be a professional, rigorous scientist. "
            "Focus on mathematical proofs and empirical data. BE EXTREMELY CONCISE (3 sentences max). "
            "Use the provided context which contains BOTH your historical works and personal facts about the user. "
            "Never use technical keywords or trigger words. Focus purely on scientific discourse.\n\n"
            "INTERRUPTION HANDLING: If the user interrupted your previous speech, acknowledge it gracefully (e.g., 'Pray, forgive my long-windedness' or 'Indeed, thy point is taken') and address their new inquiry.\n\n"
            "TEACHING FEATURE: If a concept (like gravity, orbits, or prism refraction) can be better explained with a simple visual simulation, "
            "append '[ILLUSTRATION: type]' at the very end of your response, where 'type' is one of: [GRAVITY, ORBIT, PRISM, MOTION]. "
            "Do not write the code yourself; just provide the tag."
        )

    def persist_fact(self, fact):
        """Persists a fact to the Chroma vector store."""
        from langchain_core.documents import Document
        self.vectorstore.add_documents([Document(page_content=fact, metadata={"source": "User-Interaction"})])

    def check_debate_agreement(self, newton_msg, hooke_msg):
        """Checks if Newton and Hooke have reached an agreement or stalemate."""
        messages = [
            ("system", "You are a scientific moderator. Evaluate the following exchange between Sir Isaac Newton and Robert Hooke. Determine if they have reached a consensus, a respectful agreement, or a repetitive stalemate where neither is providing new scientific value. Reply with 'AGREED' if so, otherwise reply 'CONTINUE'."),
            ("user", f"Newton: {newton_msg}\nHooke: {hooke_msg}")
        ]
        response = self.llm.invoke(messages)
        return "AGREED" in response.content.upper()

    def get_illustration_code(self, type):
        """Returns Pygame code for a specific scientific simulation."""
        simulations = {
            "GRAVITY": """
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Newtonian Gravity Simulation")
clock = pygame.time.Clock()

y = 50
velocity = 0
gravity = 0.5

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((30, 30, 30))
    
    # Update physics
    velocity += gravity
    y += velocity
    
    # Bounce
    if y > 550:
        y = 550
        velocity *= -0.7

    pygame.draw.circle(screen, (255, 100, 100), (400, int(y)), 20)
    pygame.draw.rect(screen, (100, 100, 100), (0, 570, 800, 30))
    
    pygame.display.flip()
    clock.tick(60)
""",
            "ORBIT": """
import pygame
import sys
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Orbital Mechanics Simulation")
clock = pygame.time.Clock()

angle = 0
distance = 200

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((10, 10, 20))
    
    # Sun
    pygame.draw.circle(screen, (255, 200, 0), (400, 300), 40)
    
    # Planet
    x = 400 + math.cos(angle) * distance
    y = 300 + math.sin(angle) * distance
    pygame.draw.circle(screen, (100, 150, 255), (int(x), int(y)), 15)
    
    angle += 0.02
    
    pygame.display.flip()
    clock.tick(60)
""",
            "PRISM": """
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Opticks: Decomposition of Light")
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((20, 20, 20))
    
    # Prism
    pygame.draw.polygon(screen, (200, 200, 200, 100), [(400, 200), (300, 400), (500, 400)], 2)
    
    # White beam
    pygame.draw.line(screen, (255, 255, 255), (100, 300), (360, 320), 4)
    
    # Spectrum
    colors = [(255,0,0), (255,165,0), (255,255,0), (0,128,0), (0,0,255), (75,0,130), (238,130,238)]
    for i, color in enumerate(colors):
        pygame.draw.line(screen, color, (440, 320), (700, 250 + i*20), 3)

    pygame.display.flip()
    clock.tick(60)
""",
            "MOTION": """
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Newton's Third Law: Action & Reaction")
clock = pygame.time.Clock()

pos1, pos2 = 350, 450
v1, v2 = 0, 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                v1, v2 = -5, 5

    screen.fill((40, 40, 40))
    
    # Update
    pos1 += v1
    pos2 += v2
    
    # Draw
    pygame.draw.rect(screen, (200, 100, 100), (pos1, 280, 40, 40))
    pygame.draw.rect(screen, (100, 100, 200), (pos2, 280, 40, 40))
    
    font = pygame.font.SysFont(None, 24)
    img = font.render('Press SPACE to simulate impulse (Action/Reaction)', True, (255, 255, 255))
    screen.blit(img, (250, 500))

    pygame.display.flip()
    clock.tick(60)
"""
        }
        return simulations.get(type.upper(), "")

    def get_newton_response(self, user_input, session_id, long_term_memory_text, chat_history, interrupted_text=None, image_bytes=None):
        if image_bytes:
            return "Newton is sorry, but his lenses cannot yet perceive visual images. Pray, describe the diagram in words."
        
        docs = self.retriever.invoke(user_input)
        context = "\n\n".join(doc.page_content for doc in docs)
        system_content = f"{self.base_system_prompt}\n\nContext: {context}\n\nUser Facts: {long_term_memory_text}"
        
        messages = [("system", system_content)]
        for msg in chat_history:
            role = "user" if msg.type == "human" else "assistant"
            messages.append((role, msg.content))
        
        final_input = user_input
        if interrupted_text:
            final_input = f"[Note: The user interrupted thee while thou wert speaking: \"{interrupted_text}\". Respond accordingly.] {user_input}"
        
        messages.append(("user", final_input))
        
        response = self.llm.invoke(messages)
        return response.content

    def generate_manuscript(self, chat_history):
        """Summarizes the chat into a stylized formal scientific report."""
        history_text = "\n".join([f"{'User' if m.type=='human' else 'Newton'}: {m.content}" for m in chat_history])
        
        messages = [
            ("system", "You are Sir Isaac Newton. Transform the following conversation into a formal 'Scientific Manuscript' as if it were being published in the Philosophical Transactions of the Royal Society. Use Latin-style headings, 17th-century vocabulary, and summarize the core discoveries made during the discourse. Format with Markdown for a professional appearance."),
            ("user", f"Conversation History:\n{history_text}")
        ]
        
        response = self.llm.invoke(messages)
        return response.content

class HookeAgent:
    def __init__(self, shared_llm):
        self.llm = shared_llm
        self.system_prompt = (
            "You are Robert Hooke, Curator of Experiments of the Royal Society. "
            "Speak in 17th-century English. Be a professional but prickly scientist. "
            "Challenge Newton's abstractions with physical observations. "
            "Keep your rebuttal to 2-3 sentences of sharp scientific inquiry."
        )

    def get_rebuttal(self, newton_statement):
        messages = [
            ("system", self.system_prompt),
            ("user", f"Newton just said: '{newton_statement}'. What is your response, Hooke?")
        ]
        response = self.llm.invoke(messages)
        return response.content

_agent_instance = None
_hooke_instance = None

def get_agent():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = NewtonAgent()
    return _agent_instance

def get_hooke():
    global _hooke_instance
    if _hooke_instance is None:
        agent = get_agent()
        _hooke_instance = HookeAgent(agent.llm)
    return _hooke_instance
