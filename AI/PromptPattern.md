# AI Prompt Patterns

## I. Chain-of-Thought

If I need the AI to reason or solve a multi-step problem, I’ll ask it to "think step by step" or "show your reasoning." This makes its process transparent and often leads to more accurate answers. For example, "Solve this math problem. Show your step-by-step reasoning: (10 + 5) * 2."

Chain-of-Thought isn’t just about getting the right answer; it’s about making the AI’s logic traceable and debuggable.

* **Simple**

```xml
I need to solve this probability question: In a group of 70 people, 40 like chocolate, 35 like vanilla, and 20 like both. How many people don't like either flavor?

Please solve this step by step, showing all of your work and reasoning before providing the final answer.
```

* **Better**

```xml
<general_goal>
I need to determine the best location for our new retail store. 
</general_goal>

We have the following data
<data>
- Location A: 2,000 sq ft, $4,000/month, 15,000 daily foot traffic
- Location B: 1,500 sq ft, $3,000/month, 12,000 daily foot traffic
- Location C: 2,500 sq ft, $5,000/month, 18,000 daily foot traffic
</data>

<instruction>
Analyze this decision step by step. First calculate the cost per square foot, then the cost per potential customer (based on foot traffic), then consider qualitative factors like visibility and accessibility. Show your reasoning at each step before making a final recommendation.
</instruction>
```

## II. Role-Playing - The Expertise Persona Pattern

Sometimes, I need the AI to adopt a specific persona. If I need a technical explanation, I’ll tell it, "Act as a senior software engineer." This helps the AI use appropriate language and knowledge.

This pattern involves asking a model to adopt the mindset and knowledge of a specific expert when responding to your questions. It's remarkably effective at accessing the model's specialized knowledge in particular domains.

When you're changing a perspective of a model, the LLM accesses more domain-specific knowledge and applies appropriate frameworks, terminology, and approaches relevant to that field. The simplest perspective shifting prompt can start with `Act as a Senior DevOps engineer from FAANG`

* **Simple**

```xml
I'd like you to respond as an experienced data scientist with expertise in natural language processing. I'm trying to build a sentiment analysis model for customer reviews.
What approach would you recommend for a small team with limited ML experience, and what are the key considerations we should keep in mind?
```

* **Better**

```xml
I'd like you to respond as a senior software architect with 20+ years of experience in scalable systems and a track record of migrating legacy applications to cloud infrastructure. 

You take a pragmatic approach that balances technical debt reduction with business continuity.

My company has a 15 year old Java monolith application handling our core business processes. We need to modernize it while keeping it operational.
What migration strategy would you recommend, what pitfalls should we watch for, and how would you structure the team to execute this transition?
```

## III. Delimiters - Use XML tags

For longer prompts with different sections (instructions, context, input), I use clear separators like ### , --- , or even XML-like tags ( `<instruction> , <text>` ). This helps the AI understand the structure of my prompt.

Claude was trained with XML tags in the training data. So using XML tags like `<example> , <document>` , etc. to structure your prompts can help guide Claude's output.

* **For Example**

```XML
You are a helpful AI fortune teller. Predict how long a user will live.
<examples>
<example>
<user>old and fat</user>
<answer>not much time left</answer>
</example>
<example>
<user>healthy</user>
<answer>lots of time</answer>
</example>
</examples>
```

## IV. Pre-fill the beginning of Claude’s response

To prefill, include the desired initial text in the Assistant message (Claude’s response will continue from where the Assistant message leaves off):

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-1-20250805",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What is your favorite color?"},
        {"role": "assistant", "content": "As an AI assistant, I don't have a favorite color, But if I had to pick, it would be green because"}  # Prefill here
    ]
)
```

## V. The Working Memory Technique

This technique helps the model to maintain and refer back to information across a conversation, creating a makeshift working memory that improves continuity and context awareness.

While modern models have generous context windows (especially Gemini), explicitly defining key information as important to remember signals that certain details should be prioritized and referenced throughout the conversation.

* **Simple**

```xml
I'm planning a marketing campaign with the following constraints:
- Budget: $15,000
- Timeline: 6 weeks (Starting April 10, 2025)
- Primary audience: SME business founders and CEOs, ages 25-40
- Goal: 200 qualified leads

Please keep these details in mind throughout our conversation. Let's start by discussing channel selection based on these parameters.
```

* **Better**

```xml
I'm planning a marketing campaign and need your ongoing assistance while keeping these key parameters in working memory:

CAMPAIGN PARAMETERS:
- Budget: $15,000
- Timeline: 6 weeks (Starting April 10, 2025)
- Primary audience: SME business founders and CEOs, ages 25-40
- Goal: 200 qualified leads

Throughout our conversation, please actively reference these constraints in your recommendations. If any suggestion would exceed our budget, timeline, or doesn't effectively target SME founders and CEOs, highlight this limitation and provide alternatives that align with our parameters.

Let's begin with channel selection. Based on these specific constraints, what are the most cost-effective channels to reach SME business leaders while staying within our $15,000 budget and 6 week timeline to generate 200 qualified leads?
```

## VI. Using Decision Tress for Nuanced Choices

The Decision Tree pattern guides the model through complex decision making by establishing a clear framework of if/else scenarios. This is particularly valuable when multiple factors influence decision making.

Decision trees provide models with a structured approach to navigate complex choices, ensuring all relevant factors are considered in a logical sequence.

* **Simple**

```xml
I need help deciding which Blog platform/system to use for my small media business. Please create a decision tree that considers:

1. Budget (under $100/month vs over $100/month)
2. Daily visitor (under 10k vs over 10k)
3. Primary need (share freemium content vs paid content)
4. Technical expertise available (limited vs substantial)

For each branch of the decision tree, recommend specific Blogging solutions that would be appropriate.
```

* **Better**

```xml
I need help selecting the optimal blog platform for my small media business. Please create a detailed decision tree that thoroughly analyzes:

DECISION FACTORS:
1. Budget considerations
   - Tier A: Under $100/month
   - Tier B: $100-$300/month 
   - Tier C: Over $300/month

2. Traffic volume expectations
   - Tier A: Under 10,000 daily visitors
   - Tier B: 10,000-50,000 daily visitors
   - Tier C: Over 50,000 daily visitors

3. Content monetization strategy
   - Option A: Primarily freemium content distribution
   - Option B: Subscription/membership model
   - Option C: Hybrid approach with multiple revenue streams

4. Available technical resources
   - Level A: Limited technical expertise (no dedicated developers)
   - Level B: Moderate technical capability (part-time technical staff)
   - Level C: Substantial technical resources (dedicated development team)

For each pathway through the decision tree, please:
1. Recommend 2-3 specific blog platforms most suitable for that combination of factors
2. Explain why each recommendation aligns with those particular requirements
3. Highlight critical implementation considerations or potential limitations
4. Include approximate setup timeline and learning curve expectations

Additionally, provide a visual representation of the decision tree structure to help visualize the selection process.
```

Here are some key improvements like expanded decision factors, adding more granular tiers for each decision factor, clear visual structure, descriptive labels, comprehensive output request implementation context, and more.

The best way to master these patterns is to experiment with them on your own tasks. Start with the example prompts provided, then gradually modify them to fit your specific needs. Pay attention to how the model's responses change as you refine your prompting technique.

Remember that effective prompting is an iterative process. Don't be afraid to refine your approach based on the results you get
