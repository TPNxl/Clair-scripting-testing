import os
from openai import OpenAI

API_KEY='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')
import sys

# Folder for system prompt .txt files
SYSTEM_PROMPTS_FOLDER = "./prompts"
MODEL_NAME = "gpt-4o-mini"

class ChatSystem:
    def __init__(self,
                 folder_path: str = SYSTEM_PROMPTS_FOLDER,
                 default_system_prompts: list[str] = ["None"],
                 model_name: str = MODEL_NAME,
                 api_key: str = API_KEY,
                 temperature: float = 0.7,
                ):
        """
        Config bits
        """
        self.MODEL_NAME = model_name
        self.client = OpenAI(api_key=api_key)
        self.temperature = temperature

        """
        Chat history
        """
        self.chat_history = []
        self.default_system_prompts = default_system_prompts

        """
        Get system messages and store them as a dictionary
        """
        self.system_message_dict = {}
        if not os.path.exists(folder_path):
            print(f"Warning: System prompts folder '{folder_path}' not found.")

        for filename in sorted(os.listdir(folder_path)):  # Sort for consistency
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        self.system_message_dict[filename[:-4]] = content

    def get_system_messages(self, keys=None):
        keys = keys or self.default_system_prompts
        messages = []
        messages.append({"role": "system", "content": self.system_message_dict[k]} for k in keys)
        return messages

    def stream_chat_completion(self, messages, model=MODEL_NAME) -> str:
        """
        Calls OpenAI ChatCompletion API and streams the response in real-time.
        """
        try:
            response = self.client.chat.completions.create(model=model,
            messages=messages,
            temperature=self.temperature,
            stream=True)

            full_response = []  # To collect response tokens
            for chunk in response:
                text = chunk.choices[0].delta.content
                if text is not None:
                    print(text, end="", flush=True)  # Print response in real-time
                    full_response.append(text)

            print()  # Line break after completion
            return "".join(full_response)  # Return full assistant message
        except Exception as e:
            print(f"\n[Error] OpenAI API call failed: {e}")
            print(f"Last chunk processed: {chunk}")
            return ""
    
    def chat(self, user_input, llm_instruction, append_system_instructions=True):
        """
        Chat with the AI model, getting a specific response
        """
        messages = []
        if append_system_instructions:
            messages.extend(self.get_system_messages())
        messages.extend(self.chat_history)
        messages.append({"role": "user", "content": user_input})
        if llm_instruction:
            messages.append({"role": "system", "content": llm_instruction})
        response = self.stream_chat_completion(messages)
        self.chat_history.append({"role": "assistant", "content": response})

    def add_system_message_to_chat(self, key=None, message=None):
        assert not (key is None and message is None), "Either key or message must be provided."
        if message:
            self.chat_history.append({"role": "system", "content": message})
        elif key:
            self.chat_history.append({"role": "system", "content": self.system_message_dict[key]})
        else:
            raise ValueError("Either key or message must be provided.")
        
    def main(self):


def main():
    # CLear the terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f"=== Terminal GPT Chat, using the model {MODEL_NAME} ===")

    # Load all system prompts
    system_prompts = load_system_prompts(SYSTEM_PROMPTS_FOLDER)

    # Initialize conversation history with system prompts
    conversation_history = list(system_prompts)

    print("Enter your message. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"] or user_input == "":
                print("Exiting chat.")
                break

            # Add user message to conversation history
            conversation_history.append({"role": "user", "content": user_input})

            print("Assistant: ", end="", flush=True)

            # Stream response and store it
            assistant_message = stream_chat_completion(conversation_history)
            if assistant_message:
                conversation_history.append({"role": "assistant", "content": assistant_message})

        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat.")
            exit()
    
    reset = True if input("Do you want to reset the terminal? (y/n, default y): ").strip().lower() != "n" else False
    if reset:
        main()

if __name__ == "__main__":
    main()