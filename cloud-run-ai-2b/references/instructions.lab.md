---
id: cloud-run-adk-gemini-bq-mcp
summary: Learn how to build and deploy AI Agents with Gemini and BigQuery MCP server in Cloud Run
categories: Cloud Run, Gemini, ADK, BigQuery, MCP
tags: web
feedback_link: https://github.com/googlecodelabs/feedback/issues/new?title=[cloud-run-adk-gemini-bq-mcp]:&labels[]=content-platform&labels[]=cloud
analytics_account: UA-66226300-1
keywords: docType:Codelab,product:CloudRun

---

# Build and Deploy AI Agents with Gemini and BigQuery MCP server in Cloud Run

[Codelab Feedback](https://github.com/googlecodelabs/feedback/issues/new?title=[cloud-run-adk-gemini-bq-mcp]:&labels[]=content-platform&labels[]=cloud)

## Introduction

### What you'll learn

* How to create an AI Agent using
[Agent Development Kit (ADK)](https://adk.dev/)
with [Gemini in Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/start/get-started-with-gemini-3).
* How to give AI Agents access to structured data in BigQuery using
[BigQuery MCP server](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp).

**Cloud Run** is a fully managed, serverless compute platform
that lets you run containerized applications and services
without managing any underlying infrastructure.

**Agent Development Kit (ADK)** is an open-source agent development framework
that lets you build, debug, and deploy reliable AI agents at enterprise scale.

**BigQuery** is a fully managed, serverless enterprise data warehouse
that allows you store, query, and analyze massive datasets.

**Model Context Protocol (MCP)** standardizes how large language models (LLMs)
and AI applications or agents connect to external data sources.
MCP servers let you use their tools, resources, and prompts to take actions
and get updated data from their backend service.
**BigQuery MCP Server** gives your AI agents a direct, secure
way to analyze data in BigQuery.
This fully managed MCP server removes management overhead,
enabling you to focus on developing intelligent agents.

## Setup and Requirements

> aside positive
> This entire lab can be executed on the command line. You can use Cloud Shell
> (click the prompt icon at the top right of the console) to start the
> environment.

Start from setting default project and Cloud Run region:

```bash
# set the project
gcloud config set project YOUR_PROJECT_ID
```

Replace **YOUR_PROJECT_ID** with your Google Cloud Project Id.

```bash
# set Cloud Run region
gcloud config set run/region CLOUD-RUN-REGION
```

Replace **CLOUD-RUN-REGION** with one of the [regions supported
by Cloud Run](https://docs.cloud.google.com/run/docs/locations).

Here are environment variables that will be used throughout this codelab. You
can save these in an environment file and "source" it. Make sure to correctly
set the value of you project ID and optionally the region.

```bash
# Cloud Project Id and Cloud Run region
export GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project -q)}"
export GOOGLE_CLOUD_REGION="${GOOGLE_CLOUD_REGION:-$(CR_REGION=$(gcloud config get-value run/region -q 2>/dev/null); echo "${CR_REGION:-us-central1}")}"
# Gemini API in Agent Platform
export GOOGLE_GENAI_USE_ENTERPRISE="True" # Use Agent Platform
export GOOGLE_CLOUD_LOCATION="global" # Use global Gemini API endpoint
```

> aside positive
>
> **Note:** It's useful to save this snippet as a script file
and re-use it in the future, in cases when Cloud Shell session is reset.
Save it as `env.sh` and run `source env.sh` to set the environment variables
when running subsequent steps.
**Do not commit `env.sh` to version control systems.**

Enable APIs needed for this Codelab.
API changes may take 2-3 minutes to take effect.

```bash
gcloud services enable --project "${GOOGLE_CLOUD_PROJECT}" \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    bigquery.googleapis.com \
    aiplatform.googleapis.com
```

## Create a Data Agent using Agent Development Kit

### Write agent's code

From Cloud Shell Terminal or your local terminal,
create a root directory for your agentic app:

```bash
mkdir data_agent
```

Open Cloud Shell Editor or another text editor,
and create `agent.py` in `data_agent` directory:

```none
data_agent/
    agent.py
```

**agent.py**

```python
import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

import google.auth
from google.auth.transport.requests import Request

# Fetch Application Default Credentials (ADC)
# to use as agent's own identity for accessing BigQuery MCP Server
_application_default_credentials, project_id = google.auth.default()
_request = Request()
_application_default_credentials.refresh(_request)

# Retrieve Google Cloud project to use.
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", project_id)
if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set.")

# Builds authentication headers for MCP Server requests,
# and refreshes credentials if needed.
def _adc_auth_header_provider(context = None) -> dict[str, str]:
    if not _application_default_credentials.valid:
        _application_default_credentials.refresh(_request)

    return {
        "Authorization": f"Bearer {_application_default_credentials.token}",
        "x-goog-user-project": project_id
    }

# Initialize the MCP Toolset with the connection parameters
bigquery_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://bigquery.googleapis.com/mcp",
        tool_filter=[
            'get_dataset_info',
            'list_table_ids',
            'get_table_info',
            # Using readonly is a security measure to prevent accidental data modification.
            'execute_sql_readonly',
        ]
    ),
    header_provider=_adc_auth_header_provider # Auth header provider function
)

# Configure the agent

system_instruction = f"""
You are a helpful assistant that can answer questions about data in BigQuery.
To answer the user's question, use data you have access to by using tools `list_table_ids` and `get_table_info`.
Your data is in `bigquery-public-data.new_york_citibike` dataset (Citi Bike trips and stations in the NYC area.)

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
    model="gemini-3.6-flash",
    name="data_agent",
    instruction=system_instruction,
    description="A helpful assistant that can answer questions using NYC Citibike data.",
    tools=[bigquery_toolset]
)
```

ADK also requires `__init__.py` and `requirements.txt` for deployment:

* `__init__.py` must have an import for the agent.
* `requirements.txt` list Python dependencies:
`google-adk` for Agent Development Kit,
and `mcp` for Model Context Protocol client.

These commands help you create `__init__.py` and `requirements.txt`:

```bash
echo "from . import agent" > data_agent/__init__.py
echo -e "google-adk==2.4.*\nmcp==1.29.*" > data_agent/requirements.txt
```

The final folder structure should look like this:

```none
data_agent/
    __init__.py
    agent.py
    requirements.txt
```

### Try the agent locally

Agent Development Kit comes with `adk` CLI tool -
an interactive terminal interface for testing your agents.
This is useful for quick testing, scripted interactions, and CI/CD pipelines.
One of the features it provides is `adk web` -
[ADK Web Interface](https://adk.dev/runtime/web-interface/) -
a simple way to interactively develop and debug your agents.
ADK Web is not meant for use in production deployments,
but makes it very straightforward to try the agent.

> aside negative
>
> **Note:** Before running this command,
make sure your current directory has `data_agent` directory in it
(with `ls` command).

This command launches `adk web` that starts a local web server on port 8080.

```bash
uv tool run --with "mcp==1.29.*" --from "google-adk[mcp]==2.4.*" adk web --allow_origins="*" --port 8080 .
```

One the service started, open the local ADK Web page: http://localhost:8080/.

**If you are using Google Cloud Shell**, click Web Preview
![Web Preview](https://docs.cloud.google.com/static/shell/docs/images/web_preview.svg)
button, and select "Preview on port 8080" menu item.

In the ADK Web UI, ask the agent about data it has access to:

```text
What data do you have?
```

The agent will use BigQuery MCP tools to explore the citibike dataset.
It will give you an overview of available tables and fields
in the Citibike dataset.

## Deploy the agent to Cloud Run

This command will deploy the agent to Cloud Run using ADK CLI.

```bash
uv tool run --from google-adk==2.4.0 \
  adk deploy cloud_run \
      --with_ui \
      --project $GOOGLE_CLOUD_PROJECT \
      --region $GOOGLE_CLOUD_REGION \
      --service_name bq-data-agent \
      --app_name data_agent \
      data_agent \
      -- \
      --allow-unauthenticated \
      --max-instances 1 \
      --set-env-vars GOOGLE_GENAI_USE_ENTERPRISE=True,GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}"
```

### Try the agent

We used `--with_ui` option for our agent deployment.
It deployed the agent with
[ADK Web Interface](https://adk.dev/runtime/web-interface/).

1. Open the agent URL in the web browser.
`adk deploy` command returned it, and you can also retrieve the URL by running
`gcloud run services` command:

```bash
gcloud run services describe bq-data-agent \
  --project $GOOGLE_CLOUD_PROJECT \
  --region $GOOGLE_CLOUD_REGION \
  --format 'value(status.url)'
```

2. Ask the agent to reason on the available Citibike data:

```text
We have budget for 3 coffee trucks.
We want to find the best city bike stations to place our coffee trucks.
```

The agent should explore Citibike dataset using BigQuery MCP server,
run a few SQL queries, and return a list of 3 citibike stations.

## Congratulations!

Congratulations for completing the codelab!

We recommend reviewing the [Cloud Run](https://cloud.google.com/run)
documentation.

#### What we've covered

* How to create an AI Agent with Agent Development Kit and Gemini
* How to connect the agent to BigQuery MCP server.
* How to deploy the agent to Cloud Run.

## Clean up

To avoid incurring charges to your Google Cloud account for the resources used
in this tutorial,
you can either delete the project or delete the individual resources.

### Option 1: Delete the Service

**Delete the Cloud Run Service**

```bash
gcloud run services delete bq-data-agent \
      --project "${GOOGLE_CLOUD_PROJECT}" \
      --region "${GOOGLE_CLOUD_REGION}" \
      --quiet
```

### Option 2: Delete the Project

To delete the entire project, go to
[Manage Resources](https://console.cloud.google.com/cloud-resource-manager),
select the project you created in Step 2, and choose Delete. If you delete the
project, you'll need to change projects in your Cloud SDK. You can view the list
of all available projects by running `gcloud projects list`.
If you'd like to stick to the command line, you can also use this command:

```bash
gcloud projects delete ${GOOGLE_CLOUD_PROJECT}
```
