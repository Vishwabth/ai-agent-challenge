#  Agent-as-Coder Challenge

An autonomous coding agent that writes custom parsers for **bank statement PDFs** — fully self-correcting with up to three test-fix loops.  
This project demonstrates lightweight agentic behavior (plan → generate → test → self-fix) using the **Gemini API**.

---

## Agent Architecture
  ``` bash
    ┌──────────────────────────────┐
    │        agent.py (CLI)        │
    └──────────────┬───────────────┘
                   │
┌──────────────────┴──────────────────┐
│                                     │
[1] plan → generate parser [2] run tests (pytest)
│ │
└───────────► observe & self-fix ◄────┘
(loop ≤ 3 attempts)
```
##  5-Step Run Instructions

### 1️⃣ Clone or Fork this repository
```bash
git clone https://github.com/<your-username>/ai-agent-challenge.git
cd ai-agent-challenge
```
### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Set up your Gemini API key
``` bash
# macOS / Linux
export GEMINI_API_KEY="your_api_key_here"

# Windows (PowerShell)
setx GEMINI_API_KEY "your_api_key_here"

```
### 4️⃣ Run the agent for a target bank
``` bash
python agent.py --target icici --verbose
```
### 5️⃣ Verify the output manually (optional)
``` bash
from custom_parsers.icici_parser import parse
df = parse("data/icici/icici_sample.pdf")
print(df.head())
```
## Folder Structure
``` bash
ai-agent-challenge/
│
├── agent.py                 # Core self-correcting agent logic
├── custom_parsers/          # Auto-generated bank parsers
├── data/                    # Sample PDF and expected CSV files
├── tests/                   # Pytest validation scripts
├── requirements.txt         # Dependencies
└── README.md                # Project documentation
```
## Example Run
``` bash
$ python agent.py --target icici --verbose

--- Attempt 1 ---
[agent] wrote custom_parsers/icici_parser.py
✅ Tests passed.
```
## Summary
``` bash

| Feature       | Description                                                     |
| ------------- | --------------------------------------------------------------- |
|   Framework   | Lightweight SDK + Gemini API                                    |
|   Loop Type   | plan → generate → test → self-correct (≤3 attempts)             |
|   Output      | Fully functional PDF → CSV parser                               |
|   Goal        | Demonstrate autonomous agent behavior with minimal dependencies |
```

