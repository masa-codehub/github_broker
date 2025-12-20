# Issue Creator Kit Usage Guide

This document provides instructions on how to use the Issue Creator Kit to create and validate GitHub issues from Markdown files.

## Overview

The Issue Creator Kit is a command-line tool designed to streamline the process of creating GitHub issues from local Markdown files. It offers two main functionalities:

1.  **Issue Creation:** Create new GitHub issues directly from the content of a Markdown file.
2.  **Validation:** Validate the format and content of a Markdown file before creating an issue to ensure it meets the required standards.

## Installation

The Issue Creator Kit is part of the `github_broker` project and is available as a command-line entry point. Ensure that you have the project dependencies installed by running:

```bash
pip install -e .
```

## Usage

The Issue Creator Kit provides two main commands: `create-issues` and `validate-docs`.

### Creating Issues

The `create-issues` command allows you to create GitHub issues from Markdown files located in the `_in_box` directory.

**Command:**

```bash
create-issues --repo <owner>/<repository_name>
```

**Arguments:**

*   `--repo`: The full name of the GitHub repository (e.g., `owner/repo`) where issues will be created. Can also be set via the `GITHUB_REPOSITORY` environment variable.
*   `--token`: A GitHub token for authentication. Can also be set via the `GITHUB_TOKEN` environment variable.

**Note:** This command is intended for use in a CI environment and requires the `PR_NUMBER` environment variable to be set.

**Workflow:**

1.  Commit and push the Markdown files to the `_in_box` directory on the repository's default branch.
2.  Run the `create-issues` command in your CI environment with the necessary arguments and environment variables.
3.  The tool will process each Markdown file from the repository, create a corresponding GitHub issue, and then move the processed file to the `_done_box` directory in the CI runner's local workspace.

### Validating Documents

The `validate-docs` command allows you to check your Markdown files against a set of predefined rules to ensure they are valid for issue creation.

**Command:**

```bash
validate-docs <path_to_file...>
```

**Arguments:**

*   `<path_to_file...>`: One or more paths to Markdown files to be validated. To process all files in a directory, use shell globbing (e.g., `validate-docs _in_box/*.md`).

**Workflow:**

1.  Run the `validate-docs` command, providing the path to your file or directory.
2.  The tool will check the file(s) against the validation rules.
3.  If any errors are found, they will be displayed in the console.

For more details on the specific validation rules, please refer to the [Validation Rules Document](../../issue_creator_kit/docs/validation-rules.md).
