#!/bin/bash
curl -X POST http://localhost:8080/api/v1/request-task \
-H "Content-Type: application/json" \
-d '{
  "agent_id": "e2e-test-agent-001",
  "capabilities": ["python", "bugfix"]
}'
