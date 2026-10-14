const form = document.querySelector("#question-form");
const questionInput = document.querySelector("#question");
const sendButton = document.querySelector("#send-button");
const messages = document.querySelector("#messages");
const suggestionButtons = document.querySelectorAll(".suggestion");

const knowledgeBase = [
  {
    keywords: ["what is python", "python programming language"],
    answer: "Python is a high-level, general-purpose programming language known for readable syntax and a broad ecosystem of libraries.",
  },
  {
    keywords: ["variable", "variables", "assign a value"],
    answer: "Create a variable by assigning a value, for example: `count = 3`. Python infers the value's type; you do not declare it separately.",
  },
  {
    keywords: ["data type", "data types", "string", "integer", "float", "boolean"],
    answer: "Common built-in types include `int` (whole numbers), `float` (decimal numbers), `str` (text), and `bool` (`True` or `False`). Use `type(value)` to inspect a value's type.",
  },
  {
    keywords: ["list", "lists", "array"],
    answer: "A list is an ordered, mutable collection. Create one with `items = [1, 2, 3]`; access an item by index, such as `items[0]`, and add an item with `items.append(4)`.",
  },
  {
    keywords: ["tuple", "tuples"],
    answer: "A tuple is an ordered, immutable collection. Create one with `point = (3, 4)`. Use a tuple when the collection should not be changed after creation.",
  },
  {
    keywords: ["dictionary", "dictionaries", "dict", "key value"],
    answer: "A dictionary stores key-value pairs. For example, `person = {'name': 'Ada'}` and `person['name']` reads the value. Use `person.get('age')` when a key may be absent.",
  },
  {
    keywords: ["set", "sets"],
    answer: "A set is an unordered collection of unique values. Create one with `colors = {'red', 'blue'}`. Sets are useful for removing duplicates and checking membership.",
  },
  {
    keywords: ["if statement", "conditional", "conditionals", "else"],
    answer: "Use `if`, `elif`, and `else` to choose which code runs, for example:\n`if score >= 60:`\n`    print('pass')`\n`else:`\n`    print('try again')`",
  },
  {
    keywords: ["for loop", "for loops", "loop", "loops", "while loop"],
    answer: "Use a `for` loop to iterate over items, for example `for name in names: print(name)`. Use a `while` loop when repetition should continue until a condition changes.",
  },
  {
    keywords: ["function", "functions", "def"],
    answer: "Define a function with `def` and return a result with `return`, for example:\n`def add(a, b):`\n`    return a + b`",
  },
  {
    keywords: ["class", "classes", "object oriented"],
    answer: "A class defines a type of object, including its data and behavior. For example:\n`class Dog:`\n`    def __init__(self, name):`\n`        self.name = name`",
  },
  {
    keywords: ["exception", "exceptions", "error handling", "try except"],
    answer: "Handle expected errors with `try` and `except`, for example:\n`try:`\n`    number = int(text)`\n`except ValueError:`\n`    print('Please enter a whole number')`",
  },
  {
    keywords: ["module", "modules", "import"],
    answer: "A module is a Python file or library you can reuse. Load one with `import math`, then call its functions, such as `math.sqrt(9)`. Use `from math import sqrt` to import a specific name.",
  },
  {
    keywords: ["pip", "install package", "install packages"],
    answer: "Use `python -m pip install package_name` to install a package. Running pip through `python -m` helps ensure it uses the intended Python interpreter.",
  },
  {
    keywords: ["virtual environment", "venv", "environment"],
    answer: "A virtual environment keeps a project's packages isolated. Create one with `python -m venv .venv`, then activate it using the command for your operating system before installing project packages.",
  },
  {
    keywords: ["list comprehension", "comprehension"],
    answer: "A list comprehension builds a list from an iterable concisely. For example, `[n * n for n in numbers if n > 0]` makes the squares of the positive numbers.",
  },
];

function words(text) {
  return text.toLowerCase().match(/[a-z0-9_]+/g) || [];
}

function containsPhrase(inputWords, phrase) {
  const phraseWords = words(phrase);
  return inputWords.some((_, index) =>
    phraseWords.every((word, offset) => inputWords[index + offset] === word),
  );
}

function answerQuestion(question) {
  const inputWords = words(question);
  if (inputWords.length === 0) {
    return "Please enter a Python question.";
  }

  const hasList = inputWords.some((word) => word === "list" || word === "lists");
  const hasTuple = inputWords.some((word) => word === "tuple" || word === "tuples");
  const comparesCollections =
    inputWords.some((word) =>
      ["difference", "differences", "compare", "compared", "versus", "vs"].includes(word),
    );
  if (
    containsPhrase(inputWords, "difference between list and tuple") ||
    (hasList && hasTuple && comparesCollections)
  ) {
    return "Both lists and tuples are ordered collections. Lists are mutable (for example, `[1, 2]`), while tuples are immutable (for example, `(1, 2)`). Choose a list when items need to change and a tuple when they should remain fixed.";
  }

  const matches = knowledgeBase.flatMap((entry) => {
    const keywords = entry.keywords.filter((keyword) =>
      containsPhrase(inputWords, keyword),
    );
    return keywords.length > 0
      ? [{
          score: keywords.reduce((total, keyword) => total + words(keyword).length, 0),
          answer: entry.answer,
        }]
      : [];
  });
  matches.sort((left, right) => right.score - left.score);

  return matches[0]?.answer ||
    "I don't know that one yet. Try Python basics, variables, data types, collections, loops, functions, classes, exceptions, modules, pip, virtual environments, or list comprehensions.";
}

function addMessage(role, text) {
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
  content.append(author, body);
  article.append(content);
  messages.append(article);
  article.scrollIntoView({ behavior: "smooth", block: "end" });
}

function askQuestion(question) {
  if (!question || sendButton.disabled) {
    return;
  }

  addMessage("user", question);
  const answer = question.toLowerCase() === "help" ||
      question.toLowerCase() === "topics"
    ? "Try asking about variables, data types, lists, tuples, dictionaries, sets, conditionals, loops, functions, classes, exceptions, modules, pip, virtual environments, or list comprehensions."
    : answerQuestion(question);
  addMessage("assistant", answer);
  questionInput.value = "";
  questionInput.focus();
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
