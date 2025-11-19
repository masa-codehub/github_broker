---
title: "ADR-013: Agent Role Configuration"
---

## Epic Information

- **Epic Title:** Implement ADR-013: Agent Role Configuration
- **JIRA Epic:** [PROJECT-12345]
- **Status:** Completed
- **Priority:** High
- **Start Date:** 2023-10-26
- **End Date:** 2023-11-10
- **Assignee:** AI Agent (BACKEND_CODER)

## Description

This epic implements the architecture defined in ADR-013 to establish a flexible and extensible system for configuring AI agent roles and personas. The current hardcoded approach will be replaced with a configuration-driven system, allowing for easier management and scalability of agent behaviors.

## Goals

- Implement a `AgentConfigLoader` to load agent definitions from a TOML file.
- Define `AgentDefinition` and `AgentConfigList` Pydantic models for type-safe configuration.
- Refactor `TaskService` to utilize the loaded agent configurations.
- Update the DI container to manage and inject agent configuration dependencies.
- Ensure comprehensive test coverage for the new configuration loading and handling logic.

## User Stories

- [Story-1: Load Agent Configurations from TOML File](#story-1)
- [Story-2: Integrate Agent Configurations into TaskService](#story-2)

---

## Stories

### <a name="story-1"></a>Story-1: Load Agent Configurations from TOML File

- **Story Title:** As a Developer, I want to load agent configurations from a TOML file so that I can easily manage agent roles and personas.
- **JIRA Story:** [PROJECT-12346]
- **Status:** To Do
- **Priority:** High
- **Assignee:** AI Agent (BACKEND_CODER)
- **Acceptance Criteria:**
  - An `agents.toml` file is created with initial agent role configurations.
  - A `AgentConfigLoader` class is implemented to parse the TOML file.
  - `AgentDefinition` and `AgentConfigList` Pydantic models are created to represent the configuration structure.
  - Unit tests are written to verify that the loader correctly parses valid and invalid TOML files.

### <a name="story-2"></a>Story-2: Integrate Agent Configurations into TaskService

- **Story Title:** As a System, I want to use the loaded agent configurations to dynamically assign personas in the `TaskService`.
- **JIRA Story:** [PROJECT-12347]
- **Status:** To Do
- **Priority:** High
- **Assignee:** AI Agent (BACKEND_CODER)
- **Acceptance Criteria:**
  - The `punq` DI container is updated to provide `AgentConfigList` as a dependency.
  - `TaskService` is refactored to accept `AgentConfigList` in its constructor.
  - The `_create_task` method in `TaskService` is updated to use the agent configurations to populate the `agent_roles` dictionary.
  - Unit tests for `TaskService` are updated to reflect the new dependency and logic.
  - End-to-end tests are created to ensure the system correctly processes tasks with the new configuration-driven approach.

## 親Issue (Parent Issue)

## 子Issue (Sub-Issues)

## As-is (現状)

## To-be (あるべき姿)

## 完了条件 (Acceptance Criteria)

## 成果物 (Deliverables)

## ブランチ戦略 (Branching Strategy)
