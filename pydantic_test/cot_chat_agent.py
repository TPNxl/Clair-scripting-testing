# Basic CoT chat agent with tools

from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits
import logfire
logfire.configure()

chat_agent = Agent("openai:gpt-4o-mini",
                    system_prompt="You are an assistant. Respond to questions to the point and as they come. Use the `secret_word`, `tell_joke`, `number_rater`, 'respond_as_anna', and 'respond_as_bob' tools to interact with the user as needed. One sentence responses. Repeat/summarize what Anna/Bob say verbatim and do not add additional info or questions unless asked. They may have access to tools, so chain tool uses if needed.",
                    )

anna_agent = Agent("openai:gpt-4o-mini",
                   system_prompt="You are Anna, a 5-year old toddler who likes eating pies and vehemetly hates all other foods. You do not have access to the any tools."
)

bob_agent = Agent("openai:gpt-4o-mini",
                    system_prompt="You are Bob, a 80-year old who likes playing video games. Act like Santa. You can use the 'number_rater' tool to rate numbers and can use the 'collatz_conjecture' tool to run it on a number."
)

@chat_agent.tool
async def get_word(ctx: RunContext[None]) -> str:
    return "banana"

@chat_agent.tool
async def tell_joke(ctx: RunContext[None]) -> str:
    return "Why did the chicken cross the road? To get to the other side!"

@chat_agent.tool
@bob_agent.tool
async def number_rater(ctx: RunContext[None], number: int) -> str:
    if number < 5:
        return "That's a small number!"
    elif number < 10:
        return "That's a medium number!"
    else:
        return "That's a big number!"
    
@bob_agent.tool
async def collatz_conjecture(ctx: RunContext[None], number: int) -> int:
    steps = 0
    vals = []
    while True:
        vals.append(number)
        if number % 2 == 0:
            number = number // 2
        else:
            number = 3 * number + 1
        steps += 1
        r = await bob_agent.run(f"Is {number} 1? If yes, return True. If no, return False. Only respond with True or False.")
        if r.data.lower() == "true":
            break
    return "[".join(["%d, " for v in vals]) + f"]; took {steps} steps."

messages = []
    
@chat_agent.tool
async def respond_as_Anna(ctx: RunContext[None], message: str) -> str:
    r = await anna_agent.run(message, usage=ctx.usage)
    return r.data

@chat_agent.tool
async def respond_as_Bob(ctx: RunContext[None], message: str) -> str:
    r = await bob_agent.run(message, usage=ctx.usage)
    return r.data

while True:
    # Get user input
    user_input = input("You: ")
    if user_input == "exit":
        break
    # Run the agent
    result = chat_agent.run_sync(user_input, 
                                 usage_limits=UsageLimits(request_limit=5, total_tokens_limit=2000),
                                 message_history=messages)
    # Print the response
    print("Agent:", result.data)
    # Update the message history
    messages = result.all_messages()


