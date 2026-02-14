# Skill: File Triage for Inbox Markdown Tasks

## Objective
To efficiently process incoming markdown task files from the `Inbox/` directory, summarize their content, determine their status, and move them to the appropriate action directory.

## Procedure

### Step 1: Read a Task from Inbox Markdown
1.  **Monitor:** Continuously observe the `vault/Inbox/` directory for newly created `.md` files.
2.  **Identify:** When a new `.md` file appears, identify its full path.
3.  **Access:** Read the entire content of the newly identified markdown file.

### Step 2: Summarize the Task
1.  **Extract Title:** The first line of the markdown file is typically the title. Extract this line.
2.  **Generate Summary:**
    *   Read the subsequent lines of the file.
    *   Concatenate the first 2-3 meaningful sentences or paragraphs as a brief summary of the task. Ignore any metadata or non-essential formatting.
    *   If the file is very short, the entire content after the title can serve as the summary.

### Step 3: Decide Action (Needs Action or Done)
1.  **Analyze Content:** Review the extracted title and summary for keywords or phrases that indicate the task's status.
    *   **"Done" Indicators:** Look for terms like "completed", "resolved", "closed", "finished", or explicit statements indicating finality.
    *   **"Needs Action" Indicators:** Look for terms like "to do", "investigate", "follow up", "fix", "implement", "review", "bug", "feature", or any open-ended questions/requests.
2.  **Default to "Needs Action":** If no clear indicators are found, or if there is any ambiguity, default the task status to "Needs Action". This ensures no task is overlooked.

### Step 4: Write Output Markdown
1.  **Construct Output File Name:** Create a new markdown file name. A suggested format is to prepend a timestamp or a unique identifier to the original file's name to avoid conflicts, for example: `YYYYMMDD_OriginalFileName.md`.
2.  **Format Output Content:**
    *   Start with a clear heading for the task's title (e.g., `# Task: [Extracted Title]`).
    *   Follow with a "Summary:" section containing the generated summary.
    *   Include a "Status:" section indicating whether it was deemed "Needs Action" or "Done".
    *   Add a "Source File:" link or reference to the original file in `Inbox/`.
    *   (Optional) Add a section for "Agent Notes" or "Next Steps" to guide future processing.
3.  **Write to Directory:**
    *   If the decision in Step 3 was "Needs Action", write the constructed markdown content to a new file in the `vault/Needs_Action/` directory.
    *   If the decision was "Done", write the constructed markdown content to a new file in the `vault/Done/` directory.
4.  **Move Original File:** After successful processing and writing the output file, move the original file from `vault/Inbox/` to a `vault/Processed/` (create if not exists) or `vault/Archive/` directory to keep the `Inbox/` clean.
