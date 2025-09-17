# Common Configurations among most AI models

## TEMPERATURE

In Claude, `Temperature` controls the `randomness or "creativity"` of the model’s response.

* **Lower values (0.0-0.3)**: More deterministic, focused responses. Better for factual questions, classification, or tasks where consistency is critical.

* **Medium values (0.4-0.7)**: Balanced between determinism and creativity. Good for general use cases.

* **Higher values (0.8-1.0)**: More creative, varied, and potentially surprising responses. Better for creative writing, brainstorming, or generating diverse options.

```java
.options(ChatOptions.builder()
        .temperature(0.1)  // Very deterministic output
        .build())
```

## maxTokens

The `maxTokens` parameter limits how many tokens (word pieces) the model can generate in its response.

* **Low values (5-25)**: For single words, short phrases, or classification labels.

* **Medium values (50-500)**: For paragraphs or short explanations.

* **High values (1000+)**: For long-form content, stories, or complex explanations.

Setting appropriate output length is important to ensure you get complete responses without unnecessary verbosity and cost control.

```java
.options(ChatOptions.builder()
        .maxTokens(250)  // Medium-length response
        .build())
```

## Sampling Controls (Top-K and Top-P)

These parameters give you fine-grained control over the token selection process during generation.

* **Top-K**: Limits token selection to the K most likely next tokens. Higher values (e.g., 40-50) introduce more diversity.

* **Top-P (nucleus sampling)**: Dynamically selects from the smallest set of tokens whose cumulative probability exceeds P. Values like 0.8-0.95 are common.

```java
.options(ChatOptions.builder()
        .topK(40)      // Consider only the top 40 tokens
        .topP(0.8)     // Sample from tokens that cover 80% of probability mass
        .build())
```

## Model-Specific Options

While the portable ChatOptions provides a consistent interface across different LLM providers, Spring AI also offers model-specific options classes that expose provider-specific features and configurations. These model-specific options allow you to leverage the unique capabilities of each LLM provider.

```java
// Using OpenAI-specific options
OpenAiChatOptions openAiOptions = OpenAiChatOptions.builder()
        .model("gpt-4o")
        .temperature(0.2)
        .frequencyPenalty(0.5)      // OpenAI-specific parameter
        .presencePenalty(0.3)       // OpenAI-specific parameter
        .responseFormat(new ResponseFormat("json_object"))  // OpenAI-specific JSON mode
        .seed(42)                   // OpenAI-specific deterministic generation
        .build();

String result = chatClient.prompt("...")
        .options(openAiOptions)
        .call()
        .content();

// Using Anthropic-specific options
AnthropicChatOptions anthropicOptions = AnthropicChatOptions.builder()
        .model("claude-3-7-sonnet-latest")
        .temperature(0.2)
        .topK(40)                   // Anthropic-specific parameter
        .thinking(AnthropicApi.ThinkingType.ENABLED, 1000)  // Anthropic-specific thinking configuration
        .build();

String result = chatClient.prompt("...")
        .options(anthropicOptions)
        .call()
        .content();
```

Each model provider has its own implementation of chat options (e.g., OpenAiChatOptions, AnthropicChatOptions, MistralAiChatOptions) that exposes provider-specific parameters while still implementing the common interface. This approach gives you the flexibility to use portable options for cross-provider compatibility or model-specific options when you need access to unique features of a particular provider.

Note that when using model-specific options, your code becomes tied to that specific provider, reducing portability. It’s a trade-off between accessing advanced provider-specific features versus maintaining provider independence in your application.

---

[More details](https://docs.spring.io/spring-ai/reference/api/chat/prompt-engineering-patterns.html#_llm_provider_selection)
