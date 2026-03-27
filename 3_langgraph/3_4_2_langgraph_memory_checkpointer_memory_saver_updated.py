from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# 1. Define a proper State Schema
# The 'add' reducer is what allows the "Elephant" to remember and sum up.
class GameState(TypedDict):
    score: Annotated[int, add]
    points: int

# 2. Define the logic (Notice: we ONLY return the new points)
def add_points_node(state: GameState):
    p = state.get("points", 0)
    return {"score": p} # Reducer handles: total = existing_score + p

# 3. Build the Graph
builder = StateGraph(GameState)
builder.add_node("adder", add_points_node)
builder.add_edge(START, "adder")
builder.add_edge("adder", END)

# --- THE COMPARISON ---

# A. THE GOLDFISH (No Memory)
# It resets every single time because there is no checkpointer.
goldfish_app = builder.compile()

print("--- GOLDFISH (No Memory) ---")
r1 = goldfish_app.invoke({"score": 0, "points": 10})
print(f"Call 1 (Add 10): Total Score = {r1['score']}")

r2 = goldfish_app.invoke({"points": 5}) 
print(f"Call 2 (Add 5):  Total Score = {r2['score']} <- It forgot the 10!")


# B. THE ELEPHANT (With Memory)
# It uses the checkpointer to save state between calls.
memory = MemorySaver()
elephant_app = builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "player_1"}}

print("\n--- ELEPHANT (With Memory) ---")
# Call 1: Start with 0, add 10
r1 = elephant_app.invoke({"score": 0, "points": 10}, config=config)
print(f"Call 1 (Add 10): Total Score = {r1['score']}")

# Call 2: ONLY send the new points. 
# LangGraph retrieves the 10 from memory automatically.
r2 = elephant_app.invoke({"points": 5}, config=config)
print(f"Call 2 (Add 5):  Total Score = {r2['score']} <- It remembered and added!")