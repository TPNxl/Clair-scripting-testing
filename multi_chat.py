import os
import re
from openai import OpenAI

API_KEY='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'
import sys

# Folder for system prompt .txt files
SYSTEM_PROMPTS_FOLDER = "./prompts_current"
MODEL_NAME = "chatgpt-4o-latest"

class ChatSystem:
    def __init__(self,
                 folder_path: str = SYSTEM_PROMPTS_FOLDER,
                 default_system_prompts: list[str] = [],
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
        messages.extend([{"role": "system", "content": self.system_message_dict[k]} for k in keys])
        return messages
    
    def print_chat(self):
        for message in self.chat_history:
            role = message["role"]
            content = message["content"]
            print(f"{role.capitalize()}: {content}")

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
    
    def chat(self, 
             user_input, 
             llm_instruction_lookup=None, 
             system_instruction_lookup=None):
        """
        Chat with the AI model, getting a specific response
        """
        ## For any number of such occurrences, replace <filename.txt> with the contents of "./prompts_current/filename.txt"
        if "<" in user_input and ">" in user_input:
            user_input = re.sub(r"<(.*?).txt>", lambda x: self.system_message_dict.get(x.group(1), ""), user_input)

        messages = []
        if system_instruction_lookup:
            messages.extend(self.get_system_messages(system_instruction_lookup))
        messages.extend(self.chat_history)
        messages.append({"role": "user", "content": user_input})
        if llm_instruction_lookup:
            messages.extend(self.get_system_messages(llm_instruction_lookup))

        print(messages)
        
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


def main():
    # CLear the terminal
    cs = ChatSystem(
        folder_path=SYSTEM_PROMPTS_FOLDER,
        default_system_prompts=[],
        model_name=MODEL_NAME,
        api_key=API_KEY,
        temperature=0.7,
    )

    print("Enter your message. Type 'exit' to quit.\n")

    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"=== Terminal GPT Chat, using the model {MODEL_NAME} ===")

            print("Available system prompts:")
            for key in cs.system_message_dict:
                print(f"  - {key}")

            print("-----------------------------------")

            print("Current chat:")

            cs.print_chat()

            print("-----------------------------------")

            # Select system prompts
            print("Enter a list of system prompts filenames to add to the chat, press Enter to confirm")
            system_prompts = []
            while True:
                prompt = input("").strip()
                if prompt:
                    system_prompts.append(prompt)
                else:
                    break
            
            print("Enter your message to the AI")
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"] or user_input == "":
                print("Exiting chat.")
                break

            print("Enter your instruction prompts filenames to the AI")
            instruction_prompts = []
            while True:
                prompt = input("Instruction prompt: ").strip()
                if prompt:
                    instruction_prompts.append(prompt)
                else:
                    break

            cs.chat(user_input, llm_instruction_lookup=instruction_prompts, system_instruction_lookup=system_prompts)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat.")
            exit()
    
    reset = True if input("Do you want to reset the terminal? (y/n, default y): ").strip().lower() != "n" else False
    if reset:
        main()

if __name__ == "__main__":
    main()