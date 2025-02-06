import random
import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# ⚡ SET YOUR OPENAI API KEY (replace 'your-api-key' with your actual key)
os.environ['OPENAI_API_KEY'] = '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'

# ============================
# SIMULATED DATABASES
# ============================

# Scheduled Contacts Database (Step 1)
SCHEDULED_CONTACTS = {
    1: {"name": "Alice", "phone": "+123456789"},
    2: {"name": "Bob", "phone": "+987654321"},
}

# Features of Recipient Database (Step 2)
RECIPIENT_FEATURES = {
    1: {"personality": "friendly", "preferences": ["sports", "music"]},
    2: {"personality": "reserved", "preferences": ["reading", "tech"]},
}

# Corpus of Openers Database (Step 3)
CORPUS_OF_OPENERS = [
    "Hey there! How's it going?",
    "Hello! What's new today?",
    "Yo! Ready for some fun?",
]

# Conversation Database (to log sessions)
CONVERSATION_DB = {}

# ============================
# SIMULATED THIRD-PARTY SERVICE (Twilio)
# ============================

def send_message(recipient_phone, message):
    """
    Step 6 & 11: Sends the message.
    (In a real-world scenario, integrate with Twilio or another service here.)
    """
    print(f"🚀 [SENDING] To: {recipient_phone} | Message: {message}")
    # Imagine the message is actually sent here.
    return True

def receive_message():
    """
    Step 7: Simulates receiving a response from the recipient.
    (Replace with webhook integration or polling in production.)
    """
    response = input("💌 [INCOMING] Enter recipient's response: ")
    return response

# ============================
# LANGCHAIN & GPT API FUNCTIONS
# ============================

# Initialize the LLM from OpenAI via LangChain
llm = OpenAI(temperature=0.7)  # Adjust temperature for creativity vs. precision

def analyze_response(response_text):
    """
    Step 8: Analyze the recipient's response.
    Returns sentiment, conversation level, engagement score, feature assignment, and response options.
    """
    prompt = PromptTemplate(
        input_variables=["response_text"],
        template=(
            "You are a brutally honest, no-nonsense analyst. "
            "Analyze the following response and provide a detailed report including sentiment, "
            "conversation level, engagement score, feature assignment, and possible response options:\n\n"
            "{response_text}\n\n"
            "Be direct and ruthless—no sugarcoating."
        )
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    analysis = chain.run(response_text=response_text)
    return analysis

def generate_response(analysis):
    """
    Step 10: Generate the best reply based on analysis.
    Craft a response that is direct, witty, and forces progress.
    """
    prompt = PromptTemplate(
        input_variables=["analysis"],
        template=(
            "Based on the following analysis, craft a response that is as direct and brutal as it is engaging. "
            "Your reply should challenge the recipient, demand progress, and leave no room for slackers. "
            "Analysis:\n\n{analysis}\n\n"
            "Write your reply now:"
        )
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    reply = chain.run(analysis=analysis)
    return reply

# ============================
# CHATBOT FLOW FUNCTION
# ============================

def chatbot_flow():
    print("🔥 **Starting Chatbot Flow** 🔥\nLet's dominate this conversation—no excuses, no delays! 😈")

    # Step 1: Request Recipients
    print("👉 [Step 1] Looking up scheduled contacts... 😏")
    recipients = list(SCHEDULED_CONTACTS.keys())
    print(f"Found recipients: {recipients}")

    # Step 2: Select Recipient
    # (For this template, we pick the first recipient. Customize as needed.)
    selected_recipient_id = recipients[0]
    recipient_profile = RECIPIENT_FEATURES.get(selected_recipient_id, {})
    recipient_info = SCHEDULED_CONTACTS[selected_recipient_id]
    print(f"👉 [Step 2] Selected Recipient: {recipient_info['name']} with profile: {recipient_profile} 💅")

    # Step 3: Request Opener
    print("👉 [Step 3] Fetching an opener from the corpus... 😎")
    opener = random.choice(CORPUS_OF_OPENERS)
    print(f"Chosen opener: '{opener}'")

    # Step 4: Select Opener & Initialize Conversation Session
    conversation_id = f"conv_{selected_recipient_id}"
    CONVERSATION_DB[conversation_id] = {"recipient": recipient_info, "messages": []}
    print(f"👉 [Step 4] Conversation session '{conversation_id}' initialized. 📚")

    # Step 5: Edit Opener?
    edit_choice = input("Do you want to edit the opener? (Yes/No): ").strip().lower()
    if edit_choice == "yes":
        opener = input("Enter your edited opener: ").strip()
        print("👉 Edited opener saved! 💥")
    else:
        print("👉 No edits made—using default opener. Get over your hesitation! 💪")

    # Log the opener in the Conversation DB
    CONVERSATION_DB[conversation_id]["messages"].append({"role": "system", "content": opener})

    # Step 6: Send the Opener Message
    print("👉 [Step 6] Sending opener message... 🚀")
    send_message(recipient_info["phone"], opener)

    # RESPONSE PHASE

    # Step 7: Receive Recipient's Response
    print("👉 [Step 7] Waiting for recipient's response... ⏳")
    response_text = receive_message()
    print(f"👉 Received response: {response_text}")

    # Step 8: Analyze Response
    print("👉 [Step 8] Analyzing response... 🧐")
    analysis = analyze_response(response_text)
    print("\n=== Analysis ===")
    print(analysis)
    print("================\n")

    # Step 9: Edit Analysis or Response?
    edit_analysis_choice = input("Do you want to edit the analysis? (Yes/No): ").strip().lower()
    if edit_analysis_choice == "yes":
        analysis = input("Enter your edited analysis: ").strip()
        print("👉 Analysis updated! 💣")
    else:
        print("👉 Analysis accepted as is. No mercy for half-assed inputs! 🔥")

    # Step 10: Select/Generate Response
    print("👉 [Step 10] Generating reply based on analysis... 🤖")
    reply = generate_response(analysis)
    print(f"\nGenerated Reply: {reply}\n")

    # Step 11: Send the Reply
    print("👉 [Step 11] Sending reply to recipient... 📤")
    send_message(recipient_info["phone"], reply)

    # Log the reply in the Conversation DB
    CONVERSATION_DB[conversation_id]["messages"].append({"role": "assistant", "content": reply})

    print("\n🔥 **Conversation Flow Completed!** 🔥")
    print("Remember: No flinching, no backing down. Now go out and conquer the next step! 💪🚀")
    # STOP WHEN DONE.

if __name__ == "__main__":
    chatbot_flow()
