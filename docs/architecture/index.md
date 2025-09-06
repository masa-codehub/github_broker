# Architecture Overview

This document provides a high-level overview of the GitHub Task Broker system architecture, following the C4 model for visualizing software architecture.

## System Context Diagram

The following diagram shows the system context, illustrating how the GitHub Task Broker fits into its operating environment.

```mermaid
C4Context
  title System Context Diagram for GitHub Task Broker

  Person(Developer, "AI Developer Agent", "An autonomous agent responsible for developing software.")
  System(GitHub, "GitHub", "Provides repository hosting and issue tracking.")

  System_Ext(Gemini, "Google Gemini API", "Provides intelligent task selection capabilities.")

  System(Broker, "GitHub Task Broker", "Orchestrates task assignments to prevent conflicts.")

  Rel(Developer, Broker, "Requests a new task to work on", "HTTPS/JSON")
  Rel(Broker, GitHub, "Fetches issue data and assigns tasks by applying labels", "GitHub API")
  Rel(Broker, Gemini, "Sends issue list for intelligent selection", "HTTPS/JSON")
```

## Container Diagram

The following diagram zooms into the GitHub Task Broker system, showing its main logical containers.

```mermaid
C4Container
  title Container Diagram for GitHub Task Broker

  System_Ext(GitHub, "GitHub", "Provides repository hosting and issue tracking via API.")

  System_Boundary(Broker, "GitHub Task Broker") {
    Container(FastAPI, "FastAPI Application", "Python, FastAPI", "Provides the main API endpoint for agents to request tasks.")
    Container(TaskService, "Task Service", "Python", "The core component responsible for the task assignment logic. It periodically polls GitHub for available issues.")
    ContainerDb(Redis, "Redis Cache", "Redis", "Stores the real-time state of all issues from the target repository to allow for fast and consistent task assignments.")
  }

  Rel(FastAPI, TaskService, "Delegates task requests")
  Rel(TaskService, Redis, "Reads issue states and locks issues")
  Rel(TaskService, GitHub, "Polls for new and updated issues", "GitHub API")
```

## Architectural Drivers

- **Decoupling:** The primary goal is to decouple the AI Developer Agents from each other, preventing them from working on the same issue simultaneously.
- **Simplicity:** The architecture was shifted from webhook-based to a polling-based model to simplify local development and remove the need for a publicly exposed endpoint.
- **Scalability:** While the current polling model is simple, the system is designed with a separate `TaskService` that could be scaled independently or have its polling logic improved in the future (e.g., using conditional requests with ETags).
