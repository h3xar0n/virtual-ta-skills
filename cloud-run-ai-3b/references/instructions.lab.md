---
id: cloud-run-instances-coffee-shop-assistant
summary: Learn how to run a personal agent on a Cloud Run instance
categories: cloudrun,cloudruninstances,adk
tags: web
feedback_link: https://github.com/googlecodelabs/feedback/issues/new?title=[cloud-run-instances-coffee-shop-assistant]:&labels[]=content-platform&labels[]=cloud
analytics_account: UA-66226300-1
keywords: docType:Codelab,product:CloudRun

---

# Run a personal agent (coffee shop assistant) on a Cloud Run instance

[Codelab Feedback](https://github.com/googlecodelabs/feedback/issues/new?title=[cloud-run-instances-coffee-shop-assistant]:&labels[]=content-platform&labels[]=cloud)

## Introduction

> aside positive
>
> **Note:** The [Cloud Run sandboxes](https://cloud.google.com/blog/topics/developers-practitioners/google-cloud-run-sandboxes-are-in-public-preview) and [Cloud Run instances](https://cloud.google.com/blog/products/serverless/introducing-cloud-run-instances) offerings are subject to the "Pre-GA Offerings Terms" in the General Service Terms section of the [Service Specific Terms](https://docs.cloud.google.com/terms/service-terms#1). Pre-GA features are available "as is" and might have limited support. For more information, [see the launch stage descriptions](https://cloud.google.com/products/#product-launch-stages)

### Overview

In this codelab, you will build a personal AI assistant that helps you analyze business data and perform other tasks through a chat UI. You will use a [Cloud Run instance](https://cloud.google.com/blog/topics/developers-practitioners/google-cloud-run-sandboxes-are-in-public-preview) to host your personal agent.

Your agent will use [Cloud Run sandboxes](https://cloud.google.com/blog/topics/developers-practitioners/google-cloud-run-sandboxes-are-in-public-preview). Cloud Run sandboxes are a native, secure, and ultra-fast runtime environment built specifically for executing untrusted code and agent workloads, starting in milliseconds. The sandbox allows your AI Agent to dynamically write, run, and test code on the fly to solve complex analytical problems.

Note: To ensure a seamless development experience when running locally versus in production:

  * In Production (Cloud Run sandbox): The agent runs code securely inside an isolated, containerized playground via a dedicated sandbox binary (/usr/local/gcp/bin/sandbox).
  * Locally (Your Machine): When running locally, the app detects that the production sandbox environment isn't present (IS_LOCAL_MODE = True). The agent executes Python scripts and shell commands directly on your local host machine's system terminal.


### What you'll build:

In this scenario, you manage a coffee shop in a college town preparing for a massive graduation weekend. You need your agent to cross-reference raw Point-of-Sale (POS) data with the university's ceremony schedule to uncover hidden operational bottlenecks.

The agent uses a secure sandbox to write and execute Python scripts, analyzing drink complexity versus cashier headcount to recommend staffing and inventory adjustments.

The agent pings the owner via a mock chat UI with its targeted inventory and staffing recommendations. It waits for explicit permission before updating the spreadsheet with operational TODOs for the coffee shop manager.


### What you'll learn

* How to create a Cloud Run instance
* How to deploy an ADK agent on a Cloud Run instance
* How to have an agent run code in a sandbox within a Cloud Run instance
* How to create a chat UI using WebSockets to interact with the background agent


## Setup and Requirements

> aside positive
> This entire lab can be executed on the command line. You can use CloudShell
> (click the prompt icon at the top right of the console) to start the
> environment.

Set your project ID.

```shell
GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT_ID>
```

Set your region.

```shell
REGION=<YOUR_REGION>
```

Now configure Google Cloud to use that project ID and Cloud Run to use that region.

```shell
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud config set run/region $REGION
```

Here are environment variables that will be used throughout this codelab. You
can save these in an environment file and "source" it. Make sure to correctly
set the value of you project ID and optionally the region.

```shell
SA_NAME=coffee-shop-agent-sa
SERVICE_ACCOUNT_ADDRESS=$SA_NAME@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com
```

Enable APIs needed for this Codelab

```shell
gcloud services enable --project $GOOGLE_CLOUD_PROJECT \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    sheets.googleapis.com \
    aiplatform.googleapis.com
```

## Create Service Account & Spreadsheet

Creating a dedicated Service Account for your Cloud Run instance is recommended to grant only the required roles necessary.

### Create Service Account for Cloud Run instance

```shell
gcloud iam service-accounts create $SA_NAME \
  --description="Service account for the Coffee Shop Agent Codelab" \
  --display-name="Coffee Shop Agent SA"
```

Since the agent uses Gemini APIs (GOOGLE_GENAI_USE_VERTEXAI=1), grant this service account the Agent Platform User role on your project.

```shell
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
--member="serviceAccount:$SERVICE_ACCOUNT_ADDRESS" \
--role="roles/aiplatform.user"
```

To let you run and test the agent locally using this service account, grant your personal Google Cloud identity permission to impersonate this service account:

```shell
gcloud iam service-accounts add-iam-policy-binding \
coffee-shop-agent-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
--member="user:$(gcloud config get-value account)" \
--role="roles/iam.serviceAccountTokenCreator"
```


### Create the spreadsheet

This spreadsheet represents the sales that happened last year during graduation weekend.

1. Create a new Google Sheet in your Google Drive.

2. Copy the following Comma-Separated Values (CSV) into your new Google Sheet (e.g. select cell A1 and paste).

```shell
Day,Time,Drip_Coffee,Cold_Brew,Extra_Espresso,Alt_Milk_Oz,Pastries,Cashiers_Working,Wait_Time_Minutes
Saturday,07:00:00,95,15,5,30,80,2,9
Saturday,08:00:00,80,25,10,35,60,2,7
Saturday,09:00:00,30,30,20,40,20,1,4
Saturday,10:00:00,40,130,95,50,25,2,4
Saturday,11:00:00,25,45,25,40,15,1,5
Saturday,12:00:00,30,35,15,45,20,1,3
Saturday,13:00:00,15,20,10,30,10,1,2
Saturday,14:00:00,45,60,30,65,30,2,8
Saturday,15:00:00,20,30,15,35,15,1,3
Saturday,16:00:00,25,35,10,50,20,1,4
Saturday,17:00:00,10,20,5,35,10,1,2
Saturday,18:00:00,20,40,10,190,65,2,12
Saturday,19:00:00,10,15,5,40,15,1,2
Sunday,07:00:00,90,10,5,35,75,2,8
Sunday,08:00:00,75,20,10,40,65,2,6
Sunday,09:00:00,25,25,15,35,15,1,3
Sunday,10:00:00,60,35,15,60,50,2,7
Sunday,11:00:00,20,30,10,35,10,1,3
Sunday,12:00:00,25,40,10,55,20,1,3
Sunday,13:00:00,15,25,5,40,10,1,2
Sunday,14:00:00,30,50,15,180,60,2,11
Sunday,15:00:00,15,25,10,45,15,1,3
Sunday,16:00:00,20,45,20,40,15,1,4
Sunday,17:00:00,10,25,10,30,10,1,2
Sunday,18:00:00,25,145,110,45,20,2,16
Sunday,19:00:00,15,30,15,35,10,1,4
```

3. with your data still selected, click **Data > Split text to columns** in the Google Sheets top menu.


Make sure the service account has Editor access to the spreadsheet. This is similar to how you would give access to a teammate.

1. Copy the full email of your new service account

```Shell
echo $SERVICE_ACCOUNT_ADDRESS
```

2. From your Google Sheet, click Share in the top-right corner
3. Paste the service account email, set the permission to Editor, and click Share. (You can uncheck Notify).
4. Record the spreadsheet ID that you'll pass to your agent, e.g. https://docs.google.com/spreadsheets/d/<YOUR_SPREADSHEET_ID>/edit?gid=0#gid=0

```shell
SPREADSHEET_ID=<THE SPREADHSEET ID FROM ITS URL>
```


## Create the ADK Agent

First, create a directory for your code.

```shell
mkdir coffee-mgr-agent && cd coffee-mgr-agent
```

Create a `requirements.txt` file.

```shell
fastapi>=0.100.0
uvicorn>=0.22.0
google-adk>=1.27.1
google-auth
google-api-python-client
```

Create a `Dockerfile`

```shell
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Create a `main.py` file

```python
import os
import asyncio
import subprocess
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from google.adk.agents import LlmAgent as Agent
from google.adk.tools import FunctionTool
from google.adk.apps import App
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

SANDBOX_CLI = '/usr/local/gcp/bin/sandbox'
IS_LOCAL_MODE = not Path(SANDBOX_CLI).exists()

active_connections: list[WebSocket] = []

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

def run_sandbox_process(args: list[str]):
    cmd = args[2:] if IS_LOCAL_MODE and args[:2] == ['do', '--'] else ([SANDBOX_CLI] + args if not IS_LOCAL_MODE else args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10)

def execute_sandbox_command(command: str) -> str:
    """Executes arbitrary POSIX shell/bash commands inside sandbox."""
    mode = "LOCAL" if IS_LOCAL_MODE else "CLOUD RUN SANDBOX"
    print(f"[ADK Sandbox Tool] Starting {mode} shell run...")
    try:
        res = run_sandbox_process(['do', '--', '/bin/sh', '-c', command])
        if res.returncode != 0:
            return f"Execution Failed!\nExit Code: {res.returncode}\nStdout:\n{res.stdout}\nStderr:\n{res.stderr}"
        return res.stdout
    except Exception as err:
        return f"Internal Sandbox Tool Error: {str(err)}"

def get_sheets_service():
    """Initializes and returns the Google Sheets client service."""
    from google.auth import default
    from googleapiclient.discovery import build
    credentials, _ = default(scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/cloud-platform'
    ])
    return build('sheets', 'v4', credentials=credentials)

def read_spreadsheet_values(spreadsheet_id: str, range_name: str) -> str:
    """Reads a range of cells from a Google Spreadsheet."""
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        return str(rows) if rows else "No data found in the specified range."
    except Exception as e:
        return f"Read Error: {str(e)}"

def update_spreadsheet_values(spreadsheet_id: str, range_name: str, values: List[List[str]]) -> str:
    """Updates a range of cells in a Google Spreadsheet with the provided values."""
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption="USER_ENTERED", body={'values': values}).execute()
        return f"Successfully updated {result.get('updatedCells')} cells in {range_name}."
    except Exception as e:
        return f"Write Error: {str(e)}"

def create_spreadsheet_tab(spreadsheet_id: str, tab_name: str) -> str:
    """Creates a new sheet tab in a Google Spreadsheet if it doesn't already exist."""
    try:
        service = get_sheets_service()
        # Check if tab exists
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in spreadsheet.get('sheets', []):
            if sheet.get('properties', {}).get('title') == tab_name:
                return f"Sheet tab '{tab_name}' already exists."
        # Create tab
        body = {'requests': [{'addSheet': {'properties': {'title': tab_name}}}]}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        return f"Successfully created new sheet tab '{tab_name}'."
    except Exception as e:
        return f"Error creating sheet tab: {str(e)}"

# ==========================================
# ADK AGENT & RUNNER SETUP
# ==========================================

root_agent = Agent(
    name='secure_coding_assistant',
    description='ADK agent capable of executing shell commands and managing Google Spreadsheets.',
    model=os.environ.get('GEMINI_MODEL', 'gemini-3.1-flash-lite'),
    instruction=(
        f'You are an expert AI Business Analyst for a coffee shop during university graduation weekend.\n'
        f'The Google Spreadsheet ID you are managing is: "{SPREADSHEET_ID}". Use this ID for all sheet operations.\n'
        '1. Comparative Analysis Policy:\n'
        f'   - Ingest historical POS data from the "POS-2025" sheet tab using read_spreadsheet_values with spreadsheet_id="{SPREADSHEET_ID}".\n'
        '   - Receive the current graduation schedule directly from the manager\'s prompt (the manager will paste it and indicate it is the same schedule sequence as last year).\n'
        '   - Write a python3 script via the sandbox tool to:\n'
        '     a. Correlate the 2025 product spikes (Cold Brew, Alt Milk, Extra Espresso) with the specific ceremonies ending at those times.\n'
        '     b. Map those beverage profiles to the pasted schedule (which is the same sequence) to predict exactly when and where the 2026 spikes will occur.\n'
        '     c. Identify expected wait-time bottlenecks in 2026 based on the 2025 wait times for those same profiles.\n'
        '2. Bottleneck Diagnostics (Playbook):\n'
        '   - If a predicted high-volume slot in 2026 is expected to have Wait_Time_Minutes > 10:\n'
        '     - If Cashiers_Working < 2: Recommend scheduling another cashier.\n'
        '     - If Cashiers_Working == 2 and complex items (Cold Brew, Extra Espresso, Alt Milk) spike: Deduce that the bottleneck is barista output, not cashiers. Recommend adding a "Support Barista" role to handle fulfillment.\n'
        '3. Human-in-the-Loop Policy:\n'
        '   - Present your detailed data discoveries, wait-time bottlenecks, and actionable recommendations (stocking and staffing changes) to the manager.\n'
        '   - Highlight only two or three findings for specific ceremonies.\n'
        '   - Frame your recommendations as a clean list of suggested tasks for the manager\'s TODO list.\n'
        '   - Explicitly ask: "Would you like me to add these tasks to your \'TODO-2026\' TODO list?"\n'
        '   - Do NOT modify any spreadsheet data until explicit approval is given.\n'
        '4. Post-Approval Policy:\n'
        f'   - Upon receiving explicit user approval, first verify if the "TODO-2026" sheet tab exists in spreadsheet "{SPREADSHEET_ID}".\n'
        f'   - If the "TODO-2026" sheet tab does not exist, use the tool create_spreadsheet_tab to create it in spreadsheet "{SPREADSHEET_ID}".\n'
        f'   - Once the tab exists, use update_spreadsheet_values to append the approved adjustments as tasks to the "TODO-2026" sheet tab.\n'
        '   - Write the rows under the headers: Task (the actionable job, e.g., "Schedule a Support Barista role for Saturday morning"), Category ("Staffing" or "Inventory"), Ceremony, and Date_Added (today\'s date).\n'
        '   - Always confirm to the user exactly what tasks you have written to their "TODO-2026" TODO list.'
    ),
    tools=[
        FunctionTool(func=execute_sandbox_command),
        FunctionTool(func=read_spreadsheet_values),
        FunctionTool(func=update_spreadsheet_values),
        FunctionTool(func=create_spreadsheet_tab)
    ]
)

adk_app = App(name="secure_sandbox_app", root_agent=root_agent)
runner = Runner(app=adk_app, session_service=InMemorySessionService(), auto_create_session=True)

app = FastAPI(title="Secure ADK Sandbox Assistant")

# ==========================================
# ENDPOINTS & WEBSOCKET ROUTING
# ==========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    await websocket.send_text("🔌 System: Connected. Agent is ready...")

    try:
        while True:
            owner_reply = await websocket.receive_text()
            print(f"Owner replied via WS: {owner_reply}")
            await websocket.send_text("_Agent is running tools and thinking..._")
            
            new_message = types.Content(parts=[types.Part(text=owner_reply)])
            events = await asyncio.to_thread(
                runner.run,
                user_id="local_user",
                session_id="local_session",
                new_message=new_message
            )
            
            final_response = "".join(
                part.text
                for event in events
                if event.content and event.content.parts
                for part in event.content.parts
                if part.text
            ) or "Agent completed execution updates without text output."
            
            await websocket.send_text(final_response.strip())
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)

class UserPrompt(BaseModel):
    prompt: str

@app.post("/chat")
def chat_with_agent(payload: UserPrompt):
    """Fallback HTTP POST endpoint if UI is not used."""
    try:
        events = runner.run(
            user_id="local_user",
            session_id="local_session",
            new_message=types.Content(parts=[types.Part(text=payload.prompt)])
        )
        final_response = "".join(
            part.text
            for event in events
            if event.content and event.content.parts
            for part in event.content.parts
            if part.text
        )
        return {"status": "success", "response": final_response.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent loop failed: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    """Serves the warm coffee-themed chat interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coffee Shop Agent</title>
        <!-- Load marked.js for client-side markdown rendering -->
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            body { display: flex; height: 100vh; margin: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
            #sidebar { width: 250px; background: #3E2723; color: #EFEBE9; padding: 20px; }
            #sidebar h2 { font-size: 1.3em; margin-top: 10px; color: #FFF; border-bottom: 1px solid #5D4037; padding-bottom: 10px; }
            #main { flex-grow: 1; display: flex; flex-direction: column; background: #FAF8F6; }
            #chat-history { flex-grow: 1; padding: 20px; overflow-y: auto; background: #F5EFEB; }
            #input-area { padding: 20px; border-top: 1px solid #D7CCC8; background: #FAF8F6; display: flex;}
            input { 
                flex-grow: 1; 
                padding: 12px; 
                border-radius: 6px; 
                border: 1px solid #D7CCC8; 
                margin-right: 10px;
                font-size: 1em;
                background: #FFF;
                transition: border-color 0.2s, box-shadow 0.2s;
            }
            input:focus {
                outline: none;
                border-color: #8D6E63;
                box-shadow: 0 0 0 2px rgba(141, 110, 99, 0.25);
            }
            button { 
                padding: 10px 24px; 
                background: #6D4C41; 
                color: white; 
                border: none; 
                border-radius: 6px; 
                cursor: pointer; 
                font-weight: bold;
                font-size: 1em;
                transition: background-color 0.2s, transform 0.1s;
            }
            button:hover {
                background: #5D4037;
            }
            button:active {
                background: #4E342E;
                transform: scale(0.98);
            }
            .message { margin-bottom: 15px; padding: 12px 16px; border-radius: 8px; max-width: 85%; line-height: 1.5; }
            .user-msg { background: #EFEBE9; color: #3E2723; align-self: flex-end; margin-left: auto; border: 1px solid #D7CCC8;}
            .agent-msg { background: #fff; color: #3E2723; border: 1px solid #E0DCD8; box-shadow: 0 1px 3px rgba(62,39,35,0.06); }
            
            .msg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
            .agent-name { font-weight: bold; color: #5D4037; margin: 0; font-size: 0.95em;}
            .user-name { font-weight: bold; color: #8D6E63; margin: 0; font-size: 0.95em;}
            .msg-timestamp { font-size: 0.8em; color: #8D6E63; font-weight: normal; }
            
            .day-divider {
                display: flex;
                align-items: center;
                text-align: center;
                color: #8D6E63;
                margin: 20px 0;
                font-size: 0.85em;
                font-weight: bold;
            }
            .day-divider::before, .day-divider::after {
                content: '';
                flex: 1;
                border-bottom: 1px solid #D7CCC8;
            }
            .day-divider:not(:empty)::before {
                margin-right: .5em;
            }
            .day-divider:not(:empty)::after {
                margin-left: .5em;
            }

            /* Markdown Styling inside Messages */
            .message p { margin: 4px 0 8px 0; }
            .message p:last-child { margin-bottom: 0; }
            .message ul, .message ol { margin: 4px 0 8px 0; padding-left: 20px; }
            .message li { margin-bottom: 3px; }
            .message h1, .message h2, .message h3, .message h4 { margin: 12px 0 6px 0; font-size: 1.15em; color: #3E2723; font-weight: bold; }
            .message h1:first-child, .message h2:first-child, .message h3:first-child { margin-top: 0; }
            
            /* Table Styling */
            .message table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 0.95em; }
            .message th, .message td { border: 1px solid #D7CCC8; padding: 8px 10px; text-align: left; }
            .message th { background-color: #F5EFEB; font-weight: bold; color: #3E2723; }
            .message tr:nth-child(even) { background-color: #FAF8F6; }
            
            /* Code / Blockquote styling */
            .message code { background: #EFEBE9; padding: 2px 4px; border-radius: 3px; font-family: monospace; font-size: 0.9em; color: #5D4037; }
            .message pre { background: #F5EFEB; padding: 10px; border-radius: 5px; overflow-x: auto; margin: 8px 0; border: 1px solid #D7CCC8; }
            .message pre code { background: none; padding: 0; }
            .message blockquote { margin: 8px 0; padding-left: 12px; border-left: 4px solid #6D4C41; color: #5D4037; }
        </style>
    </head>
    <body>
        <div id="sidebar">
            <h2>☕ Coffee Shop Monitor</h2>
            <p>Monitoring sheet...</p>
        </div>
        <div id="main">
            <div id="chat-history"></div>
            <div id="input-area">
                <input type="text" id="msg" placeholder="Message Coffee Shop Monitor..." onkeypress="if(event.key === 'Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            const history = document.getElementById('chat-history');

            // Scroll to the bottom on load to show latest messages
            history.scrollTop = history.scrollHeight;

            ws.onmessage = function(event) {
                // Parse markdown content from the agent
                const parsedHtml = marked.parse(event.data);
                const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                history.innerHTML += `
                    <div class="message agent-msg">
                        <div class="msg-header">
                            <span class="agent-name">Inventory Agent APP</span>
                            <span class="msg-timestamp">${timeStr}</span>
                        </div>
                        <div>${parsedHtml}</div>
                    </div>`;
                history.scrollTop = history.scrollHeight;
            };

            function sendMessage() {
                const input = document.getElementById('msg');
                const text = input.value;
                if (!text) return;
                
                // Parse user markdown if any (optional, but keeps styling consistent)
                const parsedHtml = marked.parse(text);
                const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                history.innerHTML += `
                    <div class="message user-msg">
                        <div class="msg-header">
                            <span class="user-name">You</span>
                            <span class="msg-timestamp">${timeStr}</span>
                        </div>
                        <div>${parsedHtml}</div>
                    </div>`;
                
                ws.send(text);
                input.value = '';
                history.scrollTop = history.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port_val = int(os.environ.get('PORT', 8080))
    uvicorn.run(app, host='0.0.0.0', port=port_val)
```


## Deploy the Cloud Run instance

In this codelab, you will create a repository in Artifact Registry, build your container image using Google Cloud Build, and then deploy using that image.

### Create an Artifact Registry Repository

Create a new Docker repository named `coffee-repo` in your region:

```shell
gcloud artifacts repositories create coffee-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for Coffee Shop Agent"
```

### Build and Push the Container Image

Submit a Cloud Build job to build your container image and push it to the Artifact Registry repository:

```shell
gcloud builds submit --tag $REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/coffee-repo/coffee-mgr-agent:latest .
```

### Deploy the Cloud Run Instance

Now deploy your Cloud Run instance using the built image. We will pass the `--public` flag so that you can easily access the web chat UI from your browser:

```shell
gcloud beta run instances deploy coffee-mgr-agent-instance \
    --image=$REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/coffee-repo/coffee-mgr-agent:latest \
    --region=$REGION \
    --sandbox-launcher \
    --public \
    --labels dev-tutorial=codelab-cloud-run-personal-agent-coffee-shop \
    --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=global,SPREADSHEET_ID=$SPREADSHEET_ID \
    --service-account $SERVICE_ACCOUNT_ADDRESS
```


## Chat with your agent

After the deployment, you'll see `URL: https://coffee-mgr-agent-instance-YOUR_PROJECT_NUMBER.YOUR_REGION.run.app`

Open this URL in your browser.

Send the following prompt to your agent.

```
The 2026 graduation schedule was just posted. It's the same schedule as last year. Can you review last year's POS data to help me prepare for this year?
Saturday, June 13:
College of Business (8:30 a.m.)
College of Science and Mathematics (12:30 p.m.)
College of Liberal Arts (4:30 p.m.)
Sunday, June 14:
College of Agriculture (8:30 a.m.)
College of Architecture (12:30 p.m.)
College of Engineering (4:30 p.m.)
```

Your agent should respond with something similar to the following recommendations:

```console
Based on the 2025 POS data, I have correlated graduation ceremony patterns with beverage demand spikes. Last year, the post-ceremony windows consistently experienced high demand for complex items (Cold Brew, Extra Espresso, and Alt Milk).

Key Data Discoveries for 2026

- College of Business (Saturday 8:30 a.m. ceremony):
  - Significant demand spike observed at 10:00 a.m. Saturday.
  - Data: 130 Cold Brews and 95 Extra Espresso shots. This is a primary bottleneck for barista output.
- College of Engineering (Sunday 4:30 p.m. ceremony):
  - Significant demand spike observed at 6:00 p.m. Sunday.
  - Data: 145 Cold Brews and 110 Extra Espresso shots. This is the highest intensity period of the weekend.
- Alt-Milk Surge (Saturday/Sunday 2:00 p.m. post-ceremonies):
  - Consistent, high-volume Alt Milk consumption (65-180 oz) after the 12:30 p.m. ceremonies.

Diagnostic & Staffing Recommendations

Given that these complex beverage items (Cold Brew, Extra Espresso) correlate directly with your high-traffic post-ceremony windows, the risk of hitting wait times > 10 minutes is high. Assuming you typically have 2 cashiers, my diagnostic is that these are barista output bottlenecks, not cashier bottlenecks.

Suggested Tasks for your TODO-2026 List:

1. Staffing: Schedule a dedicated "Support Barista" for Saturday 9:30 a.m. – 11:00 a.m. to handle the Cold Brew/Espresso rush.
2. Staffing: Schedule a dedicated "Support Barista" for Sunday 5:30 p.m. – 7:00 p.m. to manage the high volume after the Engineering ceremony.
3. Inventory: Pre-stage extra Alt Milk cartons at the mobile station for Saturday 1:30 p.m. and Sunday 1:30 p.m. shifts.

Would you like me to add these tasks to your 'TODO-2026' TODO list?
```

Your agent will then ask you (Human-in-the-Loop) for permission to create/update your TODO-2026 tab sheet.

Respond to your agent with `Yes`.

Now when you look at your TODO-2026 tab sheet, you'll see something similar to the following:

```console
Task	Category	Ceremony	Date_Added
Schedule a Support Barista role for Saturday morning rush	Staffing	College of Business	2025-05-22
Schedule a Support Barista role for Sunday evening rush	Staffing	College of Engineering	2025-05-22
Pre-stage extra Alt Milk cartons at mobile station	Inventory	College of Science/Math & Architecture	2025-05-22
```


## Additional Scenarios

Here are a few ideas for future scenarios that you could try with your coffee shop agent, building upon the tools and data already present in this codelab:

### 1. Inventory Forecasting & Ordering

* **Scenario:** You need to place a supplier order for the busy weekend but expect a 10% increase in overall foot traffic compared to last year.
* **Prompt Idea:** "I expect 10% more customers this graduation weekend than last year. Can you calculate the total gallons of Alt-Milk and number of pastries I need to order, and add a 'Purchase Order' tab to the spreadsheet?"

### 2. Weather Impact Analysis

* **Scenario:** The forecast calls for an unseasonably cold and rainy graduation weekend.
* **Prompt Idea:** "The forecast says it's going to rain all day Saturday. Based on typical rainy days, people buy 30% less Cold Brew and 20% more Drip Coffee and Pastries. How does this change our bottlenecks and your staffing recommendations for Saturday?"

### 3. Simulating a New Menu Item

* **Scenario:** You want to introduce a time-consuming "Graduation Frappe".
* **Prompt Idea:** "I want to add a 'Graduation Frappe' to the menu. It takes twice as long to make as a Cold Brew. If 15% of our Cold Brew orders switch to the Frappe, what will happen to our wait times during the peak Sunday afternoon rush?"

### 4. Automated Shift Scheduling

* **Scenario:** Turning the staffing recommendations into an actual schedule.
* **Prompt Idea:** "Thanks for the staffing recommendations. Assuming shifts must be at least 4 hours long, can you draft a weekend schedule for the 'Support Barista' role and save it to a new 'Schedule-2026' tab?"


## Congratulations!

Congratulations for completing the codelab!

We recommend reviewing the [Cloud Run](https://cloud.google.com/run) documentation, the [Cloud Run instances](https://docs.cloud.google.com/run/docs/instances/create-and-manage-instances) documentation, the [Cloud Run sandboxes](https://docs.cloud.google.com/run/docs/code-execution) documentation, and the [ADK documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk).

#### What we've covered

* How to create a Cloud Run instance
* How to deploy an ADK agent on a Cloud Run instance
* How to have an agent run code in a sandbox within a Cloud Run instance

## Clean up

To avoid incurring charges to your Google Cloud account for the resources used
in this tutorial, you can either delete the project or delete the individual resources.

### Option 1: Delete Resources

Here is a succinct overview of the steps to clean up your project and avoid unnecessary charges.

**Delete the Cloud Run Instance**

```shell
gcloud beta run instances delete coffee-mgr-agent-instance --region $REGION
```

**Delete the Service Account: Remove the dedicated spreadsheet service account**

```shell
gcloud iam service-accounts delete $SERVICE_ACCOUNT_ADDRESS
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
