# Usage Example: Ralph Wiggum Stop Hook Loop

The **Ralph Wiggum Pattern** allows the AI to work autonomously until a task is fully complete. 
It monitors the output for a "completion promise" or watches the file system for a "task move" to `/Done`.

### Command Wrapper: `/ralph-loop` (Python CLI Implementation)

```bash
# 1. Start a loop that waits for a specific promise string in the output
python -m scripts.ralph.cli_wrapper 
    "Analyze the latest transactions and create a CEO briefing." 
    --completion-promise "BRIEFING_COMPLETE" 
    --max-iterations 5

# 2. Start a loop that waits for a file to move to the /Done folder
python -m scripts.ralph.cli_wrapper 
    "Draft an invoice for Client A and move it to /Done when approved." 
    --target-file "AI_Employee_Vault/Needs_Action/INVOICE_Client_A.md" 
    --max-iterations 10
```

### Stop Hook Flow

1.  **State Initialization**: Saves the prompt and completion targets to `.ralph_state.json`.
2.  **Autonomous Execution**: Calls the reasoning engine (Claude Code) with the prompt.
3.  **The Intercept (Stop Hook)**:
    - Before the AI process exits, the hook checks for the `--completion-promise` in the `last_output`.
    - It also checks if the `--target-file` has been moved to `AI_Employee_Vault/Done/`.
4.  **Context Re-injection**:
    - If **NOT** complete, the hook blocks the exit.
    - It re-injects the previous output's context + the original goal back to the AI.
5.  **Completion/Failure**:
    - Loop exits only when targets are met or `--max-iterations` is reached.
    - Logs each iteration's output summary for audit and continuity.

### State Snapshot (`.ralph_state.json`)

```json
{
    "prompt": "Analyze transactions...",
    "completion_promise": "BRIEFING_COMPLETE",
    "target_file": "AI_Employee_Vault/Done/CEO_Briefing.md",
    "max_iterations": 10,
    "current_iteration": 3,
    "history": [
        { "iteration": 1, "output_summary": "...read file A..." },
        { "iteration": 2, "output_summary": "...calculating metrics..." }
    ],
    "status": "active"
}
```
