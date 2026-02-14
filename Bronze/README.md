# Personal AI Employee: Bronze Tier Implementation

This project is an implementation of the "Personal AI Employee Hackathon 0: Building Autonomous FTEs" Bronze Tier deliverables, with several "Beyond Bronze" features integrated for robustness and extensibility. The goal is to set up the foundational infrastructure for an AI agent that can manage personal and business affairs, utilizing a local-first, agent-driven, human-in-the-loop architecture.

## Project Overview

The "Personal AI Employee" aims to create a Digital Full-Time Equivalent (FTE) that proactively manages tasks using AI. This implementation sets up the core file-based workflow, watcher mechanisms, and a modular skill dispatch system to prepare for future Large Language Model (LLM) integration.

## Architecture & Tech Stack Highlights

*   **The Vault (Memory/GUI):** Obsidian-compatible Markdown files are used for tasks, plans, logs, and approvals within the `vault/` and `AI_Employee_Vault/` directories, ensuring data remains local.
*   **Watchers (Perception):** Lightweight Python scripts monitor file system changes to trigger AI processing.
*   **Task Processor (Reasoning/Orchestration):** The `run_ai_employee.py` script acts as the central processor, reading tasks, applying logic, dispatching to skills, and routing files.
*   **Agent Skills (Action):** Modular Python scripts (`gmail_send.py`, `linkedin_post.py`, `vault_file_manager.py`) encapsulate specific actions the AI can take.
*   **Human-in-the-Loop (HITL):** A file-based approval system routes sensitive tasks for manual review before execution.
*   **Robustness:** Implemented logging with rotation and file-based locking mechanisms for daemon processes.
*   **Scheduling:** Provided setup scripts for cron (Linux/macOS) and Task Scheduler (Windows) to run the AI Employee as a persistent daemon.

## Bronze Tier Deliverables (Completed)

All "Bronze Tier" requirements as specified in the hackathon guide have been met:

1.  **Obsidian vault with Dashboard.md and Company_Handbook.md:**
    *   `vault/Dashboard.md` and `vault/Company_Handbook.md` exist as placeholder files.
2.  **One working Watcher script (file system monitoring):**
    *   `watcher.py` monitors `vault/Inbox` for new markdown files, processes them, creates a `response_` file in `vault/Needs_Action`, and moves the original to `vault/Done`.
3.  **Claude Code successfully reading from and writing to the vault:**
    *   The `run_ai_employee.py` script (simulating the "Claude Code" brain) reads tasks from `AI_Employee_Vault/Inbox` and writes processed output to `AI_Employee_Vault/Needs_Action` or `AI_Employee_Vault/Needs_Approval`. It also moves original files to `AI_Employee_Vault/Done`. This establishes the file-based read/write mechanism.
4.  **Basic folder structure: /Inbox, /Needs_Action, /Done:**
    *   These folders (and `/Needs_Approval`) are set up within both the `vault/` and `AI_Employee_Vault/` directories.
5.  **All AI functionality should be implemented as Agent Skills:**
    *   The core processing logic in `run_ai_employee.py` dispatches to modular Python scripts for actions like sending emails (`skills/gmail_send.py`), posting to LinkedIn (`skills/linkedin_post.py`), and general file management (`skills/vault_file_manager.py`).

## Beyond Bronze Features Implemented

*   **Modular Agent Skills:** Dedicated Python modules for `gmail_send`, `linkedin_post`, and `vault_file_manager` provide clear separation of concerns.
*   **Human-in-the-Loop Approval Workflow:** Tasks containing keywords like "approve", "review", or "human_in_the_loop" are routed to `AI_Employee_Vault/Needs_Approval/` for manual intervention.
*   **Production Daemon Scheduler Setup:**
    *   `scripts/setup_cron.sh` provides instructions for setting up a cron job on Linux/macOS.
    *   `scripts/setup_windows_scheduler.bat` provides instructions for setting up a Task Scheduler job on Windows.
*   **Deduplication Ledger:** The `claude/skills/vault-watcher/scripts/watch_inbox.py` script uses `vault_watcher_ledger` to prevent reprocessing of already handled tasks.
*   **Audit Logging with Rotation:** All daemon scripts (`watcher.py`, `run_ai_employee.py`, `watch_inbox.py`) now log their actions to files (`logs/actions.log`, `logs/ai_employee.log`) using `logging.handlers.RotatingFileHandler` to manage log file size.
*   **Lock Files:** Daemon scripts (`run_ai_employee.py`, `watch_inbox.py`) implement a file-based locking mechanism to prevent multiple instances from running concurrently.
*   **Refactored Advanced Watcher:** `claude/skills/vault-watcher/scripts/watch_inbox.py` has been refactored to use the `BaseWatcher` pattern (as suggested in the guide for robustness) for its polling mechanism.

## Setup Instructions

1.  **Clone this repository:**
    ```bash
    git clone https://github.com/MJibranR/Hackathon-0-Personal-AI-Employee/
    cd Bronze
    ```
2.  **Ensure Python 3.10+ is installed and in your PATH.**
3.  **Install Python dependencies:**
    ```bash
    pip install watchdog
    ```
    (Note: `playwright` and `google-api-python-client` would be needed for actual implementations of WhatsApp and Gmail watchers, but are not required for the current placeholder skills).
4.  **Verify folder structure:** The required directories (`logs`, `lockfiles`, `vault/Inbox`, `vault/Needs_Action`, `vault/Done`, `AI_Employee_Vault/Inbox`, etc.) are created dynamically by the scripts or were set up during initial project creation.
5.  **Make setup scripts executable (Linux/macOS):**
    ```bash
    chmod +x scripts/setup_cron.sh
    ```
6.  **Set up daemon (optional):**
    *   **Linux/macOS (cron):** Run `./scripts/setup_cron.sh`
    *   **Windows (Task Scheduler):** Run `scripts\setup_windows_scheduler.bat` (as Administrator)

## Testing Instructions

### Quick Test: The Simple Watcher (`watcher.py`)

1.  **Terminal 1: Start the watcher**
    ```powershell
    python watcher.py
    ```
2.  **Terminal 2: Drop a test file into Inbox**
    ```powershell
    echo "# Test Task`nPlease review the Q1 sales report" > vault/Inbox/my_test.md
    ```
3.  **Expected result:** Terminal 1 shows `[DETECTED]` and `[PROCESSED]`, and a new file appears in `vault/Needs_Action/response_my_test.md`. The original `my_test.md` will be moved to `vault/Done/my_test.md`.
4.  **Press Ctrl+C in Terminal 1 to stop the watcher.**

### Test: The AI Employee Pipeline (`scripts/run_ai_employee.py`)

1.  **Clean up `AI_Employee_Vault` (if not already empty):**
    ```powershell
    Remove-Item -Path "AI_Employee_Vault/Inbox/*" -ErrorAction SilentlyContinue -Recurse
    Remove-Item -Path "AI_Employee_Vault/Needs_Action/*" -ErrorAction SilentlyContinue -Recurse
    Remove-Item -Path "AI_Employee_Vault/Done/*" -ErrorAction SilentlyContinue -Recurse
    Remove-Item -Path "AI_Employee_Vault/Needs_Approval/*" -ErrorAction SilentlyContinue -Recurse
    ```
2.  **Drop test tasks into `AI_Employee_Vault/Inbox`:**
    *   **Email Task (`AI_Employee_Vault/Inbox/email_task.md`):**
        ```powershell
        echo "# Send Welcome Email`nPlease send an email. To: client@example.com Subject: Welcome! Body: Hello, welcome aboard!" > AI_Employee_Vault/Inbox/email_task.md
        ```
    *   **LinkedIn Task (`AI_Employee_Vault/Inbox/linkedin_task.md`):**
        ```powershell
        echo "# Post on LinkedIn`nPost to LinkedIn. Content: Exciting new AI trends!" > AI_Employee_Vault/Inbox/linkedin_task.md
        ```
    *   **Approval Task (`AI_Employee_Vault/Inbox/approval_task.md`):**
        ```powershell
        echo "# Review Document`nPlease review the attached document for human_in_the_loop approval." > AI_Employee_Vault/Inbox/approval_task.md
        ```
3.  **Run the AI Employee once:**
    ```powershell
    python scripts/run_ai_employee.py --once
    ```
4.  **Verify results:**
    *   `AI_Employee_Vault/Inbox` should be empty.
    *   `AI_Employee_Vault/Needs_Action` should be empty.
    *   `AI_Employee_Vault/Done` should contain `email_task.md`, `linkedin_task.md`, and `approval_task.md` (the original files) AND `processed_email_task.md`, `processed_linkedin_task.md`.
    *   `AI_Employee_Vault/Needs_Approval` should contain `processed_approval_task.md`.
    *   `logs/ai_employee.log` should contain log entries for skill dispatches and file processing.

### Test: The Advanced Vault Watcher (`claude/skills/vault-watcher/scripts/watch_inbox.py`)

1.  **Reset the deduplication ledger:**
    ```powershell
    python claude/skills/vault-watcher/scripts/watch_inbox.py --reset
    ```
2.  **Terminal 1: Start the advanced watcher**
    ```powershell
    python claude/skills/vault-watcher/scripts/watch_inbox.py
    ```
3.  **Terminal 2: Drop a test file into Inbox**
    ```powershell
    echo "# Urgent LinkedIn Update`nPost a LinkedIn update: Major company announcement." > AI_Employee_Vault/Inbox/linkedin_update.md
    ```
4.  **Expected result:** Terminal 1 output and `logs/actions.log` will show processing. `AI_Employee_Vault/Inbox` will be empty. `AI_Employee_Vault/Done` will contain `linkedin_update.md` (original) and `processed_linkedin_update.md`. `vault_watcher_ledger` will contain a hash for the processed file.
5.  **Press Ctrl+C in Terminal 1 to stop the watcher.**

## Future Enhancements

The next major step is to integrate a Large Language Model (LLM) as the "Brain" of the AI Employee (e.g., using Google's Gemini, OpenAI's GPT, or Anthropic's Claude Code directly). This would involve:

*   Selecting a specific LLM and obtaining API access.
*   Designing detailed prompt engineering for task interpretation and decision-making.
*   Parsing LLM output to extract structured instructions for skill dispatch.
*   Implementing more sophisticated logic for dynamically calling skills and managing multi-step tasks.

Other potential enhancements include:

*   **Implementing actual `gmail_send` and `linkedin_post` functionality** using their respective APIs or automation tools (e.g., Playwright).
*   **Implementing `lock files`** (if not fully cross-platform robust with current implementation).
*   **Adding specific `vault-file-manager` skill calls** within `run_ai_employee.py` for more granular control over vault operations.

This README provides a comprehensive overview of the implemented system.
