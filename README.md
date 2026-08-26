# AI Prompt Agent

A modular AI engineering application for experimenting with prompt engineering, local open-source LLMs, structured outputs, prompt comparison, persistent conversations, and basic agentic AI workflows.

The project uses **Mistral locally through Ollama** and exposes the functionality through a **FastAPI backend** with a lightweight web frontend and **SQLite persistence**.

---

## 1. Project Overview

The AI Prompt Agent is a Week 8 LLM engineering project designed to demonstrate practical implementation of modern LLM application concepts.

The application allows users to:

- Enter questions or tasks.
- Select different prompt engineering techniques.
- Generate reusable prompts.
- Execute prompts against a local Mistral model.
- Configure model parameters.
- Compare multiple prompting strategies.
- Request structured JSON responses.
- Maintain persistent conversations.
- Continue previous conversations.
- Delete conversations.
- Execute basic agent tasks.
- Use deterministic tools through the agent architecture.
- Handle LLM and application failures safely.

The project is intentionally designed with a clean separation between:

- API layer
- Business logic
- Prompt engineering
- LLM providers
- Agent logic
- Tools
- Database access
- Frontend

This makes the application easier to understand, maintain, extend, and demonstrate as an AI engineering project.

---

## 2. Project Goals

The primary goals are:

1. Demonstrate practical prompt engineering.
2. Integrate an open-source/local LLM.
3. Implement provider-independent LLM communication.
4. Demonstrate model parameter control.
5. Implement structured output handling.
6. Compare different prompting strategies.
7. Persist conversations using SQLite.
8. Implement chat history and deletion.
9. Demonstrate basic agentic AI architecture.
10. Implement reusable tool abstractions.
11. Maintain clean application architecture.
12. Provide a practical portfolio-ready implementation.

---

## 3. Core Features

### Prompt Engineering

The application supports multiple prompting techniques:

- Zero-shot prompting
- One-shot prompting
- Few-shot prompting
- Role-based prompting
- Reasoning-oriented prompting
- Structured prompting

Prompt construction is centralized so prompt logic is not duplicated across API routes.

---

### LLM Integration

The primary LLM is:

**Mistral running locally through Ollama**

The application communicates with Ollama through its HTTP API.

The provider layer isolates Ollama-specific implementation from the rest of the application.

---

### Model Parameters

Users can configure:

- Temperature
- Top-P
- Maximum Tokens

The backend validates these parameters before sending requests to the LLM.

---

### Structured Output

The application can request structured JSON responses.

The structured-output pipeline includes:

1. Structured prompt generation.
2. LLM request.
3. Response extraction.
4. JSON parsing.
5. Schema validation.
6. Graceful error handling.

Invalid model output is treated as an application-level failure rather than being trusted blindly.

---

### Prompt Comparison

A single question can be evaluated using multiple prompting techniques.

Example:

```text
Question:
Explain Python decorators.

Techniques:

Zero-shot
One-shot
Few-shot
Role-based
Reasoning-oriented
Structured