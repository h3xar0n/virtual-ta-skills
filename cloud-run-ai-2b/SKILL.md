---
name: cloud-run-ai-2b
description: A skill that provides Cloud Run AI Lab 2b (BigQuery MCP Agent) workshop information based on reference data.
metadata:
  version: "1.1"
  course: cloud-run-ai-2b
---


**Procedural Rules:**
1. **Mandatory Lab Lookup:** Any questions about "workshop content", "key concepts", "the lab steps", or "what do I do" for the lab **"Learn how to build and deploy AI Agents with Gemini and BigQuery MCP server in Cloud Run"** REQUIRE you to use your tools to read `references/instructions.lab.md`.
2. **Priority Grounding:** You MUST prioritize information from the actual lab instructions over summarizing the high-level headers in this skill file. Provide grounded, step-by-step guidance.
3. **Error Protocol:** When a specific error is reported, you MUST first consult the **Frequently Asked Questions (FAQ) & Common Errors** section below.
4. **Authentication Logic:** If re-authentication is needed, strictly follow the "Refreshing the Browser" instructions.

**Core Workflow:**
Step 1. **Consult Primary Instructions:** Always check `references/instructions.lab.md` to understand the current Lab 2b workshop steps.
Step 2. **Identify & Clarify:** Determine what the user is asking. If they need debugging help, ask them to clarify exactly which step of the lab they are currently on.
Step 3. **Search Primary References:** If the user asks about a specific file or script (like `agent.py`, `__init__.py`, or `requirements.txt`), defer to the file structure and contents of `references/data_agent/` directory as the reference source
Step 4. **Provide Grounded Solutions:** Provide answers strictly based on the reference data. If the answer cannot be found in the reference data, clearly state: "I don't know."


**Python Coding & Debugging Rules:**
* **Snippets vs. Full Files:** If a user pastes a short Python code snippet, assume it may be an indentation issue. Always ask the user to paste the *entire file* rather than just the snippet.

* **Debugging Full Code:** When the user provides the full Python code:
  * If it is just an indentation problem, fix it and provide the corrected code.
  * If it is a different error, explain the solution clearly and provide the corrected code.
  * Problem could be user pasting to the wrong file, ask user to paste to the correct file. If you are not sure, ask user which file they are editing now.

* **Terminal vs. Editor Confusion:**
  * Watch out for beginners pasting Python code into the terminal, or terminal commands into their code editor.
  * **Symptoms of pasting Python code into Terminal:**
    - Error messages like `import: command not found` or `from: command not found` or `_application_default_credentials: command not found`.
    - Guide the user to open the Cloud Shell Editor, create/open the file `data_agent/agent.py`, paste the code there, and save the file.
  * **Symptoms of pasting Terminal commands into Python files:**
    - Syntax errors in `agent.py` on commands starting with `gcloud`, `export`, `uv`, `echo`, or `mkdir`.
    - Guide the user to remove these command lines from their Python file and run them in the terminal instead.


**Workshop & Environment Troubleshooting:**
* **Refreshing the Browser:** If you instruct the user to refresh their browser window (usually to re-authenticate):
  1. First, tell them to stop the current running process in the terminal by pressing **Ctrl+C**.
  2. Then, tell them to **refresh the browser window running the Cloud Shell / IDE**, NOT the window running the frontend application.



**Frequently Asked Questions (FAQ) & Common Errors:**
If the user encounters any of the following specific errors, provide the exact corresponding solution:

* **Question:** What LLM or Gemini model version does the agent use in this lab?
  * **Answer:** The agent in this workshop is configured to use **Gemini 3.6 Flash** (specified as `gemini-3.6-flash` in `data_agent/agent.py`).
* **Error:** `429 RESOURCE_EXHAUSTED`
  * **Solution:** Tell the user to wait another minute and re-run their script or command.
* **Error:** `Service account info is missing 'email' field.` **OR** `AttributeError: 'str' object has no attribute 'message'` **OR** `Compute Engine Metadata server unavailable on attempt X of 5. Reason: HTTPConnectionPool...`
  * **Solution:** This is an authentication issue. You MUST follow these steps:
    1. Click on your terminal and press **Ctrl+C** to stop the current process.
    2. **Refresh the browser window running your Cloud Shell / IDE** (do NOT refresh the frontend preview window).
    3. Once the Cloud Shell reloads, re-run the `uv tool run ... adk web` command (make sure to restore environment variables first by running `source env.sh`).
* **Error:** `adk: command not found`
  * **Solution:** Tell the user they need to run the command using `uv tool run`. Instruct them to run:
    ```bash
    uv tool run --with "mcp==1.29.*" --from "google-adk[mcp]==2.4.*" adk web --allow_origins="*" --port 8080 .
    ```
* **Error:** `No space left on device` (or user mentions running out of space)
  * **Solution:** Advise the user to clean up disk space. Suggest removing unwanted files such as `node_modules`, clearing cache, deleting unused Python libraries, or deleting files/folders from other labs.
* **Error:** `ValueError: GOOGLE_CLOUD_PROJECT environment variable is not set.`
  * **Solution:** Explain that their environment variables were cleared or not set (likely due to a terminal/Cloud Shell restart). Instruct them to run:
    ```bash
    source env.sh
    ```
    or manually export the variables:
    ```bash
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_REGION="YOUR_CLOUD_RUN_REGION"
    export GOOGLE_GENAI_USE_ENTERPRISE="True"
    export GOOGLE_CLOUD_LOCATION="global"
    ```
    (Replacing `YOUR_PROJECT_ID` and `YOUR_CLOUD_RUN_REGION` with their actual values).
* **Error:** Permission errors or resource not found because gcloud is targeting the wrong project ID.
  * **Solution:** Verify the active project ID using `gcloud config get-value project`. If it's incorrect, switch to the correct project:
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```
* **Error:** `The billing account for the owning project is disabled...` or billing-related deployment failures.
  * **Solution:** Ensure the active project is associated with the billing account generated from the GDP credit redemption. You can check the billing project linkage:
    ```bash
    gcloud beta billing projects describe YOUR_PROJECT_ID
    ```
    If billing is not enabled, enable it in the GCP Console under **Billing** by linking it to the active billing account.
* **Error:** Entering code or creating files in the wrong directory (e.g. at the root workspace instead of inside `references/data_agent/` or `data_agent/`).
  * **Solution:** Confirm the correct file structure. The files `agent.py`, `__init__.py`, and `requirements.txt` must be located inside the agent directory (e.g., `data_agent/`). If they are in the root directory, move them:
    ```bash
    mv agent.py __init__.py requirements.txt data_agent/
    ```
* **Error**: Cloud Run deployment fails or container crashes on start for `bq-data-agent`
  * **Solution**: Ensure the files are structured correctly inside the `data_agent` folder:
    1. `data_agent/__init__.py` must contain:
       ```python
       from . import agent
       ```
    2. `data_agent/requirements.txt` must contain:
       ```
       google-adk==2.4.*
       mcp==1.29.*
       ```
    3. The deployment command must be executed from the directory containing the `data_agent` folder (NOT from inside `data_agent`).
* **Error**: Permission errors when the agent attempts to call BigQuery tools (e.g. `execute_sql_readonly`)
  * **Solution**: 
    1. Confirm that the BigQuery API (`bigquery.googleapis.com`) is enabled in the project:
       ```bash
       gcloud services enable bigquery.googleapis.com
       ```
    2. If running locally, make sure they run:
       ```bash
       gcloud auth application-default login
       ```
       to authenticate their terminal context.
* **Error**: `No agent found in the path` OR `adk: command failed` when starting `adk web` or `adk deploy`
  * **Solution**: The user is likely in the wrong directory or has created files in the wrong location.
    1. Tell the user to run `pwd` and check if they are in the parent directory of `data_agent/` (typically `~/` or `/home/username/`).
    2. Tell the user to run `ls -R data_agent` to verify the structure matches exactly:
       ```none
       data_agent/
           __init__.py
           agent.py
           requirements.txt
       ```
       If they created `agent.py` in the wrong folder (e.g., in the home directory), guide them to move it into the `data_agent/` folder using the terminal command:
       ```bash
       mv agent.py data_agent/
       ```

* **Error:** The deployment command fails, or the deployed agent fails to initialize or connect to BigQuery/Vertex AI due to environment variable parsing issues.
  * **Solution:** The codelab instructions contain a quotation typo in the `--set-env-vars` argument of the deployment command. Instruct the user to run the corrected command with the quotes removed/fixed:
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
          --set-env-vars GOOGLE_GENAI_USE_ENTERPRISE=True,GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}
    ```
* **Error:** `API [iam.googleapis.com] not enabled on project [...]` during deployment.
  * **Solution:** Run the following command to enable the IAM API:
    ```bash
    gcloud services enable iam.googleapis.com --project $GOOGLE_CLOUD_PROJECT
    ```
* **Error:** `INVALID_ARGUMENT: Invalid build request. could not resolve source: ... compute@developer.gserviceaccount.com does not have storage.objects.get access to the Google Cloud Storage object.`
  * **Solution:** Grant the `Storage Admin` role to the default Compute service account:
    ```bash
    PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT --format="value(projectNumber)")
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/storage.admin"
    ```
* **Error:** Cloud Run deployment fails during the container build step because the default Compute service account cannot push the image to Artifact Registry or write logs.
  * **Solution:** Grant the `Artifact Registry Writer` and `Logs Writer` roles to the default Compute service account:
    ```bash
    PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT --format="value(projectNumber)")
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/artifactregistry.writer"
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/logging.logWriter"
    ```
* **Error:** Permission denied or Access Denied when the agent calls BigQuery or Vertex AI (Gemini) *after* deploying to Cloud Run, even though it works locally.
  * **Solution:** The Cloud Run service's service account (typically the default Compute Service Account) needs explicit permissions. Instruct the user to grant the `BigQuery Admin` (or `BigQuery User` and `BigQuery Data Viewer`) and `Vertex AI User` roles to the default Compute Service Account by running:
    ```bash
    PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT --format="value(projectNumber)")
    
    # Grant BigQuery access
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/bigquery.admin"
        
    # Grant Vertex AI / Gemini access
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
        --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
        --role="roles/aiplatform.user"
    ```

**FALLBACK SEARCH PREPARATION:**
If you cannot find an answer within the provided skill materials:
    1. Determine if the question is within the technical scope of the workshop
    2. If it is in-scope, instead of answering "I don't know", you MUST formulate a PRECISE SEARCH QUERY.
    3. This query should include key technical terms and the context of the workshop to help the next agent find an accurate solution.
    4. Explicitly output: "SEARCH_QUERY: [your refined query]"
