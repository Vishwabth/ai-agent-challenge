import argparse, os, subprocess, sys
from pathlib import Path
import google.generativeai as genai
import re
import ssl
ROOT, PKG, TESTS = Path(__file__).parent, Path("custom_parsers"), Path("tests")
ssl._create_default_https_context = ssl._create_unverified_context

def ensure_pkg():
    PKG.mkdir(exist_ok=True); (PKG / "__init__.py").write_text("", "utf-8")
    TESTS.mkdir(exist_ok=True)
    cf = TESTS / "conftest.py"
    if not cf.exists():
        cf.write_text("import sys, pathlib; sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))")

def run_pytest(target, verbose=False):
    testf = ROOT / f"tests/test_{target}.py"
    cmd = ["pytest", "-q", str(testf if testf.exists() else "tests")]
    out = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(ROOT)})
    if verbose: print(out.stdout, out.stderr)
    return out.returncode == 0, out.stdout + out.stderr

def gen_parser(target, attempt, log=""):
    prompt = f"""
Write valid Python code for custom_parsers/{target}_parser.py.

Requirements:
- Must start with imports (pandas, pdfplumber).
- Implement: def parse(pdf_path: str) -> pandas.DataFrame
- Extract tables from the PDF (use pdfplumber).
- Always return a DataFrame with columns ['Date','Description','Debit Amt','Credit Amt','Balance'].
- Normalize headers by mapping:
    * 'Debit Amt','Withdrawal Amt' → 'Debit Amt'
    * 'Credit Amt','Deposit Amt'   → 'Credit Amt'
    * 'Balance','Closing Balance'  → 'Balance'
    * 'Description','Narration','Particulars' → 'Description'
    * 'Date','Txn Date','Transaction Date' → 'Date'
- Keep Debit Amt/Credit Amt as floats where possible, blank where empty.
- Balance: numeric float, NaN allowed.
- Do not use pd.NA in type hints. Use Optional[float] instead of Union[float, pd.NA].
- Date: parsed to DD-MM-YYYY string (dayfirst=True).
- If no valid transactions, return pd.DataFrame(columns=['Date','Description','Debit Amt','Credit Amt','Balance']).
- Output ONLY valid Python code.
Attempt {attempt}. Previous errors:\n{log}
"""

    model = genai.GenerativeModel("models/gemini-flash-latest")
    resp = model.generate_content(prompt)
    code = resp.candidates[0].content.parts[0].text
    cleaned = []
    for line in code.splitlines():
        if line.strip().startswith("```"):
            continue
        cleaned.append(line)
    code = "\n".join(cleaned).strip()

    schema_patch = """# --- Final Schema Enforcement ---
required = ["Date", "Description", "Debit Amt", "Credit Amt", "Balance"]
for col in required:
    if col not in df_final.columns:
        df_final[col] = "" if col in ("Date","Description") else 0.0 if col in ("Debit Amt","Credit Amt") else pd.NA

# Reorder
df_final = df_final[required]
return df_final"""
    match = re.search(r"^(\s*)return\s+(df\w*)", code, flags=re.MULTILINE)
    if match:
        indent = match.group(1)
        df_var = match.group(2) 
        indented_patch = schema_patch.replace("df_final", df_var)
        indented_patch = "\n".join(indent + line if line.strip() else "" for line in indented_patch.splitlines())
        code = re.sub(r"^(\s*)return\s+%s[^\n]*" % df_var, indented_patch, code, flags=re.MULTILINE)

    path = PKG / f"{target}_parser.py"
    path.write_text(code, "utf-8")
    print(f"[agent] wrote {path}")
    return path

def loop(state):
    while state["attempt"] <= state["max_attempts"]:
        print(f"\n--- Attempt {state['attempt']} ---")
        gen_parser(state["target"], state["attempt"], state.get("log", ""))
        ok, log = run_pytest(state["target"], state["verbose"])
        if ok: print("Tests passed."); return True
        state.update(attempt=state["attempt"]+1, log=log)
        print("Failed, retrying...")
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    ensure_pkg()
    state = {"target": args.target.lower(), "attempt": 1,
             "max_attempts": args.max_attempts, "verbose": args.verbose}
    sys.exit(0 if loop(state) else 1)

if __name__ == "__main__": main()
