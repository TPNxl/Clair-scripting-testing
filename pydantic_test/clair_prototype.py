'''
This is a prototype of Clair, a snarky AI assistant that uses PydanticAI and PydanticGraph to build a chatbot.

Clair's goals:
- Help the user overcome their social fears by shit-testing them in a way that feels real
- Provide structured guidance as needed, with a focus on practicum instead of ignorance or theory

Basic flow: We are prototyping this interaction like Clair is going on a first date with the user - out of simplicity.
0. Describe who the user is
1a. Offer a choice of scenarios from {workplace interaction, professional presentation, first date}
1b. Select the difficulty level
1c. Check scenario_generate.txt for more info
2. Generate the scenario - setting, purpose, shared interests
3. Generate a character on the backend - personality, interests, etc., but store this in a state and don't reveal to the user
4. Enter the interaction. Set the scene for the user
5. Building rapport mode - talking about shared topics to build rapport with the user
6. Sparring mode - enter CoT evaluation. Check clair_response_cot.txt for more info
    - **Assess the difficulty level of the interaction.**  
    - **Detect signs of avoidance.**  
    - **Evaluate emotional state.**  
    - **Determine engagement vs. resistance.**  
    - **Identify what would make the interaction feel real.**  
5/6b. During either building rapport or sparring mode, Clair can access the following tools:
    - **Generate a description of concepts/explain the interaction.**
    - **Provide examples of how to respond.**
    - **Generate an emotional story.**
    - **Peel back the curtain and simulate the character's perspective - what they would say behind the user's back.**
7. Once the interaction is over, provide feedback and guidance
8. Offer to save the important parts of the interaction as a transcript in memory

We will use a PydanticGraph to represent the state of the interaction.
'''

from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits
from pydantic_graph import BaseNode, End, Graph, GraphRunContext
from dataclasses import dataclass
import asyncio
from time import sleep
from IPython.display import Image
import logfire

# Define the state (classes)

@dataclass
class InteractionState:
    scenario: str
    character: str
    difficulty: int
    history: list
    last_interaction_state: str
    last_evaluation: dict

    def __init__(self):
       pass


# Define agents
# Use the frontend_agent for Clair's responses and the brain for Clair's thinking
# The receptionist agent will be the starting agent, but with no tools added
# The frontend agent will be the one that the user interacts with - more expensive and nuanced
# The brain agent will be the one that Clair interacts with - cheaper to run (so can do CoT processing cheaply)
# Characters is a dictionary that stores the characters (and their agent objects) that Clair has generated

frontend_agent = Agent(
    'openai:chatgpt-4o-latest',
    system_prompt=""
)
brain_agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt=""
)
characters: dict = {}

# Define the graph classes - let's define all the nodes in the graph first and then move forward
# Define the graph classes in proper dependency order

@dataclass
class SaveTranscript(BaseNode[InteractionState]):
    # This class will save the important parts of the interaction as a transcript in memory
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> End[None]:
        last_interaction_state = ctx.state.last_interaction_state
        return End(None)

@dataclass
class PostFeedback(BaseNode[InteractionState]):
    # This class will provide feedback to the user
    # It should evaluate the user's performance and provide guidance
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> SaveTranscript:
        last_interaction_state = ctx.state.last_interaction_state
        return SaveTranscript()

@dataclass
class SparringMode(BaseNode[InteractionState]):
    # This class will enter sparring mode with the user
    # It should evaluate the user's responses and provide feedback
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> PostFeedback:
        ctx.state.last_interaction_state = "SparringMode"
        return PostFeedback()

@dataclass
class BuildingRapport(BaseNode[InteractionState]):
    # This class will build rapport with the user
    # It should talk about shared interests and topics
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> SparringMode:
        ctx.state.last_interaction_state = "BuildingRapport"
        return SparringMode()

@dataclass
class SetScene(BaseNode[InteractionState]):
    # This class will set the scene for the user
    # It should describe the setting and the purpose of the interaction
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> BuildingRapport:
        return BuildingRapport()

@dataclass
class GenerateCharacter(BaseNode[InteractionState]):
    # This class will generate a character for the user
    # It should generate a character with a personality and interests
    # It should also generate an agent for the character
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> SetScene:
        return SetScene()

@dataclass
class GenerateScenario(BaseNode[InteractionState]):
    # This class will generate the scenario for the user
    # It should already be mostly generated from the ScenarioGenerate node or the ScenarioChoice node
    # But this should fill in any details that are missing
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> GenerateCharacter:
        return GenerateCharacter()

@dataclass
class DifficultyChoice(BaseNode[InteractionState]):
    # This class will offer the user a choice of difficulty levels
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> GenerateScenario:
        return GenerateScenario()

@dataclass
class ScenarioGenerate(BaseNode[InteractionState]):
    # This class will generate a scenario for the user
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> DifficultyChoice:
        return DifficultyChoice()

@dataclass
class ScenarioChoice(BaseNode[InteractionState]):
    # This class will offer the user a choice of scenarios to choose from
    # Or the user can generate a scenario
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> DifficultyChoice | ScenarioGenerate:
        return DifficultyChoice()

@dataclass
class Welcome(BaseNode):
    # This class will introduce Clair to the user and describe who Clair is
    async def run(
            self, ctx: GraphRunContext[InteractionState]
        ) -> ScenarioChoice:
        return ScenarioChoice()

# Define tools and helper functions after the nodes to avoid reference issues
@frontend_agent.tool
async def GeneratePossibleResponses(ctx: RunContext[InteractionState]) -> str:
    # This tool will generate possible responses for the user
    # It should provide examples of how to respond
    return "This is a possible response."

@frontend_agent.tool
async def PeelBackCurtain(ctx: RunContext[InteractionState]) -> str:
    # This tool will simulate the character's perspective
    # It should show what the character would say behind the user's back
    return "This is what the character would say behind your back."

@frontend_agent.tool
async def TeachMode(ctx: RunContext[InteractionState]) -> str:
    # This class will provide guidance to the user
    # It should explain the interaction and provide examples
    return "This is an explanation of the interaction."

@frontend_agent.tool
async def EmotionalStory(ctx: RunContext[InteractionState]) -> str:
    # This class will generate an emotional story
    return "This is an emotional story."

@frontend_agent.tool
async def EvaluateInteraction(ctx: RunContext[InteractionState]) -> str:
    # This class will evaluate the user's performance using the brain agent. It's only called as a tool where necessary to save latency.
    # If the evaluate_interaction tool is not called, the brain agent will evaluate the user's performance in the background
    evaluate(ctx)
    return evaluation_to_string(ctx.state.last_evaluation)

def evaluation_to_string(evaluation: dict) -> str:
    # This function will convert the evaluation to a string
    return "This is the evaluation of your performance."

async def queue_evaluation(ctx: RunContext[InteractionState]):
    # This class will queue the evaluation of the user's performance using the brain agent
    # It should be called in the background to save latency
    pass

async def evaluate(ctx: RunContext[InteractionState]):
    # This class will evaluate the user's performance using the brain agent
    # It should be called in the background to save latency
    pass

# Compile the graph
graph = Graph(nodes=(Welcome, 
                     ScenarioChoice, 
                     ScenarioGenerate, 
                     DifficultyChoice, 
                     GenerateScenario, 
                     GenerateCharacter, 
                     SetScene, 
                     BuildingRapport, 
                     SparringMode, 
                     PostFeedback, 
                     SaveTranscript))
    
async def main():
    # Save graph to file
    open("clair_graph.png", "wb").write(Image(graph.mermaid_image(start_node=Welcome)).data)
    # Make the graph
    print("--------------- Code -------------------")
    print(graph.mermaid_code(start_node=Welcome))
    print("----------------------------------------\n")
    # Run the graph
    await graph.run(Welcome(), state=InteractionState())


if __name__ == "__main__":
    logfire.configure()
    sleep(0.2)
    asyncio.run(main())