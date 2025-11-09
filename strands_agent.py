import os
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SlidingWindowConversationManager

MODEL_ID = 'AI Model ID' 

monday_mcp_server_params = StdioServerParameters(
    command="npx",
    args=["@mondaydotcomorg/monday-api-mcp", #the monday MCP
    "-t", 
    # -t prefix for your monday api token
    "Your Monday API token"
    # the token itself
    "--enable-dynamic-api-tools",
    # setting dynamic tools to true allows for all forms of API calls to be made, still in beta
    "true"]
)
session_manager = FileSessionManager(session_id="test-session") # initializes the agents session/context window
monday_mcp_client = MCPClient(lambda: stdio_client(monday_mcp_server_params))

def run_monday_agent(user_query: str):
    """
    Initializes and runs the Strands Agent.
    """
    print(f"--- Running Agent with Query: '{user_query}' ---")
    
    with monday_mcp_client:
        tools = monday_mcp_client.list_tools_sync()
        
        system_prompt = (
            "You are an expert Monday.com operations assistant. "
            "You must use the provided tools to interact with the Monday.com workspace. "
            "Be concise and clearly state the action you take."
        )
        conversation_manager = SlidingWindowConversationManager(
            window_size=10,  # Maximum number of message pairs to keep
        )
        agent = Agent(
            model=MODEL_ID,
            conversation_manager=conversation_manager,
            session_manager=session_manager,
            tools=tools,
            system_prompt=system_prompt,
            # Setting verbose to True helps debug tool usage
            # verbose=True 
        )

        result = agent(user_query)
        
        print("\n--- Agent Final Response ---")
        print(agent.messages)

if __name__ == "__main__":
    
    query = f"Delete the board called November Sprint."
    
    run_monday_agent(query)

    # query_2 = "On the board 'Start from scratch' change the status of the item called Item 1 to done ."
    # run_monday_agent(query_2)
