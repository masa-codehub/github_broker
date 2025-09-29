# 005-multi-repository-support

## Context

The current Redis key design in our system is implicitly tied to a single repository. Redis keys are generated without incorporating any repository-specific identification. For example, keys like `issue_lock` or `open_issues_cache` are global across the Redis instance. This design choice means that the system can only safely operate with one GitHub repository at a time. If multiple repositories were to be processed concurrently or managed by the same Redis instance, key collisions would occur, leading to data corruption or incorrect behavior (e.g., an issue lock for one repository affecting another, or cached issues from one repository overwriting those of another). This limitation prevents the system from scaling to support multiple GitHub repositories simultaneously, which is a critical requirement for future enhancements and broader applicability.

## Decision

To enable future multi-repository support, we will introduce a unique repository identifier prefix to all Redis keys. This prefix will follow the format `repo_{owner}_{repo_name}:`. All existing and future Redis keys will be prepended with this identifier.

For example:
- `issue_lock` will become `repo_{owner}_{repo_name}:issue_lock`
- `open_issues_cache` will become `repo_{owner}_{repo_name}:open_issues_cache`

The `{owner}` and `{repo_name}` will be dynamically determined based on the GitHub repository being processed. This ensures that each repository's data in Redis is isolated and uniquely identifiable, preventing conflicts when managing multiple repositories.

## Consequences

### Benefits

*   **Multi-repository Support:** The primary benefit is the ability to safely manage and process multiple GitHub repositories concurrently using a single Redis instance.
*   **Data Isolation:** Each repository's data in Redis will be logically isolated, preventing cross-repository data corruption or unintended interactions.
*   **Scalability:** The system can scale to handle a larger number of repositories without requiring separate Redis instances for each, simplifying infrastructure management.
*   **Clarity:** Redis keys will become more descriptive, clearly indicating which repository they belong to, which aids in debugging and monitoring.

### Impact on Existing Code

*   **Redis Client Abstraction:** The Redis client or any component responsible for generating Redis keys will need to be updated to incorporate the repository identifier prefix. This change should ideally be encapsulated within a Redis key generation utility or a modified Redis client wrapper to minimize widespread code changes.
*   **Configuration:** The system will need to be configured with the current repository's owner and name, which will be used to construct the Redis key prefix.
*   **Migration:** Existing Redis data (if any) will become inaccessible with the new key format. A migration strategy will be required if backward compatibility with existing single-repository data is necessary. For a new system or a system with ephemeral Redis data, this might not be a significant concern.
*   **Testing:** All Redis-related operations will need thorough testing to ensure that keys are correctly prefixed and that data is stored and retrieved as expected for multiple repositories.
