# Gets two magic numbers from two tools, adds them, and prints the result

from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits
import logfire
logfire.configure()

calculator_agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt=(
        'Use the `get_magic_number_1` and `get_magic_number_2` tool to get two magic numbers, then add them and return the result. '
        'You must return just a single number.'
    ),
)

@calculator_agent.tool
async def get_magic_number_1(ctx: RunContext[None]) -> int:
    return 42

@calculator_agent.tool
async def get_magic_number_2(ctx: RunContext[None]) -> int:
    return 100

result = calculator_agent.run_sync(
    'Add two magic numbers.',
    usage_limits=UsageLimits(request_limit=5, total_tokens_limit=2000),
)
print(result.data)
#> 142
print(result.usage())
print(result.all_messages())