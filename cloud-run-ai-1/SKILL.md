---
name: cloud-run-ai-1
description: A skill that provides Lab 1 workshop information based on reference data.
metadata:
  version: "1.0"
  course: cloud-run-ai-1
---

**Procedural Rules:**
1. **Mandatory Lab Lookup:** Any questions about "workshop content", "key concepts", "the lab steps", or "what do I do" REQUIRE you to use your tools to read `references/instructions.lab.md`.
2. **Priority Grounding:** You MUST prioritize information from the actual lab instructions over summarizing the high-level headers in this skill file. Provide grounded, step-by-step guidance.
3. **Error Protocol:** When a specific error is reported, you MUST first consult the **Frequently Asked Questions (FAQ) & Common Errors** section below.
4. **Authentication Logic:** If re-authentication is needed, strictly follow the "Refreshing the Browser" instructions.


**Core Workflow:**

Step 1. **Consult Primary Instructions:** Always check `references/instructions.lab.md` to understand the current Level 1 workshop steps.
Step 2. **Identify & Clarify:** Determine what the user is asking. If they need debugging help, ask them to clarify exactly which step of the lab they are currently on.
Step 3. **Search Primary References:** If the user asks about a specific file or script (like agent.py, app.py, menu.json, requirements.txt, or seed.py), defer to the file structure and contents of references/level_1/ directory as the reference source.
Step 4. **Provide Grounded Solutions:** Provide answers strictly based on the reference data. If the answer cannot be found in the reference data, clearly state: "I don't know."


**Python Coding & Debugging Rules:**
* **Snippets vs. Full Files:** If a user pastes a short Python code snippet, assume it may be an indentation issue. Always ask the user to paste the *entire file* rather than just the snippet.

* **Debugging Full Code:** When the user provides the full Python code:
  * If it is just an indentation problem, fix it and provide the corrected code.
  * If it is a different error, explain the solution clearly and provide the corrected code.
  * Problem could be user pasting to the wrong file, ask user to paste to the correct file. If you are not sure, ask user which file they are editing now?
* **Terminal vs. Editor Confusion:** Beginners often paste Python code into the terminal, or terminal commands into their code editor. Watch out for this and gently guide them to paste code/commands into the correct interface.


**Workshop & Environment Troubleshooting:**
* **Refreshing the Browser:** If you instruct the user to refresh their browser window (usually to re-authenticate):
  1. First, tell them to stop the current running process in the terminal by pressing **Ctrl+C**.
  2. Then, tell them to **refresh the browser window running the Cloud Shell / IDE**, NOT the window running the frontend application.
* **Event Codes:** If a user asks for the event code, tell them to check today's landing page (likely formatted as `goo.gle/buildwithai-[location]`) or advise them to ask the TAs in the room. And if user is in New York event, the event code is `buildwithai-nyc`, if user is in Sunnyvale event, the event code is `buildwithai-svl`, if user is in Washington DC event, the event code is `buildwithai-dc`.


**Frequently Asked Questions (FAQ) & Common Errors:**
If the user encounters any of the following specific errors, provide the exact corresponding solution:

* **Question:** What LLM or Gemini model version does the agent use in this lab?
  * **Answer:** The agent in this workshop is configured to use **Gemini 3.5 Flash** (specified as `gemini-3.5-flash` in `agent.py`).
* **Error:** `429 RESOURCE_EXHAUSTED`
  * **Solution:** Tell the user to wait another minute and re-run their script or command.
* **Error:** `Service account info is missing 'email' field.` **OR** `AttributeError: 'str' object has no attribute 'message'` **OR** `Compute Engine Metadata server unavailable on attempt X of 5. Reason: HTTPConnectionPool...`
  * **Solution:** This is an authentication issue. You MUST follow these steps:
    1. Click on your terminal and press **Ctrl+C** to stop the current process.
    2. **Refresh the browser window running your Cloud Shell / IDE** (do NOT refresh the frontend preview window).
    3. Once the Cloud Shell reloads, re-run your `gcloud run deploy` command.
* **Error:** `ValueError: GOOGLE_CLOUD_PROJECT environment variable is not set.` OR project/region variables are missing.
  * **Solution:** If the terminal or Cloud Shell restarted, the environment variables were cleared. Re-export them:
    ```bash
    export PROJECT_ID="YOUR_PROJECT_ID"
    export REGION="YOUR_REGION"
    gcloud config set project $PROJECT_ID
    gcloud config set run/region $REGION
    ```
* **Error:** Permission errors or resource not found because `gcloud` is targeting the wrong project ID.
  * **Solution:** Verify the active project ID:
    ```bash
    gcloud config get-value project
    ```
    If it's incorrect, switch to the correct project:
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```
* **Error:** `The billing account for the owning project is disabled...`
  * **Solution:** Ensure the active project is associated with the billing account. TAs/users can check the billing project linkage:
    ```bash
    gcloud beta billing projects describe YOUR_PROJECT_ID
    ```
* **Error:** Creating files in the wrong directory (e.g., home directory `~` instead of `~/coffee-barista-agent`).
  * **Solution:** The files `agent.py`, `app.py`, `menu.json`, `requirements.txt`, and `seed.py` must be inside `~/coffee-barista-agent`. Verify the structure by running:
    ```bash
    ls -R ~/coffee-barista-agent
    ```
    If any files were created in the home directory, move them:
    ```bash
    mv ~/agent.py ~/app.py ~/menu.json ~/requirements.txt ~/coffee-barista-agent/
    ```
* **Question:** How do I verify that Firestore has been seeded correctly?
  * **Answer:** Run this quick python snippet in Cloud Shell to list seeded menu items from the `coffee-menu` database:
    ```bash
    python3 -c "
    from google.cloud import firestore
    db = firestore.Client(database='coffee-menu')
    docs = db.collection('menu').stream()
    for d in docs:
        print(d.id, d.to_dict().get('name'))
    "
    ```
* The `gcloud services enable` command requires a 2 to 3 minute propagation window. Moving too quickly to subsequent tasks may result in failures. Use the following command to check if APIs are enabled: 
  ```shell
  gcloud services list --enabled | grep -E "run|aiplatform|cloudbuild"
  ```
* Manual JSON entry into the editor is prone to errors like truncated content, trailing commas, or missing braces. Make sure to validate using the following command:
  ```shell
  cat menu.json | python3 -m json.tool > /dev/null && echo "Valid JSON!"
  ```
* Copy-pasting ADK or Streamlit logic into Cloud Shell often breaks indentation. This frequently triggers an `IndentationError` during the execution or deployment phase.  
* During `gcloud run deploy`, a prompt asking `Do you want to continue (Y/n)?` appears for repository creation. Watch for attendees who stall here, assuming the process is still running.  
* Moving from a local JSON source to a live production database involves significant file changes and is a high-risk point for lab failures.

| Codelab Task | Potential Gotcha | Troubleshooting Tips |
| :---- | :---- | :---- |
| 8.1: Initialize Firestore | Incorrect database name used in creation. | The database MUST be named exactly "coffee-menu". If they run the create command without the \--database="coffee-menu" flag (using (default)), the app will crash because "coffee-menu" is hardcoded in the scripts. |
| 8.2: Seed Firestore | ModuleNotFoundError: No module named 'google' | They forgot to run pip3 install google-cloud-firestore==2.27.0 google-genai==2.11.0 locally in Cloud Shell before executing seed.py. Run the pip3 installation command first. |
| 8.2: Seed Firestore | Seeding script hangs or fails due to empty env vars. | If their Cloud Shell restarted, PROJECT\_ID and REGION env vars are missing. seed.py will fail to initialize the client. Re-export variables before running `python3 seed.py`. |
| 8.3: Composite Index | Index build latency causes search failures. | Creating a Firestore vector index runs asynchronously and takes 2 to 5 minutes. If they redeploy and query immediately, the app will throw a Firestore search exception. TAs should tell them to check the build progress in the Cloud Console or wait a few minutes. |
| 8.4: IAM Roles | Confusing Datastore vs. Firestore roles | TAs must ensure they run the exact command adding roles/datastore.user. Even though it’s Firestore Native, Google Cloud utilizes unified Datastore IAM roles for access. |
| 8.5: Code Updates | Incomplete block replacement in agent.py & app.py. | Attendees will often append the new Firestore blocks to the bottom of the files instead of replacing the \# \[START ...\] blocks. This causes syntax/naming conflicts. TAs must verify they deleted the old blocks entirely. |
| 8.5: Code Updates | Forgetting to update requirements.txt | If they don't append the two new Firestore libraries to requirements.txt, the Cloud Run buildpack will fail to package them, and the redeployed container will crash on start. |



**FALLBACK SEARCH PREPARATION:**
If you cannot find an answer within the provided skill materials:
    1. Determine if the question is within the technical scope of the workshop
    2. If it is in-scope, instead of answering "I don't know", you MUST formulate a PRECISE SEARCH QUERY.
    3. This query should include key technical terms and the context of the workshop to help the next agent find an accurate solution.
    4. Explicitly output: "SEARCH_QUERY: [your refined query]"

