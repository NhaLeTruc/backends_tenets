# Best Practices — Custom Exceptions in Python

This document summarizes recommended patterns for implementing custom exception types in Python, with concise rationale and examples you can apply to `src/utils/validators.py`.

## Overview

- Purpose: define clear, inspectable error types that are easy to catch, log, serialize, and test.
- Design goals: specific classes, small and stable public attributes, human-friendly messages, machine-friendly metadata.

## Best Practices

- **Package-specific base error:** Create a single base exception (e.g. `AppError`) and subclass it for domain errors. This enables `except AppError:` handling for broad catch-all behaviors while keeping specific types for targeted handling.

- **Inherit from the most appropriate built-in when useful:** For semantic alignment, you may subclass `ValueError`, `RuntimeError`, etc., if that preserves useful behavior or expectations.

- **Be specific and small:** One class per distinct failure mode (e.g., `ValidationError`, `SchemaMismatchError`). Avoid lumping unrelated conditions into a single exception type.

- **Provide structured attributes:** Add typed attributes (e.g., `field`, `value`, `code`) so callers can programmatically inspect errors without parsing the message.

- **Human-friendly message, machine-friendly metadata:** Reserve `str(e)` for readable context and use explicit attributes or a `to_dict()` method for programmatic consumers.

- **Support chaining:** Preserve original context with `raise NewError(...) from exc` to retain tracebacks.

- **Avoid heavy logic in constructors:** Keep `__init__` cheap and side-effect free.

- **Design for serialization:** If errors cross process boundaries, include a stable `code` and minimal serializable attributes, or provide `to_dict()`/`from_dict()` helpers.

- **Document exceptions and attributes:** Describe each exception type and its attributes in module docs or README so callers know what to catch and inspect.

- **Test exception behavior explicitly:** Unit tests should assert the exception type, message, attributes, and chaining behavior where relevant.

- **Use stable attribute names and optional args:** Add new attributes as optional keyword-only parameters to avoid breaking callers.

- **Catch specifically:** Encourage `except ValidationError as exc:` instead of `except Exception:` to avoid swallowing unrelated errors.

## Example pattern

```python
class AppError(Exception):
    """Base class for application exceptions."""
    pass


class ValidationError(AppError):
    def __init__(self, message: str, *, field: str | None = None, code: str | None = None):
        super().__init__(message)
        self.field = field
        self.code = code

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "message": str(self),
            "field": self.field,
            "code": self.code,
        }

    def __str__(self) -> str:
        # concise, user-friendly message
        return super().__str__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={super().__str__()!r}, field={self.field!r}, code={self.code!r})"
```

## Quick application to `src/utils/validators.py`

- Replace the simple `class ValidationError(Exception): pass` with the `ValidationError` above (and an `AppError` base if desired).
- Use keyword args when raising for clarity: `raise ValidationError("Missing required field", field="event_id", code="validation.missing_field")`.
- When handling and returning errors across API boundaries, call `exc.to_dict()` to build the serialized payload.

## Serialization and Inter-process considerations

- Keep serialized payloads small and stable: prefer `{ "code": "validation.missing_field", "message": "...", "field": "..." }`.
- Ensure attributes are basic types (str/int/None/list/dict) so pickling/JSON is safe.

## Testing checklist

- Assert correct exception class is raised for each invalid input.
- Assert `field`, `code`, and `message` attributes when present.
- Assert `raise ... from` preserves original exception in traceback when used.

## When to subclass built-ins

- Subclass a built-in only if user code or third-party libs expect that built-in (e.g., an API that catches `ValueError`). Otherwise prefer a clear domain base class.

## Summary

- Use small, specific exception types with structured attributes and clear messages.
- Provide programmatic access (attributes / `to_dict`) and keep constructors cheap.
- Document and test exceptions thoroughly.

---

If you want, I can implement this refactor directly in `src/utils/validators.py` and add unit tests. Would you like me to proceed?
