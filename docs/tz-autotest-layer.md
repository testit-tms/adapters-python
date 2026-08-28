# Technical assignment: autotest layer (test pyramid)

## Context

TMS supports a **test pyramid layer** on an **autotest** card. The layer can be assigned manually, by rules, or from automation runs.

Adapters can set the layer when creating or updating an autotest during a test run. The layer source in API is **`Run`** (set by the adapter).

## Business need

As an automation engineer, I want to declare the pyramid level of each autotest **in test code** so that after a run the autotest card shows:

- the layer name (e.g. `API`, `E2E`);
- the source **Run** (adapter), distinct from Manual / Rule / Report.

## Goal

In every adapter that creates or updates autotests, support an optional **layer** metadata field:

- read from test code only (annotation / mark / tag — per language);
- send on **create** and **update** autotest API calls when present;
- **omit** the field when the user did not specify a layer.

## Scope

Apply consistently to all Test IT adapters (any language / framework) and any entry point that upserts autotests via the standard adapters API.

**In scope:** autotest `layer` on create/update.

**Out of scope:**

- layer on **test run** entity;
- layer on **test result** as a separate API field (UI may show layer from the linked autotest);
- configuration / env / CLI default layer for a whole run;
- runtime API to set layer during test execution;
- validating layer names against a fixed whitelist (adapters pass the string as-is).

## API contract

Use existing autotest endpoints and models:

```json
{
  "layer": {
    "name": "API",
    "source": "Run"
  }
}
```

| Operation | Behaviour |
|-----------|-----------|
| **Create autotest** | Include `layer` only when the test declares a non-empty layer |
| **Update autotest** | Always send `resetLayer: false`; include `layer` only when the test declares a non-empty layer |
| **No layer in test** | Send `resetLayer: false`; do **not** send `layer` |

Recommended layer names (constants in client libraries, not enforced): `E2E`, `UI`, `API`, `Contract`, `Integration`, `Component`, `Unit`.

Any other non-empty string is valid.

`LayerSource` values: `Manual`, `Report`, `Run`, `Rule`. Adapters always use **`Run`**.

## Functional requirements

### 1. Declaration in test code only

The user sets layer on the **test method / scenario**, not via adapter config.

| Stack | Suggested syntax |
|-------|------------------|
| Java (JUnit / TestNG) | `@Layer("API")` or `@Layer(TestLayers.API)` on test method |
| Python (pytest) | `@pytest.mark.layer("api")` |
| C# (NUnit / xUnit) | `[Layer("API")]` on test method |
| JavaScript (Jest / Mocha) | `@layer('API')` or framework-specific decorator |
| Cucumber (Gherkin) | `@Layer=API` on scenario |
| JBehave | Meta: `@Layer API` on scenario |

Parameter substitution (e.g. `{param}` in Java) should work if the framework already supports it for other annotations.

### 2. Mapping flow

```
test code (annotation / tag)
    → internal test result model (optional layer field)
    → Converter / mapper
    → AutoTestCreateApiModel.layer / AutoTestUpdateApiModel.layer
    → TMS
```

### 3. Independence from other metadata

- Layer ≠ labels / tags on autotest.
- Layer ≠ test run tags.
- Do not change existing labels/tags behaviour.

### 4. Failed-test update path

Some adapters send a minimal update when a test fails (copy existing autotest from TMS). Still apply `layer` from the test annotation when present.

## Non-goals

- Default layer for all tests in a run via config.
- `Adapter.addLayer()` or similar dynamic API.
- Resetting layer when annotation is absent (`resetLayer: true`).
- OpenAPI / client regeneration in adapter repos (use existing generated `LayerApiModel`).

## Acceptance criteria

1. User adds layer in test code → autotest in TMS shows that layer with source **Run** after create/update.
2. User omits layer → adapter does not send `layer` on create/update.
3. Custom layer string is accepted without validation.
4. Recommended constants documented; arbitrary strings work.
5. Cross-language doc describes the same rules with per-language syntax examples.
6. Unit tests: with layer / without layer / custom string / failed-update path.

## Suggested implementation outline (language-agnostic)

1. Add `@Layer` (or equivalent) in shared annotations package.
2. Add optional `layer` field to internal `TestResult` (or equivalent).
3. Extract layer from test method in each framework listener.
4. In create/update mapper: if layer non-empty → `LayerApiModel { name, source: Run }`; on update always send `resetLayer: false`.
5. BDD adapters: parse `@Layer=` / meta `Layer` like other scenario tags.
6. Document in adapter README; add samples and tests.

## Example (Java)

```java
import ru.testit.annotations.Layer;
import ru.testit.models.TestLayers;

@Layer(TestLayers.API)
@Test
void createUser() {
    // ...
}

@Layer("my-custom-layer")
@Test
void customLayer() {
    // ...
}
```

## Example (pytest)

```python
import pytest
from testit import layer, TestLayers

@pytest.mark.layer("api")
def test_create_user_with_mark():
    ...

@layer(TestLayers.API)
def test_create_user_with_decorator():
    ...

@layer("my-custom-layer")
def test_with_custom_layer():
    ...
```

---

## Java adapters status

Implemented in `testit-java-commons` (shared by all Java adapters):

- `@Layer` on test method (`ru.testit.annotations.Layer`)
- `TestLayers` constants (`ru.testit.models.TestLayers`)
- `TestResult.layer`, `Utils.extractLayer`
- `Converter`: `layer` + `LayerSource.RUN` on create when set; on update always `resetLayer: false`, `layer` only when set
- Framework listeners: JUnit 4/5, TestNG, Cucumber 4–7 (`@Layer=`), JBehave (meta `Layer`)

## Python adapters status

Implemented in `testit-python-commons` (shared by pytest / behave / nose / robot):

- Decorator: `@layer("API")` or `@layer(TestLayers.API)` (`testit.layer`, `testit.TestLayers`)
- `TestResult.set_layer` / `get_layer`
- `Converter.layer_to_api_model`: `LayerApiModel(name, source=Run)` on create when set; on update always `resetLayer: false`, `layer` only when set
- No config/env/CLI layer; no layer on test run or test result

### Syntax by adapter

| Adapter | How to declare layer in test code |
|---------|-----------------------------------|
| pytest | `@pytest.mark.layer("API")` or `@layer(TestLayers.API)` from `testit` |
| behave | `@Layer=API` on scenario/feature |
| nose (nose2) | `@layer("API")` from `testit` on test function |
| robotframework | `[Tags] testit.layer:API` |

### Recommended constants

```python
from testit import TestLayers

TestLayers.E2E
TestLayers.UI
TestLayers.API
TestLayers.CONTRACT
TestLayers.INTEGRATION
TestLayers.COMPONENT
TestLayers.UNIT
```

Any other non-empty string is accepted without validation.

### API mapping rules

| Scenario | Adapter behaviour |
|----------|-------------------|
| Layer set in test | create: send `layer: { name, source: Run }` |
| Layer set in test | update: send `layer` + `resetLayer: false` |
| Layer not set | send `resetLayer: false`; do not send `layer` |

### Cross-language implementation guide

When porting to another language, keep the same contract:

1. Read layer **only from test code** (annotation / mark / tag).
2. Store it in the internal test result model as an optional string.
3. On autotest **create**, include `layer` only when non-empty.
4. On autotest **update**, always send `resetLayer: false`; include `layer` only when non-empty.
5. Always set `source` to `Run`.
6. Do not validate layer name against a whitelist; document recommended constants only.
7. Do not add config/env/CLI defaults for run-level layer.
8. Do not send layer on test run or test result entities.
