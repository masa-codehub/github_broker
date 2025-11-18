import os


def get_plan_files():
    plan_files = []
    for root, _dirs, files in os.walk('plans'):
        for file in files:
            if file.endswith('.md'):
                plan_files.append(os.path.join(root, file))
    return plan_files

def fix_plan_files(files):
    required_headers = [
        "## 親Issue (Parent Issue)",
        "## 子Issue (Sub-Issues)",
        "## As-is (現状)",
        "## To-be (あるべき姿)",
        "## 完了条件 (Acceptance Criteria)",
        "## 成果物 (Deliverables)",
        "## ブランチ戦略 (Branching Strategy)",
    ]

    for file_path in files:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Remove duplicate sections
        lines = content.split('\n')
        seen_headers = set()
        new_lines = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('## '):
                if stripped_line not in seen_headers:
                    seen_headers.add(stripped_line)
                    new_lines.append(line)
            else:
                new_lines.append(line)

        content = '\n'.join(new_lines)

        # Add missing headers
        for header in required_headers:
            if header not in content:
                content += '\n' + header + '\n'

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    plan_files = get_plan_files()
    fix_plan_files(plan_files)
