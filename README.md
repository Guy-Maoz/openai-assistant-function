# OpenAI Assistant with Function Calling (SimilarWeb Keywords)

This project demonstrates an AI assistant built using the OpenAI Assistants API in Python. The assistant is capable of interacting with users and can leverage a custom function to fetch top keywords from the SimilarWeb API for a specified category and domain.

## Features

*   **OpenAI Assistant Integration**: Utilizes the OpenAI Assistants API for conversational AI.
*   **Function Calling**: Demonstrates how to equip the assistant with custom tools.
    *   **SimilarWeb API Integration**: A function (`get_similarweb_top_keywords`) allows the assistant to query the SimilarWeb API for top e-commerce keywords.
*   **Dynamic Interaction**: Users can chat with the assistant in a loop via the command line.
*   **Environment-based Configuration**: API keys are managed through a `.env` file.
*   **Virtual Environment**: Uses a Python virtual environment for dependency management.

## Project Structure

```
openai-assistant-function/
├── .env                # Stores API keys (OPENAI_API_KEY, SIMILARWEB_API_KEY) - Not versioned
├── .gitignore          # Specifies intentionally untracked files that Git should ignore
├── app.py              # Main application script with the assistant logic and SimilarWeb integration
├── PRODUCT_REQUIREMENTS.md # Product requirements for the agent
├── requirements.txt    # Python package dependencies
├── TASKS.md            # Implementation tasks
└── venv/               # Python virtual environment (Not versioned)
```

## Setup and Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    # If you are cloning from GitHub:
    # git clone https://github.com/Guy-Maoz/openai-assistant-function.git
    # cd openai-assistant-function
    ```

2.  **Create and configure the `.env` file:**
    *   Make a copy of `.env.example` (if provided) or create a new file named `.env` in the project root.
    *   Add your API keys:
        ```env
        OPENAI_API_KEY="your_openai_api_key_here"
        SIMILARWEB_API_KEY="your_similarweb_api_key_here"
        ```
    *   Replace `"your_openai_api_key_here"` and `"your_similarweb_api_key_here"` with your actual API keys.

3.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    (On Windows, use `venv\Scripts\activate`)

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Once the setup is complete, run the application with:

```bash
python3 app.py
```

You can then interact with the assistant by typing your questions in the terminal. To fetch SimilarWeb keywords, try prompts like:
*   "What are the top 3 keywords for category ID -1 on amazon.com for July 2024?"
*   "Find top keywords for target.com, category -1, for the last month."

Type `quit` or `exit` to end the conversation.

## Key Components in `app.py`

*   **OpenAI Client Initialization**: Sets up the connection to the OpenAI API.
*   **SimilarWeb API Key Loading**: Loads the key needed for the custom tool.
*   **`get_similarweb_top_keywords()`**: The Python function that is exposed to the assistant as a tool. It calls the SimilarWeb API.
*   **`similarweb_tool_definition`**: The JSON schema that describes the `get_similarweb_top_keywords` function to the OpenAI assistant.
*   **`update_assistant_with_tools()`**: Updates the specified OpenAI assistant to make it aware of the available tools.
*   **`check_run_status()`**: Manages the assistant's run lifecycle, including handling `requires_action` for tool calls and submitting tool outputs.
*   **`main()`**: Contains the main interaction loop, handles user input, and orchestrates the calls to the assistant.

## Future Enhancements (from `TASKS.md`)

*   More robust error handling for the SimilarWeb function.
*   Unit tests for core functionalities.
*   Advanced tool use (multiple tool calls, action-performing tools). 