---
name: make-plan
description: Analyzes files in the 'Needs Action' folder and creates a plan document. Trigger with 'Make a plan for tasks'.
---

# Make a Plan

This skill guides you in creating a plan document based on the files in the `Needs Action` folder.

## Workflow

1.  **Read Files in `Needs Action`**:
    *   Use the `list_directory` tool to get a list of all files in the `Needs Action` folder.
    *   For each file in the list, use the `read_file` tool to read its content.

2.  **Analyze and Summarize**:
    *   After reading all the files, analyze their content to understand the pending tasks.
    *   Based on your analysis, generate the following sections:
        *   **Summary of Pending Tasks**: A brief overview of all the tasks.
        *   **Suggested Order of Execution**: A prioritized list of tasks.
        *   **Risks or Unclear Items**: Anything that is ambiguous or might pose a challenge.
        *   **Strategy Paragraph**: A short paragraph outlining the overall approach to completing the tasks.

3.  **Create the Plan Document**:
    *   Generate a timestamp in the format `YYYY-MM-DD_HH-MM-SS`.
    *   Create a new file named `Plan <timestamp>.md` inside the `Plans` folder. For example: `Plans/Plan 2026-02-11_15-30-00.md`.
    *   Use the `write_file` tool to write the generated summary and plan into this new file. The content should be well-formatted using Markdown.