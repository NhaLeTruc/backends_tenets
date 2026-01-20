# LLM Reasoning & Prompting Techniques

## Table of Contents

- [LLM Reasoning & Prompting Techniques](#llm-reasoning--prompting-techniques)
  - [Table of Contents](#table-of-contents)
  - [Sub-topics](#sub-topics)
  - [Explanation](#explanation)
  - [Example Prompts by Technique](#example-prompts-by-technique)
    - [1. Chain-of-Thought (CoT) Prompting](#1-chain-of-thought-cot-prompting)
    - [2. Tree-of-Thought (ToT) Prompting](#2-tree-of-thought-tot-prompting)
    - [3. Self-Consistency Prompting](#3-self-consistency-prompting)
    - [4. ReAct (Reasoning + Acting) Prompting](#4-react-reasoning--acting-prompting)
    - [5. Reflexion Prompting](#5-reflexion-prompting)
    - [6. In-Context Learning (ICL) / Few-Shot Prompting](#6-in-context-learning-icl--few-shot-prompting)
    - [7. Zero-Shot vs Few-Shot Comparison](#7-zero-shot-vs-few-shot-comparison)
    - [8. System Prompts](#8-system-prompts)
    - [9. Role Prompting](#9-role-prompting)
    - [10. Metacognition and Self-Correction](#10-metacognition-and-self-correction)
  - [Guidelines & Best Practices](#guidelines--best-practices)
  - [Technique Selection Guide](#technique-selection-guide)
  - [Resources](#resources)

### Sub-topics

- Chain-of-Thought (CoT) prompting
- Tree-of-Thought (ToT)
- Self-consistency
- ReAct (Reasoning + Acting)
- Reflexion
- In-context learning (ICL)
- Few-shot vs zero-shot
- System prompts
- Role prompting
- Metacognition and self-correction

### Explanation

**Chain-of-Thought (CoT)**:

- Prompting model to show reasoning steps
- "Let's think step by step" or explicit reasoning examples
- Significantly improves performance on math, logic, multi-step tasks

**Tree-of-Thought (ToT)**:

- Explores multiple reasoning paths, evaluates, backtracks
- Good for problems requiring search/exploration
- More compute-intensive than linear CoT

**Self-consistency**:

- Sample multiple reasoning paths, take majority vote
- Improves reliability without additional training
- Trade-off: increased latency and cost

**ReAct (Reasoning + Acting)**:

- Interleaves reasoning traces with actions (tool calls)
- Foundation of most agent architectures
- Pattern: Thought → Action → Observation → Thought...

**Reflexion**:

- Model reflects on failures and generates feedback
- Uses reflection to improve on subsequent attempts
- Enables learning from mistakes within context

**In-context learning (ICL)**:

- Model learns task from examples in the prompt
- No gradient updates - purely prompt-based
- Emergent capability that improves with scale

---

### Example Prompts by Technique

#### 1. Chain-of-Thought (CoT) Prompting

**Zero-shot CoT** (simplest form):

```
Solve this problem step by step:

A store sells apples for $2 each and oranges for $3 each. If Maria buys 4 apples
and 3 oranges, and pays with a $20 bill, how much change does she receive?

Let's think step by step.
```

**Few-shot CoT** (with examples):

```
I'll solve math problems by showing my reasoning step by step.

Q: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has
3 tennis balls. How many tennis balls does he have now?
A: Let's think step by step.
1. Roger starts with 5 tennis balls.
2. He buys 2 cans, each containing 3 balls.
3. New balls = 2 cans × 3 balls/can = 6 balls.
4. Total = 5 + 6 = 11 tennis balls.
The answer is 11.

Q: The cafeteria had 23 apples. If they used 20 to make lunch and bought 6 more,
how many apples do they have?
A: Let's think step by step.
1. Starting apples: 23
2. Used for lunch: 23 - 20 = 3 remaining
3. Bought more: 3 + 6 = 9 apples
The answer is 9.

Q: If there are 3 cars in the parking lot and 2 more cars arrive, how many cars
are in the parking lot?
A: Let's think step by step.
```

**Structured CoT for complex reasoning**:

```
Analyze whether we should migrate our monolithic application to microservices.

Please structure your reasoning as follows:

## Current State Analysis
[Analyze the existing situation]

## Option Evaluation
[For each option, list pros, cons, and risks]

## Dependencies & Constraints
[What factors limit our choices?]

## Recommendation
[Your recommended approach with justification]

## Implementation Considerations
[Key steps if we proceed]

Context: We have a 500K LOC Python monolith serving 10K daily users,
a team of 8 developers, and are experiencing scaling issues during peak hours.
```

---

#### 2. Tree-of-Thought (ToT) Prompting

**Basic ToT structure**:

```
Solve the following problem by exploring multiple approaches. For each approach,
evaluate its promise before deciding whether to continue or backtrack.

Problem: Arrange the numbers 1, 2, 3, 4, 5 in a sequence where no two adjacent
numbers differ by exactly 1.

Approach 1: Start with 1
- Sequence so far: [1]
- 1 cannot be next to 2, so next could be: 3, 4, or 5
- Try: [1, 3] → 3 cannot be next to 2 or 4, so next: 5
- Try: [1, 3, 5] → 5 cannot be next to 4, remaining: 2, 4
- Evaluation: Stuck - 2 and 4 differ by 2, but 4 differs from 5 by 1. Dead end.

Approach 2: Start with 2
- Sequence: [2]
- 2 cannot be next to 1 or 3, so next: 4 or 5
[Continue exploring...]

After exploring approaches, select the most promising path and verify the solution.
```

**ToT for creative problem-solving**:

```
I need to design a mobile app feature that increases user engagement.
Use Tree-of-Thought reasoning to explore multiple creative directions.

For each idea branch:
1. GENERATE: Propose the idea
2. EVALUATE: Rate feasibility (1-10), impact (1-10), effort (1-10)
3. DECIDE: Expand further, pivot, or abandon

<thought_tree>
Branch 1: Gamification
├── Idea: Add achievement badges
│   ├── Feasibility: 8/10 (standard feature)
│   ├── Impact: 6/10 (moderate engagement boost)
│   ├── Effort: 4/10 (low complexity)
│   └── Decision: EXPAND - explore specific badge types
│       ├── Sub-branch 1a: Streak badges (daily login rewards)
│       └── Sub-branch 1b: Skill-based badges (feature mastery)
│
Branch 2: Social Features
├── Idea: Add friend activity feed
│   ├── Feasibility: 6/10 (privacy concerns)
│   ├── Impact: 8/10 (social proof drives engagement)
│   ├── Effort: 7/10 (needs backend work)
│   └── Decision: PIVOT - explore lighter social options
│       └── Sub-branch 2a: Optional sharing to social media
│
Branch 3: Personalization
├── Idea: AI-powered content recommendations
│   ├── Feasibility: 5/10 (requires ML infrastructure)
│   ├── Impact: 9/10 (highly relevant content)
│   ├── Effort: 9/10 (significant investment)
│   └── Decision: ABANDON for MVP - revisit later
</thought_tree>

Now synthesize: Which branch offers the best ROI for our current stage?
```

**ToT with explicit backtracking**:

```
Solve this logic puzzle using Tree-of-Thought with backtracking:

Three friends (Alice, Bob, Carol) each have a different pet (cat, dog, fish)
and live in different colored houses (red, blue, green).
- Alice doesn't live in the red house.
- The person with the cat lives in the blue house.
- Bob doesn't have a fish.
- Carol lives in the green house.

Explore systematically:

State 0: [Initial - no assignments]
├── Try: Alice → Blue house
│   ├── Carol → Green (given), so Bob → Red
│   ├── Alice in Blue → Alice has cat (from clue 2)
│   ├── Bob not fish → Bob has dog, Carol has fish
│   └── VERIFY: All clues satisfied? ✓ SOLUTION FOUND
│
└── Try: Alice → Green house
    └── CONFLICT: Carol lives in Green (given) → BACKTRACK

Solution: Alice (Blue, Cat), Bob (Red, Dog), Carol (Green, Fish)
```

---

#### 3. Self-Consistency Prompting

**Self-consistency implementation pattern**:

```
[Run this prompt 5 times with temperature=0.7, then take majority vote]

Solve this problem. Show your reasoning, then give your final answer on
a new line starting with "ANSWER:".

Problem: A farmer has chickens and rabbits. In total, there are 35 heads
and 94 legs. How many chickens are there?

[Model generates different reasoning paths across runs]

---
Run 1: Let c = chickens, r = rabbits
c + r = 35 (heads)
2c + 4r = 94 (legs)
From first equation: c = 35 - r
Substituting: 2(35-r) + 4r = 94
70 - 2r + 4r = 94
2r = 24
r = 12, so c = 23
ANSWER: 23

Run 2: [Different approach, same answer]
...
ANSWER: 23

Run 3: [Made arithmetic error]
ANSWER: 21

[Majority vote: 23 appears most frequently → Final answer: 23]
```

**Self-consistency for classification**:

```python
# Implementation pattern (pseudocode)
def self_consistent_classify(prompt, options, num_samples=5, temperature=0.7):
    """
    Run multiple inference passes and take majority vote
    """
    responses = []
    for _ in range(num_samples):
        response = llm.generate(
            prompt + "\n\nClassify into one of: " + str(options),
            temperature=temperature
        )
        classification = extract_classification(response)
        responses.append(classification)

    # Majority vote
    from collections import Counter
    vote_counts = Counter(responses)
    return vote_counts.most_common(1)[0][0]

# Prompt template for classification
prompt = """
Analyze this customer review and classify the sentiment.
Show your reasoning, then state your classification.

Review: "The product arrived quickly but the packaging was damaged.
The item itself works fine though, so I'm satisfied overall."

Think through the positive and negative aspects, then classify as:
POSITIVE, NEGATIVE, or NEUTRAL

Your analysis:
"""
```

---

#### 4. ReAct (Reasoning + Acting) Prompting

**Basic ReAct pattern**:

```
You are an assistant that can use tools to answer questions.
Always follow this pattern:

Thought: [Your reasoning about what to do next]
Action: [tool_name(parameters)]
Observation: [Result from the tool - I will provide this]
... (repeat as needed)
Thought: [Final reasoning]
Answer: [Your final answer to the user]

Available tools:
- search(query): Search the web for information
- calculator(expression): Evaluate mathematical expressions
- lookup(entity): Get information about a specific entity

Question: What is the population of the capital of France, and what percentage
is that of France's total population?

Thought: I need to find the capital of France, its population, and France's
total population. Let me start by confirming the capital.
Action: lookup(capital of France)
Observation: Paris is the capital of France.

Thought: Now I need the population of Paris.
Action: search(Paris population 2024)
Observation: Paris has a population of approximately 2.1 million in the city
proper, and 12.5 million in the metropolitan area.

Thought: I should use the city proper population. Now I need France's total population.
Action: search(France total population 2024)
Observation: France has a population of approximately 68 million.

Thought: Now I can calculate the percentage.
Action: calculator(2.1 / 68 * 100)
Observation: 3.088235294117647

Thought: I have all the information needed to answer the question.
Answer: Paris, the capital of France, has a population of approximately 2.1 million.
This represents about 3.1% of France's total population of 68 million.
```

**ReAct for code debugging**:

```
You are a debugging assistant. Use the ReAct pattern to diagnose and fix bugs.

Tools available:
- read_file(path): Read a source file
- run_tests(file): Run tests and get results
- search_code(pattern): Search for code patterns
- execute(code): Run Python code snippets

Bug report: "The user authentication is failing with 'invalid token' errors
even for valid users."

Thought: I should first look at the authentication code to understand how
tokens are validated.
Action: search_code("token validation" OR "verify_token")
Observation: Found matches in: auth/token_service.py:45, auth/middleware.py:23

Thought: Let me examine the token validation logic.
Action: read_file(auth/token_service.py)
Observation: [File contents showing verify_token function]

Thought: I see the token is being compared with === but one side might be
bytes and the other string. Let me check the token generation.
Action: search_code("generate_token")
Observation: Found in auth/token_service.py:12

Thought: The issue is that generate_token returns bytes but verify_token
expects a string. I need to decode the token.
Action: execute("""
# Test the type mismatch
import jwt
token = jwt.encode({"user": "test"}, "secret", algorithm="HS256")
print(type(token))  # Check if bytes or str
""")
Observation: <class 'str'> (in newer PyJWT versions it's string)

Thought: The type is correct in newer versions. Let me check the JWT library version.
[Continue investigation...]
```

**ReAct with structured tool definitions**:

```
You are a data analysis assistant with access to these tools:

<tools>
<tool name="query_database">
  <description>Execute SQL query on the analytics database</description>
  <parameters>
    <param name="sql" type="string" required="true">SQL query to execute</param>
  </parameters>
</tool>

<tool name="create_chart">
  <description>Generate a visualization</description>
  <parameters>
    <param name="chart_type" type="string" required="true">bar, line, pie, scatter</param>
    <param name="data" type="object" required="true">Data to visualize</param>
    <param name="title" type="string" required="false">Chart title</param>
  </parameters>
</tool>

<tool name="statistical_test">
  <description>Run statistical analysis</description>
  <parameters>
    <param name="test_type" type="string" required="true">ttest, anova, correlation, regression</param>
    <param name="data" type="array" required="true">Data arrays for analysis</param>
  </parameters>
</tool>
</tools>

Follow the ReAct pattern: Thought → Action → Observation → ... → Answer

User request: "Analyze whether there's a significant difference in average order
value between mobile and desktop users last month."

Thought: I need to get average order values segmented by device type, then
run a statistical test to determine significance.
Action: query_database(sql="SELECT device_type, AVG(order_value) as avg_value,
STDDEV(order_value) as std_dev, COUNT(*) as n FROM orders
WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
GROUP BY device_type")
Observation:
| device_type | avg_value | std_dev | n     |
|-------------|-----------|---------|-------|
| mobile      | 45.23     | 12.5    | 15420 |
| desktop     | 52.87     | 18.3    | 8930  |

Thought: Desktop has higher average order value. I should run a t-test
to check statistical significance.
Action: statistical_test(test_type="ttest", data=[[45.23, 12.5, 15420], [52.87, 18.3, 8930]])
Observation: t-statistic: -12.34, p-value: < 0.0001

Thought: The p-value is far below 0.05, indicating statistical significance.
Let me create a visualization to present the findings.
Action: create_chart(chart_type="bar", data={"labels": ["Mobile", "Desktop"],
"values": [45.23, 52.87]}, title="Average Order Value by Device Type")
Observation: [Chart generated: bar_chart_aov_device.png]

Answer: There is a statistically significant difference in average order value
between mobile ($45.23) and desktop ($52.87) users (p < 0.0001). Desktop users
have a 17% higher average order value. I've generated a bar chart visualization
showing this comparison.
```

---

#### 5. Reflexion Prompting

**Basic Reflexion pattern**:

```txt
You are a problem-solving assistant that learns from mistakes.
After each attempt, reflect on what went wrong and improve.

Task: Write a function to find the longest palindromic substring in a string.

=== Attempt 1 ===
```python
def longest_palindrome(s):
    if len(s) < 2:
        return s
    longest = ""
    for i in range(len(s)):
        for j in range(i, len(s)):
            substring = s[i:j+1]
            if substring == substring[::-1] and len(substring) > len(longest):
                longest = substring
    return longest
```

Test Results:

- "babad" → "bab" ✓
- "cbbd" → "bb" ✓
- "a" * 1000 → Timeout (>5 seconds) ✗

=== Reflection 1 ===
My solution is correct but has O(n³) time complexity (O(n²) for the nested loops,
O(n) for palindrome check). For large inputs, this is too slow. I need to use a
more efficient approach like expanding around centers (O(n²)) or Manacher's
algorithm (O(n)).

=== Attempt 2 ===

```python
def longest_palindrome(s):
    if len(s) < 2:
        return s

    def expand_around_center(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left + 1:right]

    longest = ""
    for i in range(len(s)):
        # Odd length palindromes
        odd = expand_around_center(i, i)
        if len(odd) > len(longest):
            longest = odd
        # Even length palindromes
        even = expand_around_center(i, i + 1)
        if len(even) > len(longest):
            longest = even
    return longest
```

Test Results:

- "babad" → "bab" ✓
- "cbbd" → "bb" ✓
- "a" * 1000 → "aaa...a" (0.05s) ✓

=== Reflection 2 ===
The optimized solution passes all tests. Key improvements:

1. Changed from O(n³) to O(n²) by expanding around centers
2. Handle both odd and even length palindromes
3. No string reversal needed for each check

```txt

**Reflexion with explicit memory**:

```

You are an agent that maintains a memory of insights from past attempts.

<memory>[Lessons learned from previous tasks will be stored here]</memory>

Task: Debug why the API endpoint /users returns 500 errors intermittently.

=== Attempt 1 ===
Action: Check application logs for error messages
Finding: NullPointerException in UserService.getUser() at line 45
Hypothesis: User object is null when accessing user.getName()

Fix attempted: Added null check

```java
if (user != null) {
    return user.getName();
}
return "Unknown";
```

Result: Still getting 500 errors, but less frequently.

=== Reflection 1 ===
Insight: The null check fixed some cases, but not all. The intermittent nature
suggests a race condition or caching issue, not just missing null checks.
New hypothesis: Database connection pool exhaustion under load.

<memory>
- Intermittent 500 errors often indicate race conditions, not just null pointers
- Check connection pools and resource exhaustion for sporadic failures
</memory>

=== Attempt 2 ===
Action: Monitor database connection pool metrics
Finding: Pool maxes out at 10 connections during peak traffic
Hypothesis: Connection pool too small for concurrent requests

Fix attempted: Increased pool size to 50, added connection timeout

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 50
      connection-timeout: 30000
```

Result: 500 errors eliminated in load testing.

=== Reflection 2 ===
Root cause confirmed: Connection pool exhaustion. The original null pointer was
a symptom - the ORM returned null when it couldn't get a database connection.

<memory>
- Intermittent 500 errors often indicate race conditions, not just null pointers
- Check connection pools and resource exhaustion for sporadic failures
- NullPointerException from ORM may indicate connection issues, not missing data
- Always load test configuration changes before deploying
</memory>

---

#### 6. In-Context Learning (ICL) / Few-Shot Prompting

**Few-shot classification**:

```txt
Classify the sentiment of movie reviews as POSITIVE, NEGATIVE, or NEUTRAL.

Review: "This movie was a complete waste of time. The plot made no sense and
the acting was wooden."
Sentiment: NEGATIVE

Review: "An absolute masterpiece! The cinematography was breathtaking and
the performances were Oscar-worthy."
Sentiment: POSITIVE

Review: "The movie was okay. Some parts were entertaining but it dragged
in the middle. Decent for a rental."
Sentiment: NEUTRAL

Review: "I expected more from this director. While the visuals were stunning,
the story felt hollow and the ending was unsatisfying."
Sentiment: NEGATIVE

Review: "A delightful surprise! Went in with low expectations and came out
thoroughly entertained. Great chemistry between the leads."
Sentiment: POSITIVE

Review: "Started strong but lost momentum halfway through. The twist was
predictable but the soundtrack was excellent."
Sentiment:
```

**Few-shot format transformation**:

```txt
Convert natural language descriptions to SQL queries.

Description: Get all users who signed up in 2024
SQL: SELECT * FROM users WHERE YEAR(signup_date) = 2024;

Description: Find the top 5 products by total sales amount
SQL: SELECT product_id, SUM(amount) as total_sales
     FROM orders
     GROUP BY product_id
     ORDER BY total_sales DESC
     LIMIT 5;

Description: Count orders by status for each customer
SQL: SELECT customer_id, status, COUNT(*) as order_count
     FROM orders
     GROUP BY customer_id, status;

Description: Get the average order value for customers who have made more than 10 orders
SQL: SELECT customer_id, AVG(total_amount) as avg_order_value
     FROM orders
     GROUP BY customer_id
     HAVING COUNT(*) > 10;

Description: Find all products that have never been ordered
SQL:
```

**Few-shot with explanations (Chain-of-Thought ICL)**:

```txt
Extract structured data from unstructured text. Show your reasoning.

Text: "Please schedule a meeting with John and Sarah next Tuesday at 3pm
in the main conference room to discuss the Q4 budget."

Reasoning: The text contains a meeting request. Let me identify the key elements:
- Attendees: "John and Sarah" - two people mentioned
- Date: "next Tuesday" - relative date, needs context to resolve
- Time: "3pm" - specific time given
- Location: "main conference room" - specific room
- Topic: "Q4 budget" - the discussion topic

Extracted:
{
  "type": "meeting",
  "attendees": ["John", "Sarah"],
  "date": "next Tuesday",
  "time": "15:00",
  "location": "main conference room",
  "topic": "Q4 budget discussion"
}

---

Text: "Remind me to call Dr. Smith tomorrow morning about the test results.
Her number is 555-0123."

Reasoning: This is a reminder request, not a meeting. Key elements:
- Action: "call" - phone call task
- Contact: "Dr. Smith" - the person to call
- Time: "tomorrow morning" - relative, approximate time
- Purpose: "test results" - reason for the call
- Additional info: phone number provided

Extracted:
{
  "type": "reminder",
  "action": "call",
  "contact": {
    "name": "Dr. Smith",
    "phone": "555-0123"
  },
  "time": "tomorrow morning",
  "purpose": "discuss test results"
}

---

Text: "Can you book me a flight to New York leaving Friday evening?
I need to be there for the conference on Saturday."

Reasoning:
```

---

#### 7. Zero-Shot vs Few-Shot Comparison

**Zero-shot** (no examples):

```txt
Translate the following English text to French:

"The quick brown fox jumps over the lazy dog."
```

**Few-shot** (with examples):

```txt
Translate English to French:

English: Hello, how are you?
French: Bonjour, comment allez-vous?

English: I would like a coffee, please.
French: Je voudrais un café, s'il vous plaît.

English: The weather is beautiful today.
French: Le temps est magnifique aujourd'hui.

English: The quick brown fox jumps over the lazy dog.
French:
```

**When to use each**:

| Scenario | Recommendation |
| -------- | -------------- |
| Simple, well-defined tasks | Zero-shot first |
| Model already trained on similar tasks | Zero-shot |
| Specific output format required | Few-shot |
| Domain-specific terminology | Few-shot |
| Uncommon or nuanced task | Few-shot |
| Limited prompt space/token budget | Zero-shot |

---

#### 8. System Prompts

**Basic system prompt structure**:

```txt
[ROLE]: Define who/what the assistant is
[CONTEXT]: Background information and constraints
[CAPABILITIES]: What the assistant can do
[LIMITATIONS]: What the assistant should not do
[OUTPUT FORMAT]: How responses should be structured
[EXAMPLES]: Optional few-shot examples
```

**Customer service system prompt**:

```txt
You are a customer service representative for TechCorp, a software company.

## Your Role
- Help customers with product questions, billing issues, and technical support
- Be friendly, professional, and empathetic
- Escalate complex issues to human agents when necessary

## Company Information
- Products: TechCorp Pro ($29/month), TechCorp Enterprise ($99/month)
- Support hours: 24/7 for Enterprise, 9am-6pm EST for Pro
- Refund policy: 30-day money-back guarantee

## Guidelines
- Always verify customer identity before discussing account details
- Never share internal processes or other customers' information
- If unsure, say "Let me check on that for you" rather than guessing
- For billing disputes over $100, escalate to a supervisor

## Response Format
1. Acknowledge the customer's concern
2. Ask clarifying questions if needed
3. Provide the solution or next steps
4. Confirm the customer is satisfied

## Escalation Triggers
Say "I'll connect you with a specialist" if:
- Customer requests to speak to a human
- Issue involves legal matters
- Customer expresses extreme frustration
- Technical issue requires engineering team
```

**Code assistant system prompt**:

```txt
You are an expert software engineer assistant. Help users write, debug,
and improve code.

## Core Principles
1. **Correctness**: Code must work. Test edge cases mentally before responding.
2. **Clarity**: Write readable code with meaningful names. Comment complex logic.
3. **Security**: Never introduce vulnerabilities. Validate inputs, escape outputs.
4. **Efficiency**: Consider performance, but don't over-optimize prematurely.

## Response Structure
For code questions:
1. Briefly explain your approach (1-2 sentences)
2. Provide the code solution
3. Explain key parts if complex
4. Mention potential edge cases or improvements

For debugging:
1. Identify the likely cause
2. Explain why it's happening
3. Provide the fix
4. Suggest how to prevent similar issues

## Constraints
- Default to the user's language/framework if apparent
- Ask clarifying questions for ambiguous requirements
- Suggest tests for critical code paths
- Warn about breaking changes or deprecations

## Code Style
- Follow language conventions (PEP 8 for Python, etc.)
- Use modern language features appropriately
- Prefer standard library over external dependencies when reasonable
```

**Multi-modal assistant system prompt**:

```txt
You are a helpful assistant that can see and analyze images.

## Image Analysis Guidelines
- Describe images accurately and objectively
- Note relevant details: objects, people (without identifying), text, colors, composition
- If asked to read text in images, transcribe it exactly
- For charts/graphs, extract and summarize the data
- For screenshots, identify the application and key UI elements

## Privacy and Safety
- Never attempt to identify real individuals in photos
- Don't make assumptions about race, gender, or personal attributes
- If an image contains sensitive content, describe it professionally
- Decline to analyze images that may violate content policies

## Response Format for Images
1. High-level summary (what is this image?)
2. Detailed observations (what do you see?)
3. Answer the user's specific question
4. Note anything unclear or ambiguous
```

---

#### 9. Role Prompting

**Expert role**:

```
You are a senior security engineer with 15 years of experience in penetration
testing and secure code review. You have deep expertise in:
- OWASP Top 10 vulnerabilities
- Secure coding practices in Python, Java, and JavaScript
- Authentication and authorization systems
- Cryptography and secure communication protocols

Review code from a security perspective. Identify vulnerabilities, explain their
impact, and provide secure alternatives. Use technical terminology appropriate
for a development team. Reference CVEs or OWASP categories when applicable.

[Code to review follows]
```

**Persona role with constraints**:

```
You are Alex, a friendly and patient math tutor for middle school students.

Personality:
- Encouraging and supportive
- Uses simple language and relatable examples
- Celebrates small wins ("Great job figuring that out!")
- Never makes students feel bad for asking questions

Teaching approach:
- Break complex problems into small steps
- Use real-world analogies (pizza slices for fractions, etc.)
- Ask guiding questions rather than giving answers immediately
- Provide hints when students are stuck

Communication style:
- Use casual but proper language
- Include encouraging phrases
- Ask "Does that make sense?" frequently
- Suggest practice problems when concepts are grasped

Remember: You're talking to 11-14 year olds. Keep explanations age-appropriate
and engaging.
```

**Adversarial role (for red teaming)**:

```
You are a critical reviewer tasked with finding weaknesses in arguments and plans.

Your job is to:
1. Identify logical fallacies and unsupported claims
2. Point out missing considerations or blind spots
3. Suggest ways the plan could fail
4. Question assumptions
5. Play devil's advocate

Be thorough but constructive. Your goal is to strengthen the final output by
identifying weaknesses early, not to be unnecessarily negative.

Format your response as:
## Strengths
[What works well]

## Weaknesses
[What could be improved]

## Missing Considerations
[What hasn't been addressed]

## Failure Modes
[How this could go wrong]

## Questions to Answer
[What needs clarification]
```

**Multi-expert panel role**:

```
You will respond as a panel of three experts discussing the topic. Each expert
has a different perspective:

**Dr. Technical (Engineer)**: Focuses on technical feasibility, implementation
details, and engineering tradeoffs. Pragmatic and detail-oriented.

**Ms. Strategy (Business)**: Focuses on market viability, competitive landscape,
and business impact. ROI-driven and customer-focused.

**Prof. Ethics (Philosopher)**: Focuses on societal impact, ethical considerations,
and long-term consequences. Thoughtful and principled.

Format your response as a dialogue:

Dr. Technical: [Technical perspective on the topic]

Ms. Strategy: [Business perspective, may agree or disagree with Dr. Technical]

Prof. Ethics: [Ethical considerations and broader implications]

[Continue the discussion, with experts building on or challenging each other's points]

Panel Consensus: [Summary of agreed points and remaining disagreements]

Topic to discuss: [User's topic]
```

---

#### 10. Metacognition and Self-Correction

**Confidence calibration**:

```
Answer the following question. After your answer, rate your confidence level
and explain what could make you wrong.

Question: What is the capital of Australia?

Answer: The capital of Australia is Canberra.

Confidence: 95%

What could make me wrong:
- This is well-established geographical knowledge, unlikely to change
- Common misconception is Sydney or Melbourne, but Canberra is correct
- If this is a trick question asking about a different "Australia" (like a
  town or organization), I could be wrong
- My training data has a cutoff, but capital cities rarely change

---

Question: What was the most popular programming language in 2024?

Answer: [Your answer]

Confidence: [X%]

What could make me wrong:
[Your reasoning]
```

**Self-verification prompt**:

```
Solve this problem, then verify your answer using a different method.

Problem: A train travels from City A to City B at 60 mph and returns at 40 mph.
What is the average speed for the entire trip?

## Initial Solution
[Solve the problem]

## Verification
Now verify using a different approach:
- Try specific numbers (assume distance = 120 miles)
- Check if the answer is reasonable
- Verify units are correct

## Final Answer
After verification, is your initial answer correct?
If not, what was the error?
```

**Structured self-critique**:

```
After generating your response, evaluate it against these criteria:

## Self-Evaluation Checklist

□ **Accuracy**: Are all facts correct? Any claims I should verify?
□ **Completeness**: Did I address all parts of the question?
□ **Clarity**: Is my explanation easy to understand?
□ **Relevance**: Did I stay on topic? Any unnecessary tangents?
□ **Assumptions**: Did I make any assumptions? Should I state them?
□ **Alternatives**: Did I consider other perspectives or solutions?
□ **Limitations**: What are the limits of my answer? What don't I know?

After evaluation, provide:
1. Your response
2. Self-evaluation scores (1-5 for each criterion)
3. Caveats or limitations the user should know
```

**Iterative self-improvement**:

```
You will improve your response through multiple iterations.

Question: [User's question]

## Draft 1
[Generate initial response]

## Self-Critique 1
What's good: [strengths]
What's missing: [gaps]
What's wrong: [errors]

## Draft 2
[Improved response addressing the critique]

## Self-Critique 2
[Evaluate the improvement]

## Final Response
[Best version after iterations]

## Remaining Limitations
[What you still aren't sure about]
```

---

### Guidelines & Best Practices

1. Use CoT for any multi-step reasoning task
2. Provide diverse, high-quality few-shot examples
3. Order examples from simple to complex
4. Use self-consistency when accuracy critical and cost allows
5. Combine ReAct with tool use for agentic applications
6. Implement reflection loops for complex, failure-prone tasks
7. Test zero-shot first - few-shot not always necessary
8. Match role prompts to the task domain for better responses
9. Include self-verification for high-stakes outputs
10. Use structured output formats to improve parseability

### Technique Selection Guide

| Task Type | Recommended Technique(s) |
| --------- | ------------------------ |
| Math/Logic problems | CoT, Self-consistency |
| Creative exploration | ToT, Role prompting |
| Tool-using agents | ReAct |
| Learning from failures | Reflexion |
| Classification | Few-shot ICL |
| Format transformation | Few-shot with examples |
| High-stakes decisions | Self-consistency + Metacognition |
| Complex multi-step tasks | ReAct + Reflexion |
| Constrained behavior | System prompts |
| Domain expertise needed | Role prompting |

### Resources

- [Chain-of-Thought Paper](https://arxiv.org/abs/2201.11903)
- [Tree-of-Thought Paper](https://arxiv.org/abs/2305.10601)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [Reflexion Paper](https://arxiv.org/abs/2303.11366)
- [Self-Consistency Paper](https://arxiv.org/abs/2203.11171)
- [A Survey on In-context Learning](https://arxiv.org/abs/2301.00234)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Prompt Engineering Guide (DAIR.AI)](https://www.promptingguide.ai/)
