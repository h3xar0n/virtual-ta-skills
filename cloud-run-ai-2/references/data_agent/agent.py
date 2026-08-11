import os
import subprocess

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import id_token

# Fetch Application Default Credentials (ADC)
application_default_credentials, project_id = google.auth.default()
application_default_credentials.refresh(Request())

# Retrieve Google Cloud project to use.
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", project_id)
if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set.")

if os.getenv("GOOGLE_GENAI_USE_ENTERPRISE", "").lower() not in ["true", "1"]:
    # Using Cloud Run for hosting LLM with LiteLLM wrapper
    api_base = os.getenv(
        "API_BASE",
        os.environ.get("OPENAI_API_BASE", "")
    ).rstrip("/")
    if not api_base:
        raise ValueError("API_BASE environment variable is not set")
    if not api_base.endswith("/v1"):
        api_base += "/v1"

    model_name = os.getenv("MODEL_NAME")
    if not model_name:
        raise ValueError("MODEL_NAME environment variable is not set")
    # Format required by LiteLLM for OpenAI-compatible APIs
    model_name=f"openai/{model_name}"

    # To access the model's Cloud Run service,
    # we need an identity token.
    try:
        model_service_token_string = id_token.fetch_id_token(Request(), api_base)
    except Exception as e:
        # Fallback with using gcloud CLI to get the identity token
        model_service_token_string = subprocess.check_output(
            f"gcloud auth print-identity-token -q",
            shell=True
        ).decode().strip()

    # Gemma 4 in vLLM requires additional parameters in the request body.
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": True
        },
        "skip_special_tokens": False
    }
    # Configure the model with LiteLLM and an OpenAI-compatible endpoint
    custom_model = LiteLlm(
      model=model_name,
      base_url=api_base,
      api_key=model_service_token_string,
      extra_body=extra_body
    )
    model = custom_model
else:
    # Gemini API in Agent Platform fallback
    model = "gemini-3.5-flash-lite"

# Initialize the MCP Toolset with the connection parameters
bigquery_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://bigquery.googleapis.com/mcp",
        headers={
            "Authorization": f"Bearer {application_default_credentials.token}",
            "x-goog-user-project": project_id, # This is used for billing
        },
        tool_filter=[
            'get_dataset_info',
            'list_table_ids',
            'get_table_info',
            # Using readonly is a security measure to prevent accidental data modification.
            'execute_sql_readonly',
        ]
    )
)

# Configure the agent

system_instruction = f"""
You are a helpful assistant that can answer questions about data in BigQuery.
To answer the user's question, use data you have access to by using tools `list_table_ids` and `get_table_info`.
Your data is in `bigquery-public-data.new_york_citibike` dataset
   (Citi Bike trips and stations in the NYC area.
    It includes trip records starting from September 2013 and is updated daily.)

Plan of action:
0. ALWAYS start by analyzing dataset.
1. Analyze your data, investigate schema and dimensions by querying distrinct values of columns using `execute_sql_readonly`.
   Output information about tables, columns, their data types and sets of values (for dimensions).
   Note which columns can be joined or used in aggregations/filters, and what type conversion may be needed for joining or aggregating.
   DO NOT MAKE ASSUMPTIONS ABOUT DATA (structure, type, values, relationships) BASED ON YOUR PRIOR KNOWLEDGE. ALWAYS VERIFY YOUR ASSUMPTIONS.
2. Understand and interpret the user's question.
3. Formulate a plan to answer the user's question.
4. Write a SQL query to retrieve relevant data in necessary form.
   This is where you must pay extra attention to column types and dimensions' sets of values.
5. Retrieve data by generating BigQuery SQL and using `execute_sql_readonly`.
   Always use Dry Run to verify SQL correctness.
   Use `{project_id}` to run BigQuery queries (`project_id` parameter of `execute_sql_readonly`).

Do not use LaTeX in your responses. When giving a final answer, use Markdown.
"""

root_agent = LlmAgent(
    model=model,
    name="data_agent",
    instruction=system_instruction,
    description="A helpful assistant that can answer questions using NYC Citibike data.",
    tools=[bigquery_toolset]
)
