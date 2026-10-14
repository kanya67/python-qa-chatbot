"""Shared Python-question matching and AI-answering logic."""

from dataclasses import dataclass
import re

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


@dataclass(frozen=True)
class KnowledgeEntry:
    keywords: tuple[str, ...]
    answer: str


KNOWLEDGE_BASE = (
    KnowledgeEntry(
        ("what is python", "python programming language"),
        "Python is a high-level, general-purpose programming language known for "
        "readable syntax and a broad ecosystem of libraries.",
    ),
    KnowledgeEntry(
        ("variable", "variables", "assign a value"),
        "Create a variable by assigning a value, for example: `count = 3`. "
        "Python infers the value's type; you do not declare it separately.",
    ),
    KnowledgeEntry(
        ("data type", "data types", "string", "integer", "float", "boolean"),
        "Common built-in types include `int` (whole numbers), `float` "
        "(decimal numbers), `str` (text), and `bool` (`True` or `False`). "
        "Use `type(value)` to inspect a value's type.",
    ),
    KnowledgeEntry(
        ("list", "lists", "array"),
        "A list is an ordered, mutable collection. Create one with "
        "`items = [1, 2, 3]`; access an item by index, such as `items[0]`, "
        "and add an item with `items.append(4)`.",
    ),
    KnowledgeEntry(
        ("tuple", "tuples"),
        "A tuple is an ordered, immutable collection. Create one with "
        "`point = (3, 4)`. Use a tuple when the collection should not be "
        "changed after creation.",
    ),
    KnowledgeEntry(
        ("dictionary", "dictionaries", "dict", "key value"),
        "A dictionary stores key-value pairs. For example, "
        "`person = {'name': 'Ada'}` and `person['name']` reads the value. "
        "Use `person.get('age')` when a key may be absent.",
    ),
    KnowledgeEntry(
        ("set", "sets"),
        "A set is an unordered collection of unique values. Create one with "
        "`colors = {'red', 'blue'}`. Sets are useful for removing duplicates "
        "and checking membership.",
    ),
    KnowledgeEntry(
        ("if statement", "conditional", "conditionals", "else"),
        "Use `if`, `elif`, and `else` to choose which code runs, for example:\n"
        "`if score >= 60:`\n"
        "`    print('pass')`\n"
        "`else:`\n"
        "`    print('try again')`",
    ),
    KnowledgeEntry(
        ("for loop", "for loops", "loop", "loops", "while loop"),
        "Use a `for` loop to iterate over items, for example "
        "`for name in names: print(name)`. Use a `while` loop when repetition "
        "should continue until a condition changes.",
    ),
    KnowledgeEntry(
        ("function", "functions", "def"),
        "Define a function with `def` and return a result with `return`, "
        "for example:\n`def add(a, b):`\n`    return a + b`",
    ),
    KnowledgeEntry(
        ("class", "classes", "object oriented"),
        "A class defines a type of object, including its data and behavior. "
        "For example:\n`class Dog:`\n`    def __init__(self, name):`\n"
        "`        self.name = name`",
    ),
    KnowledgeEntry(
        ("exception", "exceptions", "error handling", "try except"),
        "Handle expected errors with `try` and `except`, for example:\n"
        "`try:`\n`    number = int(text)`\n`except ValueError:`\n"
        "`    print('Please enter a whole number')`",
    ),
    KnowledgeEntry(
        ("module", "modules", "import"),
        "A module is a Python file or library you can reuse. Load one with "
        "`import math`, then call its functions, such as `math.sqrt(9)`. "
        "Use `from math import sqrt` to import a specific name.",
    ),
    KnowledgeEntry(
        ("pip", "install package", "install packages"),
        "Use `python -m pip install package_name` to install a package. "
        "Running pip through `python -m` helps ensure it uses the intended "
        "Python interpreter.",
    ),
    KnowledgeEntry(
        ("virtual environment", "venv", "environment"),
        "A virtual environment keeps a project's packages isolated. Create "
        "one with `python -m venv .venv`, then activate it using the command "
        "for your operating system before installing project packages.",
    ),
    KnowledgeEntry(
        ("list comprehension", "comprehension"),
        "A list comprehension builds a list from an iterable concisely. "
        "For example, `[n * n for n in numbers if n > 0]` makes the squares "
        "of the positive numbers.",
    ),
    KnowledgeEntry(
        ("difference between list and tuple", "list versus tuple",
         "list vs tuple"),
        "Both lists and tuples are ordered collections. Lists are mutable "
        "(for example, `[1, 2]`), while tuples are immutable "
        "(for example, `(1, 2)`). Choose a list when items need to change "
        "and a tuple when they should remain fixed.",
    ),
)


def _words(text: str) -> tuple[str, ...]:
    """Normalize text into words so punctuation and capitalization do not matter."""
    return tuple(re.findall(r"[a-z0-9_]+", text.lower()))


def _contains_phrase(words: tuple[str, ...], phrase: str) -> bool:
    phrase_words = _words(phrase)
    width = len(phrase_words)
    return any(words[index:index + width] == phrase_words
               for index in range(len(words) - width + 1))


def answer_question(question: str) -> str:
    """Return a matching answer from the predefined Python knowledge base."""
    words = _words(question)
    if not words:
        return "Please enter a Python question, or type `help` to see example topics."

    has_list = any(word in words for word in ("list", "lists"))
    has_tuple = any(word in words for word in ("tuple", "tuples"))
    if _contains_phrase(words, "difference between list and tuple") or (
        has_list and has_tuple
        and any(word in words for word in ("difference", "differences", "compare",
                                            "compared", "versus", "vs"))
    ):
        return KNOWLEDGE_BASE[-1].answer

    matches = []
    for entry in KNOWLEDGE_BASE[:-1]:
        matched_keywords = [
            keyword for keyword in entry.keywords
            if _contains_phrase(words, keyword)
        ]
        if matched_keywords:
            score = sum(len(_words(keyword)) for keyword in matched_keywords)
            matches.append((score, entry.answer))

    if matches:
        return max(matches, key=lambda match: match[0])[1]
    return (
        "I don't know that one yet. I can help with Python basics, variables, "
        "data types, collections, loops, functions, classes, exceptions, "
        "modules, pip, virtual environments, and list comprehensions."
    )


def ask_openai(
    client: OpenAI,
    question: str,
    conversation: list[ChatCompletionMessageParam],
) -> str:
    """Ask OpenAI a Python question, including earlier turns for context."""
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are a friendly Python programming tutor. Answer Python "
                "questions clearly and accurately, with concise examples "
                "when useful. If a question is unrelated to Python, briefly "
                "ask the user to keep the conversation Python-focused."
            ),
        },
        *conversation,
        {"role": "user", "content": question},
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    if not response.choices:
        raise RuntimeError("OpenAI returned no answer choices.")
    answer = response.choices[0].message.content
    if not answer or not answer.strip():
        raise RuntimeError("OpenAI returned an empty answer.")
    return answer.strip()
