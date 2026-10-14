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

## Publish for everyone with Render

1. Push this project to a GitHub repository. Do not include `.venv` or an API
   key in the repository.
2. In Render, create a **Blueprint** and connect that repository. Render reads
   `render.yaml` to build and run the web service.
3. In the service's environment settings, set `OPENAI_API_KEY` to an API key
   you created in your OpenAI account. Keep the key private and only enter it
   as a Render secret; never put it in browser code or source control.
4. Wait for the deployment to finish, then share the public `onrender.com`
   address shown by Render.

If `OPENAI_API_KEY` is not set in Render, the public website still works with
the built-in answers, but it cannot provide broader AI answers. Visitors do not
need their own API key; AI requests use the key configured by the service
owner, and any resulting OpenAI charges are billed to that owner's account.
The chat endpoint limits each client to 15 requests per minute.

Questions and conversation context sent while AI answers are enabled are
forwarded to OpenAI. Avoid submitting secrets or sensitive personal
information.

## Run the desktop app

Install the requirements above, set `OPENAI_API_KEY` if you want AI answers,
then run:

```powershell
.\.venv\Scripts\python.exe chatpot.py
```
