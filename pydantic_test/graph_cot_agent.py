# This code is of a red agent and a blue agent debating about which color is better.
# This code has the following flow:
# 1. Blue agent says something.
# 2. Red agent responds.
# 3. Judge checks whether the debate is over.
# 4. If the debate is not over, repeat.

from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits
from pydantic_graph import BaseNode, End, Graph, GraphRunContext
from dataclasses import dataclass
import asyncio
from time import sleep
from IPython.display import Image
import logfire

red_agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt=(
        'You are the red agent. You must argue that red is the best color. '
        'You must return just a single sentence.'
    ),
)

blue_agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt=(
        'You are the blue agent. You must argue that blue is the best color. '
        'You must return just a single sentence.'
    ),
)

judge_agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt=(
        'You are the judge. You must decide whether the debate is over based on the previous messages.'
        'You must return either True or False.'
    ),
)

class JudgeChecks(BaseNode):
    pass

@dataclass
class RedAgentResponds(BaseNode):
    async def run(self, ctx: GraphRunContext) -> JudgeChecks:
        r = await red_agent.run("Red is the best color.")
        print("Red agent says:", r.data)
        return JudgeChecks()

@dataclass
class BlueAgentSays(BaseNode):
    async def run(self, ctx: GraphRunContext) -> RedAgentResponds:
        r = await blue_agent.run("Blue is the best color.")
        print("Blue agent says:", r.data)
        return RedAgentResponds()

@dataclass
class JudgeChecks(BaseNode):
    async def run(self, ctx: GraphRunContext) -> BlueAgentSays | End[bool]:
        r = await judge_agent.run("Is the debate over?")
        print("Judge says:", r.data)
        if r.data.lower() == "true":
            return End(True)
        else:
            return BlueAgentSays()

@dataclass
class StartNode(BaseNode[None, None, None]):
    async def run(self, ctx: GraphRunContext) -> BlueAgentSays:
        print("Welcome to the debate!")
        return BlueAgentSays()
        
debate_graph = Graph(nodes=[StartNode, BlueAgentSays, RedAgentResponds, JudgeChecks])

async def main():
    # Save graph to file
    open("debate_graph.png", "wb").write(Image(debate_graph.mermaid_image(start_node=StartNode)).data)
    # Make the graph
    print("--------------- Code -------------------")
    print(debate_graph.mermaid_code(start_node=StartNode))
    print("----------------------------------------\n")
    # Run the graph
    await debate_graph.run(StartNode())


if __name__ == "__main__":
    logfire.configure()
    sleep(0.2)
    asyncio.run(main())