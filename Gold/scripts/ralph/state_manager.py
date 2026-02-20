# scripts/ralph/state_manager.py
import json
import os
from pathlib import Path
from datetime import datetime

STATE_FILE = Path(".ralph_state.json")

class RalphState:
    def __init__(self, prompt, completion_promise=None, target_file=None, max_iterations=10):
        self.prompt = prompt
        self.completion_promise = completion_promise
        self.target_file = Path(target_file) if target_file else None
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.history = []
        self.status = "active" # active, completed, failed

    def save(self):
        data = {
            "prompt": self.prompt,
            "completion_promise": self.completion_promise,
            "target_file": str(self.target_file) if self.target_file else None,
            "max_iterations": self.max_iterations,
            "current_iteration": self.current_iteration,
            "history": self.history,
            "status": self.status,
            "last_updated": datetime.now().isoformat()
        }
        with open(STATE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load(cls):
        if not STATE_FILE.exists():
            return None
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        
        state = cls(
            data["prompt"],
            data["completion_promise"],
            data["target_file"],
            data["max_iterations"]
        )
        state.current_iteration = data["current_iteration"]
        state.history = data["history"]
        state.status = data["status"]
        return state

    def add_history(self, output):
        self.history.append({
            "iteration": self.current_iteration,
            "timestamp": datetime.now().isoformat(),
            "output_summary": output[-500:] # Keep last 500 chars for context re-injection
        })
        self.current_iteration += 1
        self.save()

    def is_complete(self, last_output):
        # 1. Check for completion promise in output
        if self.completion_promise and self.completion_promise in last_output:
            self.status = "completed"
            return True
        
        # 2. Check if target file moved to /Done
        if self.target_file and "/Done/" in str(self.target_file) and self.target_file.exists():
            self.status = "completed"
            return True
            
        # 3. Check max iterations
        if self.current_iteration >= self.max_iterations:
            self.status = "failed"
            return True
            
        return False
