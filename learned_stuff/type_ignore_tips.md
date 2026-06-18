# Suppressing Type Checker Warnings with `# type: ignore`

When working with strict type checkers like Pyright/Pylance in VS Code, you might encounter type checking warnings on code that you know is correct or safe at runtime. 

You can suppress these warnings using special inline comments.

---

## 1. General Type Ignore (All Type Checkers)

To suppress all type warnings on a specific line of code, add `# type: ignore` to the end of the line:

```python
# Suppress the "Iterable" error when passing a potentially None/object variable to enumerate
for index, item in enumerate(todos):  # type: ignore
    pass
```

* **How it works:** This is a universal syntax recognized by all PEP-compliant Python type checkers (including Pyright, Pylance, mypy, and PyCharm).
* **Scope:** It will ignore **all** type errors occurring on that specific line.

---

## 2. Pyright-Specific Ignore (Targeted)

If you only want to ignore a specific type of error in Pyright while still catching other errors on the same line, use `# pyright: ignore`:

```python
for index, item in enumerate(todos):  # pyright: ignore [reportArgumentType]
    pass
```

* **How it works:** This tells Pyright specifically to suppress only the `reportArgumentType` diagnostic for that line.
* **Common Pyright Rules:**
  * `[reportArgumentType]`: For argument type mismatches.
  * `[reportAttributeAccessIssue]`: For missing attributes/methods on an object.
  * `[reportOptionalMemberAccess]`: For potential `None` dereferencing.
