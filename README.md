# CodeCraft-AI
Creation of code through AI agents

`ai_agents.py` has four AI agents that use OpenAI GPT-4 for intelligent code generation:

* **PlannerAgent:** Breaks down high-level goals into micro-tasks  
* **CodeAgent:** Generates actual code snippets with proper error handling and validation
* **CriticAgent:** Reviews code for logic and performance issues
* **TestAgent:** Creates test cases and validates code

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
export XAI_API_KEY=your_key_here # If you're using Grok
```

## Usage

```bash
python ai_agents.py "create a password validator function" --show-code
python ai_agents.py "build a REST API client class" --save api_client --show-tests
```

The agents leverage real AI for planning, code generation, review, and test creation. Each agent sends specialized prompts to OpenAI to ensure quality output.

## License
[MIT](LICENSE) — use it however you want, just keep the license file and toss some credit my way.
