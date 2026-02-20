import os
import re
import datetime
import json
from pathlib import Path
from collections import defaultdict

# --- Configuration & Paths ---
VAULT_PATH = Path("AI_Employee_Vault")
GOALS_FILE = VAULT_PATH / "Business_Goals.md"
ACCOUNTING_DIR = VAULT_PATH / "Accounting"
BRIEFINGS_DIR = VAULT_PATH / "Briefings"
DONE_DIR = VAULT_PATH / "Done"
LOGS_DIR = VAULT_PATH / "Logs"

# --- Patterns & Logic ---
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Netflix',
    'spotify.com': 'Spotify',
    'adobe.com': 'Adobe Creative Cloud',
    'notion.so': 'Notion',
    'slack.com': 'Slack',
    'aws.amazon.com': 'AWS',
    'openai.com': 'OpenAI',
    'zoho.com': 'Zoho Books',
    'odoo.com': 'Odoo',
    'stripe.com': 'Stripe',
    'upwork.com': 'Upwork'
}

TOOL_CATEGORIES = {
    'Notion': 'Productivity',
    'Slack': 'Productivity',
    'Adobe Creative Cloud': 'Design',
    'AWS': 'Infrastructure',
    'OpenAI': 'AI',
    'Zoho Books': 'Accounting',
    'Odoo': 'Accounting',
    'Stripe': 'Payment Gateway',
    'Upwork': 'Freelance'
}

class CEOBriefingGenerator:
    def __init__(self):
        self.goals = {}
        self.transactions = []
        self.completed_tasks = []
        self.logs = []
        self.today = datetime.date.today()
        self.briefing_date = self.today.strftime("%Y-%m-%d")

    def load_business_goals(self):
        """Parses Business_Goals.md for targets and metrics."""
        if not GOALS_FILE.exists():
            return
        
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
        revenue_match = re.search(r'Monthly goal: \$([\d,]+)', content)
        if revenue_match:
            self.goals['revenue_target'] = float(revenue_match.group(1).replace(',', ''))

    def load_accounting_data(self):
        """Parses current month's transactions."""
        current_month_file = ACCOUNTING_DIR / "Current_Month.md"
        if not current_month_file.exists():
            files = list(ACCOUNTING_DIR.glob("*.md"))
            if files:
                current_month_file = max(files, key=os.path.getmtime)
            else:
                return

        with open(current_month_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            if '|' in line and '---' not in line and 'Date' not in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 3:
                    try:
                        date_str, desc, amount_str = parts[0], parts[1], parts[2]
                        amount = float(amount_str.replace('$', '').replace(',', ''))
                        self.transactions.append({
                            'date': date_str,
                            'description': desc,
                            'amount': amount,
                            'category': parts[3] if len(parts) > 3 else 'Uncategorized'
                        })
                    except ValueError:
                        continue

    def load_logs(self):
        """Loads recent logs for activity analysis."""
        cutoff = self.today - datetime.timedelta(days=30)
        if not LOGS_DIR.exists():
            return
            
        for log_file in LOGS_DIR.glob("*.jsonl"):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if 'timestamp' in entry:
                            ts_str = entry['timestamp'].split('T')[0]
                            entry_date = datetime.date.fromisoformat(ts_str)
                            if entry_date >= cutoff:
                                self.logs.append(entry)
                    except (json.JSONDecodeError, ValueError, KeyError):
                        continue

    def analyze_subscriptions(self):
        seen_tools = defaultdict(list)
        
        for txn in self.transactions:
            # Skip income transactions for subscription audit
            if txn['amount'] > 0:
                continue

            desc_lower = txn['description'].lower()
            for pattern, tool_name in SUBSCRIPTION_PATTERNS.items():
                if pattern.lower() in desc_lower or tool_name.lower() in desc_lower:
                    seen_tools[tool_name].append(txn)
                    break
        
        analysis = []
        for tool, txns in seen_tools.items():
            category = TOOL_CATEGORIES.get(tool, 'Other')
            
            # Calculate average cost (absolute value)
            avg_cost = sum(abs(t['amount']) for t in txns) / len(txns)
            cost_alert = avg_cost > 100 
            
            # Check for Login Activity
            has_login = False
            if self.logs:
                has_login = any(tool.lower() in json.dumps(log).lower() for log in self.logs)
            else:
                pass
            
            login_alert = not has_login
            
            analysis.append({
                'tool': tool,
                'category': category,
                'cost': avg_cost,
                'cost_alert': cost_alert,
                'login_alert': login_alert
            })
            
        return analysis

    def check_duplicate_tools(self, sub_analysis):
        duplicates = defaultdict(list)
        for item in sub_analysis:
            if item['category'] != 'Other':
                duplicates[item['category']].append(item['tool'])
        return {k: v for k, v in duplicates.items() if len(v) > 1}

    def generate_report(self):
        self.load_business_goals()
        self.load_accounting_data()
        self.load_logs()
        
        # --- Metrics ---
        total_revenue = sum(t['amount'] for t in self.transactions if t['amount'] > 0)
        total_expenses = sum(abs(t['amount']) for t in self.transactions if t['amount'] < 0)
        
        target = self.goals.get('revenue_target', 10000.0) 
        mtd_pct = (total_revenue / target) * 100 if target else 0
        
        # --- Analysis ---
        sub_analysis = self.analyze_subscriptions()
        duplicate_tools = self.check_duplicate_tools(sub_analysis)
        completed_count = len(list(DONE_DIR.glob("*.md"))) if DONE_DIR.exists() else 0
        
        # --- Report Content ---
        report = f"""---
type: briefing
date: {self.briefing_date}
tags: #briefing #ceo
---

# Monday Morning CEO Briefing: {self.briefing_date}

## 1. Executive Summary
- **Revenue MTD**: ${total_revenue:,.2f} ({mtd_pct:.1f}% of ${target:,.0f} Target)
- **Expenses MTD**: ${total_expenses:,.2f}
- **Net Income**: ${total_revenue - total_expenses:,.2f}

## 2. Subscription Audit
### Active Subscriptions
| Tool | Category | Cost | Usage Alert | Cost Alert |
|------|----------|------|-------------|------------|
"""
        for item in sub_analysis:
            usage_flag = "⚠️ No Login 30d" if item['login_alert'] else "✅ Active"
            cost_flag = "⚠️ High Cost" if item['cost_alert'] else "OK"
            report += f"| {item['tool']} | {item['category']} | ${item['cost']:.2f} | {usage_flag} | {cost_flag} |\n"

        if duplicate_tools:
            report += "\n### ⚠️ Redundancy Alert\n"
            for cat, tools in duplicate_tools.items():
                report += f"- **{cat}**: Multiple tools detected ({', '.join(tools)}). Consider consolidating.\n"

        report += f"""
## 3. Bottlenecks & Productivity
- **Tasks Completed this week**: {completed_count}

## 4. Proactive Suggestions
"""
        if mtd_pct < 50 and self.today.day > 15:
            report += f"- 📉 **Revenue Alert**: Revenue is below 50% mid-month (${total_revenue:,.2f}). Follow up on outstanding invoices.\n"
        
        for item in sub_analysis:
            if item['login_alert']:
                report += f"- 💸 **Unused Sub**: **{item['tool']}** flagged for inactivity. Potential savings: ${item['cost']:.2f}/mo.\n"

        report += "\n---\n*Generated by AI Employee Auto-Audit System*"
        
        BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
        filename = BRIEFINGS_DIR / f"{self.briefing_date}_Monday_Briefing.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filename

if __name__ == "__main__":
    generator = CEOBriefingGenerator()
    path = generator.generate_report()
    print(f"Briefing generated at: {path}")
