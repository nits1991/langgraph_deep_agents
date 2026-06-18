# Understanding `NotRequired` in Python `TypedDict`

In Python's typing system, **`NotRequired`** (introduced in PEP 655 / Python 3.11) is used to specify that a key is optional to include in a `TypedDict`.

---

## 1. What it Means

By default, every key defined in a `TypedDict` is **required** to be present when you instantiate it. Using `NotRequired` tells type checkers that a key can be omitted entirely.

```python
from typing import NotRequired
from typing_extensions import TypedDict

class User(TypedDict):
    name: str
    age: NotRequired[int]

# Valid: 'age' is omitted
user1: User = {"name": "Alice"}

# Valid: 'age' is provided with correct type
user2: User = {"name": "Bob", "age": 30}
```

---

## 2. `NotRequired` vs. `Optional`

It is common to confuse `NotRequired` with `Optional` (or `Union[T, None]`), but they behave very differently within a `TypedDict`:

| Feature | `Optional[T]` / `T | None` | `NotRequired[T]` |
| :--- | :--- | :--- |
| **Key Presence** | **Must** exist in the dictionary. | **Does not need** to exist in the dictionary. |
| **Allowed Values** | Can be `None` or type `T`. | Must be of type `T` (cannot be `None` unless typed as `NotRequired[Optional[T]]`). |

### Code Comparison

```python
# Using Optional (Key MUST be present)
class OptionalState(TypedDict):
    todos: list[str] | None

state_opt: OptionalState = {}                # INVALID (missing 'todos' key)
state_opt: OptionalState = {"todos": None}   # VALID

# Using NotRequired (Key CAN be missing)
class NotRequiredState(TypedDict):
    todos: NotRequired[list[str]]

state_nr: NotRequiredState = {}              # VALID (omitted entirely)
state_nr: NotRequiredState = {"todos": []}   # VALID
```

---

## 3. Why it is Used in LangGraph

LangGraph states are built using `TypedDict`. Using `NotRequired` is highly useful because:

1. **Clean Initialization:** It allows you to initialize the Graph State with only the basic keys (like `messages`) without needing to provide empty lists or default dictionaries for every custom field (like `todos` or `files`) at the start.
2. **Incremental Updates:** Nodes and tools can write to these fields incrementally only when needed, and type checkers will understand that these fields may not exist in the state at certain steps of the graph execution.
