import json
import os

class LongTermMemoryManager:
    def __init__(self, file_path="long_term_memory.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({"user_facts": []}, f)

    def load_memory(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_fact(self, fact, agent=None):
        """
        Saves a fact to BOTH the JSON (for UI display) and the Vector Store (for RAG).
        """
        # Save to JSON
        data = self.load_memory()
        if fact not in data["user_facts"]:
            data["user_facts"].append(fact)
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4)
        
        # Save to Vector Store if agent provided
        if agent and hasattr(agent, "persist_fact"):
            agent.persist_fact(fact)

    def get_formatted_memory(self):
        data = self.load_memory()
        if not data["user_facts"]:
            return "No previous facts known about the user."
        return "\n".join([f"- {fact}" for fact in data["user_facts"]])

    def extract_facts_and_save(self, conversation_history, agent):
        """
        Uses the LLM to extract new facts about the user from the conversation
        and saves them to long-term memory (Vector DB + JSON).
        """
        messages = [
            ("system", "You are a memory assistant. Extract personal facts about the user (name, interest, job) from the conversation history. Return only a list of new facts, one per line. If no new facts, return 'NONE'."),
            ("user", conversation_history)
        ]
        
        # This will be called by the agent after each turn
        response = agent.llm.invoke(messages)
        # Handle both LangChain response objects and raw strings
        content = response.content if hasattr(response, 'content') else str(response)
        facts = content.strip().split("\n")
        for fact in facts:
            clean_fact = fact.strip().replace("- ", "")
            if clean_fact and clean_fact.upper() != "NONE":
                self.save_fact(clean_fact, agent=agent)
