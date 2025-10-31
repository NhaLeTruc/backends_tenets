package main

// Converted from Python commit-msg hook to Go.
// Enforces Conventional Commits + basic best-practice checks.
//
// Install (example):
//   go build -o .githooks/commit-msg .githooks/commit-msg.go
//   chmod +x .githooks/commit-msg
// Optionally: git config core.hooksPath .githooks

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "regexp"
    "strings"
)

const (
    maxSubjectLen = 72
    maxBodyLine   = 100
)

var (
    allowedTypes = []string{"feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "ci", "build", "revert", "hotfix"}
    conventional = regexp.MustCompile(`(?i)^(` + strings.Join(allowedTypes, "|") + `)(\([a-z0-9._/-]+\))?:\s.+$`)
    template     = `# Commit message template (Conventional Commits)
# Format: <type>(optional-scope): short summary
# - type: one of: ` + strings.Join(allowedTypes, ", ") + `
# - scope: optional, lowercase, no spaces
# - subject: brief summary, <= ` + fmt.Sprint(maxSubjectLen) + ` chars, no trailing period
#
# Blank line, then an optional body explaining WHY the change was made.
# Wrap body lines at ~` + fmt.Sprint(maxBodyLine) + ` chars.
#
# Examples:
#   feat(auth): add refresh token support
#
#   Add server-side token refresh to avoid forcing re-login. Updated tests
#   and docs.
#
#   Resolves: PROJ-123
#
`
)

func main() {
    if len(os.Args) < 2 {
        fmt.Fprintln(os.Stderr, "usage: commit-msg <path-to-commit-msg-file>")
        os.Exit(2)
    }
    msgPath := os.Args[1]
    data, err := os.ReadFile(msgPath)
    if err != nil {
        fmt.Fprintf(os.Stderr, "ERROR: cannot read commit message file: %v\n", err)
        os.Exit(2)
    }
    if len(strings.TrimSpace(string(data))) == 0 {
        if err := writeTemplate(msgPath, string(data)); err != nil {
            fmt.Fprintf(os.Stderr, "ERROR: cannot write template: %v\n", err)
            os.Exit(2)
        }
        fmt.Fprintln(os.Stderr, "ERROR: Empty commit message. A template was written to the file. Edit and retry commit.")
        os.Exit(1)
    }

    lines := splitLines(string(data))
    subjIdx, subject := firstNonCommentLine(lines)
    if subjIdx == -1 {
        if err := writeTemplate(msgPath, string(data)); err == nil {
            fmt.Fprintln(os.Stderr, "ERROR: No commit subject found. Template written to the file. Edit and retry commit.")
        }
        os.Exit(1)
    }
    subject = strings.TrimSpace(subject)

    if err := validateSubject(subject); err != nil {
        printValidationError(err)
        os.Exit(1)
    }
    if err := validateBody(lines, subjIdx); err != nil {
        printValidationError(err)
        os.Exit(1)
    }

    os.Exit(0)
}

func writeTemplate(path, existing string) error {
    f, err := os.OpenFile(path, os.O_WRONLY|os.O_TRUNC, 0o666)
    if err != nil {
        // try create fallback
        f, err = os.Create(path)
        if err != nil {
            return err
        }
    }
    defer f.Close()
    _, err = io.WriteString(f, template+"\n"+existing)
    return err
}

func splitLines(s string) []string {
    // preserve trailing newlines as separate entries? simple split is fine
    return strings.Split(s, "\n")
}

func firstNonCommentLine(lines []string) (int, string) {
    for i, ln := range lines {
        trim := strings.TrimSpace(ln)
        if trim == "" || strings.HasPrefix(trim, "#") {
            continue
        }
        return i, ln
    }
    return -1, ""
}

func validateSubject(subject string) error {
    if len(subject) > maxSubjectLen {
        return fmt.Errorf("subject exceeds %d characters (got %d)", maxSubjectLen, len(subject))
    }
    if strings.HasSuffix(subject, ".") {
        return fmt.Errorf("subject should not end with a period")
    }
    if !conventional.MatchString(subject) {
        return fmt.Errorf("subject does not match Conventional Commits format: type(scope?): subject. allowed types: %s", strings.Join(allowedTypes, ", "))
    }
    return nil
}

func validateBody(lines []string, subjIdx int) error {
    // If any non-comment lines after subject exist, require a blank line immediately after subject
    if subjIdx+1 < len(lines) {
        second := strings.TrimSpace(lines[subjIdx+1])
        if second != "" {
            // There may be comment lines; require actual blank line (not comment) per policy.
            return fmt.Errorf("when providing a body, the second line must be blank (one blank line between subject and body)")
        }
    }

    inCodeBlock := false
    // check body line lengths, skipping comments and code blocks
    for i := subjIdx + 2; i < len(lines); i++ {
        ln := lines[i]
        trim := strings.TrimSpace(ln)
        if strings.HasPrefix(trim, "```") {
            inCodeBlock = !inCodeBlock
            continue
        }
        if inCodeBlock {
            continue
        }
        if strings.HasPrefix(strings.TrimLeft(ln, " \t"), "#") || trim == "" {
            continue
        }
        if len(ln) > maxBodyLine {
            return fmt.Errorf("body line %d exceeds %d characters", i+1, maxBodyLine)
        }
    }
    return nil
}

func printValidationError(err error) {
    fmt.Fprintln(os.Stderr, "ERROR: Invalid commit message:")
    fmt.Fprintf(os.Stderr, "  %v\n\n", err)
    fmt.Fprintln(os.Stderr, "Tip: Follow Conventional Commits. Example:")
    fmt.Fprintln(os.Stderr, "  feat(auth): add token refresh")
}
```// filepath: .githooks/commit-msg.go
package main

// Converted from Python commit-msg hook to Go.
// Enforces Conventional Commits + basic best-practice checks.
//
// Install (example):
//   go build -o .githooks/commit-msg .githooks/commit-msg.go
//   chmod +x .githooks/commit-msg
// Optionally: git config core.hooksPath .githooks

import (
    "bufio"
    "fmt"
    "io"
    "os"
    "regexp"
    "strings"
)

const (
    maxSubjectLen = 72
    maxBodyLine   = 100
)

var (
    allowedTypes = []string{"feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "ci", "build", "revert", "hotfix"}
    conventional = regexp.MustCompile(`(?i)^(` + strings.Join(allowedTypes, "|") + `)(\([a-z0-9._/-]+\))?:\s.+$`)
    template     = `# Commit message template (Conventional Commits)
# Format: <type>(optional-scope): short summary
# - type: one of: ` + strings.Join(allowedTypes, ", ") + `
# - scope: optional, lowercase, no spaces
# - subject: brief summary, <= ` + fmt.Sprint(maxSubjectLen) + ` chars, no trailing period
#
# Blank line, then an optional body explaining WHY the change was made.
# Wrap body lines at ~` + fmt.Sprint(maxBodyLine) + ` chars.
#
# Examples:
#   feat(auth): add refresh token support
#
#   Add server-side token refresh to avoid forcing re-login. Updated tests
#   and docs.
#
#   Resolves: PROJ-123
#
`
)

func main() {
    if len(os.Args) < 2 {
        fmt.Fprintln(os.Stderr, "usage: commit-msg <path-to-commit-msg-file>")
        os.Exit(2)
    }
    msgPath := os.Args[1]
    data, err := os.ReadFile(msgPath)
    if err != nil {
        fmt.Fprintf(os.Stderr, "ERROR: cannot read commit message file: %v\n", err)
        os.Exit(2)
    }
    if len(strings.TrimSpace(string(data))) == 0 {
        if err := writeTemplate(msgPath, string(data)); err != nil {
            fmt.Fprintf(os.Stderr, "ERROR: cannot write template: %v\n", err)
            os.Exit(2)
        }
        fmt.Fprintln(os.Stderr, "ERROR: Empty commit message. A template was written to the file. Edit and retry commit.")
        os.Exit(1)
    }

    lines := splitLines(string(data))
    subjIdx, subject := firstNonCommentLine(lines)
    if subjIdx == -1 {
        if err := writeTemplate(msgPath, string(data)); err == nil {
            fmt.Fprintln(os.Stderr, "ERROR: No commit subject found. Template written to the file. Edit and retry commit.")
        }
        os.Exit(1)
    }
    subject = strings.TrimSpace(subject)

    if err := validateSubject(subject); err != nil {
        printValidationError(err)
        os.Exit(1)
    }
    if err := validateBody(lines, subjIdx); err != nil {
        printValidationError(err)
        os.Exit(1)
    }

    os.Exit(0)
}

func writeTemplate(path, existing string) error {
    f, err := os.OpenFile(path, os.O_WRONLY|os.O_TRUNC, 0o666)
    if err != nil {
        // try create fallback
        f, err = os.Create(path)
        if err != nil {
            return err
        }
    }
    defer f.Close()
    _, err = io.WriteString(f, template+"\n"+existing)
    return err
}

func splitLines(s string) []string {
    // preserve trailing newlines as separate entries? simple split is fine
    return strings.Split(s, "\n")
}

func firstNonCommentLine(lines []string) (int, string) {
    for i, ln := range lines {
        trim := strings.TrimSpace(ln)
        if trim == "" || strings.HasPrefix(trim, "#") {
            continue
        }
        return i, ln
    }
    return -1, ""
}

func validateSubject(subject string) error {
    if len(subject) > maxSubjectLen {
        return fmt.Errorf("subject exceeds %d characters (got %d)", maxSubjectLen, len(subject))
    }
    if strings.HasSuffix(subject, ".") {
        return fmt.Errorf("subject should not end with a period")
    }
    if !conventional.MatchString(subject) {
        return fmt.Errorf("subject does not match Conventional Commits format: type(scope?): subject. allowed types: %s", strings.Join(allowedTypes, ", "))
    }
    return nil
}

func validateBody(lines []string, subjIdx int) error {
    // If any non-comment lines after subject exist, require a blank line immediately after subject
    if subjIdx+1 < len(lines) {
        second := strings.TrimSpace(lines[subjIdx+1])
        if second != "" {
            // There may be comment lines; require actual blank line (not comment) per policy.
            return fmt.Errorf("when providing a body, the second line must be blank (one blank line between subject and body)")
        }
    }

    inCodeBlock := false
    // check body line lengths, skipping comments and code blocks
    for i := subjIdx + 2; i < len(lines); i++ {
        ln := lines[i]
        trim := strings.TrimSpace(ln)
        if strings.HasPrefix(trim, "```") {
            inCodeBlock = !inCodeBlock
            continue
        }
        if inCodeBlock {
            continue
        }
        if strings.HasPrefix(strings.TrimLeft(ln, " \t"), "#") || trim == "" {
            continue
        }
        if len(ln) > maxBodyLine {
            return fmt.Errorf("body line %d exceeds %d characters", i+1, maxBodyLine)
        }
    }
    return nil
}

func printValidationError(err error) {
    fmt.Fprintln(os.Stderr, "ERROR: Invalid commit message:")
    fmt.Fprintf(os.Stderr, "  %v\n\n", err)
    fmt.Fprintln(os.Stderr, "Tip: Follow Conventional Commits. Example:")
    fmt.Fprintln(os.Stderr, "  feat(auth): add token refresh")
}