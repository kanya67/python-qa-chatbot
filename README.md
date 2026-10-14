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

## Live demo

The hosted live demo for this app is:

https://python-qa-chatbot.onrender.com/

This is the default Render URL for the app name `python-qa-chatbot`. After the
Render service is created, the live site will be available there.

## Publish a free public website with GitHub Pages

The public GitHub repository includes a static website in the root
`index.html`. GitHub Pages can host this site for free from a public repository.
It uses the built-in Python answers and does not require a server, API key, or
visitor login. It does not provide AI-generated answers.

To publish it, open the repository's **Settings → Pages**. Under **Build and
deployment**, select **Deploy from a branch**, choose the `main` branch and
`/(root)` folder, and click **Save**. GitHub will build the site and show its
public URL on the Pages settings screen. Share that URL so everyone can open
the chatbot in a browser.

The Flask server and desktop app remain available for local use. To deploy
those versions with AI answers instead, use a Python web host and keep the
OpenAI API key in that host's private environment settings. OpenAI API usage
may incur separate charges.

## Deploy the full app on Render (free)

This project includes a Render configuration that works with the Flask app on
the free tier. Push this repository to GitHub, then in Render choose **New →
Web Service**, select the repository, and use the default settings. Render will
install the Python dependencies and start the app with the included
`render.yaml` file.

Set the `OPENAI_API_KEY` environment variable in the Render dashboard if you
want AI responses; if it is missing, the app automatically falls back to the
built-in Python knowledge base.

## Run the desktop app

Install the requirements above, set `OPENAI_API_KEY` if you want AI answers,
then run:

```powershell
.\.venv\Scripts\python.exe chatpot.py
```
