// Commit-msg hook converted to Rust.
// Build: `rustc .githooks/commit-msg.rs -o .githooks/commit-msg`
// Install: `chmod +x .githooks/commit-msg` and optionally `git config core.hooksPath .githooks`

use regex::Regex;
use std::env;
use std::fs::{read_to_string, OpenOptions};
use std::io::{self, Read, Write};
use std::process::exit;

const MAX_SUBJECT_LEN: usize = 72;
const MAX_BODY_LINE_LEN: usize = 100;
const ALLOWED_TYPES: &[&str] = &[
    "feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "ci", "build", "revert",
    "hotfix",
];

fn template() -> String {
    format!(
        r#"# Commit message template (Conventional Commits)
# Format: <type>(optional-scope): short summary
# - type: one of: {types}
# - scope: optional, lowercase, no spaces
# - subject: brief summary, <= {max_subject} chars, no trailing period
#
# Blank line, then an optional body explaining WHY the change was made.
# Wrap body lines at ~{max_body} chars.
#
# Examples:
#   feat(auth): add refresh token support
#
#   Add server-side token refresh to avoid forcing re-login. Updated tests
#   and docs.
#
#   Resolves: PROJ-123
#
"#,
        types = ALLOWED_TYPES.join(", "),
        max_subject = MAX_SUBJECT_LEN,
        max_body = MAX_BODY_LINE_LEN
    )
}

fn write_template_and_fail(path: &str, existing: &str) -> io::Result<()> {
    let mut f = OpenOptions::new().write(true).create(true).truncate(true).open(path)?;
    f.write_all(template().as_bytes())?;
    f.write_all(b"\n")?;
    f.write_all(existing.as_bytes())?;
    eprintln!(
        "ERROR: Empty commit message. A template was written to {}. Please edit and try again.",
        path
    );
    exit(1);
}

fn first_non_comment_line(lines: &[&str]) -> Option<(usize, &str)> {
    for (i, ln) in lines.iter().enumerate() {
        let s = ln.trim();
        if s.is_empty() || s.starts_with('#') {
            continue;
        }
        return Some((i, *ln));
    }
    None
}

fn validate_subject(subject: &str, re: &Regex) -> Result<(), String> {
    if subject.len() > MAX_SUBJECT_LEN {
        return Err(format!(
            "Subject exceeds {} characters (got {}).",
            MAX_SUBJECT_LEN,
            subject.len()
        ));
    }
    if subject.ends_with('.') {
        return Err("Subject should not end with a period.".to_string());
    }
    if !re.is_match(subject) {
        return Err(format!(
            "Subject does not match Conventional Commits format: <type>(optional-scope): short summary. Allowed types: {}",
            ALLOWED_TYPES.join(", ")
        ));
    }
    Ok(())
}

fn validate_body(lines: &[&str], subj_idx: usize) -> Result<(), String> {
    // If there are any non-comment lines after subject, require a blank line immediately after subject
    if subj_idx + 1 < lines.len() {
        let second_line = lines[subj_idx + 1].trim();
        if !second_line.is_empty() {
            return Err("When including a body, the second line must be blank (one blank line between subject and body).".to_string());
        }
    }

    let mut in_code_block = false;
    for (i, ln) in lines.iter().enumerate().skip(subj_idx + 2) {
        let line = ln;
        let trimmed = line.trim_start();
        if trimmed.starts_with("```") {
            in_code_block = !in_code_block;
            continue;
        }
        if in_code_block {
            continue;
        }
        // skip comment lines
        if trimmed.starts_with('#') || trimmed.is_empty() {
            continue;
        }
        // skip indented code block heuristic (4 spaces)
        if line.starts_with("    ") {
            continue;
        }
        if line.len() > MAX_BODY_LINE_LEN {
            return Err(format!(
                "Body line {} exceeds {} characters.",
                i + 1,
                MAX_BODY_LINE_LEN
            ));
        }
    }
    Ok(())
}

fn print_validation_error(err: &str) {
    eprintln!("ERROR: Invalid commit message:\n  {}\n", err);
    eprintln!("Tip: Follow the Conventional Commits format. Example:\n  feat(auth): add token refresh");
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: commit-msg <path-to-commit-msg-file>");
        exit(2);
    }
    let msg_file = &args[1];

    let content = match read_to_string(msg_file) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("ERROR: cannot read commit message file: {}", e);
            exit(2);
        }
    };

    if content.trim().is_empty() {
        if let Err(e) = write_template_and_fail(msg_file, &content) {
            eprintln!("ERROR: cannot write template to file: {}", e);
            exit(2);
        }
    }

    let lines_vec: Vec<&str> = content.lines().collect();
    let (subj_idx, subject) = match first_non_comment_line(&lines_vec) {
        Some((i, s)) => (i, s.trim()),
        None => {
            if let Err(e) = write_template_and_fail(msg_file, &content) {
                eprintln!("ERROR: cannot write template to file: {}", e);
                exit(2);
            }
            unreachable!();
        }
    };

    let pattern = format!(
        r"(?i)^({})(\([a-z0-9._/-]+\))?:\s.+$",
        ALLOWED_TYPES.join("|")
    );
    let re = Regex::new(&pattern).expect("regex compile");

    if let Err(e) = validate_subject(subject, &re) {
        print_validation_error(&e);
        exit(1);
    }

    if let Err(e) = validate_body(&lines_vec, subj_idx) {
        print_validation_error(&e);
        exit(1);
    }

    // All checks passed
    exit(0);
}