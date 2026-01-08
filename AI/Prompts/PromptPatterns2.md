# Even More Prompt Patterns

## Build Reusable Components

Develop modular elements that can be reused across different templates. These might include role descriptions, task instructions, output formats, and validation steps. For instance:

```xml
ROLE DEFINITION:
You are a [specific role] tasked with [primary responsibility].

BEHAVIORAL GUIDELINES:
- Maintain [specific tone or style]  
- Prioritize [primary goals or objectives]  
- Adhere to [specific format or structure]  

TASK INSTRUCTIONS:  
1. Evaluate input based on [criteria or standards].  
2. Process the information using [method or approach].  
3. Deliver output in [desired format].  

VALIDATION RULES:  
- Confirm compliance with [specific requirements or standards].  
- Ensure accuracy in [key elements].  
- Verify [specific details].
```

[Details](https://latitude-blog.ghost.io/blog/5-patterns-for-scalable-prompt-design/)

## Multi-Agent Prompt Systems

Multi-agent systems take the modular approach a step further by using multiple specialized agents to handle complex tasks. These systems rely on multiple AI instances working together to solve problems through coordinated prompt interactions, offering a scalable way to expand the capabilities of large language models (LLMs).

[Details](https://latitude-blog.ghost.io/blog/5-patterns-for-scalable-prompt-design/)

## Structured Output Pattern

If you need the model's response to be easily parseable by a program, you must specify the format clearly. This is particularly important when you want to use the output as an input for a different part of your software, such as generating JSON configuration files, XML for web services, or even markdown (MD) files for documentation. By telling the model to adhere to a rigid structure, you ensure the output is consistent and reliable.

```python
import json
from openai import OpenAI

client = OpenAI()

def generate_product_list(product_info):
    prompt = f"""
    Generate a JSON object for the following product information.
    The JSON should have a 'products' key, which is an array of objects.
    Each object should have keys for 'name', 'category', 'price', and 'in_stock' (a boolean).

    Product Information:
    {product_info}

    Provide only the JSON output, and nothing else.
    """

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    # Try to parse the response as JSON
    try:
        json_output = json.loads(response.output_text)
        return json_output
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

# Let's try it out
product_data = """
Laptop Pro, Electronics, 1500, True
Ergo Mouse, Accessories, 50, True
Wireless Keyboard, Accessories, 90, False
"""

product_list = generate_product_list(product_data)
if product_list:
    print(json.dumps(product_list, indent=2))
```

In this example, the prompt is the instruction you give to the LLM. It's a text string that outlines a clear task and specifies the output format (a JSON object with specific keys). The response from the model is the raw text it generates, which should be the JSON object you requested. The Python code then attempts to parse this raw text response into a structured JSON object using json.loads().

## Context Pattern

GPT-5’s massive context window is a game-changer for working with a full file or even a small project. Instead of just giving it a snippet, you can feed it an entire script and ask it to analyze, refactor, or optimize it.

```python
async def my_optimize_codebase(code_file: str) -> str:
    prompt = f"""
    You are a performance optimization expert. Analyze the following JavaScript 
    code file for potential performance bottlenecks, redundant code, or memory leaks. 
    Provide a detailed report and then a refactored version of the code.

    Code to analyze:
    \"\"\"
    {code_file}
    \"\"\"
    """
    # For this demonstration, we'll just return the prompt
    return prompt


# User input: "your text input here"
my_code = """
// A large, unoptimized JavaScript file
const fetchData = async () => {
  const data = await fetch('https://api.example.com/data');
  const jsonData = await data.json();
  const filteredData = jsonData.filter(item => item.isActive);
  const mappedData = filteredData.map(item => {
    return {
      id: item.id,
      name: item.name.toUpperCase(),
      status: 'active'
    };
  });

  // This is a loop that could be more efficient
  const res= [];
  for (let i = 0; i < mappedData.length; i++) {
    for (let j = 0; j < 10000; j++) {
      res.append(mappedData[i])
    }
  }
  return res;
};
"""

import asyncio

async def main():
    prompt = await my_optimize_codebase(my_code)
    print(prompt)

asyncio.run(main())
```
