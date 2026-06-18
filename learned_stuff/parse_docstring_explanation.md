# LangChain Tool Decorator: `parse_docstring` & `description`

When creating tools using the `@tool` decorator in LangChain, the library automatically builds a JSON schema of the tool to send to the LLM. You can configure this behavior using the `parse_docstring` and `description` parameters.

---

## 1. What does `parse_docstring` do?

By default, `@tool` does not parse the internal structure of your function's docstring.

* **`parse_docstring=False` (Default):** 
  The entire docstring text is copied as the tool's main description. The individual function arguments (parameters) will **not** have descriptions in the tool schema.
  
* **`parse_docstring=True`:** 
  LangChain parses your function's docstring (using **Google-style** formatting, e.g., `Args:`) to extract descriptions for each function argument. It inserts these descriptions into the parameter schema. This helps the LLM understand what each parameter does.

---

## 2. Interaction with the `description` Parameter

You can combine `parse_docstring` with a custom `description` argument to control how the tool is documented.

### Option A: Both `description` and `parse_docstring=True`
```python
@tool(description="My custom main description.", parse_docstring=True)
def my_tool(param1: str):
    """
    This docstring text is ignored for the main tool description.

    Args:
        param1: This parameter description IS extracted and sent to the LLM.
    """
    pass
```
* **Tool's Main Description:** Sets to `"My custom main description."` (the docstring's top text is ignored).
* **Parameter Descriptions:** The `Args:` section is still parsed to extract `param1`'s description.

---

### Option B: Only `parse_docstring=True` (No custom description)
```python
@tool(parse_docstring=True)
def my_tool(param1: str):
    """
    Main tool description extracted from here.

    Args:
        param1: Parameter description extracted from here.
    """
    pass
```
* **Tool's Main Description:** Automatically extracted from the top portion of the docstring (everything before the `Args:` section).
* **Parameter Descriptions:** Extracted from the `Args:` section.

---

### Option C: Only `parse_docstring=False` (Default Behavior)
```python
@tool
def my_tool(param1: str):
    """
    Main tool description.

    Args:
        param1: Parameter description.
    """
    pass
```
* **Tool's Main Description:** The entire block (including the literal text `Args: param1: ...`) is treated as the tool's main description.
* **Parameter Descriptions:** The schema's parameter-level descriptions remain **empty**.

---

## 3. Important Gotcha: Injected Arguments & `ValueError`

If your function uses injected parameters (like `InjectedToolCallId` or `InjectedState`), LangChain automatically removes these arguments from the tool's public schema, since they are supplied at runtime by the framework rather than the LLM.

### The Problem
If `parse_docstring=True` is enabled and you document an injected argument in the `Args:` section:

```python
@tool(parse_docstring=True)
def my_tool(
    todos: list[Todo],
    tool_call_id: Annotated[str, InjectedToolCallId]
):
    """
    Args:
        todos: List of Todo items
        tool_call_id: The tool call ID (INJECTED)
    """
    pass
```

You will get this error:
`ValueError: Arg tool_call_id in docstring not found in function signature.`

This happens because LangChain tries to match the arguments in the docstring against the public schema, but the injected `tool_call_id` has already been stripped out.

### The Solution
Do not list injected arguments (like `tool_call_id` or `state`) in the `Args:` block of your docstring:

```python
@tool(parse_docstring=True)
def my_tool(
    todos: list[Todo],
    tool_call_id: Annotated[str, InjectedToolCallId]
):
    """
    Args:
        todos: List of Todo items
    """
    pass
```

