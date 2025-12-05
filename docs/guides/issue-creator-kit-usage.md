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
create-issues --repo <repository_name> --owner <repository_owner>
```

**Arguments:**

*   `--repo`: The name of the GitHub repository where the issues will be created.
*   `--owner`: The owner of the GitHub repository.

**Workflow:**

1.  Place the Markdown files you want to convert into issues in the `_in_box` directory.
2.  Run the `create-issues` command with the appropriate repository and owner.
3.  The tool will process each Markdown file, create a corresponding GitHub issue, and then move the processed file to the `_done_box` directory.

### Validating Documents

The `validate-docs` command allows you to check your Markdown files against a set of predefined rules to ensure they are valid for issue creation.

**Command:**

```bash
validate-docs <path_to_file_or_directory>
```

**Arguments:**

*   `<path_to_file_or_directory>`: The path to a single Markdown file or a directory containing Markdown files to be validated.

**Workflow:**

1.  Run the `validate-docs` command, providing the path to your file or directory.
2.  The tool will check the file(s) against the validation rules.
3.  If any errors are found, they will be displayed in the console.

For more details on the specific validation rules, please refer to the [Validation Rules Document](issue_creator_kit/docs/validation-rules.md).
