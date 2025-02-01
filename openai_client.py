import os
from openai import OpenAI

client = OpenAI(api_key='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')
import sys

# Folder for system prompt .txt files
SYSTEM_PROMPTS_FOLDER = "./prompts_old"
MODEL_NAME = "chatgpt-4o-latest"

def load_system_prompts(folder_path: str):
    """
    Reads all .txt files in the specified folder and returns a list of system messages.
    """
    system_messages = []
    if not os.path.exists(folder_path):
        print(f"Warning: System prompts folder '{folder_path}' not found.")
        return system_messages

    for filename in sorted(os.listdir(folder_path)):  # Sort for consistency
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    system_messages.append({"role": "system", "content": content})
                    print(f"Loaded system prompt from '{filename}'")

    return system_messages

def stream_chat_completion(messages, model=MODEL_NAME, temperature=0.7):
    """
    Calls OpenAI ChatCompletion API and streams the response in real-time.
    """
    try:
        response = client.chat.completions.create(model=model,
        messages=messages,
        temperature=temperature,
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