# Claude Code Repository Boilerplate Template - Implementation Plan

**Version**: 1.0
**Last Updated**: 2026-01-07
**Author**: Tech Lead (Claude Code Assisted)

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Tool Stack & Rationale](#tool-stack--rationale)
3. [Implementation Phases](#implementation-phases)
4. [Configuration Files (Complete)](#configuration-files-complete)
5. [Hook Scripts (Complete)](#hook-scripts-complete)
6. [Claude Code Integration](#claude-code-integration)
7. [Setup & Installation](#setup--installation)
8. [Enforcement Matrix](#enforcement-matrix)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [References & Sources](#references--sources)

---

## Executive Summary

This document provides a complete implementation plan for creating a production-ready Git repository boilerplate template optimized for Claude Code assisted development. The template enforces code quality and architectural best practices through **automated Git hooks, multi-language static analysis, and CI/CD integration**.

### Goals

- **Automatic Enforcement**: Pre-commit hooks prevent bad code from entering the repository
- **Multi-Language Support**: Auto-detect and lint TypeScript, Python, and Java
- **Dual-Layer Security**: Gitleaks (fast) + TruffleHog (deep) secret detection
- **SOLID Principles**: Static analysis enforces Single Responsibility, Open/Closed, etc.
- **Zero Configuration**: One-command setup script for new team members
- **Claude Code Optimized**: Custom documentation files and slash commands

### Key Features

- All .md/.pdf files enforced to docs/ directory
- All tests must pass before commit
- All code linted before commit (ESLint/pylint/Checkstyle)
- Maximum 500 lines per file (with exceptions support)
- SOLID principles enforced via static analysis
- Dependency injection best practices
- No circular dependencies
- No secrets exposed in codebase
- Conventional Commits message template

---

## Tool Stack & Rationale

### Core Technologies

| Tool | Purpose | Rationale |
|------|---------|-----------|
| **Husky v9** | Git hook manager | 18M+ weekly downloads, zero-install, cross-platform compatibility, team-friendly |
| **Commitizen + Commitlint** | Commit message enforcement | Industry standard for Conventional Commits, integrates with changelogs |
| **Gitleaks v8** | Fast secret scanning | 46% precision, 88% recall, fastest scan times, customizable patterns |
| **TruffleHog** | Deep historical scanning | Entropy analysis, comprehensive historical git scans, ideal for CI/CD |
| **git-filter-repo** | Secret cleanup | Emergency removal of secrets from git history |
| **Madge** | Circular dependency detection | Visual dependency graphs, CI-friendly exit codes, TypeScript-aware |
| **ESLint + plugins** | TypeScript linting | Cognitive complexity, SOLID enforcement, import organization |
| **Prettier** | Code formatting | Zero-config, consistent formatting across team |

### Multi-Language Support

#### TypeScript/Node.js (Primary)

```json
{
  "devDependencies": {
    "eslint": "^8.56.0",
    "@typescript-eslint/eslint-plugin": "^6.17.0",
    "@typescript-eslint/parser": "^6.17.0",
    "eslint-plugin-sonarjs": "^0.23.0",
    "eslint-plugin-import": "^2.29.0",
    "eslint-config-prettier": "^9.1.0",
    "prettier": "^3.1.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1"
  }
}
```

#### Python (Auto-detected when .py files present)

```txt
# requirements-dev.txt
pylint>=3.0.0
black>=23.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
mypy>=1.7.0
```

#### Java (Auto-detected when .java files present)

```xml
<!-- pom.xml dependencies -->
<dependency>
  <groupId>com.puppycrawl.tools</groupId>
  <artifactId>checkstyle</artifactId>
  <version>10.12.0</version>
</dependency>
```

### Tool Comparison & Trade-offs

#### Hook Management

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Husky** ✅ | Simple, Node-native, widely adopted, zero-install | Node.js only | **Recommended** |
| pre-commit framework | Language-agnostic, extensive plugins | Python dependency, steeper learning curve | For polyglot teams |
| Manual hooks | Zero dependencies, full control | Not version-controlled, manual setup | Avoid |

#### Secret Detection

| Tool | Performance | Accuracy | Ease of Use | Verdict |
|------|-------------|----------|-------------|---------|
| **Gitleaks** ✅ | Excellent (Go) | High (46% precision, 88% recall) | Easy (TOML config) | **Pre-commit** |
| **TruffleHog** ✅ | Moderate (Python) | Excellent (entropy analysis) | Complex setup | **CI/CD deep scans** |
| git-secrets | Good | Low | Moderate | AWS-specific only |

---

## Implementation Phases

### Phase 1: Foundation Setup (Week 1)

**Goal**: Establish core infrastructure

#### Step 1.1: Update package.json

```json
{
  "name": "your-project-name",
  "version": "1.0.0",
  "scripts": {
    "prepare": "husky install",
    "commit": "cz",

    "lint": "eslint src --ext .ts",
    "lint:fix": "eslint src --ext .ts --fix",
    "lint:python": "pylint **/*.py",
    "lint:java": "java -jar checkstyle.jar -c checkstyle.xml src/",

    "format": "prettier --write \"src/**/*.ts\"",
    "format:check": "prettier --check \"src/**/*.ts\"",
    "format:python": "black .",
    "format:java": "java -jar google-java-format.jar --replace $(find . -name '*.java')",

    "test": "jest",
    "test:coverage": "jest --coverage",
    "test:python": "pytest --cov",
    "test:java": "mvn test",

    "check:deps": "madge --circular --ts-config ./tsconfig.json --extensions ts src/",
    "check:secrets": "gitleaks detect --source . --verbose",
    "check:secrets:deep": "bash scripts/security/scan-history.sh",
    "check:file-size": "node scripts/hooks/check-file-size.js",
    "check:docs": "node scripts/hooks/check-documentation.js",
    "check:languages": "node scripts/hooks/detect-languages.js",

    "check:all": "npm run check:languages && npm run lint && npm run format:check && npm run test && npm run check:deps && npm run check:file-size && npm run check:docs && npm run check:secrets",

    "build": "tsc",
    "build:python": "python setup.py build",
    "build:java": "mvn compile"
  },
  "devDependencies": {
    "husky": "^9.0.0",
    "commitizen": "^4.3.0",
    "@commitlint/cli": "^18.0.0",
    "@commitlint/config-conventional": "^18.0.0",
    "@commitlint/cz-commitlint": "^18.0.0",
    "gitleaks": "^8.18.0",
    "madge": "^7.0.0",
    "@typescript-eslint/eslint-plugin": "^6.17.0",
    "@typescript-eslint/parser": "^6.17.0",
    "eslint": "^8.56.0",
    "eslint-plugin-sonarjs": "^0.23.0",
    "eslint-plugin-import": "^2.29.0",
    "eslint-config-prettier": "^9.1.0",
    "prettier": "^3.1.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1",
    "typescript": "^5.3.3"
  },
  "config": {
    "commitizen": {
      "path": "@commitlint/cz-commitlint"
    }
  }
}
```

#### Step 1.2: Initialize Husky

```bash
npm install
npm pkg set scripts.prepare="husky install"
npm run prepare
```

#### Step 1.3: Create Base Configuration Files

See [Configuration Files](#configuration-files-complete) section below for complete file contents.

---

### Phase 2: Quality Gates (Week 2)

**Goal**: Implement all enforcement mechanisms

#### Step 2.1: Secret Detection (Multi-layered)

Create `.gitleaks.toml` - see [Configuration Files](#configuration-files-complete)

Create `scripts/security/scan-history.sh`:

```bash
#!/bin/bash
# Deep historical secret scan using TruffleHog

echo "🔍 Running deep historical secret scan with TruffleHog..."
echo "This may take several minutes for large repositories."
echo ""

if ! command -v trufflehog &> /dev/null; then
    echo "❌ TruffleHog not installed"
    echo "Install: https://github.com/trufflesecurity/trufflehog"
    exit 1
fi

# Run TruffleHog on entire git history
trufflehog git file://. --since-commit="" --only-verified --json > trufflehog-results.json

if [ $? -eq 0 ]; then
    echo "✅ Deep scan complete"
    echo "Results saved to: trufflehog-results.json"
else
    echo "❌ Secrets detected in git history!"
    echo "Review: trufflehog-results.json"
    exit 1
fi
```

Create `scripts/security/cleanup-secrets.sh`:

```bash
#!/bin/bash
# Emergency secret cleanup using git-filter-repo

echo "⚠️  WARNING: This will rewrite git history!"
echo "Make sure you have a backup and team coordination."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted"
    exit 0
fi

if ! command -v git-filter-repo &> /dev/null; then
    echo "❌ git-filter-repo not installed"
    echo "Install: pip install git-filter-repo"
    exit 1
fi

# Example: Remove specific file from history
# git filter-repo --path path/to/secret/file --invert-paths

echo "Provide the file path to remove from history:"
read -p "File path: " filepath

git filter-repo --path "$filepath" --invert-paths --force

echo ""
echo "✅ File removed from history"
echo "⚠️  Force push required: git push --force"
echo "⚠️  Notify team to rebase their branches"
```

#### Step 2.2-2.4: Additional Scripts

See [Hook Scripts](#hook-scripts-complete) section for:
- `scripts/hooks/check-file-size.js`
- `scripts/hooks/check-documentation.js`
- `scripts/hooks/detect-languages.js`

---

### Phase 3: Git Hooks (Week 3)

**Goal**: Wire all checks into Git workflow

#### Step 3.1: Pre-commit Hook

Create `.husky/pre-commit`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo "🔍 Running pre-commit checks..."
echo ""

FAILED=0

# 1. Detect languages in the project
echo "🌐 Detecting project languages..."
LANGUAGES=$(node scripts/hooks/detect-languages.js)

# 2. Run linting based on detected languages
echo ""
echo "📝 Linting code..."

if echo "$LANGUAGES" | grep -q "typescript"; then
    npm run lint || FAILED=1
fi

if echo "$LANGUAGES" | grep -q "python"; then
    npm run lint:python || FAILED=1
fi

if echo "$LANGUAGES" | grep -q "java"; then
    npm run lint:java || FAILED=1
fi

# 3. Run tests
echo ""
echo "🧪 Running tests..."

if echo "$LANGUAGES" | grep -q "typescript"; then
    npm run test || FAILED=1
fi

if echo "$LANGUAGES" | grep -q "python"; then
    npm run test:python || FAILED=1
fi

if echo "$LANGUAGES" | grep -q "java"; then
    npm run test:java || FAILED=1
fi

# 4. Check file sizes
echo ""
echo "📏 Checking file sizes..."
node scripts/hooks/check-file-size.js || FAILED=1

# 5. Check documentation location
echo ""
echo "📚 Checking documentation location..."
node scripts/hooks/check-documentation.js || FAILED=1

# 6. Scan for secrets
echo ""
echo "🔐 Scanning for secrets..."
npm run check:secrets || FAILED=1

# 7. Check formatting
echo ""
echo "💅 Checking code formatting..."

if echo "$LANGUAGES" | grep -q "typescript"; then
    npm run format:check || FAILED=1
fi

if echo "$LANGUAGES" | grep -q "python"; then
    black --check . || FAILED=1
fi

if [ $FAILED -ne 0 ]; then
    echo ""
    echo "❌ Pre-commit checks failed!"
    echo "Fix errors above or use --no-verify to skip (not recommended)"
    exit 1
fi

echo ""
echo "✅ All pre-commit checks passed!"
```

#### Step 3.2: Prepare-commit-msg Hook

Create `.husky/prepare-commit-msg`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

exec < /dev/tty && npx cz --hook || true
```

#### Step 3.3: Commit-msg Hook

Create `.husky/commit-msg`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx --no -- commitlint --edit $1
```

#### Step 3.4: Pre-push Hook

Create `.husky/pre-push`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo "🚀 Running pre-push checks..."
echo ""

FAILED=0

# 1. Check for circular dependencies
echo "🔄 Checking for circular dependencies..."
npm run check:deps || FAILED=1

# 2. Run full test coverage
echo ""
echo "📊 Running tests with coverage..."
npm run test:coverage || FAILED=1

# 3. Build check
echo ""
echo "🏗️  Building project..."
npm run build || FAILED=1

# 4. Optional: Deep secret scan (set DEEP_SCAN_ENABLED=true in env)
if [ "$DEEP_SCAN_ENABLED" = "true" ]; then
    echo ""
    echo "🔍 Running deep secret scan..."
    npm run check:secrets:deep || FAILED=1
fi

if [ $FAILED -ne 0 ]; then
    echo ""
    echo "❌ Pre-push checks failed!"
    exit 1
fi

echo ""
echo "✅ All pre-push checks passed!"
```

---

### Phase 4: CI/CD Integration (Week 4)

**Goal**: Mirror local checks in cloud

#### GitHub Actions Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop, 'feature/**' ]
  pull_request:
    branches: [ main, develop ]

jobs:
  quality-checks:
    name: Quality Checks
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for secret scanning

      - name: Setup Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Install dependencies
        run: npm ci

      - name: Detect languages
        id: languages
        run: |
          LANGS=$(node scripts/hooks/detect-languages.js)
          echo "languages=$LANGS" >> $GITHUB_OUTPUT

      - name: Run ESLint
        if: contains(steps.languages.outputs.languages, 'typescript')
        run: npm run lint

      - name: Run pylint
        if: contains(steps.languages.outputs.languages, 'python')
        run: npm run lint:python

      - name: Run Checkstyle
        if: contains(steps.languages.outputs.languages, 'java')
        run: npm run lint:java

      - name: Check formatting
        run: npm run format:check

      - name: Check file sizes
        run: npm run check:file-size

      - name: Scan for secrets (Gitleaks)
        run: npm run check:secrets

      - name: Check circular dependencies
        run: npm run check:deps

  tests:
    name: Tests
    runs-on: ubuntu-latest
    needs: quality-checks

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests with coverage
        run: npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
          flags: unittests
          fail_ci_if_error: true

  security-deep-scan:
    name: Deep Security Scan
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install TruffleHog
        run: |
          curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

      - name: Run TruffleHog
        run: bash scripts/security/scan-history.sh

      - name: Upload scan results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: trufflehog-results
          path: trufflehog-results.json
          retention-days: 30

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [quality-checks, tests]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build project
        run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 7
```

Create `.github/workflows/security-scan.yml`:

```yaml
name: Weekly Security Scan

on:
  schedule:
    # Run every Sunday at 2 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:  # Allow manual trigger

jobs:
  trufflehog-scan:
    name: TruffleHog Deep Scan
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history

      - name: Install TruffleHog
        run: |
          curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin

      - name: Run TruffleHog scan
        run: |
          trufflehog git file://. --since-commit="" --only-verified --json > trufflehog-weekly.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: weekly-security-scan
          path: trufflehog-weekly.json
          retention-days: 90

      - name: Notify on findings
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🔐 Security Alert: Secrets Detected in Repository History',
              body: 'TruffleHog detected potential secrets in the repository history. Please review the scan results and take appropriate action.',
              labels: ['security', 'urgent']
            })
```

---

## Configuration Files (Complete)

### .eslintrc.js

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    project: './tsconfig.json',
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:import/recommended',
    'plugin:import/typescript',
    'plugin:sonarjs/recommended',
    'prettier', // Must be last
  ],
  plugins: [
    '@typescript-eslint',
    'import',
    'sonarjs',
  ],
  rules: {
    // ============ SOLID PRINCIPLES ENFORCEMENT ============

    // Single Responsibility Principle
    'sonarjs/cognitive-complexity': ['error', 15],  // Max complexity per function
    'max-lines-per-function': ['warn', { max: 50, skipBlankLines: true, skipComments: true }],

    // Open/Closed Principle
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/explicit-module-boundary-types': 'warn',

    // Liskov Substitution Principle
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/strict-boolean-expressions': 'warn',

    // Interface Segregation Principle
    '@typescript-eslint/prefer-readonly': 'warn',

    // Dependency Inversion Principle
    '@typescript-eslint/no-parameter-properties': 'off', // Allow DI via constructor

    // ============ DEPENDENCY INJECTION BEST PRACTICES ============
    'no-new': 'error',  // Prefer factory functions
    '@typescript-eslint/prefer-readonly-parameter-types': 'off',  // Allow mutable params for DI

    // ============ CIRCULAR DEPENDENCIES ============
    'import/no-cycle': ['error', { maxDepth: Infinity, ignoreExternal: true }],
    'import/no-self-import': 'error',

    // ============ CODE QUALITY ============
    'sonarjs/no-duplicate-string': ['error', 3],
    'sonarjs/no-identical-functions': 'error',
    'sonarjs/no-collapsible-if': 'warn',
    'sonarjs/prefer-immediate-return': 'warn',

    // ============ IMPORT ORGANIZATION ============
    'import/order': ['error', {
      'groups': [
        'builtin',    // Node.js built-in modules
        'external',   // npm packages
        'internal',   // Internal modules
        'parent',     // Parent directories
        'sibling',    // Same directory
        'index',      // Index files
      ],
      'newlines-between': 'always',
      'alphabetize': { order: 'asc', caseInsensitive: true },
    }],
    'import/no-duplicates': 'error',

    // ============ GENERAL BEST PRACTICES ============
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'no-debugger': 'error',
    '@typescript-eslint/no-unused-vars': ['error', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
    }],
    'prefer-const': 'error',
    'no-var': 'error',
  },
  settings: {
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
        project: './tsconfig.json',
      },
    },
  },
};
```

### .prettierrc.json

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "bracketSpacing": true,
  "jsxBracketSameLine": false
}
```

### .editorconfig

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
max_line_length = off

[*.{yml,yaml}]
indent_size = 2

[*.py]
indent_size = 4
max_line_length = 100

[*.java]
indent_size = 4
max_line_length = 120

[Makefile]
indent_style = tab

[{package.json,.eslintrc,*.code-workspace}]
indent_size = 2
```

### commitlint.config.js

```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature
        'fix',      // Bug fix
        'docs',     // Documentation only
        'style',    // Formatting changes
        'refactor', // Code change that neither fixes a bug nor adds a feature
        'perf',     // Performance improvement
        'test',     // Adding or updating tests
        'chore',    // Maintenance, dependency updates
        'ci',       // CI/CD changes
        'build',    // Build system changes
        'revert',   // Revert previous commit
      ],
    ],
    'scope-enum': [
      2,
      'always',
      [
        'core',
        'cli',
        'api',
        'ui',
        'db',
        'auth',
        'tests',
        'docs',
        'deps',
        'config',
        'hooks',
        'ci',
        'security',
      ],
    ],
    'subject-case': [2, 'always', 'sentence-case'],
    'subject-max-length': [2, 'always', 100],
    'subject-empty': [2, 'never'],
    'body-max-line-length': [2, 'always', 100],
    'footer-max-line-length': [2, 'always', 100],
  },
  prompt: {
    questions: {
      type: {
        description: 'Select the type of change you are committing',
        enum: {
          feat: {
            description: 'A new feature',
            title: 'Features',
          },
          fix: {
            description: 'A bug fix',
            title: 'Bug Fixes',
          },
          docs: {
            description: 'Documentation only changes',
            title: 'Documentation',
          },
          style: {
            description: 'Changes that do not affect the meaning of the code',
            title: 'Styles',
          },
          refactor: {
            description: 'A code change that neither fixes a bug nor adds a feature',
            title: 'Code Refactoring',
          },
          perf: {
            description: 'A code change that improves performance',
            title: 'Performance Improvements',
          },
          test: {
            description: 'Adding missing tests or correcting existing tests',
            title: 'Tests',
          },
          build: {
            description: 'Changes that affect the build system or external dependencies',
            title: 'Builds',
          },
          ci: {
            description: 'Changes to our CI configuration files and scripts',
            title: 'Continuous Integrations',
          },
          chore: {
            description: "Other changes that don't modify src or test files",
            title: 'Chores',
          },
          revert: {
            description: 'Reverts a previous commit',
            title: 'Reverts',
          },
        },
      },
      scope: {
        description: 'What is the scope of this change (component/feature)',
      },
      subject: {
        description: 'Write a short, imperative tense description of the change',
      },
      body: {
        description: 'Provide a longer description of the change (optional)',
      },
      isBreaking: {
        description: 'Are there any breaking changes?',
      },
      breakingBody: {
        description: 'Describe the breaking changes',
      },
      breaking: {
        description: 'Describe the breaking changes',
      },
      issues: {
        description: 'Add issue references (e.g., "fix #123", "re #456")',
      },
    },
  },
};
```

### .gitleaks.toml

```toml
title = "Gitleaks Configuration"

[extend]
useDefault = true

[[rules]]
description = "AWS Access Key"
id = "aws-access-key"
regex = '''(?i)(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'''
tags = ["aws", "secret", "key"]

[[rules]]
description = "AWS Secret Key"
id = "aws-secret-key"
regex = '''(?i)aws(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]'''
tags = ["aws", "secret"]

[[rules]]
description = "GitHub Personal Access Token"
id = "github-pat"
regex = '''ghp_[0-9a-zA-Z]{36}'''
tags = ["github", "token"]

[[rules]]
description = "GitHub OAuth Token"
id = "github-oauth"
regex = '''gho_[0-9a-zA-Z]{36}'''
tags = ["github", "token"]

[[rules]]
description = "GitHub App Token"
id = "github-app-token"
regex = '''(ghu|ghs)_[0-9a-zA-Z]{36}'''
tags = ["github", "token"]

[[rules]]
description = "GitHub Refresh Token"
id = "github-refresh-token"
regex = '''ghr_[0-9a-zA-Z]{76}'''
tags = ["github", "token"]

[[rules]]
description = "Generic API Key"
id = "generic-api-key"
regex = '''(?i)(api[_-]?key|apikey|api[_-]?token)['\"]?\s*[:=]\s*['\"]?[0-9a-zA-Z\-_]{20,}['\"]?'''
tags = ["api", "secret", "key"]

[[rules]]
description = "Generic Secret"
id = "generic-secret"
regex = '''(?i)(secret|password|passwd|pwd)['\"]?\s*[:=]\s*['\"]?[0-9a-zA-Z\-_!@#$%^&*()+=]{12,}['\"]?'''
tags = ["secret", "password"]

[[rules]]
description = "Private Key"
id = "private-key"
regex = '''-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----'''
tags = ["key", "private"]

[[rules]]
description = "Slack Token"
id = "slack-token"
regex = '''xox[baprs]-([0-9a-zA-Z]{10,48})'''
tags = ["slack", "token"]

[[rules]]
description = "Slack Webhook"
id = "slack-webhook"
regex = '''https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}'''
tags = ["slack", "webhook"]

[[rules]]
description = "Google API Key"
id = "google-api-key"
regex = '''AIza[0-9A-Za-z\\-_]{35}'''
tags = ["google", "api", "key"]

[[rules]]
description = "Google OAuth"
id = "google-oauth"
regex = '''[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com'''
tags = ["google", "oauth"]

[[rules]]
description = "Heroku API Key"
id = "heroku-api-key"
regex = '''(?i)heroku(.{0,20})?['\"][0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}['\"]'''
tags = ["heroku", "api", "key"]

[[rules]]
description = "Stripe API Key"
id = "stripe-api-key"
regex = '''(?i)(sk|pk)_(test|live)_[0-9a-zA-Z]{24,}'''
tags = ["stripe", "api", "key"]

[[rules]]
description = "Twilio API Key"
id = "twilio-api-key"
regex = '''SK[0-9a-fA-F]{32}'''
tags = ["twilio", "api", "key"]

[allowlist]
description = "Allowlisted files and patterns"
files = [
  '''.gitleaks.toml''',
  '''package-lock.json''',
  '''yarn.lock''',
  '''pnpm-lock.yaml''',
  '''.*\.example$''',
  '''.*\.sample$''',
  '''.*\.template$''',
  '''.*\.md$''',
  '''.*\.test\.ts$''',
  '''.*\.spec\.ts$''',
]

regexes = [
  '''test[_-]?key''',
  '''fake[_-]?api[_-]?key''',
  '''example[_-]?token''',
  '''dummy[_-]?secret''',
  '''mock[_-]?password''',
  '''0{20,}''',  # All zeros
  '''1{20,}''',  # All ones
]

paths = [
  '''tests/fixtures/''',
  '''examples/''',
  '''docs/''',
]
```

### .trufflehog.yaml

```yaml
# TruffleHog configuration for deep historical scans

# Enable verified findings only (reduces false positives)
only-verified: true

# Scan entire git history
since-commit: ""

# JSON output format
json: true

# Exclude patterns
exclude:
  - path: ".*\\.example$"
  - path: ".*\\.sample$"
  - path: ".*\\.md$"
  - path: "node_modules/"
  - path: "dist/"
  - path: "coverage/"
  - path: "tests/fixtures/"

# Custom detectors (optional)
detectors:
  - name: "custom-api-key"
    regex: "custom_api_[0-9a-zA-Z]{32}"
```

### .madgerc

```json
{
  "detectiveOptions": {
    "ts": {
      "skipTypeImports": true,
      "skipAsyncImports": false
    }
  },
  "fileExtensions": ["ts", "tsx", "js", "jsx"],
  "tsConfig": "./tsconfig.json",
  "excludeRegExp": [
    "^node_modules/",
    "^dist/",
    "^coverage/",
    "^build/",
    "\\.test\\.(ts|js)$",
    "\\.spec\\.(ts|js)$",
    "\\.mock\\.(ts|js)$"
  ],
  "backgroundColor": "#000000",
  "nodeColor": "#c6c5fe",
  "noDependencyColor": "#cfffac",
  "cyclicNodeColor": "#ff6c60",
  "edgeColor": "#757575",
  "graphVizOptions": {
    "G": {
      "rankdir": "LR",
      "concentrate": "true",
      "splines": "ortho"
    }
  }
}
```

### .filesize-exceptions

```txt
# File Size Exceptions
# Add file patterns that are allowed to exceed 500 lines
# Supports glob patterns

# Generated files
src/generated/*.ts
src/types/generated/*.ts

# Configuration files
config/database.config.ts

# Complex parsers (justified)
src/core/parser/sql-parser.ts
src/core/validator/constraint-validator.ts

# Legacy code (temporary - add ticket references)
# TODO: Refactor by Q2 2026 - Issue #123
src/legacy/monolithic-service.ts
```

### .pylintrc (Python)

```ini
[MASTER]
init-hook='import sys; sys.path.append(".")'
jobs=4
persistent=yes
suggestion-mode=yes

[MESSAGES CONTROL]
disable=C0111,  # missing-docstring
        R0903,  # too-few-public-methods
        R0913,  # too-many-arguments
        C0103   # invalid-name

[FORMAT]
max-line-length=100
indent-string='    '
expected-line-ending-format=LF

[DESIGN]
max-args=7
max-locals=15
max-returns=6
max-branches=12
max-statements=50
min-public-methods=1

[BASIC]
good-names=i,j,k,ex,Run,_,id,db

[SIMILARITIES]
min-similarity-lines=10
```

### pyproject.toml (Python)

```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  | dist
  | .eggs
  | .git
  | build
  | __pycache__
  | .venv
)/
'''

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --cov --cov-report=term-missing --cov-report=html"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["."]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
]

[tool.coverage.report]
precision = 2
skip_empty = true
fail_under = 80

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
ignore_missing_imports = true
```

### checkstyle.xml (Java)

```xml
<?xml version="1.0"?>
<!DOCTYPE module PUBLIC
    "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
    "https://checkstyle.org/dtds/configuration_1_3.dtd">

<module name="Checker">
    <property name="severity" value="error"/>

    <module name="FileTabCharacter">
        <property name="eachLine" value="true"/>
    </module>

    <module name="LineLength">
        <property name="max" value="120"/>
        <property name="ignorePattern" value="^package.*|^import.*"/>
    </module>

    <module name="TreeWalker">
        <!-- Naming Conventions -->
        <module name="ConstantName"/>
        <module name="LocalFinalVariableName"/>
        <module name="LocalVariableName"/>
        <module name="MemberName"/>
        <module name="MethodName"/>
        <module name="PackageName"/>
        <module name="ParameterName"/>
        <module name="StaticVariableName"/>
        <module name="TypeName"/>

        <!-- Import Checks -->
        <module name="AvoidStarImport"/>
        <module name="IllegalImport"/>
        <module name="RedundantImport"/>
        <module name="UnusedImports"/>
        <module name="ImportOrder">
            <property name="groups" value="java,javax,org,com"/>
            <property name="ordered" value="true"/>
            <property name="separated" value="true"/>
        </module>

        <!-- Size Violations -->
        <module name="MethodLength">
            <property name="max" value="50"/>
        </module>
        <module name="ParameterNumber">
            <property name="max" value="7"/>
        </module>

        <!-- Whitespace -->
        <module name="EmptyForIteratorPad"/>
        <module name="GenericWhitespace"/>
        <module name="MethodParamPad"/>
        <module name="NoWhitespaceAfter"/>
        <module name="NoWhitespaceBefore"/>
        <module name="OperatorWrap"/>
        <module name="ParenPad"/>
        <module name="TypecastParenPad"/>
        <module name="WhitespaceAfter"/>
        <module name="WhitespaceAround"/>

        <!-- Modifiers -->
        <module name="ModifierOrder"/>
        <module name="RedundantModifier"/>

        <!-- Blocks -->
        <module name="AvoidNestedBlocks"/>
        <module name="EmptyBlock"/>
        <module name="LeftCurly"/>
        <module name="NeedBraces"/>
        <module name="RightCurly"/>

        <!-- Coding -->
        <module name="EmptyStatement"/>
        <module name="EqualsHashCode"/>
        <module name="HiddenField">
            <property name="ignoreConstructorParameter" value="true"/>
            <property name="ignoreSetter" value="true"/>
        </module>
        <module name="IllegalInstantiation"/>
        <module name="InnerAssignment"/>
        <module name="MissingSwitchDefault"/>
        <module name="SimplifyBooleanExpression"/>
        <module name="SimplifyBooleanReturn"/>

        <!-- SOLID Principles -->
        <module name="CyclomaticComplexity">
            <property name="max" value="15"/>
        </module>
        <module name="NPathComplexity">
            <property name="max" value="200"/>
        </module>

        <!-- Class Design -->
        <module name="FinalClass"/>
        <module name="HideUtilityClassConstructor"/>
        <module name="InterfaceIsType"/>
        <module name="VisibilityModifier">
            <property name="protectedAllowed" value="true"/>
        </module>
    </module>
</module>
```

---

## Hook Scripts (Complete)

### scripts/hooks/check-file-size.js

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const MAX_LINES = 500;
const EXCEPTIONS_FILE = '.filesize-exceptions';
const EXCLUDE_PATTERNS = ['node_modules', 'dist', 'coverage', 'build', '.git', '__pycache__'];

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
};

function loadExceptions() {
  if (!fs.existsSync(EXCEPTIONS_FILE)) {
    return [];
  }

  return fs.readFileSync(EXCEPTIONS_FILE, 'utf-8')
    .split('\n')
    .map(line => line.trim())
    .filter(line => line && !line.startsWith('#'));
}

function countLines(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    return content.split('\n').length;
  } catch (error) {
    console.warn(`${colors.yellow}Warning: Could not read ${filePath}${colors.reset}`);
    return 0;
  }
}

function matchesPattern(filePath, pattern) {
  // Convert glob pattern to regex
  const regexPattern = pattern
    .replace(/\./g, '\\.')
    .replace(/\*/g, '.*')
    .replace(/\?/g, '.');

  const regex = new RegExp(`^${regexPattern}$`);
  return regex.test(filePath);
}

function isExcluded(filePath, exceptions) {
  return exceptions.some(pattern => matchesPattern(filePath, pattern));
}

function getStagedFiles() {
  try {
    const output = execSync('git diff --cached --name-only --diff-filter=ACM', {
      encoding: 'utf-8'
    });
    return output.trim().split('\n').filter(Boolean);
  } catch (error) {
    console.warn(`${colors.yellow}Warning: Could not get staged files${colors.reset}`);
    return [];
  }
}

function getAllSourceFiles(dir = '.') {
  const files = [];

  function traverse(currentDir) {
    try {
      const entries = fs.readdirSync(currentDir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(currentDir, entry.name);
        const relativePath = fullPath.startsWith('./') ? fullPath.slice(2) : fullPath;

        // Skip excluded directories
        if (EXCLUDE_PATTERNS.some(pattern => relativePath.includes(pattern))) {
          continue;
        }

        if (entry.isDirectory()) {
          traverse(fullPath);
        } else if (entry.isFile()) {
          // Check source code extensions
          if (/\.(ts|tsx|js|jsx|py|java|go|rs|cpp|c|h)$/.test(entry.name)) {
            files.push(relativePath);
          }
        }
      }
    } catch (error) {
      // Silently skip directories we can't read
    }
  }

  traverse(dir);
  return files;
}

function formatViolationMessage(violations) {
  let message = `${colors.red}❌ File size violations detected:${colors.reset}\n\n`;

  violations.forEach(({ file, lines }) => {
    const excess = lines - MAX_LINES;
    message += `  ${colors.red}${file}${colors.reset}: ${lines} lines (${excess} over limit)\n`;
  });

  message += `\n${colors.yellow}Maximum allowed: ${MAX_LINES} lines per file${colors.reset}\n`;
  message += `\nTo add exceptions, update ${EXCEPTIONS_FILE}:\n`;
  message += `  ${colors.yellow}# Example:${colors.reset}\n`;
  message += `  ${colors.yellow}src/specific/file.ts${colors.reset}\n`;
  message += `  ${colors.yellow}src/generated/*.ts${colors.reset}\n`;

  return message;
}

function main() {
  console.log('🔍 Checking file sizes...\n');

  const exceptions = loadExceptions();
  const stagedFiles = getStagedFiles();

  // If running in git hook context, only check staged files
  // Otherwise, check all source files
  const filesToCheck = stagedFiles.length > 0 ? stagedFiles : getAllSourceFiles();

  if (filesToCheck.length === 0) {
    console.log(`${colors.yellow}No files to check${colors.reset}\n`);
    process.exit(0);
  }

  const violations = [];

  for (const file of filesToCheck) {
    if (!fs.existsSync(file)) continue;

    // Only check source code files
    if (!/\.(ts|tsx|js|jsx|py|java|go|rs|cpp|c|h)$/.test(file)) continue;

    // Skip if in exceptions list
    if (isExcluded(file, exceptions)) {
      continue;
    }

    const lineCount = countLines(file);

    if (lineCount > MAX_LINES) {
      violations.push({ file, lines: lineCount });
    }
  }

  if (violations.length > 0) {
    console.error(formatViolationMessage(violations));
    process.exit(1);
  }

  console.log(`${colors.green}✅ All files are within size limits${colors.reset}\n`);
  process.exit(0);
}

main();
```

### scripts/hooks/check-documentation.js

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DOCS_DIR = 'docs';
const DOC_EXTENSIONS = ['.md', '.pdf', '.txt'];
const ALLOWED_ROOT_DOCS = [
  'README.md',
  'LICENSE',
  'LICENSE.md',
  'LICENSE.txt',
  'CHANGELOG.md',
  'CONTRIBUTING.md',
  'CODE_OF_CONDUCT.md',
];

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
};

function getStagedFiles() {
  try {
    const output = execSync('git diff --cached --name-only --diff-filter=ACM', {
      encoding: 'utf-8'
    });
    return output.trim().split('\n').filter(Boolean);
  } catch (error) {
    return [];
  }
}

function isDocFile(file) {
  return DOC_EXTENSIONS.some(ext => file.toLowerCase().endsWith(ext));
}

function isAllowedRootDoc(file) {
  const basename = path.basename(file);
  return ALLOWED_ROOT_DOCS.includes(basename);
}

function main() {
  console.log('📚 Checking documentation location...\n');

  const stagedFiles = getStagedFiles();
  const violations = [];

  for (const file of stagedFiles) {
    if (!isDocFile(file)) continue;

    const isInDocs = file.startsWith(`${DOCS_DIR}/`);
    const isRoot = !file.includes('/');

    if (!isInDocs && !isRoot) {
      // Doc file in subdirectory that's not docs/
      violations.push({
        file,
        reason: `should be in ${DOCS_DIR}/ directory`,
      });
    } else if (isRoot && !isAllowedRootDoc(file)) {
      // Doc file in root that's not allowed
      violations.push({
        file,
        reason: `not in allowed root docs list`,
      });
    }
  }

  if (violations.length > 0) {
    console.error(`${colors.red}❌ Documentation files in wrong location:${colors.reset}\n`);
    violations.forEach(({ file, reason }) => {
      console.error(`  ${colors.red}${file}${colors.reset}`);
      console.error(`    → ${reason}\n`);
    });

    console.error(`${colors.yellow}Allowed root documentation files:${colors.reset}`);
    ALLOWED_ROOT_DOCS.forEach(doc => {
      console.error(`  - ${doc}`);
    });
    console.error('');
    console.error(`${colors.yellow}All other .md/.pdf files must be in ${DOCS_DIR}/${colors.reset}\n`);

    process.exit(1);
  }

  console.log(`${colors.green}✅ All documentation files are correctly placed${colors.reset}\n`);
  process.exit(0);
}

main();
```

### scripts/hooks/detect-languages.js

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const LANGUAGE_PATTERNS = {
  typescript: ['.ts', '.tsx'],
  javascript: ['.js', '.jsx'],
  python: ['.py'],
  java: ['.java'],
  go: ['.go'],
  rust: ['.rs'],
  cpp: ['.cpp', '.cc', '.cxx', '.c', '.h', '.hpp'],
};

const EXCLUDE_DIRS = [
  'node_modules',
  'dist',
  'build',
  'coverage',
  '__pycache__',
  '.git',
  '.venv',
  'venv',
  'target',
];

function detectLanguages(dir = '.') {
  const languages = new Set();

  function traverse(currentDir) {
    try {
      const entries = fs.readdirSync(currentDir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = path.join(currentDir, entry.name);

        // Skip excluded directories
        if (EXCLUDE_DIRS.includes(entry.name)) {
          continue;
        }

        if (entry.isDirectory()) {
          traverse(fullPath);
        } else if (entry.isFile()) {
          // Check file extension against language patterns
          for (const [language, extensions] of Object.entries(LANGUAGE_PATTERNS)) {
            if (extensions.some(ext => entry.name.endsWith(ext))) {
              languages.add(language);
            }
          }
        }
      }
    } catch (error) {
      // Silently skip directories we can't read
    }
  }

  traverse(dir);
  return Array.from(languages);
}

function main() {
  const languages = detectLanguages();

  if (languages.length === 0) {
    console.log('No source files detected');
    process.exit(0);
  }

  // Output as comma-separated list
  console.log(languages.join(','));
  process.exit(0);
}

main();
```

---

## Claude Code Integration

### .claude/CLAUDE.md

```markdown
# Claude Code Instructions

This repository uses automated quality gates to ensure code quality and architectural consistency. Please follow these guidelines when working with Claude Code.

## Repository Best Practices

### 1. Documentation Location

**Rule**: ALL `.md` and `.pdf` files MUST be in the `docs/` directory

**Exceptions**: These files are allowed in root:
- README.md
- LICENSE / LICENSE.md
- CHANGELOG.md
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md

**Why**: Centralized documentation improves discoverability and maintains clean repository structure.

**Example**:
```
✅ docs/api-guide.md
✅ docs/setup-instructions.pdf
❌ src/README.md
❌ components/guide.md
```

### 2. File Size Limits

**Rule**: Maximum 500 lines per file

**Exceptions**: Add patterns to `.filesize-exceptions`

**Why**: Enforces Single Responsibility Principle and improves code maintainability.

**When to add exceptions**:
- Generated files (e.g., `src/generated/*.ts`)
- Complex parsers with justification
- Temporary: Legacy code with refactoring ticket

**Example .filesize-exceptions**:
```txt
# Generated files
src/generated/*.ts

# Complex parser - justified
src/core/parser/sql-parser.ts

# TODO: Refactor by Q2 2026 - Issue #456
src/legacy/monolithic-service.ts
```

### 3. Commit Messages

**Rule**: ALWAYS use Conventional Commits format

**Command**: Run `npm run commit` for interactive commit creation

**Format**: `type(scope): description`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting changes
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance, dependency updates
- `ci`: CI/CD changes
- `build`: Build system changes
- `revert`: Revert previous commit

**Scopes**: core, cli, api, ui, db, auth, tests, docs, deps, config, hooks, ci, security

**Examples**:
```
✅ feat(api): add user authentication endpoint
✅ fix(core): resolve circular dependency in data loader
✅ docs(setup): update installation instructions
✅ refactor(db): extract connection pool to separate module
❌ Added stuff
❌ Fix bug
```

### 4. Code Quality Requirements

**All checks MUST pass before commit**:
- ✅ ESLint (TypeScript/JavaScript)
- ✅ pylint (Python, if present)
- ✅ Checkstyle (Java, if present)
- ✅ Prettier formatting
- ✅ Jest/pytest/JUnit tests (80% coverage minimum)
- ✅ No secrets in codebase
- ✅ No circular dependencies
- ✅ File size limits

**Manual check**: `npm run check:all`

### 5. Architecture Patterns

**SOLID Principles** (enforced via ESLint):

1. **Single Responsibility Principle**:
   - Max 50 lines per function
   - Max 15 cognitive complexity
   - Break down large functions

2. **Open/Closed Principle**:
   - Explicit function return types
   - Explicit module boundary types

3. **Liskov Substitution Principle**:
   - No `any` types
   - Strict boolean expressions

4. **Interface Segregation Principle**:
   - Prefer readonly properties
   - Small, focused interfaces

5. **Dependency Inversion Principle**:
   - Use constructor injection
   - Depend on abstractions (interfaces), not concretions

**Dependency Injection Example**:
```typescript
// ✅ Good: Constructor injection
class UserService {
  constructor(
    private readonly userRepository: IUserRepository,
    private readonly emailService: IEmailService
  ) {}

  async createUser(data: UserData): Promise<User> {
    const user = await this.userRepository.create(data);
    await this.emailService.sendWelcome(user.email);
    return user;
  }
}

// ❌ Bad: Direct instantiation
class UserService {
  private userRepository = new UserRepository();
  private emailService = new EmailService();

  async createUser(data: UserData): Promise<User> {
    const user = await this.userRepository.create(data);
    await this.emailService.sendWelcome(user.email);
    return user;
  }
}
```

### 6. Testing

**Requirements**:
- Write tests for all new features
- Maintain 80% code coverage minimum
- Use Jest for TypeScript unit/integration tests
- Use pytest for Python tests
- Use JUnit for Java tests

**Test file location**:
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests

**Example**:
```typescript
// src/services/user.service.ts → tests/unit/services/user.service.test.ts
```

### 7. Git Workflow

**Pre-commit hooks automatically run**:
1. Language detection
2. Linting (ESLint/pylint/Checkstyle)
3. Testing (Jest/pytest/JUnit)
4. File size check
5. Documentation location check
6. Secret scanning (Gitleaks)
7. Format checking (Prettier/Black/Google Java Format)

**Pre-push hooks automatically run**:
1. Circular dependency check (Madge)
2. Full test coverage (80% threshold)
3. Build verification
4. Optional: Deep secret scan (TruffleHog)

**Bypass**: Use `--no-verify` ONLY in emergencies with user approval

### 8. Secret Detection

**Fast scan** (pre-commit): Gitleaks
**Deep scan** (pre-push, optional): TruffleHog

**If secrets detected**:
1. Remove secret from code
2. Add to `.gitignore`
3. Rotate/invalidate the secret
4. If in git history: Run `npm run check:secrets:deep`
5. Emergency cleanup: Use `scripts/security/cleanup-secrets.sh`

**Never commit**:
- API keys
- Passwords
- Private keys
- OAuth tokens
- Database credentials
- AWS access keys

**Use instead**:
- Environment variables
- `.env` files (gitignored)
- Secret management services (AWS Secrets Manager, Vault)

## Slash Commands

Use these commands for common workflows:

### /commit-push-pr
Complete workflow: commit (with Commitizen), push, create PR

### /run-checks
Run all pre-commit checks manually without committing

### /fix-violations
Auto-fix linting and formatting issues

### /check-secrets
Run comprehensive secret scan (Gitleaks + TruffleHog)

## Common Pitfalls

### 1. Don't bypass hooks without permission
**Why**: Hooks exist for quality assurance. Bypassing defeats the purpose.
**When to ask**: User explicitly requests urgent fix with `--no-verify`

### 2. Don't create large files
**Why**: Violates Single Responsibility Principle.
**Fix**: Break down into smaller, focused modules.

### 3. Don't ignore circular dependencies
**Why**: Creates tight coupling and makes testing difficult.
**Fix**: Extract shared code to new module, use dependency injection.

### 4. Don't commit secrets
**Why**: Security risk, cannot be easily removed from git history.
**Fix**: Use environment variables, rotate compromised secrets.

### 5. Don't skip tests
**Why**: Tests ensure code quality and prevent regressions.
**Fix**: Write tests alongside code, maintain 80% coverage.

## Emergency Procedures

If hooks are blocking urgent fixes:

1. **Ask user permission first**
2. Use `git commit --no-verify` ONLY with approval
3. Create follow-up issue to fix violations (required)
4. NEVER use `--no-verify` for routine commits

## File Organization

```
project/
├── docs/                # ALL documentation files
├── src/                 # Source code
│   ├── core/           # Core business logic
│   ├── api/            # API endpoints
│   ├── cli/            # CLI interface
│   └── utils/          # Shared utilities
├── tests/              # All tests
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── .claude/           # Claude Code configuration
│   ├── CLAUDE.md      # This file
│   ├── project_conventions.md
│   ├── architecture_decisions.md
│   └── common_patterns.md
└── scripts/           # Utility scripts
```

## Questions?

Refer to:
- [docs/SETUP.md](docs/SETUP.md) - Setup instructions
- [docs/HOOKS.md](docs/HOOKS.md) - Git hooks documentation
- [docs/SECURITY.md](docs/SECURITY.md) - Secret detection guide
- [.claude/project_conventions.md](.claude/project_conventions.md) - Coding standards
- [.claude/architecture_decisions.md](.claude/architecture_decisions.md) - Architecture patterns
- [.claude/common_patterns.md](.claude/common_patterns.md) - Reusable code patterns
```

---

## Enforcement Matrix

| Best Practice | Enforcement Mechanism | Hook Stage | Can Bypass | Rationale |
|---------------|----------------------|------------|------------|-----------|
| Documentation in docs/ | Custom script check | pre-commit | With --no-verify | Centralized docs improve discoverability |
| Tests pass (all languages) | Jest/pytest/JUnit | pre-commit | With --no-verify | Prevents broken code from entering repo |
| Code linted (all languages) | ESLint/pylint/Checkstyle | pre-commit | With --no-verify | Enforces consistent code style and catches errors |
| Code formatted | Prettier/Black/Google Java Format | pre-commit | With --no-verify | Eliminates style debates, consistent formatting |
| Max 500 lines/file | Custom script + exceptions file | pre-commit | Via .filesize-exceptions | Enforces Single Responsibility Principle |
| SOLID principles | ESLint rules + SonarJS | pre-commit | Only by fixing | Improves maintainability and testability |
| Dependency injection | ESLint rules + manual review | pre-commit | Only by fixing | Reduces coupling, improves testability |
| No recursive loops | Static analysis (future) | pre-commit | Only by fixing | Prevents infinite loops and performance issues |
| No secrets (fast scan) | Gitleaks | pre-commit | With --no-verify | Fast detection of common secret patterns |
| No secrets (deep scan) | TruffleHog | pre-push + CI | With --no-verify | Comprehensive historical secret detection |
| Conventional Commits | Commitlint | commit-msg | With --no-verify | Consistent commit history, automated changelogs |
| No circular deps | Madge + ESLint | pre-push | With --no-verify | Reduces coupling, improves module boundaries |
| 80% test coverage | Jest/pytest/JaCoCo thresholds | pre-push | With --no-verify | Ensures adequate testing |
| Build succeeds | TypeScript/Python/Java compilers | pre-push | With --no-verify | Prevents broken builds from being pushed |

---

## Troubleshooting Guide

### Hook Failed: Secrets Detected

**Problem**: Gitleaks or TruffleHog detected potential secrets

**Solutions**:

1. **False positive**: Add to `.gitleaks.toml` allowlist
   ```toml
   [allowlist]
   regexes = [
     '''test[_-]?key_12345''',  # Specific test key
   ]
   ```

2. **Real secret in current commit**:
   ```bash
   # Remove secret from file
   # Add to .env (gitignored)
   # Rotate/invalidate the secret
   git add .
   npm run commit
   ```

3. **Secret in git history**:
   ```bash
   # Run deep scan
   npm run check:secrets:deep

   # Review results
   cat trufflehog-results.json

   # Remove from history (DANGEROUS!)
   bash scripts/security/cleanup-secrets.sh
   ```

### Hook Failed: Circular Dependencies

**Problem**: Madge detected circular dependencies

**View dependency graph**:
```bash
npx madge --image graph.svg --circular src/
open graph.svg
```

**Common fixes**:

1. **Extract shared code**:
   ```typescript
   // Before: A → B → A (circular)
   // moduleA.ts
   import { funcB } from './moduleB';
   export const funcA = () => funcB();

   // moduleB.ts
   import { funcA } from './moduleA';  // ❌ Circular!
   export const funcB = () => funcA();

   // After: A → Shared ← B
   // shared.ts
   export const sharedFunc = () => { /* ... */ };

   // moduleA.ts
   import { sharedFunc } from './shared';
   export const funcA = () => sharedFunc();

   // moduleB.ts
   import { sharedFunc } from './shared';
   export const funcB = () => sharedFunc();
   ```

2. **Use dependency injection**:
   ```typescript
   // Before: A imports B, B imports A

   // After: Inject dependencies
   class ServiceA {
     constructor(private serviceB: ServiceB) {}
   }

   class ServiceB {
     constructor(private serviceA: ServiceA) {}
   }

   // Factory creates instances
   export const createServices = () => {
     const serviceA = new ServiceA(null!);
     const serviceB = new ServiceB(serviceA);
     serviceA.serviceB = serviceB;
     return { serviceA, serviceB };
   };
   ```

3. **Break dependency chain**:
   - Move interface to separate file
   - Use events/pub-sub pattern
   - Invert control flow

### Hook Failed: File Size

**Problem**: File exceeds 500 lines

**Solutions**:

1. **Refactor file** (preferred):
   ```typescript
   // Before: UserService.ts (800 lines)
   class UserService {
     create() { /* 100 lines */ }
     update() { /* 100 lines */ }
     delete() { /* 100 lines */ }
     validate() { /* 200 lines */ }
     sendEmail() { /* 150 lines */ }
     generateReport() { /* 150 lines */ }
   }

   // After: Split into focused modules
   // UserService.ts (200 lines)
   class UserService {
     constructor(
       private validator: UserValidator,
       private emailService: EmailService,
       private reportService: ReportService
     ) {}

     create() { /* 100 lines */ }
     update() { /* 50 lines */ }
     delete() { /* 50 lines */ }
   }

   // UserValidator.ts (200 lines)
   // EmailService.ts (150 lines)
   // ReportService.ts (150 lines)
   ```

2. **Add exception** (temporary):
   ```txt
   # .filesize-exceptions
   # TODO: Refactor by Q2 2026 - Issue #456
   src/services/user-service.ts
   ```

### Hook Failed: Test Coverage Below 80%

**Problem**: Test coverage below threshold

**Check coverage report**:
```bash
npm run test:coverage
open coverage/lcov-report/index.html
```

**Add missing tests**:
```typescript
// src/services/user.service.ts
export class UserService {
  createUser(data: UserData): User {
    if (!data.email) throw new Error('Email required');
    return { id: generateId(), ...data };
  }
}

// tests/unit/services/user.service.test.ts
describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  it('should create user with valid data', () => {
    const user = service.createUser({ email: 'test@example.com', name: 'Test' });
    expect(user).toMatchObject({ email: 'test@example.com', name: 'Test' });
  });

  it('should throw error when email is missing', () => {
    expect(() => service.createUser({ name: 'Test' })).toThrow('Email required');
  });
});
```

### Hook Failed: Linting Errors

**Auto-fix**:
```bash
npm run lint:fix
npm run format
```

**Manual fixes** (common issues):

1. **Unused imports**:
   ```typescript
   // ❌ Before
   import { used, unused } from './module';

   // ✅ After
   import { used } from './module';
   ```

2. **Missing return type**:
   ```typescript
   // ❌ Before
   function getUser(id: string) {
     return users.find(u => u.id === id);
   }

   // ✅ After
   function getUser(id: string): User | undefined {
     return users.find(u => u.id === id);
   }
   ```

3. **Cognitive complexity too high**:
   ```typescript
   // ❌ Before: Complexity = 20
   function processData(data: Data[]): Result {
     for (const item of data) {
       if (item.type === 'A') {
         if (item.valid) {
           if (item.priority > 5) {
             // ... 50 lines of nested logic
           }
         }
       }
     }
   }

   // ✅ After: Extract functions
   function processData(data: Data[]): Result {
     return data
       .filter(isTypeA)
       .filter(isValid)
       .filter(isHighPriority)
       .map(processItem);
   }

   function isTypeA(item: Data): boolean {
     return item.type === 'A';
   }

   function isValid(item: Data): boolean {
     return item.valid;
   }

   function isHighPriority(item: Data): boolean {
     return item.priority > 5;
   }

   function processItem(item: Data): Result {
     // ... focused logic
   }
   ```

---

## References & Sources

### Tool Documentation

- **Husky**: https://typicode.github.io/husky/
- **Commitizen**: https://github.com/commitizen/cz-cli
- **Commitlint**: https://github.com/conventional-changelog/commitlint
- **Gitleaks**: https://github.com/gitleaks/gitleaks
- **TruffleHog**: https://github.com/trufflesecurity/trufflehog
- **git-filter-repo**: https://github.com/newren/git-filter-repo
- **Madge**: https://github.com/pahen/madge
- **ESLint**: https://eslint.org/
- **TypeScript-ESLint**: https://typescript-eslint.io/
- **SonarJS**: https://github.com/SonarSource/eslint-plugin-sonarjs
- **Prettier**: https://prettier.io/

### Research & Comparisons

- [Comparing pre-commit Alternatives](https://jellybeanz.medium.com/comparing-pre-commit-alternatives-and-applying-git-hooks-with-husky-9863c2e9fb4c)
- [TruffleHog vs Gitleaks Comparison](https://www.jit.io/resources/appsec-tools/trufflehog-vs-gitleaks-a-detailed-comparison-of-secret-scanning-tools)
- [Top 8 Git Secrets Scanners](https://www.jit.io/resources/appsec-tools/git-secrets-scanners-key-features-and-top-tools-)
- [20 Powerful Static Analysis Tools for TypeScript](https://www.in-com.com/blog/20-powerful-static-analysis-tools-every-typescript-team-needs/)
- [Detecting Circular Dependencies with Madge](https://dev.to/greenroach/detecting-circular-dependencies-in-a-reacttypescript-app-using-madge-229)
- [Conventional Commits with Commitizen](https://medium.com/@imdavidrock/why-should-you-use-commitizen-husky-for-conventional-commit-and-have-unified-lint-41047aad6d)

### SOLID Principles

- Clean Code by Robert C. Martin
- Clean Architecture by Robert C. Martin
- SOLID Principles: https://en.wikipedia.org/wiki/SOLID

---

## Appendix: Quick Reference

### Package.json Scripts Cheat Sheet

```bash
# Commit workflow
npm run commit              # Interactive commit with Commitizen

# Linting
npm run lint                # ESLint (TypeScript)
npm run lint:fix            # Auto-fix ESLint issues
npm run lint:python         # pylint (Python)
npm run lint:java           # Checkstyle (Java)

# Formatting
npm run format              # Format TypeScript with Prettier
npm run format:check        # Check formatting without changes
npm run format:python       # Format Python with Black
npm run format:java         # Format Java with Google Java Format

# Testing
npm run test                # Run Jest tests
npm run test:coverage       # Run tests with coverage
npm run test:python         # Run pytest
npm run test:java           # Run JUnit

# Checks
npm run check:deps          # Check circular dependencies (Madge)
npm run check:secrets       # Fast secret scan (Gitleaks)
npm run check:secrets:deep  # Deep secret scan (TruffleHog)
npm run check:file-size     # Check file size limits
npm run check:docs          # Check documentation location
npm run check:languages     # Detect project languages
npm run check:all           # Run ALL checks

# Building
npm run build               # Build TypeScript
npm run build:python        # Build Python
npm run build:java          # Build Java
```

### Git Commands

```bash
# Commit with interactive Commitizen
git commit

# Bypass hooks (emergency only, with approval)
git commit --no-verify
git push --no-verify

# View staged files
git diff --cached --name-only

# View dependency graph
npx madge --image graph.svg --circular src/
```

### File Locations

```
.
├── .claude/
│   ├── CLAUDE.md                    # Claude Code instructions
│   ├── project_conventions.md       # Coding standards
│   ├── architecture_decisions.md    # ADRs
│   ├── common_patterns.md           # Reusable patterns
│   ├── commands/                    # Slash commands
│   └── settings.json                # Settings
│
├── .husky/
│   ├── pre-commit                   # Pre-commit hook
│   ├── prepare-commit-msg           # Commitizen launcher
│   ├── commit-msg                   # Message validator
│   └── pre-push                     # Pre-push hook
│
├── scripts/
│   ├── hooks/
│   │   ├── check-file-size.js       # File size checker
│   │   ├── check-documentation.js   # Docs location checker
│   │   └── detect-languages.js      # Language detector
│   ├── security/
│   │   ├── scan-history.sh          # TruffleHog scan
│   │   └── cleanup-secrets.sh       # Secret removal
│   ├── setup.sh                     # Linux/macOS setup
│   └── setup.ps1                    # Windows setup
│
├── docs/
│   ├── template_plan.md             # This file
│   ├── SETUP.md                     # Setup guide
│   ├── HOOKS.md                     # Hooks documentation
│   └── SECURITY.md                  # Security guide
│
└── Config files
    ├── .eslintrc.js
    ├── .prettierrc.json
    ├── commitlint.config.js
    ├── .gitleaks.toml
    ├── .trufflehog.yaml
    ├── .madgerc
    ├── .filesize-exceptions
    ├── .pylintrc (Python)
    ├── pyproject.toml (Python)
    └── checkstyle.xml (Java)
```

---

**End of Implementation Plan**

**Version**: 1.0
**Last Updated**: 2026-01-07
**Total Files to Create**: 37
**Estimated Implementation Time**: 6 weeks

For questions or clarifications, refer to the individual documentation files in the docs/ directory or consult the team lead.
