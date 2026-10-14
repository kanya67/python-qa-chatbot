# Python Q&A Chatbot

A responsive web chatbot for Python learners. It uses an OpenAI tutor when the
server has an API key and the built-in Python knowledge base when it does not.
The original Tkinter desktop interface remains available too.

## Run the web app locally

From PowerShell in this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENAI_API_KEY = "your-OpenAI-API-key"
.\.venv\Scripts\python.exe -m flask --app app run
```

Open `http://127.0.0.1:5000` in a browser. The API key is optional for local
testing; without it, the app answers from the built-in knowledge base.

## Publish a free personal site with Vercel

Vercel's Hobby plan is $0 for personal projects and has usage limits. Check
Vercel's current [pricing](https://vercel.com/pricing) and
[Hobby plan terms](https://vercel.com/docs/limits/overview) before publishing.

1. The project is in the public repository
   [kanya67/python-qa-chatbot](https://github.com/kanya67/python-qa-chatbot).
2. Sign in to [Vercel](https://vercel.com/) with GitHub and choose **Add New
   Project**. Import `kanya67/python-qa-chatbot`, keep the detected Flask
   settings, and deploy.
3. After deployment, Vercel shows a public `vercel.app` address. Share that
   address so people can open the chatbot in their browser.
4. To enable broader AI answers, add `OPENAI_API_KEY` under the project's
   **Settings → Environment Variables** in Vercel, then redeploy. This is
   optional; without it, the website answers using the built-in knowledge base.

Visitors do not need their own API key. If configured, AI requests use the key
belonging to the project owner, and OpenAI API usage may incur separate
charges. Never put the key in the source code or browser. Questions and recent
conversation context are sent to OpenAI when the AI tutor is enabled. Avoid
submitting secrets or sensitive personal information.

The chat endpoint applies a per-client request limit; serverless hosting may
reset in-memory limit counters between instances.

## Run the desktop app

Install the requirements above, set `OPENAI_API_KEY` if you want AI answers,
then run:

```powershell
.\.venv\Scripts\python.exe chatpot.py
```
