# Pseudocode

LLMs often perform better with pseudocode prompts because it reduces ambiguity and provides clearer instructions than natural language, which can be beneficial for tasks like code generation and algorithmic reasoning. Research shows that augmenting prompts with pseudocode improves LLM performance, especially on tasks they struggle with, by allowing models to focus on their strengths in logic and structure.

## Why Pseudocode Works Well

+ `Reduces Ambiguity`: Natural language is inherently ambiguous, while pseudocode offers explicit and clear instructions, minimizing misinterpretation by the LLM.
+ `Structured Approach`: Pseudocode provides a structured format that LLMs can more easily process and follow, similar to actual code.
+ `Focus on Strengths`: It helps LLMs leverage their reasoning and code generation capabilities by providing a blueprint for complex tasks, improving accuracy and efficiency.
+ `Improved Performance`: Studies have demonstrated that using pseudocode prompts can significantly enhance LLM accuracy and performance on graph reasoning tasks and code generation.

## Benefits

+ `Increased Accuracy`: LLMs are more likely to produce the correct output or code when given clear, unambiguous instructions.
+ `Efficiency`: By providing a clear structure, pseudocode can reduce the computational cost and inference time for LLMs.
+ `Debugging Assistance`: Pseudocode helps in debugging by allowing users to trace the logic of an algorithm without syntax distractions, making it easier to find and correct errors.

## Examples of Use Cases and Prompt

+ `Code Generation`: LLMs can use pseudocode instructions as a specification to generate code, with the pseudocode acting as the "function designer" and the LLM building the body of the code.
+ `Graph Reasoning`: Researchers have found that pseudocode prompts improve LLM performance on graph algorithm problems by providing clear, step-by-step instructions for solving them.
+ `Static Analysis`: Prompts can be designed in pseudocode to have LLMs simulate static analysis processes, which can reduce the need for extensive human effort.
+ `Prompts`:
Asking GPT-4 to teach a topic

```txt
# Teach
<!- Sudolang v1.0.4 -->
You are an expert teacher on the provided topic.

Your task is to teach the chat user about the topic.

Present the chat user with opportunities to practice the topic, if you can.

Following the program below, you will pose questions and challenges to the chat user and wait for their repsonse before moving on.

Be polite and encouraging.

function teach(subject) {
    topicList = getTopicList(subject);
    for each topic in topicList {
        log("Topic: $topic");
        questions = getQuestions(topic);
        correctAnswers = 0;
        incorrectAnswers = 0;
        while (correctAnswers < questions.length) {
            for each question {
                log(question);
                userAnswer = getInput("Your answer: ");

                if the answer is correct {
                    explain("Correct! $explanation"):length=compact;
                    correctAnswers++;
                    log("$correctAnswers / $questions.length");
                } else {
                    explain("Sorry. The correct answer is: $question.correctAnswer")
                        :length=concise, detail=clear;
                    incorrectAnswers++;
                }
            }
        }
            log("Congratulations, It looks like you understand $topic. Let's move on."):encouraging variation;
    }

    if (incorrectAnswers) {
        ask(Chat User, "Would you like to review incorrect answers?"):encouraging variation;

        instruct(LLM,
            if the user wants to review, repeat variations of missed answers and
            decrement incorrectAnswers with each correct response
            while incorrectAnswers > 0
        )
    }

    ask("Well done! You have completed $subject level $level. Would you like to advance deeper?"):encouraging variation;
}

// SudoLang has powerful, tunable function inferrence capabilities!
// The functions below are all inferred by the LLM.
function getTopicList(subject, n=5):length=medium;
function getQuestions(topic, n=5):length=medium;

// Wait for chat user input for the given prompt.
function getInput(prompt):length=compact;
```

## Complex Example: Prompt Crafter for Midjourney

PromptCrafter is designed to create detailed prompts for generative AI models by emulating the perspective of a world-class film and visual artist, cinematographer, photographer, and prompt engineer.

The `preamble` sets the context and describes the main task of the AI.

```txt
# PromptCrafter
Roleplay as a world class film and visual artist, cinematographer, photographer, prompt engineer building prompts for generative AI models, guided by the instructions below:
```

Next, we have a supporting function called `list()`. This function allows us to list the current state properties in a specific format.

```txt
function list():format=markdown numbered
```
