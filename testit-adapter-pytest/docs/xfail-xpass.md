# Обработка `@pytest.mark.xfail` (XFAIL / XPASS)

Документ описывает **текущий** контракт pytest-адаптера для маркера `xfail`: какие `outcome` и `status_type` уходят в Test IT и почему их нельзя «упрощать» до обычных passed/failed.

---

## Термины

| Понятие | Смысл |
|---------|--------|
| XFAIL | Тест с `@pytest.mark.xfail` **упал как ожидалось** (pytest обычно помечает как skipped + `wasxfail`) |
| XPASS | Тест с `@pytest.mark.xfail` **прошёл**, хотя ожидалось падение |
| XPASS strict | То же, но `xfail(strict=True)`: pytest форсит `outcome=failed` при unexpected pass |
| `outcome` | Строка результата адаптера (`xfailed` / `xpassed`); при наличии кода в workflow проекта уходит как `status_code` |
| `status_type` | Базовый тип Test IT (`Succeeded` / `Failed` / …), если кастомного статуса нет |

Кастомные статусы в workflow: коды **`XFAILED`** / **`XPASSED`** (сравнение через `outcome.upper()` в commons).

---

## Маппинг (инвариант)

| Случай | Признаки pytest report | `outcome` | `status_type` |
|--------|------------------------|-----------|---------------|
| XFAIL | есть `wasxfail`, не passed и не failed (обычно skipped) | `xfailed` | `Succeeded` |
| XPASS (non-strict) | есть `wasxfail`, `passed` | `xpassed` | `Failed` |
| XPASS (strict) | есть `wasxfail`, `failed` | `xpassed` | `Failed` |

**Нельзя без явного запроса / тикета:**

- мапить XFAIL в `Failed` / обычный `failed` (ожидаемое падение ≠ провал прогона);
- мапить XPASS в обычный `passed` / `Succeeded` (неожиданный успех ≠ обычный успех);
- для strict XPASS оставлять голый `failed` или путать с `xfailed`.

Константы: `OUTCOME_XFAILED` / `OUTCOME_XPASSED` в `utils.py`.

---

## Где в коде

1. **`utils.resolve_xfail_outcome(report)`** — детект XFAIL/XPASS → `XfailResolution(outcome, status_type)`.
2. **`utils.STATUS_TYPE`** — таблица outcome → `StatusType` (в т.ч. xfailed → Succeeded, xpassed → Failed).
3. **`TmsListener.pytest_runtest_logreport`** — после обычного `report.outcome` / failed результат **перезаписывается** из `resolve_xfail_outcome` (порядок важен: xpass strict должен перекрыть `failed`).

В TMS:

- всегда уходит `status_type`;
- `status_code` = `outcome`, если код есть в статусах workflow проекта.

---

## Тесты

Контракт зафиксирован в `tests/test_listener.py`:

- `TestResolveXfailOutcome`
- `TestPytestRuntestLogreportXfail` (включая strict XPASS поверх failed)
