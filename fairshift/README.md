# FairShift Hackathon Prototype

## Run on Windows / VS Code
1. Install Python 3.10+.
2. Extract the ZIP and open the `fairshift` folder in VS Code.
3. In the VS Code PowerShell terminal run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If activation is blocked, run these instead:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

4. Open http://127.0.0.1:5000.

## 2-minute demo
1. Worker Portal → Construction → Check in.
2. Submit a sample safety report.
3. Employer Dashboard → set report status to In Progress or Resolved.
4. Switch the industry to College.
5. Explain salary is an illustrative estimate and attendance uses server time.

## Honest prototype limits
No login/role access control, GPS/QR verification, anonymous reporting, voice input, real payroll or full translation. Use only sample data; do not enter sensitive information. The pay estimate is a demo rule, not a legal/payroll calculation.
