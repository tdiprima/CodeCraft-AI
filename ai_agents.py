#!/usr/bin/env python3
"""
AI Agent System for Code Generation using OpenAI API
Four specialized agents that use OpenAI to generate quality code from prompts.

Author: Tammy DiPrima
"""

import os
import json
import argparse
from openai import OpenAI


class AIAgent:
    """Base AI agent that uses OpenAI API"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        # self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
    
    def call_openai(self, prompt: str, system_message: str) -> str:
        """Make API call to OpenAI"""
        try:
            response = self.client.chat.completions.create(
                # model="gpt-4.1-nano",
                model="grok-4-0709",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"


class PlannerAgent(AIAgent):
    """Breaks down high-level goals into micro-tasks"""
    
    def __init__(self):
        super().__init__("PlannerAgent", "Task Planner")
    
    def process(self, prompt: str) -> list:
        system_msg = """You are a task planning expert. Break down programming requests into 3-5 specific, actionable micro-tasks. 
        Return as JSON array with format: [{"id": "1", "task": "description", "priority": "high/medium/low"}]"""
        
        response = self.call_openai(prompt, system_msg)
        try:
            return json.loads(response)
        except:
            # Fallback if JSON parsing fails
            return [{"id": "1", "task": "Analyze requirements", "priority": "high"},
                   {"id": "2", "task": "Implement solution", "priority": "high"}]


class CodeAgent(AIAgent):
    """Generates actual code snippets"""
    
    def __init__(self):
        super().__init__("CodeAgent", "Code Generator")
    
    def process(self, prompt: str, tasks: list) -> dict:
        task_summary = "\n".join([f"- {task['task']}" for task in tasks])
        
        system_msg = f"""You are an expert programmer. Generate clean, well-documented code based on this request.
        
        Tasks to implement:
        {task_summary}
        
        Requirements:
        - Include error handling
        - Add input validation
        - Use clear variable names
        - Add docstrings/comments
        - Return only the code, no explanations"""
        
        code = self.call_openai(prompt, system_msg)
        
        # Detect language
        language = "python"
        if any(keyword in code.lower() for keyword in ["function", "const", "let", "var"]):
            language = "javascript"
        elif any(keyword in code.lower() for keyword in ["public class", "private", "import java"]):
            language = "java"
        
        return {
            "code": code,
            "language": language,
            "description": prompt[:100] + "..."
        }


class CriticAgent(AIAgent):
    """Reviews code for logic and performance issues"""
    
    def __init__(self):
        super().__init__("CriticAgent", "Code Reviewer")
    
    def process(self, code_result: dict) -> dict:
        system_msg = """You are a senior code reviewer. Analyze the code for:
        - Logic errors
        - Security issues
        - Performance problems
        - Code quality issues
        - Missing error handling
        
        Return JSON format:
        {
            "score": 1-10,
            "issues": ["list of issues found"],
            "suggestions": ["list of improvements"],
            "approved": true/false
        }"""
        
        prompt = f"Review this {code_result['language']} code:\n\n{code_result['code']}"
        response = self.call_openai(prompt, system_msg)
        
        try:
            return json.loads(response)
        except:
            # Fallback
            return {
                "score": 7,
                "issues": ["Could not parse review"],
                "suggestions": ["Manual review recommended"],
                "approved": True
            }


class TestAgent(AIAgent):
    """Creates test cases and validates code"""
    
    def __init__(self):
        super().__init__("TestAgent", "Test Generator")
    
    def process(self, code_result: dict) -> dict:
        system_msg = f"""You are a test automation expert. Generate comprehensive unit tests for this {code_result['language']} code.
        
        Include:
        - Basic functionality tests
        - Edge case tests  
        - Error handling tests
        
        Return only the test code, properly formatted."""
        
        prompt = f"Create tests for:\n\n{code_result['code']}"
        test_code = self.call_openai(prompt, system_msg)
        
        return {
            "test_code": test_code,
            "language": code_result['language'],
            "description": f"Tests for {code_result['description']}"
        }


class AIAgentOrchestrator:
    """Coordinates all agents to generate quality code"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.coder = CodeAgent()
        self.critic = CriticAgent()
        self.tester = TestAgent()
    
    def generate_code(self, prompt: str) -> dict:
        """Generate quality code from prompt using all agents"""
        
        print(f"🤖 Processing: {prompt[:50]}...")
        
        # Step 1: Plan
        print("📋 Planning tasks...")
        tasks = self.planner.process(prompt)
        print(f"   Created {len(tasks)} tasks")
        
        # Step 2: Generate code
        print("💻 Generating code...")
        code_result = self.coder.process(prompt, tasks)
        print(f"   Generated {code_result['language']} code")
        
        # Step 3: Review
        print("🔍 Reviewing code...")
        review = self.critic.process(code_result)
        print(f"   Quality score: {review['score']}/10")
        
        # Step 4: Create tests
        print("🧪 Creating tests...")
        tests = self.tester.process(code_result)
        print("   Tests generated")
        
        # Compile results
        return {
            "prompt": prompt,
            "tasks": tasks,
            "code": code_result['code'],
            "language": code_result['language'],
            "review": review,
            "tests": tests['test_code'],
            "quality_score": review['score'],
            "approved": review['approved']
        }
    
    def save_result(self, result: dict, filename: str = None):
        """Save generated code and tests"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}"
        
        # Save main code
        ext = ".py" if result['language'] == "python" else ".js"
        with open(f"{filename}{ext}", 'w') as f:
            f.write(result['code'])
        
        # Save tests
        with open(f"{filename}_test{ext}", 'w') as f:
            f.write(result['tests'])
        
        # Save metadata
        metadata = {k: v for k, v in result.items() if k not in ['code', 'tests']}
        with open(f"{filename}_info.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"💾 Saved: {filename}{ext}, {filename}_test{ext}, {filename}_info.json")


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="AI Agent Code Generator")
    parser.add_argument("prompt", help="What code to generate")
    parser.add_argument("--save", help="Save to filename")
    parser.add_argument("--show-code", action="store_true", help="Display generated code")
    parser.add_argument("--show-tests", action="store_true", help="Display generated tests")
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: Set OPENAI_API_KEY environment variable")
        print("   export OPENAI_API_KEY=your_api_key")
        return
    
    # Generate code
    orchestrator = AIAgentOrchestrator()
    result = orchestrator.generate_code(args.prompt)
    
    # Show results
    print("\n" + "="*50)
    print("📊 GENERATION COMPLETE")
    print("="*50)
    print(f"Language: {result['language']}")
    print(f"Quality Score: {result['quality_score']}/10")
    print(f"Approved: {result['approved']}")
    print(f"Issues: {len(result['review']['issues'])}")
    
    if args.show_code:
        print(f"\n🔧 Generated Code:\n{'-'*30}")
        print(result['code'])
    
    if args.show_tests:
        print(f"\n🧪 Generated Tests:\n{'-'*30}")
        print(result['tests'])
    
    if result['review']['issues']:
        print(f"\n⚠️  Issues Found:")
        for issue in result['review']['issues']:
            print(f"  - {issue}")
    
    if result['review']['suggestions']:
        print(f"\n💡 Suggestions:")
        for suggestion in result['review']['suggestions']:
            print(f"  - {suggestion}")
    
    # Save if requested
    if args.save:
        orchestrator.save_result(result, args.save)


if __name__ == "__main__":
    if len(__import__('sys').argv) == 1:
        print("🤖 AI Agent Code Generator")
        print("Usage: python ai_agents.py 'create a function to hash passwords'")
        print("       python ai_agents.py 'build a user class' --save user_class --show-code")
        print("\nSet OPENAI_API_KEY environment variable first!")
    else:
        main()
