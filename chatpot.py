"""Desktop interface for the Python Q&A chatbot."""

import os
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam

from chatbot_core import answer_question, ask_openai


def main() -> None:
    root = tk.Tk()
    root.title("Python Q&A Chatbot")
    root.geometry("680x560")
    root.minsize(480, 380)
    root.configure(bg="#f3f4f6")

    header = tk.Label(
        root,
        text="Python Q&A Chatbot",
        font=("Segoe UI", 18, "bold"),
        bg="#f3f4f6",
        fg="#1f2937",
        pady=16,
    )
    header.pack()

    chat = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        state=tk.DISABLED,
        font=("Segoe UI", 11),
        padx=14,
        pady=12,
        bg="white",
        fg="#1f2937",
        relief=tk.FLAT,
        borderwidth=0,
    )
    chat.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 14))
    chat.tag_configure("user", foreground="#2563eb", spacing1=8, spacing3=4)
    chat.tag_configure("bot", foreground="#15803d", spacing1=8, spacing3=12)

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None
    conversation: list[ChatCompletionMessageParam] = []
    pending_answers: queue.Queue[tuple[str, str, str]] = queue.Queue()

    def add_message(sender: str, message: str, tag: str) -> None:
        chat.configure(state=tk.NORMAL)
        chat.insert(tk.END, f"{sender}: {message}\n\n", tag)
        chat.configure(state=tk.DISABLED)
        chat.see(tk.END)

    add_message(
        "Chatbot",
        (
            "Hi! Ask me any Python question. AI answers are enabled."
            if client
            else "Hi! Ask me a Python question. Built-in topics work offline; "
            "for broader AI answers, set the OPENAI_API_KEY environment "
            "variable and restart the app."
        ),
        "bot",
    )

    controls = tk.Frame(root, bg="#f3f4f6")
    controls.pack(fill=tk.X, padx=18, pady=(0, 18))
    question_input = tk.Entry(
        controls,
        font=("Segoe UI", 11),
        relief=tk.SOLID,
        borderwidth=1,
    )
    question_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=9)

    def send_question(_event: tk.Event | None = None) -> None:
        del _event
        question = question_input.get().strip()
        if not question:
            return

        question_input.delete(0, tk.END)
        add_message("You", question, "user")
        if question.lower() in {"help", "topics"}:
            add_message(
                "Chatbot",
                "Try asking about variables, data types, lists, tuples, "
                "dictionaries, sets, conditionals, loops, functions, classes, "
                "exceptions, modules, pip, virtual environments, or list "
                "comprehensions.",
                "bot",
            )
            return

        if client is None:
            add_message(
                "Chatbot",
                "Offline knowledge-base answer: " + answer_question(question),
                "bot",
            )
            return

        send_button.configure(state=tk.DISABLED)
        question_input.configure(state=tk.DISABLED)

        def get_answer() -> None:
            try:
                answer = ask_openai(client, question, conversation)
            except (OpenAIError, RuntimeError) as error:
                pending_answers.put(("error", question, str(error)))
            else:
                pending_answers.put(("answer", question, answer))

        threading.Thread(target=get_answer, daemon=True).start()

    def check_pending_answers() -> None:
        try:
            result, question, content = pending_answers.get_nowait()
        except queue.Empty:
            pass
        else:
            if result == "answer":
                conversation.extend(
                    [
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": content},
                    ]
                )
                add_message("Chatbot", content, "bot")
            else:
                add_message(
                    "Chatbot",
                    "OpenAI request failed. Check your internet connection "
                    "and API key, then try again.\nDetails: " + content,
                    "bot",
                )
            send_button.configure(state=tk.NORMAL)
            question_input.configure(state=tk.NORMAL)
            question_input.focus_set()
        root.after(100, check_pending_answers)

    send_button = tk.Button(
        controls,
        text="Send",
        command=send_question,
        font=("Segoe UI", 10, "bold"),
        bg="#2563eb",
        fg="white",
        activebackground="#1d4ed8",
        activeforeground="white",
        relief=tk.FLAT,
        padx=18,
        pady=8,
        cursor="hand2",
    )
    send_button.pack(side=tk.LEFT, padx=(10, 0))
    question_input.bind("<Return>", send_question)
    question_input.focus_set()
    check_pending_answers()

    root.mainloop()


if __name__ == "__main__":
    main()
