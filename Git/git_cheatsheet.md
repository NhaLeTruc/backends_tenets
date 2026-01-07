# Git Cheatsheet

---

## Part 1: Git Fundamentals & Concepts (30 minutes)

Git is a distributed version control system - it's the core technology that tracks changes in source code. It operates locally on your machine and doesn't require a network connection for most operations. GitHub, on the other hand, is a cloud-based hosting service for Git repositories. It adds collaboration features like pull requests, issue tracking, code review tools, and CI/CD integration on top of Git.

Files in Git exist in three states:

1. **Modified** - You've changed the file but haven't committed it to your database yet. These changes exist only in your working directory.

2. **Staged** - You've marked a modified file in its current version to go into your next commit snapshot. This happens when you use `git add`.

3. **Committed** - The data is safely stored in your local database. The file is in the Git directory (repository).

There's also a fourth state worth mentioning: **Untracked** - files that Git doesn't know about yet.

**Sarah:** Excellent. Can you explain the difference between `git fetch`, `git pull`, and `git merge`?

**Alex:** Of course.

- **`git fetch`** downloads commits, files, and refs from a remote repository into your local repo, but it doesn't merge anything. It updates your remote-tracking branches (like `origin/main`) but leaves your working branch untouched. It's the safe way to see what others have been working on.

- **`git pull`** is essentially `git fetch` followed by `git merge`. It downloads changes from the remote AND merges them into your current branch. It's convenient but can be problematic if you have uncommitted changes.

- **`git merge`** takes the changes from one branch and integrates them into another branch. It creates a new "merge commit" that ties together the histories of both branches.

**Sarah:** What about `git rebase`? How does it differ from `git merge`, and when would you use one over the other?

**Alex:** Great question. `git rebase` rewrites commit history by moving or combining commits. Instead of creating a merge commit, it replays your commits on top of another branch, creating a linear history.

**Key differences:**

- **Merge** preserves the complete history and creates a merge commit. It's non-destructive.
- **Rebase** creates a cleaner, linear history but rewrites commit history, which can be destructive.

**When to use each:**

- **Use merge when:**
  - You're integrating a feature branch into main/develop
  - You want to preserve the complete history
  - You're working on a public branch others are using

- **Use rebase when:**
  - Cleaning up local commits before pushing
  - Updating your feature branch with latest main
  - You want a clean, linear history
  - You're working on a private branch

**Golden rule:** Never rebase commits that have been pushed to a public repository that others are working from.

**Sarah:** Excellent. Let's talk about a scenario. You've just committed something to your local branch and realize you made a mistake. What are your options, and how do they differ?

**Alex:** There are several approaches depending on the situation:

1. **`git commit --amend`** - If you haven't pushed yet and want to modify the most recent commit. This lets you change the commit message or add forgotten files. It rewrites history.

2. **`git reset --soft HEAD~1`** - Undoes the last commit but keeps changes staged. Good if you want to re-commit differently.

3. **`git reset --mixed HEAD~1`** - Undoes the last commit and unstages changes, but keeps them in working directory. This is the default reset mode.

4. **`git reset --hard HEAD~1`** - Completely removes the last commit and all changes. Dangerous - use with caution.

5. **`git revert HEAD`** - Creates a new commit that undoes the changes. This is safe for commits that have been pushed because it doesn't rewrite history.

If the commit has been pushed, I'd use `git revert` to maintain history integrity.

---

## Part 2: Branching Strategies & Workflows (25 minutes)

**Sarah:** Let's discuss branching strategies. Can you describe Git Flow and explain when it's appropriate?

**Alex:** Git Flow is a branching model designed around project releases. It uses several long-lived branches:

**Branches:**
- **main/master** - Production-ready code
- **develop** - Integration branch for features
- **feature/** - Feature development branches
- **release/** - Preparation for production release
- **hotfix/** - Emergency fixes for production

**Workflow:**
1. Features branch off `develop`
2. Completed features merge back to `develop`
3. When ready for release, create `release/` branch from `develop`
4. After testing, merge `release/` to both `main` and `develop`
5. Hotfixes branch from `main` and merge back to both `main` and `develop`

**When to use:**
- Projects with scheduled releases
- Multiple versions in production
- Teams that need strict release management
- Traditional software with longer release cycles

**Sarah:** What about alternatives? When might Git Flow not be the best choice?

**Alex:** Great question. Git Flow can be overkill for many modern projects. Alternatives include:

1. **GitHub Flow** - Simpler, single main branch with feature branches. Deploy from main. Better for continuous deployment and web apps.

2. **GitLab Flow** - Middle ground between Git Flow and GitHub Flow. Uses environment branches (staging, production).

3. **Trunk-Based Development** - Developers commit to trunk/main frequently (at least daily), use feature flags for incomplete features. Great for high-performing teams practicing CI/CD.

**When Git Flow isn't ideal:**
- Continuous deployment environments
- Small teams that ship frequently
- Web applications with single production version
- Teams that want faster iteration

For data engineering pipelines, I often prefer a modified GitHub Flow with environment-specific branches and robust testing gates.

**Sarah:** Speaking of data engineering - how would you structure branches for a data pipeline project where you have dev, staging, and production environments?

**Alex:** For data pipelines, I'd recommend a GitLab Flow-inspired approach:

```
main (production)
  ↑
staging
  ↑
develop
  ↑
feature/* branches
```

**Strategy:**
1. **Feature branches** (`feature/add-customer-etl`) - individual work
2. **Develop branch** - integration testing, runs against dev environment
3. **Staging branch** - pre-production validation with production-like data
4. **Main branch** - production deployments

**Key principles:**
- All features branch from `develop`
- Merge to `develop` triggers CI/CD to dev environment
- After testing, promote to `staging` via PR
- After validation, promote to `main` via PR
- No direct commits to `develop`, `staging`, or `main`
- Use tags for production releases
- Hotfixes can go directly to `staging` then `main`, then back-merge to `develop`

**Additional considerations for data engineering:**
- Schema migrations tracked in version control
- Data quality tests run in CI/CD
- Backward compatibility checks for pipeline changes
- Rollback procedures documented

---

## Part 3: Practical Git Commands & Workflows (35 minutes)

**Sarah:** Let's get into practical scenarios. Walk me through the exact commands you'd use to start working on a new feature.

**Alex:** Sure, here's my typical workflow:

```bash
# First, ensure my local main is up to date
git checkout main
git pull origin main

# Create and switch to a new feature branch
git checkout -b feature/add-user-analytics

# Or in one command with newer Git:
# git switch -c feature/add-user-analytics

# Verify I'm on the correct branch
git branch

# Start working... make changes to files

# Check what's changed
git status

# Review specific changes
git diff

# Stage specific files
git add src/analytics/user_metrics.py
git add tests/test_user_metrics.py

# Or stage all changes
# git add .

# Commit with a descriptive message
git commit -m "Add user analytics tracking module

- Implement daily active user metrics
- Add data retention policies
- Include unit tests for metric calculations"

# Push to remote and set upstream tracking
git push -u origin feature/add-user-analytics
```

**Sarah:** Good. Now let's say you're halfway through your feature and need to pull in the latest changes from main. How do you handle that?

**Alex:** I have two approaches depending on the situation:

**Approach 1 - Rebase (preferred for clean history):**
```bash
# Save current work if not ready to commit
git stash save "WIP: analytics feature in progress"

# Fetch latest from remote
git fetch origin

# Rebase my feature branch onto latest main
git rebase origin/main

# If conflicts occur, resolve them:
# - Edit conflicting files
# - git add <resolved-files>
# - git rebase --continue
# - Repeat until rebase complete

# If things go wrong:
# git rebase --abort

# Restore stashed work if needed
git stash pop

# Force push since rebase rewrites history
git push --force-with-lease origin feature/add-user-analytics
```

**Approach 2 - Merge (preserves history):**
```bash
# Commit or stash current work
git add .
git commit -m "WIP: checkpoint before merge"

# Fetch and merge
git fetch origin
git merge origin/main

# Resolve conflicts if any
# Then commit the merge
git add .
git commit -m "Merge latest main into feature branch"

# Push normally
git push origin feature/add-user-analytics
```

I prefer rebase for feature branches to keep history clean, but use merge for integrating completed features.

**Sarah:** What if you've started working on the wrong branch?

**Alex:** No problem, several ways to handle it:

**If you haven't committed yet:**
```bash
# Stash the changes
git stash

# Switch to correct branch (or create it)
git checkout correct-branch
# or: git checkout -b correct-branch

# Apply the stashed changes
git stash pop
```

**If you've already committed:**
```bash
# Option 1: Cherry-pick the commits
git log  # Note the commit SHAs you want to move

git checkout correct-branch
git cherry-pick <commit-sha>
git cherry-pick <another-commit-sha>

# Then remove them from wrong branch
git checkout wrong-branch
git reset --hard HEAD~2  # Remove last 2 commits

# Option 2: Create a new branch from current location
git checkout -b correct-branch  # Creates branch with all commits
git checkout wrong-branch
git reset --hard origin/wrong-branch  # Reset to remote state
```

**Sarah:** Excellent. Let's talk about merge conflicts. Walk me through how you'd resolve a complex conflict.

**Alex:** Sure, here's my systematic approach:

```bash
# After a merge or rebase creates conflicts:
# Git will show:
# CONFLICT (content): Merge conflict in src/pipeline/etl.py

# Step 1: See which files have conflicts
git status

# Step 2: Open the conflicting file
# You'll see conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> branch-name

# Step 3: Understand both sides
git show :1:src/pipeline/etl.py  # Common ancestor
git show :2:src/pipeline/etl.py  # Your version (HEAD)
git show :3:src/pipeline/etl.py  # Their version

# Step 4: Decide resolution strategy:
# - Keep yours: git checkout --ours src/pipeline/etl.py
# - Keep theirs: git checkout --theirs src/pipeline/etl.py
# - Manual merge: Edit the file to combine both

# Step 5: For manual resolution, edit the file
# Remove conflict markers
# Combine logic appropriately
# Test that it works!

# Step 6: Mark as resolved
git add src/pipeline/etl.py

# Step 7: Verify no other conflicts
git status

# Step 8: Complete the merge/rebase
git commit  # For merge
# or
git rebase --continue  # For rebase

# Step 9: Run tests!
pytest tests/

# Step 10: Push if everything works
git push
```

**Key practices:**
- Always understand WHY there's a conflict
- Run tests after resolving
- Consider using a merge tool: `git mergetool`
- For complex conflicts, communicate with the other developer

**Sarah:** What tools or commands do you use to investigate the history of a file or find when a bug was introduced?

**Alex:** Great question. I use several tools:

**1. `git log` variants:**
```bash
# Basic history
git log

# Compact one-line format
git log --oneline

# Visual branch history
git log --oneline --graph --all --decorate

# History of specific file
git log --follow src/pipeline/etl.py

# See actual changes in each commit
git log -p src/pipeline/etl.py

# See stats (files changed, insertions/deletions)
git log --stat

# Filter by author
git log --author="Alex Morgan"

# Filter by date
git log --since="2 weeks ago" --until="yesterday"

# Search commit messages
git log --grep="bug fix"

# Find commits that changed specific code
git log -S "def process_data" --source --all
```

**2. `git blame` to find who changed what:**
```bash
# See line-by-line authorship
git blame src/pipeline/etl.py

# Blame with commit messages
git blame -s src/pipeline/etl.py

# Blame specific line range
git blame -L 50,60 src/pipeline/etl.py

# See blame from specific commit
git blame <commit-sha> -- src/pipeline/etl.py
```

**3. `git bisect` to find when bug introduced:**
```bash
# Start bisect session
git bisect start

# Mark current commit as bad
git bisect bad

# Mark last known good commit
git bisect good v2.3.0

# Git checks out middle commit
# Test if bug exists
pytest tests/test_etl.py

# If bug exists:
git bisect bad
# If bug doesn't exist:
git bisect good

# Repeat until Git finds the problematic commit
# Git will tell you: "X is the first bad commit"

# End bisect session
git bisect reset
```

**4. `git show` to inspect specific commits:**
```bash
# Show commit details
git show <commit-sha>

# Show specific file from commit
git show <commit-sha>:src/pipeline/etl.py

# Show commit stats
git show --stat <commit-sha>
```

**5. `git diff` for comparisons:**
```bash
# Compare commits
git diff commit1..commit2

# Compare branches
git diff main..feature/analytics

# See what's changed in a file between commits
git diff commit1 commit2 -- src/pipeline/etl.py
```

---

## Part 4: Team Collaboration & Code Review (25 minutes)

**Sarah:** As a team lead, you'll be managing pull requests. What's your process for reviewing code and what do you look for?

**Alex:** My PR review process is systematic:

**Before reviewing:**
```bash
# Fetch latest
git fetch origin

# Check out the PR branch locally
git checkout -b review/feature-branch origin/feature-branch

# Or use GitHub CLI
gh pr checkout 123

# Review the changes
git log main..HEAD --oneline
git diff main...HEAD
```

**What I look for:**

1. **Functionality**
   - Does it solve the stated problem?
   - Are there edge cases not handled?
   - Run the code locally and test

2. **Code Quality**
   - Readability and maintainability
   - Follows team conventions
   - Appropriate abstraction levels
   - No code duplication

3. **Tests**
   - Are there tests?
   - Do they cover edge cases?
   - Do all tests pass?

4. **Data Engineering Specific**
   - Data quality checks
   - Schema compatibility
   - Performance implications
   - Resource usage (memory, CPU)
   - Backward compatibility of pipelines
   - Idempotency of operations

5. **Documentation**
   - Clear commit messages
   - Updated README if needed
   - Inline comments for complex logic
   - API documentation

6. **Security**
   - No credentials in code
   - Input validation
   - SQL injection prevention

**My review workflow:**
```bash
# Pull down PR
gh pr checkout 123

# Create review checklist
# - [ ] Tests pass locally
# - [ ] Code reviewed
# - [ ] Documentation updated
# - [ ] No security issues

# Run tests
pytest tests/

# Run linters
flake8 src/
black --check src/

# Leave comments via GitHub or CLI
gh pr review 123 --comment -b "Great work! Few suggestions..."

# Request changes if needed
gh pr review 123 --request-changes -b "Please address the error handling"

# Approve when ready
gh pr review 123 --approve -b "LGTM! Great implementation"
```

**Sarah:** How do you enforce code quality standards across the team?

**Alex:** I use a multi-layered approach:

**1. Pre-commit hooks:**
```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/flake8
    hooks:
      - id: flake8
```

**2. GitHub branch protection rules:**
- Require PR reviews (at least 1-2 approvals)
- Require status checks to pass
- Require linear history (no merge commits)
- Restrict force pushes
- Require signed commits (optional but recommended)

**3. CI/CD pipeline (.github/workflows/ci.yml):**
```yaml
name: CI
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml

      - name: Run linters
        run: |
          flake8 src/
          black --check src/
          mypy src/

      - name: Security scan
        run: bandit -r src/
```

**4. CODEOWNERS file:**
```
# .github/CODEOWNERS
# Require review from specific people

# Data pipeline code
src/pipelines/** @alex-morgan @data-team-lead

# Infrastructure
infrastructure/** @devops-lead @alex-morgan

# All SQL
**/*.sql @database-team
```

**5. PR template (.github/pull_request_template.md):**
```markdown
## Description
[Describe your changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist
- [ ] Tests pass locally
- [ ] Added/updated tests
- [ ] Updated documentation
- [ ] No breaking changes (or documented)
- [ ] Reviewed own code
```

**Sarah:** What's your strategy for keeping the team's branches clean and managing stale branches?

**Alex:** Branch hygiene is critical for team productivity:

**1. Automated cleanup:**
```bash
# Delete merged local branches
git branch --merged main | grep -v "main" | xargs git branch -d

# Prune remote tracking branches
git fetch --prune

# Or set it as default
git config fetch.prune true
```

**2. Team guidelines:**
- Delete feature branches after PR merge
- Keep branch names descriptive: `feature/add-analytics`, `fix/memory-leak`
- Use branch prefixes: `feature/`, `fix/`, `hotfix/`, `chore/`
- Set branch auto-delete in GitHub settings

**3. Regular maintenance:**
```bash
# Script to find stale branches (run weekly)
#!/bin/bash
# stale-branches.sh

echo "Branches not updated in 30 days:"
git for-each-ref --sort=committerdate refs/heads/ \
  --format='%(committerdate:short) %(refname:short)' |
  head -20

# Delete remote branches older than 60 days
git for-each-ref --format '%(refname:short) %(committerdate:unix)' refs/remotes/origin |
  awk -v cutoff="$(date -d '60 days ago' +%s)" '$2 < cutoff {print $1}' |
  sed 's|^origin/||' |
  xargs -I {} git push origin --delete {}
```

**4. GitHub Actions for automation:**
```yaml
# .github/workflows/stale-branches.yml
name: Close Stale Branches
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v5
        with:
          days-before-branch-stale: 60
          days-before-branch-close: 7
```

---

## Part 5: Advanced Git Techniques (20 minutes)

**Sarah:** Let's dive into some advanced scenarios. How do you handle a situation where you need to extract specific commits from one branch to another?

**Alex:** I'd use `git cherry-pick`:

**Basic cherry-pick:**
```bash
# Switch to target branch
git checkout main

# Cherry-pick single commit
git cherry-pick abc123

# Cherry-pick multiple commits
git cherry-pick abc123 def456 ghi789

# Cherry-pick range of commits
git cherry-pick abc123..ghi789

# Cherry-pick without committing (to modify)
git cherry-pick -n abc123
# Make changes
git commit -m "Cherry-picked and modified commit"
```

**Handling conflicts:**
```bash
# If conflict during cherry-pick
git status  # See conflicts
# Fix conflicts
git add .
git cherry-pick --continue

# Or abort
git cherry-pick --abort
```

**Use cases:**
- Backporting bug fixes to release branches
- Applying hotfixes to multiple versions
- Extracting specific features from experimental branches

**Sarah:** What about git submodules and subtrees? When would you use each?

**Alex:** Both manage dependencies, but they work differently:

**Git Submodules:**
```bash
# Add a submodule
git submodule add https://github.com/org/repo.git libs/repo

# Clone repo with submodules
git clone --recursive https://github.com/org/main-repo.git

# Or after cloning
git submodule init
git submodule update

# Update submodule to latest
cd libs/repo
git pull origin main
cd ../..
git add libs/repo
git commit -m "Update submodule to latest"

# Update all submodules
git submodule update --remote --merge
```

**Pros:**
- Explicit dependency versions
- Separate repositories
- Good for libraries you don't often change

**Cons:**
- Complex for new team members
- Easy to forget to update
- Requires extra commands

**Git Subtree:**
```bash
# Add a subtree
git subtree add --prefix=libs/repo https://github.com/org/repo.git main --squash

# Pull updates
git subtree pull --prefix=libs/repo https://github.com/org/repo.git main --squash

# Push changes back
git subtree push --prefix=libs/repo https://github.com/org/repo.git main
```

**Pros:**
- Simpler for team members
- Code is directly in your repo
- Normal Git commands work

**Cons:**
- History can get messy
- Harder to contribute back to upstream

**When to use:**
- **Submodules:** External libraries, multiple repos you maintain, need specific versions
- **Subtrees:** Vendoring dependencies, incorporating third-party code you might modify
- **Neither:** Consider package managers (pip, npm, Maven) for most dependencies

**For data engineering:**
- I prefer package management (pip, Maven) for most dependencies
- Use submodules for shared pipeline components across teams
- Use subtrees rarely, mainly for vendoring unmaintained but critical code

**Sarah:** How do you handle secrets and sensitive data in Git repositories?

**Alex:** This is critical, especially in data engineering. Multiple layers of protection:

**1. Prevention - Never commit secrets:**
```bash
# .gitignore
.env
credentials.json
*.pem
*.key
config/secrets.yaml
.aws/credentials
```

**2. Pre-commit hooks to detect secrets:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: detect-private-key
      - id: detect-aws-credentials

  - repo: https://github.com/Yelp/detect-secrets
    hooks:
      - id: detect-secrets
```

**3. Use environment variables:**
```python
# Good
import os
db_password = os.environ['DB_PASSWORD']

# Bad
db_password = "supersecret123"  # NEVER!
```

**4. Use secret management tools:**
```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id prod/db/password

# HashiCorp Vault
vault kv get secret/data/db/password

# GitHub Secrets (for CI/CD)
# Set in repo settings, access in workflows:
# ${{ secrets.DB_PASSWORD }}
```

**5. If secrets accidentally committed:**
```bash
# Option 1: Remove from history (use with caution)
# Install BFG Repo Cleaner
bfg --replace-text passwords.txt repo.git

# Option 2: Git filter-branch (more control)
git filter-branch --tree-filter 'rm -f config/secrets.yaml' HEAD

# Option 3: Git filter-repo (recommended modern tool)
git filter-repo --path config/secrets.yaml --invert-paths

# After cleaning:
# 1. Rotate the exposed secrets immediately!
# 2. Force push (coordinate with team)
git push --force --all

# 3. Have all team members re-clone
```

**6. Regular scanning:**
```bash
# Scan with truffleHog
trufflehog filesystem .

# Or in CI/CD
trufflehog git file://. --only-verified
```

**Critical rule:** If a secret is exposed, assume it's compromised. Rotate immediately!

**Sarah:** Last technical question - how do you optimize Git performance for large repositories, especially relevant for data projects?

**Alex:** Large repos are common in data engineering with data files, models, etc. Several strategies:

**1. Git LFS (Large File Storage):**
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.parquet"
git lfs track "*.csv"
git lfs track "*.pkl"
git lfs track "models/*"

# This creates/updates .gitattributes
git add .gitattributes

# Now large files are stored as pointers
git add data/large-dataset.parquet
git commit -m "Add dataset via LFS"

# Pull LFS files
git lfs pull

# See LFS files
git lfs ls-files
```

**2. Shallow clones:**
```bash
# Clone with limited history
git clone --depth 1 https://github.com/org/repo.git

# Fetch more history later if needed
git fetch --deepen=100
```

**3. Sparse checkout (only checkout specific directories):**
```bash
git clone --filter=blob:none --sparse https://github.com/org/repo.git
cd repo
git sparse-checkout init
git sparse-checkout set src/pipelines tests/pipelines
```

**4. Repository design:**
- **Don't commit:** Build artifacts, data files, model weights
- **Do commit:** Code, schemas, config (non-sensitive), small sample data
- **Separate repos:** Large data in different storage (S3, DVC)
- **Use DVC (Data Version Control):**

```bash
# Initialize DVC
dvc init

# Track data files
dvc add data/large-dataset.csv
# This creates data/large-dataset.csv.dvc

# Commit the .dvc file (not the data)
git add data/large-dataset.csv.dvc .gitignore
git commit -m "Track dataset with DVC"

# Configure remote storage
dvc remote add -d storage s3://my-bucket/dvc-storage

# Push data to remote
dvc push

# Others can pull
dvc pull
```

**5. Git configuration optimization:**
```bash
# Enable parallel index writes
git config core.preloadIndex true

# Enable filesystem monitor for faster status
git config core.fsmonitor true

# Increase pack size
git config pack.windowMemory "100m"
git config pack.packSizeLimit "100m"

# Aggressive garbage collection
git config gc.auto 256
```

**6. Regular maintenance:**
```bash
# Run git maintenance
git maintenance start

# Or manual optimization
git gc --aggressive --prune=now

# Repack for better compression
git repack -Ad
```

---

## Part 6: Leadership & Team Management (15 minutes)

**Sarah:** Now let's talk about leading a team. How would you onboard a new team member with Git best practices?

**Alex:** I'd create a structured onboarding process:

**Day 1 - Setup & Fundamentals:**

1. **Documentation:**
```markdown
# CONTRIBUTING.md

## Getting Started

### Initial Setup
git clone https://github.com/org/repo.git
cd repo
git config user.name "Your Name"
git config user.email "your.email@company.com"

# Install pre-commit hooks
pre-commit install

# Set up LFS
git lfs install

# Configure default branch
git config --global init.defaultBranch main

### Branch Naming Convention
- feature/description - New features
- fix/description - Bug fixes
- hotfix/description - Production hotfixes
- chore/description - Maintenance tasks

### Commit Message Format
<type>: <subject>

<body>

<footer>

Example:
feat: Add user analytics dashboard

- Implement daily active user metrics
- Add retention cohort analysis
- Create visualization components

Closes #123
```

2. **Hands-on walkthrough:**
```bash
# Pair programming session covering:
# - Clone repo
# - Create feature branch
# - Make small change
# - Commit
# - Push
# - Create PR
# - Code review
# - Merge
# - Delete branch
```

**Week 1 - Workflow Practice:**

3. **Assign starter tasks:**
   - Simple bug fix to practice PR workflow
   - Documentation update to learn review process
   - Pair on reviewing someone else's PR

4. **Daily check-ins:**
   - Answer Git questions
   - Review their commits
   - Provide feedback

**Week 2-4 - Advanced Topics:**

5. **Gradual complexity:**
   - Handle merge conflicts
   - Rebase feature branch
   - Cherry-pick commits
   - Review architecture decisions

6. **Resources:**
   - Internal wiki with common scenarios
   - Git workflow diagram
   - Troubleshooting guide
   - Team Git champion for questions

**Sarah:** How do you handle a situation where a team member keeps making the same Git mistakes?

**Alex:** I approach this systematically:

**1. Identify the pattern:**
- Is it force-pushing to main?
- Committing secrets?
- Not testing before pushing?
- Poor commit messages?

**2. Understand the root cause:**
- One-on-one conversation
- Is it lack of knowledge?
- Tool/workflow issue?
- Time pressure?

**3. Provide targeted support:**

**For technical gaps:**
```bash
# Create helper scripts
# ~/.gitconfig aliases
[alias]
    safe-push = "!f() { \
        branch=$(git symbolic-ref --short HEAD); \
        if [ \"$branch\" = \"main\" ] || [ \"$branch\" = \"develop\" ]; then \
            echo \"Error: Direct push to $branch not allowed\"; \
            exit 1; \
        fi; \
        git push \"$@\"; \
    }; f"
```

**For workflow issues:**
- Pair programming sessions
- Screen share to show proper workflow
- Written documentation with examples
- Pre-commit hooks to prevent issues

**4. Implement guardrails:**
```bash
# Server-side hooks (prevent bad pushes)
# Branch protection rules in GitHub
# Required status checks
# Mandatory code review
```

**5. Follow up:**
- Check their PRs more frequently initially
- Positive reinforcement when done right
- Gradual independence as they improve

**6. If issues persist:**
- More structured training plan
- Involve HR/management if needed
- But most issues are fixable with proper support

**Sarah:** What metrics or practices do you use to ensure the team's Git workflow is healthy?

**Alex:** I track several indicators:

**1. PR Metrics:**
```bash
# Average PR size (lines changed)
# Goal: < 400 lines

# Time to review
# Goal: < 4 hours for first review

# Time to merge
# Goal: < 24 hours from creation

# Review coverage
# Goal: 100% of PRs reviewed by at least 2 people
```

**2. Branch Health:**
```bash
# Number of open branches
# Goal: Each developer has < 3 active branches

# Stale branches (> 30 days)
# Goal: < 5 stale branches

# Merge conflicts frequency
# Goal: < 10% of PRs have conflicts
```

**3. Commit Quality:**
```bash
# Commits that fail CI
# Goal: < 5% failure rate

# Commits that need --amend or revert
# Goal: < 2% of commits

# Commits with proper messages
# Goal: > 95% follow convention
```

**4. Tools for monitoring:**
```python
# Script to analyze PR metrics
# GitHub API or GitLab API
import requests

def get_pr_metrics(repo, since_date):
    prs = get_closed_prs(repo, since_date)

    metrics = {
        'avg_size': avg([pr['additions'] + pr['deletions'] for pr in prs]),
        'avg_time_to_review': avg([pr['time_to_first_review'] for pr in prs]),
        'avg_time_to_merge': avg([pr['time_to_merge'] for pr in prs]),
        'review_coverage': sum([pr['review_count'] >= 2 for pr in prs]) / len(prs)
    }

    return metrics
```

**5. Regular team retrospectives:**
- Weekly: Quick Git pain points
- Monthly: Review metrics, adjust processes
- Quarterly: Major workflow improvements

**6. Team health indicators:**
- Developers feel confident with Git
- Minimal production incidents from Git issues
- Fast PR turnaround
- Clean commit history
- Good collaboration in code reviews

---

## Part 7: Disaster Recovery & Troubleshooting (15 minutes)

**Sarah:** Let's talk about when things go wrong. A developer on your team accidentally force-pushed and overwrote commits on a shared branch. What do you do?

**Alex:** This is a serious situation but usually recoverable:

**Immediate Response:**

```bash
# 1. Don't panic! Git rarely loses data permanently

# 2. Find the lost commits in reflog
git reflog
# This shows all HEAD movements, even force-pushes

# 3. Identify the commit SHA before the force-push
# Look for something like:
# abc1234 HEAD@{5}: pull: Fast-forward
# (this was before the force push)

# 4. Create a recovery branch from that point
git checkout -b recovery-branch abc1234

# 5. Compare with current state
git diff main recovery-branch

# 6. If recovery-branch has the correct code, restore it
git checkout main
git reset --hard abc1234
git push --force-with-lease origin main

# 7. Notify team immediately
# Send message: "main was accidentally overwritten but has been restored.
# Please run: git fetch --all && git reset --hard origin/main"
```

**Prevention Going Forward:**

```bash
# 1. Enable branch protection (should already be on)
# GitHub Settings → Branches → Add rule for main:
# - Require pull request reviews
# - Restrict force pushes
# - Require status checks

# 2. Use --force-with-lease instead of --force
git push --force-with-lease
# This fails if remote has commits you don't have

# 3. Set up server-side hooks to prevent force push
# pre-receive hook on server

# 4. Add to team's .gitconfig
git config --global alias.force-push-safe '!git push --force-with-lease'

# 5. Team training on dangers of force-push
```

**Sarah:** What if someone committed sensitive data (like database credentials) to the repository and pushed to main?

**Alex:** This is a security incident. Act fast:

**Immediate Actions (within minutes):**

```bash
# 1. ROTATE THE CREDENTIALS IMMEDIATELY
# This is the most important step!
# Change passwords, revoke API keys, etc.

# 2. Notify security team and management

# 3. Document the exposure
# - What was exposed?
# - How long was it public?
# - Who had access?
```

**Clean the Repository:**

```bash
# 4. Remove from history using git filter-repo
# (preferred over filter-branch)

# Install git-filter-repo
pip install git-filter-repo

# Remove specific file
git filter-repo --path credentials.json --invert-paths

# Or remove secrets from files
git filter-repo --replace-text <(echo "password=abc123==>password=REDACTED")

# 5. Force push cleaned history
git push --force --all origin
git push --force --tags origin

# 6. Notify ALL team members
# Everyone must re-clone the repository
# Old clones still have the secrets!
```

**Team Communication:**

```
Subject: URGENT - Security Incident - Repository Re-clone Required

Team,

We had a security incident where credentials were committed to the repository.

Actions taken:
✅ Credentials have been rotated
✅ Repository history has been cleaned
✅ Security team notified

Required actions for ALL team members:
1. Delete your local clone
2. Re-clone the repository
3. Verify no sensitive data: git log --all --full-history -- "*credentials*"

Do NOT pull or merge - you MUST re-clone.

Questions? Contact me immediately.
```

**Post-Incident:**

```bash
# 7. Implement prevention measures
# Add to .gitignore
echo "credentials.json" >> .gitignore
echo ".env" >> .gitignore

# 8. Add pre-commit hooks to detect secrets
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    hooks:
      - id: detect-secrets

# 9. Scan repository for other potential secrets
trufflehog git file://. --only-verified

# 10. Update security training for team
```

**Sarah:** A team member says their local repository is in a weird state and they're afraid to do anything. How do you help them troubleshoot?

**Alex:** I use a systematic diagnostic approach:

**Step 1: Gather Information**
```bash
# Safe commands that don't change anything
git status
git log --oneline -10
git branch -a
git reflog -10
git remote -v
git diff HEAD
git stash list
```

**Step 2: Diagnose Common Issues**

**Issue 1: Detached HEAD**
```bash
# Symptom: "You are in 'detached HEAD' state"
# Solution:
git checkout main  # Return to a branch

# If you made commits you want to keep:
git branch save-my-work  # Create branch from current position
git checkout main
git merge save-my-work
```

**Issue 2: Merge in progress**
```bash
# Symptom: "You have unmerged paths"
git status  # Shows conflicting files

# Options:
# A) Abort the merge
git merge --abort

# B) Complete the merge
# Fix conflicts, then:
git add .
git commit
```

**Issue 3: Rebase in progress**
```bash
# Symptom: "Interactive rebase in progress"

# Options:
# A) Abort
git rebase --abort

# B) Continue (after fixing conflicts)
git add .
git rebase --continue

# C) Skip this commit
git rebase --skip
```

**Issue 4: Accidental changes**
```bash
# Discard all local changes
git restore .

# Or restore specific file
git restore src/pipeline.py

# Discard staged changes
git restore --staged .
```

**Step 3: Nuclear Option (safe backup first)**
```bash
# If nothing else works, start fresh but save work

# 1. Backup current state
cd ..
cp -r repo repo-backup

# 2. See what you'd lose
cd repo
git status
git diff HEAD

# 3. Save any important work
git stash push -m "Backup before reset"

# 4. Return to clean state
git fetch origin
git reset --hard origin/main

# 5. Recover work if needed
git stash pop
```

**My troubleshooting script:**
```bash
#!/bin/bash
# git-doctor.sh

echo "=== Git Repository Diagnosis ==="
echo ""

echo "1. Repository status:"
git status
echo ""

echo "2. Current branch:"
git branch --show-current
echo ""

echo "3. Recent commits:"
git log --oneline -5
echo ""

echo "4. Uncommitted changes:"
git diff --stat
echo ""

echo "5. Staged changes:"
git diff --cached --stat
echo ""

echo "6. Stashed changes:"
git stash list
echo ""

echo "7. Reflog (recent actions):"
git reflog -10
echo ""

echo "=== Diagnosis complete ==="
```

---

## Part 8: Git Workflows for Data Engineering (10 minutes)

**Sarah:** Let's talk specifically about data engineering challenges. How do you version control database schemas?

**Alex:** Schema versioning is critical for data pipelines:

**1. Migration-based approach:**

```
db/
├── migrations/
│   ├── V001__initial_schema.sql
│   ├── V002__add_user_events_table.sql
│   ├── V003__add_index_on_timestamp.sql
│   └── V004__add_partition_to_events.sql
├── rollback/
│   ├── R002__rollback_user_events.sql
│   └── R003__rollback_index.sql
└── README.md
```

**Migration file format:**
```sql
-- V002__add_user_events_table.sql
-- Description: Add table for tracking user events
-- Author: Alex Morgan
-- Date: 2025-12-27

BEGIN;

CREATE TABLE user_events (
    event_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_events_timestamp
    ON user_events(event_timestamp);

CREATE INDEX idx_user_events_user_id
    ON user_events(user_id);

COMMIT;
```

**2. Git workflow for schemas:**
```bash
# Feature branch for schema change
git checkout -b schema/add-user-events

# Create migration file
# Naming: V{version}__{description}.sql
cat > db/migrations/V002__add_user_events_table.sql

# Test migration
psql -d dev_db -f db/migrations/V002__add_user_events_table.sql

# Create rollback
cat > db/rollback/R002__rollback_user_events.sql << EOF
BEGIN;
DROP TABLE IF EXISTS user_events;
COMMIT;
EOF

# Commit
git add db/migrations/V002__add_user_events_table.sql
git add db/rollback/R002__rollback_user_events.sql
git commit -m "schema: Add user_events table

- Track user interaction events
- Include timestamp indexing for queries
- Add JSONB field for flexible properties

Migration: V002
Rollback: R002"

# PR and review
git push -u origin schema/add-user-events
```

**3. Tools integration:**
```bash
# Use Flyway or Liquibase for automated migrations
# flyway.conf
flyway.url=jdbc:postgresql://localhost:5432/mydb
flyway.locations=filesystem:db/migrations
flyway.validateOnMigrate=true

# Apply migrations
flyway migrate

# In CI/CD pipeline
- name: Run migrations
  run: |
    flyway -configFiles=flyway.conf migrate
```

**4. Best practices:**
- Never modify existing migrations (create new ones)
- Always include rollback scripts
- Test migrations on copy of production data
- Include schema in PR reviews
- Document breaking changes
- Version control seed data separately

**Sarah:** How do you handle versioning for ML models and data artifacts?

**Alex:** This requires specialized tools alongside Git:

**1. Don't commit large binaries to Git:**
```bash
# .gitignore
models/*.pkl
models/*.h5
models/*.pt
data/*.parquet
data/*.csv
```

**2. Use DVC (Data Version Control):**
```bash
# Initialize DVC in repo
dvc init
git add .dvc .dvcignore
git commit -m "Initialize DVC"

# Configure remote storage (S3, GCS, Azure, etc.)
dvc remote add -d storage s3://my-bucket/dvc-storage
dvc remote modify storage region us-west-2

# Track model file
dvc add models/user_churn_model_v1.pkl
# This creates models/user_churn_model_v1.pkl.dvc

# Commit the .dvc metadata file
git add models/user_churn_model_v1.pkl.dvc models/.gitignore
git commit -m "Add user churn model v1"

# Push data to remote storage
dvc push

# Others can pull the actual data
dvc pull
```

**3. Model versioning structure:**
```
models/
├── user_churn/
│   ├── model_v1.pkl.dvc      # DVC metadata
│   ├── model_v2.pkl.dvc
│   ├── metrics_v1.json       # Committed to Git
│   ├── metrics_v2.json
│   └── config.yaml           # Committed to Git
└── README.md
```

**4. Track metadata in Git:**
```json
// models/user_churn/metrics_v2.json
{
  "version": "v2",
  "created_at": "2025-12-27",
  "model_type": "XGBoost",
  "performance": {
    "accuracy": 0.89,
    "precision": 0.87,
    "recall": 0.85,
    "f1": 0.86
  },
  "training_data": {
    "dataset": "user_events_2025_q4",
    "rows": 1000000,
    "features": 45
  },
  "hyperparameters": {
    "max_depth": 6,
    "learning_rate": 0.1,
    "n_estimators": 100
  }
}
```

**5. Git workflow for models:**
```bash
# Create experiment branch
git checkout -b experiment/improve-churn-model

# Train new model (creates model_v2.pkl)
python train_model.py --output models/user_churn/model_v2.pkl

# Track with DVC
dvc add models/user_churn/model_v2.pkl

# Create metrics file
cat > models/user_churn/metrics_v2.json << EOF
{...metrics...}
EOF

# Commit metadata
git add models/user_churn/model_v2.pkl.dvc
git add models/user_churn/metrics_v2.json
git commit -m "model: Train user churn model v2

Improvements:
- Increased max_depth from 4 to 6
- Added 5 new features
- Trained on Q4 2025 data

Results:
- Accuracy: 0.89 (+0.04)
- F1 Score: 0.86 (+0.03)"

# Push DVC data
dvc push

# Push Git metadata
git push -u origin experiment/improve-churn-model
```

**6. MLflow integration (alternative/complementary):**
```python
import mlflow

# Log experiment
with mlflow.start_run():
    mlflow.log_params(hyperparameters)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, "model")

    # Log git commit
    mlflow.set_tag("git_commit", get_git_commit_hash())
    mlflow.set_tag("git_branch", get_git_branch())
```

**Sarah:** Excellent! Last question on this topic - how do you handle data pipeline configuration across environments?

**Alex:** Multi-environment config is crucial:

**1. Directory structure:**
```
config/
├── base.yaml              # Shared config
├── dev.yaml              # Development overrides
├── staging.yaml          # Staging overrides
├── prod.yaml            # Production overrides (no secrets!)
└── README.md

secrets/                  # NOT in Git!
├── .gitignore           # Ignore this entire directory
├── dev.env
├── staging.env
└── prod.env
```

**2. Base configuration:**
```yaml
# config/base.yaml
pipeline:
  name: user_analytics
  version: "2.1.0"
  batch_size: 1000

database:
  connection_pool_size: 10
  timeout: 30

monitoring:
  enabled: true
  log_level: INFO
```

**3. Environment-specific:**
```yaml
# config/prod.yaml
# Inherits from base.yaml, overrides specific values

database:
  connection_pool_size: 50  # Override
  timeout: 60

pipeline:
  batch_size: 10000  # Override for production scale

monitoring:
  log_level: WARNING  # Less verbose in prod
```

**4. Git workflow:**
```bash
# Config files ARE committed
git add config/base.yaml config/prod.yaml
git commit -m "config: Update production batch size

Increase from 1000 to 10000 to handle growth"

# Secrets are NOT committed
# .gitignore already includes secrets/
```

**5. Usage in code:**
```python
import os
import yaml
from pathlib import Path

def load_config(env='dev'):
    """Load configuration for specified environment"""
    base_config = yaml.safe_load(open('config/base.yaml'))
    env_config = yaml.safe_load(open(f'config/{env}.yaml'))

    # Merge configs (env overrides base)
    config = {**base_config, **env_config}

    # Load secrets from environment variables or secret manager
    config['database']['password'] = os.environ.get('DB_PASSWORD')
    config['api_key'] = os.environ.get('API_KEY')

    return config

# Usage
env = os.environ.get('ENVIRONMENT', 'dev')
config = load_config(env)
```

**6. PR process for config changes:**
```bash
# Feature requiring config change
git checkout -b feature/add-data-validation

# Update configs
vim config/base.yaml      # Add validation settings
vim config/prod.yaml      # Production-specific tuning

# Document in PR
git commit -m "config: Add data quality validation

- Add validation rules for null checks
- Set production threshold to 0.01%
- Enable alerting for validation failures

Config changes:
- base.yaml: Add validation section
- prod.yaml: Set stricter thresholds"
```

---

## Closing Discussion (10 minutes)

**Sarah:** Alex, you've demonstrated excellent Git knowledge. Just a few final questions. What do you think are the most common Git anti-patterns you've seen in teams, and how do you address them?

**Alex:** Great question. Here are the top anti-patterns I've encountered:

**1. Committing directly to main/master**
- **Problem:** Bypasses code review, breaks CI/CD
- **Solution:** Branch protection rules, team education, pre-push hooks

**2. Massive commits (1000+ lines)**
- **Problem:** Impossible to review, hard to debug, risky to revert
- **Solution:** Encourage smaller, focused commits; break work into smaller PRs

**3. Meaningless commit messages**
- **Problem:** "fix bug", "update code", "wip" - no context
- **Solution:** Commit message templates, PR templates, lead by example

**4. Fear of Git (only using 5 commands)**
- **Problem:** Can't recover from issues, limited workflow
- **Solution:** Regular training, pair programming, safe sandbox for practice

**5. Not pulling before pushing**
- **Problem:** Creates unnecessary merge commits and conflicts
- **Solution:** Git aliases, pre-push hooks, team workflow documentation

**6. Using `git add .` without checking**
- **Problem:** Commits unwanted files, debug code, secrets
- **Solution:** Use `git add -p` (interactive), pre-commit hooks, .gitignore

**7. Force pushing to shared branches**
- **Problem:** Loses teammates' work
- **Solution:** Use `--force-with-lease`, branch protection, team guidelines

**8. Keeping feature branches open for weeks**
- **Problem:** Massive merge conflicts, integration issues
- **Solution:** Small incremental features, merge to main frequently, feature flags

**Sarah:** If you could give three pieces of Git advice to your new team, what would they be?

**Alex:**

**1. Commit early and often, push daily**
- Small, focused commits are easier to review and revert
- Push at least once per day so work is backed up
- Use branches freely - they're cheap

**2. Your commit message is a love letter to future you**
- Six months from now, you won't remember why you made this change
- Write commits like you're explaining to a teammate
- Good commit message = saved debugging time

**3. When in doubt, ask for help before force-pushing**
- Git is powerful but unforgiving with certain commands
- Team communication prevents disasters
- It's always better to ask than to corrupt history

**Sarah:** Perfect. Last question - where do you go to stay updated with Git best practices and new features?

**Alex:**

**Resources I use regularly:**

1. **Official Documentation**
   - Git docs: git-scm.com
   - GitHub blog for new features
   - GitLab's Git tutorials

2. **Community**
   - Stack Overflow Git tag
   - r/git subreddit
   - Git newsletters

3. **Learning**
   - "Pro Git" book (free online)
   - Atlassian Git tutorials
   - GitHub Learning Lab

4. **Following experts**
   - GitHub engineering blog
   - Git Rev News
   - Conference talks (Git Merge, GitHub Universe)

5. **Practice**
   - Try new Git features in sandbox repos
   - Read other teams' Git workflows
   - Experiment with different strategies

**Sarah:** Excellent, Alex. You've demonstrated deep Git knowledge, practical experience, and the leadership mindset we need. Do you have any questions for me?

**Alex:** Thank you, Sarah. Yes, I do have a few questions:

1. What's the current Git workflow the team is using, and are there any pain points you'd like addressed?

2. What's the team's experience level with Git - will I be mentoring beginners or working with advanced users?

3. What tools are in the current stack - GitHub, GitLab, Bitbucket? Any CI/CD integrations already in place?

4. Are there any specific Git-related incidents or challenges the team has faced recently that I should be aware of?

**Sarah:** Great questions. We're currently using GitHub with a modified Git Flow, and we've had some issues with large data files slowing down the repo - something we'd like your expertise on. The team ranges from intermediate to advanced, but we could use better standardization. We use GitHub Actions for CI/CD.

As for recent challenges, we had a force-push incident last month that caused some data loss - we recovered, but it highlighted our need for better branch protection and team training.

**Alex:** That's very helpful context. I'd be excited to help standardize the workflow, implement Git LFS for the large files, and create a training program to prevent future incidents. Based on what you've shared, I think I could add a lot of value to the team.

**Sarah:** I think so too, Alex. Thank you for your time today. You'll hear from us within the next few days.

**Alex:** Thank you for the opportunity, Sarah. I look forward to hearing from you!

---

## Interview Conclusion

**Evaluation Summary:**
- ✅ Strong understanding of Git fundamentals
- ✅ Excellent knowledge of advanced Git operations
- ✅ Practical experience with team workflows
- ✅ Strong leadership and mentoring approach
- ✅ Specific expertise relevant to data engineering
- ✅ Disaster recovery and troubleshooting skills
- ✅ Security-conscious practices

**Recommendation:** Strong hire for Senior Data Engineer (Team Lead) position.
