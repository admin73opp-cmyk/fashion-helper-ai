# Fashion Helper AI Proxy Server

A lightweight FastAPI server that proxies AI requests to OpenAI, keeping the API key server-side.

## Local Development

```bash
cd server
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key-here"
python main.py
```

Server runs at http://localhost:8080

## Deploy to Render (free tier)

1. Push this repo to GitHub
2. Go to render.com → New → Web Service
3. Connect your GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 8080`
   - Environment Variable: `OPENAI_API_KEY` = your key
5. Deploy

## Deploy to Railway

```bash
railway login
railway init
railway variables set OPENAI_API_KEY=sk-your-key-here
railway up
```

## API Endpoints

### GET /health
Returns server status and whether the API key is configured.

```json
{"status": "ok", "has_key": true}
```

### POST /suggest
Send an AI prompt, get a suggestion back.

Request:
```json
{
  "prompt": "Suggest an outfit for a casual brunch",
  "model": "gpt-4o",
  "max_tokens": 500
}
```

Response:
```json
{
  "suggestion": "1. White linen shirt — relaxed fit...",
  "model": "gpt-4o"
}
```

## iOS App Configuration

In the Fashion Helper app, go to Profile → AI Server → enter your server URL.
