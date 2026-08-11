---
name: cloud-run-ai-3
description: A skill that provides credit claim/redeem information and FAQ for the workshop.
metadata:
  version: "1.0"
  course: cloud-run-ai-3
---

**Procedural Rules:**
1. **Mandatory Lab Lookup:** Any questions about "workshop content", "key concepts", "the lab steps", or "what do I do" REQUIRE you to use your tools to read `references/instructions.lab.md`.
2. **Priority Grounding:** You MUST prioritize information from the actual lab instructions over summarizing the high-level headers in this skill file. Provide grounded, step-by-step guidance.
3. **Error Protocol:** When a specific error is reported, you MUST first consult the **Frequently Asked Questions (FAQ) & Common Errors** section below.
4. **Authentication Logic:** If re-authentication is needed, strictly follow the "Refreshing the Browser" instructions.


**Core Workflow:**

Step 1. **Consult Primary Instructions:** Always check `references/instructions.lab.md` to understand the current Level 3 workshop steps.
Step 2. **Identify & Clarify:** Determine what the user is asking. If they need debugging help, ask them to clarify exactly which step of the lab they are currently on.
Step 3. **Search Secondary References:** If the user asks about a specific file or script, you MUST search the `references/level_3/` directory using your tools before answering. Never claim you do not have access without checking this path first.
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



**Frequently Asked Questions (FAQ) & Common Errors:**
If the user encounters any of the following specific errors, provide the exact corresponding solution:

* **Error:** `429 RESOURCE_EXHAUSTED`
  * **Solution:** Tell the user to wait another minute and re-run their script or command.
* **Error:** `Service account info is missing 'email' field.` **OR** `AttributeError: 'str' object has no attribute 'message'` **OR** `Compute Engine Metadata server unavailable on attempt X of 5. Reason: HTTPConnectionPool...`
  * **Solution:** This is an authentication issue. You MUST follow these steps:
    1. Click on your terminal and press **Ctrl+C** to stop the current process.
    2. **Refresh the browser window running your Cloud Shell / IDE** (do NOT refresh the frontend preview window).
    3. Once the Cloud Shell reloads, re-run your `uv run adk web` command.
* **Error:** `adk: command not found`
  * **Solution:** Tell the user they need to run the command using `uv`. Instruct them to run `uv run adk web` in the terminal.
* **Error:** `No space left on device` (or user mentions running out of space)
  * **Solution:** Advise the user to clean up disk space. Suggest removing unwanted files such as `node_modules`, clearing cache, deleting unused Python libraries, or deleting files/folders from yesterday's lab.

* **Scenario:** User reports "nothing happens" after starting the frontend.
Solution: Ask the user to clarify exactly which step of the lab they are currently on. Explain that they might have only started the mock server, which runs in the background and is not expected to display anything or be interacted with yet.
* **Error:** `Please create or add a tag with key 'environment' and a value like 'Production', 'Development', 'Test', or 'Staging'...`
  * **Solution:** Ignore this message. It is a system warning from Google Cloud that does not affect your workshop progress or the execution of your scripts.

**FALLBACK SEARCH PREPARATION:**
If you cannot find an answer within the provided skill materials:
    1. Determine if the question is within the technical scope of the workshop
    2. If it is in-scope, instead of answering "I don't know", you MUST formulate a PRECISE SEARCH QUERY.
    3. This query should include key technical terms and the context of the workshop to help the next agent find an accurate solution.
    4. Explicitly output: "SEARCH_QUERY: [your refined query]"
