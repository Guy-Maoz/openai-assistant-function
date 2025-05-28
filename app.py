import os
import time
import json # Added for tool call argument parsing
import requests # Added for SimilarWeb API calls
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
# It's good practice to handle the case where the API key might be missing.
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in the .env file.")
client = OpenAI(api_key=api_key)

# SimilarWeb API Key
similarweb_api_key = os.getenv("SIMILARWEB_API_KEY")
if not similarweb_api_key:
    print("Warning: SIMILARWEB_API_KEY not found. Keyword functionality will be disabled.")

# --- Tool Definition for OpenAI Assistant ---

similarweb_tool_definition = {
    "type": "function",
    "function": {
        "name": "get_similarweb_top_keywords",
        "description": "Get top keywords for a specific category and domain from SimilarWeb. Useful for market research and understanding search trends related to e-commerce.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "The category to search keywords for. Often a numerical ID or a path-like string (e.g., \"All Categories\", \"/Electronics/Computers\"). Example: '-1' for all categories on some platforms."
                },
                "domain": {
                    "type": "string",
                    "description": "The domain name to analyze (e.g., amazon.com, ebay.com)."
                },
                "start_date": {
                    "type": "string",
                    "description": "The start date for the analysis period, in YYYY-MM format (e.g., \"2023-01\")."
                },
                "end_date": {
                    "type": "string",
                    "description": "The end date for the analysis period, in YYYY-MM format (e.g., \"2023-03\")."
                },
                "granularity": {
                    "type": "string",
                    "enum": ["Daily", "Weekly", "Monthly"],
                    "description": "The time granularity for the data. Defaults to Monthly."
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of keywords to return. Defaults to 10."
                }
            },
            "required": ["category", "domain", "start_date", "end_date"]
        }
    }
}

# --- Function Definitions for Assistant Tools ---

def get_similarweb_top_keywords(category: str, domain: str, start_date: str, end_date: str, granularity: str = "Monthly", limit: int = 10):
    """Fetches top keywords from SimilarWeb API for a given category, domain, and date range."""
    if not similarweb_api_key:
        print("Error: SimilarWeb API key not configured in the environment.")
        return json.dumps({"error": "SimilarWeb API key not configured by the system administrator."})

    base_url = "https://api.similarweb.com/v4/shopper/category-top-keywords"
    params = {
        "api_key": similarweb_api_key,
        "category": category,
        "domain": domain,
        "start_date": start_date, # Format YYYY-MM
        "end_date": end_date,     # Format YYYY-MM
        "granularity": granularity,
        "limit": limit,
        "format": "json"
    }
    print(f"Calling SimilarWeb API with params: {params}") # Log params (excluding api_key for security if sensitive)
    
    try:
        response = requests.get(base_url, params=params)
        print(f"SimilarWeb API raw response status: {response.status_code}")
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        
        data = response.json()
        print(f"SimilarWeb API JSON response snippet: {str(data)[:500]}...")

        if not data.get("data") and data.get("meta", {}).get("status") == "Success":
            # API call was successful but returned no specific keyword data (e.g., for a very niche query)
            print("SimilarWeb API returned success but no data items.")
            return json.dumps({"message": "The API query was successful but returned no keyword data for the specified parameters. This might indicate no significant keywords were found."})
        elif not data.get("data"):
            print(f"SimilarWeb API returned no data items. Full response: {data}")
            return json.dumps({"error": "API returned no keyword data.", "details": data})
            
        return data # Return the full JSON response dictionary for the assistant to process

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.reason}."
        details = {"status_code": http_err.response.status_code, "reason": http_err.response.reason}
        try:
            error_details_from_api = http_err.response.json()
            details["api_error"] = error_details_from_api
            print(f"SimilarWeb API HTTP error details: {error_details_from_api}")
        except json.JSONDecodeError:
            details["raw_response_text"] = http_err.response.text
            print(f"SimilarWeb API HTTP error (non-JSON response): {http_err.response.text}")
        print(f"Error calling SimilarWeb API: {error_message}")
        return json.dumps({"error": error_message, "details": details})
        
    except requests.exceptions.RequestException as req_err:
        print(f"Error calling SimilarWeb API (RequestException): {req_err}")
        return json.dumps({"error": f"A network request error occurred: {str(req_err)}"})
        
    except json.JSONDecodeError as json_err:
        print(f"Error decoding JSON from SimilarWeb API. Raw response: {response.text[:500]}... Error: {json_err}")
        return json.dumps({"error": "Invalid JSON response from SimilarWeb API. The API did not return valid JSON.", "details": {"raw_response_preview": response.text[:500]}})
    
    except Exception as e: # Catch-all for other unexpected errors
        print(f"An unexpected error occurred in get_similarweb_top_keywords: {e}")
        return json.dumps({"error": f"An unexpected error occurred while fetching data: {str(e)}"})

# --- OpenAI Assistant Core Functions (Modified where necessary) ---

def create_thread():
    """
    Creates a new conversation thread.
    """
    try:
        thread = client.beta.threads.create()
        print(f"Thread created with ID: {thread.id}")
        return thread
    except Exception as e:
        print(f"Error creating thread: {e}")
        return None

def add_message_to_thread(thread_id, content, role="user"):
    """
    Adds a message to a specific thread.
    """
    try:
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )
        print(f"Message added to thread {thread_id}.")
        return message
    except Exception as e:
        print(f"Error adding message to thread: {e}")
        return None

def run_assistant(thread_id, assistant_id, instructions="Please address the user's request."):
    """
    Runs the assistant on a specific thread.
    """
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=instructions
        )
        print(f"Run created with ID: {run.id} for thread {thread_id} with assistant {assistant_id}")
        return run
    except Exception as e:
        print(f"Error running assistant: {e}")
        return None

def check_run_status(thread_id, run_id, polling_interval=3):
    """ 
    Checks the status of a run, handles actions if required, and waits for completion.
    """
    try:
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            print(f"Run status: {run.status}")

            if run.status == "completed":
                return run
            elif run.status == "requires_action":
                if run.required_action and run.required_action.type == "submit_tool_outputs":
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []

                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        output = None

                        print(f"Assistant wants to call function: {function_name} with arguments: {arguments}")

                        if function_name == "get_similarweb_top_keywords":
                            # Ensure all required arguments are present, provide defaults from schema if applicable
                            # The schema already defines defaults for granularity and limit, but we get them from assistant
                            category_val = arguments.get("category")
                            domain_val = arguments.get("domain")
                            start_date_val = arguments.get("start_date")
                            end_date_val = arguments.get("end_date")
                            granularity_val = arguments.get("granularity", "Monthly") # Default from schema
                            limit_val = arguments.get("limit", 10) # Default from schema
                            
                            if not all([category_val, domain_val, start_date_val, end_date_val]):
                                output = json.dumps({"error": "Missing one or more required arguments: category, domain, start_date, end_date."})
                            else:
                                api_response = get_similarweb_top_keywords(
                                    category=category_val,
                                    domain=domain_val,
                                    start_date=start_date_val,
                                    end_date=end_date_val,
                                    granularity=granularity_val,
                                    limit=limit_val
                                )
                                # The API function already returns a JSON string or dict, ensure it's string for submission
                                if isinstance(api_response, dict):
                                    output = json.dumps(api_response)
                                else:
                                    output = api_response # Assuming it's already a JSON string
                        else:
                            print(f"Unknown function call: {function_name}")
                            output = json.dumps({"error": f"Function {function_name} not found."})
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": output
                        })
                    
                    # Submit tool outputs back to the assistant
                    try:
                        run = client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run_id,
                            tool_outputs=tool_outputs
                        )
                        print("Tool outputs submitted.")
                    except Exception as e:
                        print(f"Error submitting tool outputs: {e}")
                        return None # Or handle more gracefully
            elif run.status in ["queued", "in_progress"]:
                time.sleep(polling_interval)
            else: # failed, cancelled, expired
                print(f"Run ended with status: {run.status}")
                return None
    except Exception as e:
        print(f"Error checking run status: {e}")
        return None

def get_assistant_response(thread_id):
    """
    Retrieves the latest messages from the thread, filtering for assistant responses.
    """
    try:
        messages = client.beta.threads.messages.list(thread_id=thread_id, order="desc")
        # The API returns messages in descending order. The first assistant message is the latest response.
        for msg in messages.data:
            if msg.role == "assistant":
                # Assuming the response is in the first content block and is text.
                if msg.content and msg.content[0].type == "text":
                    return msg.content[0].text.value
        return "No assistant response found."
    except Exception as e:
        print(f"Error retrieving assistant response: {e}")
        return "Error fetching response."

def update_assistant_with_tools(assistant_id, tools_list):
    """Updates an existing assistant with new tools."""
    try:
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            tools=tools_list
        )
        print(f"Assistant {assistant_id} updated successfully with tools.")
        return assistant
    except Exception as e:
        print(f"Error updating assistant {assistant_id}: {e}")
        return None

def main():
    """
    Main function to demonstrate the OpenAI assistant interaction with function calling.
    Allows for continuous interaction until the user types 'quit' or 'exit'.
    """
    print("Starting AI Assistant interaction with function calling...")
    print("Type 'quit' or 'exit' to end the conversation.")

    assistant_id = "asst_djvGrAsDkIoftYlIVUKoBgTq" # Your existing assistant ID
    print(f"Using existing assistant with ID: {assistant_id}")

    # Update the assistant to be aware of the new tool
    # This only needs to be done once per assistant configuration change.
    # For simplicity in this script, it's done at the start.
    # In a production scenario, you might manage assistant versions or update them less frequently.
    print("Updating assistant with the latest tool definitions...")
    updated_assistant = update_assistant_with_tools(assistant_id, [similarweb_tool_definition])
    if not updated_assistant:
        print("Failed to update assistant with tools. Functionality might be limited. Exiting.")
        return
    print("Assistant updated.")

    thread = create_thread()
    if not thread:
        print("Exiting due to thread creation failure.")
        return
    print(f"New conversation started on Thread ID: {thread.id}")

    while True:
        try:
            user_question = input("\nYou: ")
        except EOFError:
            print("\nExiting conversation (EOF received).")
            break # Gracefully exit if input stream is closed (e.g. piping input)
        
        if user_question.lower() in ["quit", "exit"]:
            print("Exiting conversation.")
            break

        if not user_question.strip():
            print("No input received, please type a message or 'quit'/'exit'.")
            continue

        print(f"Adding message to thread {thread.id}...")
        if not add_message_to_thread(thread.id, user_question):
            print("Failed to add message. Please try again.")
            continue

        print(f"Running assistant {assistant_id} on thread {thread.id}...")
        run = run_assistant(thread.id, assistant_id,
                            instructions="Please use available tools if a user asks for keyword information. Address the user directly.")
        if not run:
            print("Failed to start assistant run. Please try again.")
            continue

        completed_run = check_run_status(thread.id, run.id)
        if not completed_run or completed_run.status != "completed":
            print("Assistant run did not complete successfully. Please try again or check logs.")
            # Potentially retrieve partial messages or more detailed error here if needed
            continue

        print("Retrieving assistant's response...")
        response = get_assistant_response(thread.id)
        print(f"\nAssistant: {response}")

    print("\nConversation finished.")

if __name__ == "__main__":
    main() 