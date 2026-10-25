# Skill: repo_navigation — SCAFFOLD

ADK skill directory. Scripts run via `run_skill_script` inside the sandbox
(share the filesystem with `run_command`, debit the central time budget).
Knowledge files are read via `load_skill_resource`.

Structure:
```
skills/repo_navigation/
├── SKILL.md          # manifest (YAML frontmatter with `name:`)
├── scripts/          # python or bash, executed in sandbox
│   └── find_test_files.py
└── resources/        # domain knowledge markdown
    └── pytest_tips.md
```