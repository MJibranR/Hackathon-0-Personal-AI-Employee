# scripts/ralph/stop_hook.py
import sys
import os
import json
from pathlib import Path
import subprocess
from .state_manager import RalphState

def ralph_stop_hook(last_output):
    """
    Ralph Wiggum Stop Hook implementation.
    Intercepts Claude's exit and decides whether to allow exit or re-inject prompt.
    """
    state = RalphState.load()
    if not state or state.status != "active":
        # No active loop, allow exit
        return True

    print(f"
--- Ralph Hook [Iteration {state.current_iteration}/{state.max_iterations}] ---")
    
    # 1. Check for completion or failure
    if state.is_complete(last_output):
        if state.status == "completed":
            print(f"Task successfully completed: {state.completion_promise or state.target_file}")
            # Mark state as done
            state.status = "done"
            state.save()
            return True # Allow exit
        else:
            print(f"Loop failed: Maximum iterations ({state.max_iterations}) reached.")
            state.status = "failed"
            state.save()
            return True # Allow exit (with failure log)

    # 2. Add last output to context history
    state.add_history(last_output)
    
    # 3. Task is incomplete, block exit and re-inject
    print("Task incomplete. Re-injecting context and continuing autonomous loop...")
    
    # In a real environment, this hook would feed back to the Claude process
    # Re-inject the original prompt + previous output summary for context continuity
    context_reinjection = f"""
I am continuing the autonomous loop (Ralph Wiggum pattern).
Previous attempt summary: {state.history[-1]['output_summary']}
Continue until {state.completion_promise or 'file is moved to /Done'}.
Remaining iterations: {state.max_iterations - state.current_iteration}
    """
    
    # We block exit by returning False and triggering another 'run' call
    # This logic depends on the CLI wrapper implementation.
    return False 
