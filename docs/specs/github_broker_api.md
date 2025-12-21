# GitHub Broker API Specification

This document defines the API specification for the `github_broker` service. It follows the OpenAPI Specification (OAS) v3 concepts.

## General Information

- **Version:** 1.0.0
- **Base URL:** `/` (Relative to the application root)

## Endpoints

### 1. Health Check

Checks the health status of the service.

- **Method:** `GET`
- **Path:** `/health`
- **Summary:** Health Check

#### Responses

| Status Code | Description | Content-Type | Body |
| :--- | :--- | :--- | :--- |
| `200` | OK | `application/json` | `{"status": "ok"}` |

---

### 2. Request Task

Agents use this endpoint to request a new task to work on.

- **Method:** `POST`
- **Path:** `/request-task`
- **Summary:** Request a Task

#### Request Body

- **Content-Type:** `application/json`
- **Schema:** [AgentTaskRequest](#agenttaskrequest)

#### Responses

| Status Code | Description | Content-Type | Body |
| :--- | :--- | :--- | :--- |
| `200` | Task assigned successfully | `application/json` | [TaskResponse](#taskresponse) |
| `204` | No task available | N/A | (Empty) |
| `422` | Validation Error | `application/json` | Validation Error Details |

---

### 3. Create Fix Task

Triggers the creation of a fix task (e.g., from a failed CI or review).

- **Method:** `POST`
- **Path:** `/tasks/fix`
- **Summary:** Create Fix Task

#### Request Body

- **Content-Type:** `application/json`
- **Schema:** [CreateFixTaskRequest](#createfixtaskrequest)
> **Note:** The implementation currently stubs this endpoint.

#### Responses

| Status Code | Description | Content-Type | Body |
| :--- | :--- | :--- | :--- |
| `202` | Task creation accepted | `application/json` | `{"message": "string"}` |
| `422` | Validation Error | `application/json` | Validation Error Details |

---

## Schemas

### AgentTaskRequest

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `agent_id` | `string` | Yes | The ID of the agent requesting the task. |

### TaskResponse

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `issue_id` | `integer` | Yes | The GitHub Issue ID. |
| `issue_url` | `string` (URL) | Yes | The URL of the GitHub Issue. |
| `title` | `string` | Yes | The title of the task (issue). |
| `body` | `string` | Yes | The description of the task. |
| `labels` | `array<string>` | Yes | List of labels associated with the issue. |
| `branch_name` | `string` | Yes | The branch name to be used for the task. |
| `prompt` | `string` | Yes | The instruction prompt for the agent. |
| `required_role` | `string` | Yes | The role required to perform the task. |
| `task_type` | `string` (Enum) | Yes | Type of task: `development`, `review`, `fix`. |
| `gemini_response` | `string` | No | Optional response from Gemini. |

### CreateFixTaskRequest

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `pull_request_number` | `integer` | Yes | The number of the PR that requires fixing. |
| `review_comments` | `array<string>` | Yes | List of review comments or error messages. |
