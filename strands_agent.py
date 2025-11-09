import os
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import StdioServerParameters, stdio_client
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SlidingWindowConversationManager

CLAUDE_MODEL = 'anthropic.claude-3-5-sonnet-20240620-v1:0' 
AWS_REGION = 'us-east-1' 

monday_mcp_server_params = StdioServerParameters(
    command="npx",
    args=["@mondaydotcomorg/monday-api-mcp", 
    "-t", 
    "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjU4MTU4NzE5NywiYWFpIjoxMSwidWlkIjo5NTQ1NTk4NSwiaWFkIjoiMjAyNS0xMS0wM1QxMToxODowOS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MzIzMDAwOTgsInJnbiI6ImV1YzEifQ.mDdNq4AM1smDxObtuHQJ3DMat3aCReeAyrJ0L7q4HYQ",
    "--enable-dynamic-api-tools",
    "true"],
    env={"monday_token": os.getenv("monday_token")}
)
session_manager = FileSessionManager(session_id="test-session")
monday_mcp_client = MCPClient(lambda: stdio_client(monday_mcp_server_params))

def run_monday_agent(user_query: str):
    """
    Initializes and runs the Strands Agent.
    """
    print(f"--- Running Agent with Query: '{user_query}' ---")

    token = os.getenv("monday_token")
    
    # NEW DIAGNOSTIC CHECK
    # if token:
    #     print(f"DIAGNOSTIC: Monday token successfully read by Python. Length: {len(token)}")
    # else:
    #     print("DIAGNOSTIC: Monday token is empty/None in Python environment.")
    # # END NEW DIAGNOSTIC CHECK
    
    # # Critical Check: Ensure setup is complete
    # if not token:
    #     print("FATAL ERROR: The 'monday_token' environment variable is not set.", file=sys.stderr)
    #     sys.exit(1)
    
  
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
            model=CLAUDE_MODEL,
            conversation_manager=conversation_manager,
            session_manager=session_manager,
            # region_name=AWS_REGION,
            tools=tools,
            system_prompt=system_prompt,
            # Setting verbose to True helps debug tool usage
            # verbose=True 
        )

        result = agent(user_query)
        
        print("\n--- Agent Final Response ---")
        print(agent.messages)

if __name__ == "__main__":
    if not os.getenv("monday_token"):
        print("ERROR: The 'monday_token' environment variable is not set.")
        print("Please set it in your terminal before running the script (see Step 1).")
    else:
        BOARD_ID = 5076840920
        
        query = f"Delete the board called November Sprint."
        
        run_monday_agent(query)

        # query_2 = "On the board 'Start from scratch' change the status of the item called Item 1 to done ."
        # run_monday_agent(query_2)
