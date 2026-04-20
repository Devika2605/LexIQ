# LexIQ React Frontend

A premium dark-themed React frontend for the LexIQ Legal Intelligence system.

## Setup

```powershell
# 1. Install Node.js from https://nodejs.org (LTS version)

# 2. Go to the frontend directory
cd E:\Lexiq\frontend-react

# 3. Install dependencies
npm install

# 4. Start the React app (runs on localhost:3000)
npm start
```

## Running the full stack

```powershell
# Terminal 1 — FastAPI backend (existing)
cd E:\Lexiq
venv\Scripts\activate
python api/main.py

# Terminal 2 — React frontend (new)
cd E:\Lexiq\frontend-react
npm start
```

Then open http://localhost:3000

## Notes
- The React app proxies API calls to http://localhost:8000 (your FastAPI)
- The `proxy` field in package.json handles this automatically
- No changes needed to your existing backend

## Structure
```
frontend-react/
  public/index.html
  src/
    index.js          # Entry point
    index.css         # Global styles + CSS variables
    App.js            # Root layout + sidebar navigation
    components/
      ChatTab.js      # Main Q&A interface
      RiskScanTab.js  # Clause risk scanner
      EvalTab.js      # Evaluation results dashboard
  package.json
```
