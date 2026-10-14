const form = document.querySelector("#question-form");
const questionInput = document.querySelector("#question");
const sendButton = document.querySelector("#send-button");
const messages = document.querySelector("#messages");
const suggestionButtons = document.querySelectorAll(".suggestion");
const aiEnabled = document.body.dataset.aiEnabled === "true";
const history = [];

function addMessage(role, text, pending = false) {
  const article = document.createElement("article");
  article.className = `message ${role === "user" ? "user-message" : "assistant-message"}`;

  if (role === "assistant") {
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "Py";
    article.append(avatar);
  }

  const content = document.createElement("div");
  content.className = "message-content";
  const author = document.createElement("p");
  author.className = "message-author";
  author.textContent = role === "user" ? "You" : "Python tutor";
  const body = document.createElement("p");
  body.className = "message-text";
  body.textContent = text;
  if (pending) {
    body.classList.add("thinking");
    body.textContent = "Thinking...";
    body.setAttribute("aria-label", "Waiting for an answer");
  }
  content.append(author, body);
  article.append(content);
  messages.append(article);
  article.scrollIntoView({ behavior: "smooth", block: "end" });
  return body;
}

async function askQuestion(question) {
  if (!question || sendButton.disabled) {
    return;
  }

  addMessage("user", question);
  const answerElement = addMessage("assistant", "", true);
  questionInput.value = "";
  questionInput.disabled = true;
  sendButton.disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, history: history.slice(-12) }),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "The question could not be answered.");
    }

    answerElement.classList.remove("thinking");
    answerElement.textContent = result.answer;
    history.push(
      { role: "user", content: question },
      { role: "assistant", content: result.answer },
    );
    history.splice(0, Math.max(0, history.length - 12));
  } catch (error) {
    answerElement.classList.remove("thinking");
    answerElement.classList.add("error-message");
    answerElement.textContent = error instanceof Error
      ? error.message
      : "Something went wrong. Please try again.";
  } finally {
    questionInput.disabled = false;
    sendButton.disabled = false;
    questionInput.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  askQuestion(questionInput.value.trim());
});

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

for (const button of suggestionButtons) {
  button.addEventListener("click", () => {
    askQuestion(button.textContent.trim());
  });
}

if (!aiEnabled) {
  document.querySelector(".disclaimer").title =
    "Responses are limited to the built-in Python knowledge base.";
}
