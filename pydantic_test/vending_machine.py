from __future__ import annotations

from dataclasses import dataclass

from rich.prompt import Prompt

from pydantic_graph import BaseNode, End, Graph, GraphRunContext

import asyncio
import logfire
from time import sleep

from IPython.display import Image


@dataclass
class MachineState:  
    user_balance: float = 0.0
    product: str | None = None


@dataclass
class InsertCoin(BaseNode[MachineState]):  
    async def run(self, ctx: GraphRunContext[MachineState]) -> CoinsInserted:  
        return CoinsInserted(float(Prompt.ask('Insert coins ($)')))  


@dataclass
class CoinsInserted(BaseNode[MachineState]):
    amount: float  

    async def run(
        self, ctx: GraphRunContext[MachineState]
    ) -> InsertCoin | ListProducts | Purchase:  
        if self.amount <= 0:  
            print('Invalid amount, try again')
            return InsertCoin()
        ctx.state.user_balance += self.amount  
        if ctx.state.product is not None:  
            return Purchase(ctx.state.product)
        else:
            return ListProducts()
        
@dataclass
class ListProducts(BaseNode[MachineState]):
    async def run(self, ctx: GraphRunContext[MachineState]) -> SelectProduct:
        # List products with prices, as well as current balance
        print(f"\n%20ls | Price" % 'Product')
        print(f"{'-' * 21}|------")
        print("".join([f"{"%20s" % k} | ${v:0.2f}\n" for k, v in PRODUCT_PRICES.items()]))
        print(f'Current balance: ${ctx.state.user_balance:0.2f}')
        return SelectProduct()


@dataclass
class SelectProduct(BaseNode[MachineState]):
    async def run(self, ctx: GraphRunContext[MachineState]) -> Purchase:
        return Purchase(Prompt.ask('Select product'))


PRODUCT_PRICES = {  
    'water': 1.25,
    'soda': 1.50,
    'crisps': 1.75,
    'chocolate': 2.00,
}


@dataclass
class Purchase(BaseNode[MachineState, None, None]):  
    product: str

    async def run(
        self, ctx: GraphRunContext[MachineState]
    ) -> End | InsertCoin | SelectProduct:
        if self.product == "":
            return End(None)
        if price := PRODUCT_PRICES.get(self.product):  
            ctx.state.product = self.product  
            if ctx.state.user_balance >= price:  
                ctx.state.user_balance -= price
                return End(None)
            else:
                diff = price - ctx.state.user_balance
                print(f'Not enough money for {self.product}, need {diff:0.2f} more')
                #> Not enough money for crisps, need 0.75 more
                return InsertCoin()  
        else:
            print(f'No such product: {self.product}, try again')
            return SelectProduct()  


vending_machine_graph = Graph(  
    nodes=[InsertCoin, CoinsInserted, ListProducts, SelectProduct, Purchase]
)


async def main():
    open("vending_machine.png", "wb").write(Image(vending_machine_graph.mermaid_image(start_node=InsertCoin)).data)
    print("--------------- Code -------------------")
    print(vending_machine_graph.mermaid_code(start_node=InsertCoin))
    print("----------------------------------------\n")
    state = MachineState()  
    await vending_machine_graph.run(InsertCoin(), state=state)  
    if state.product:
        print(f'Purchase successful!\nYou purchased {state.product}.')
    print(f"Your change is ${state.user_balance:0.2f}")

if __name__ == "__main__":
    logfire.configure()
    sleep(0.2)
    asyncio.run(main())