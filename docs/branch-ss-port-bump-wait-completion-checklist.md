# Ветка `fix/ss-port-bump-wait-completion`: суть + чеклист для других репо

> Прогон на .NET / Java / JS / Go / Python (и sibling-линиях вроде `*-TMS-6.0` / `*.post600`).  
> Связанные доки: [port-bump + wait-completion](./sync-storage-port-bump-and-wait-completion.md), [compat](./sync-storage-adapter-compat.md), [0.4 guide](./sync-storage-0.4-cross-adapter-guide.md), [SS checklist](./sync-storage-verification-checklist.md).

| Поле | Значение |
|------|----------|
| Репо / адаптер / версия | |
| Язык / runtime | |
| Sync-storage (`/health` или binary) | |
| OS | |
| Дата / кто гонял | |

---

## 1. Суть доработок в этой ветке

### 1.1 Sync-storage: port bump + lifecycle (основной фикс)

**Проблемы, которые закрывали**

1. **Чужой `testRunId` на preferred-порту** (TMS-43088) — второй прогон fail-fast / «висит», пока первый не освободит порт.
2. **Гонка старта на свободном порту** — два процесса видят «порт свободен», один выигрывает bind/register, второй раньше мог **молча продолжить без SS**.
3. **`atexit` + kill detached SS** — в CI/CD / xdist SS умирал до внешнего `wait-completion` → Work X не добивал → результаты **InProgress**.
4. **Ранний wait-completion на worker `completed`** — опасно при нескольких suite/class в одном процессе (SS/Work X уходят после первого блока тестов).

**Что сделали в Python (`SyncStorageRunner`)**

| Было | Стало |
|------|--------|
| Один порт; чужой health → ошибка / ступор | Цикл `preferred .. preferred+maxBump` (`SYNC_STORAGE_PORT_MAX_BUMP`, default 10) |
| Attach / start без явной политики | `START_NEW` \| `ATTACH` \| `TRY_NEXT` по `/health` + `testRunId` |
| Проигрыш гонки → риск «без SS» | Cleanup failed spawn → следующий порт; весь диапазон занят → явный hard fail |
| Идея убивать SS на выходе адаптера | **Detached SS, без atexit-kill**; финализацию ждёт **CI/внешний** `GET /wait-completion` |

**Жёсткое правило (не регрессировать):** финал outcome **не** через `PUT /api/v2/testResults/{id}`. Финал = Work X / send-test-result.

### 1.2 CI Nose: namespace vs эталон api-validator

**Проблема:** `nose2 --testit` из корня `python-examples/nose` даёт `__module__` = `tests.test_annotations`, а Expected в api-validator ждёт `test_annotations` → падает `CheckTestResults` на `actual.AutoTest.Namespace`.

**Фикс:** в CI `nose2 --testit -s tests` — discovery из `tests/`, короткие имена как у golden (и как у pytest-контракта). Адаптер не «стрипает» `tests.` — выровнен **discovery**, не модель.

---

## 2. Чеклист: Sync-storage (обязательно на каждом адаптере)

Отмечать: **Pass / Fail / N/A** + порт, testRunId, строка лога.

### A. Baseline

| # | Проверка | Pass? | Notes |
|---|----------|-------|-------|
| A1 | Чистый прогон (1 worker): тесты завершились, в TMS результаты **финальные** (не InProgress) | | |
| A2 | После выхода порт в итоге свободен / SS idle-exit; нет вечного orphan на preferred | | |
| A3 | В логе: register / cuts / worker `completed`; Work X или эквивалент виден в SS/TMS | | |
| A4 | Пока жив SS, в TMS уходит InProgress/cuts по контракту; **нет** PUT outcome финала | | |

### B. Port bump / чужой run

| # | Проверка | Pass? | Notes |
|---|----------|-------|-------|
| B1 | Run A на порту `P`; параллельно Run B (другой `testRunId`, тот же preferred `P`) | | |
| B2 | B **не** аттачится к SS A; поднимается на `P+1` (или следующем); в логе effective port | | |
| B3 | B завершается с финалами, пока A ещё бежит | | |
| B4 | A потом тоже финален; процесс SS A не убит B | | |
| B5 | Два worker’а **одного** `testRunId` шарят **один** SS на одном порту | | |

### C. Гонка старта / не молчать без SS

| # | Проверка | Pass? | Notes |
|---|----------|-------|-------|
| C1 | Два процесса почти одновременно на свободном preferred | | |
| C2 | Один берёт `P`, второй bump `P+1`… — **оба** остаются на sync-storage | | |
| C3 | Нет «continue without sync-storage» после failed bind/register, если в диапазоне ещё есть порт | | |
| C4 | Весь `P..P+maxBump` занят → явный hard fail (не тихий degrade) | | |

### D. Несколько suite/class в одном процессе

| # | Проверка | Pass? | Notes |
|---|----------|-------|-------|
| D1 | Один процесс, ≥2 последовательных class/suite/module | | |
| D2 | После первого блока SS ещё жив; Work X **не** отработал «на весь run» слишком рано | | |
| D3 | Второй блок всё ещё шлёт cuts / register в тот же (или корректно rebound) SS | | |
| D4 | Финалы обоих блоков появляются после **конца процесса** / внешнего wait-completion | | |

### E. Keep-alive / lifecycle

| # | Проверка | Pass? | Notes |
|---|----------|-------|-------|
| E1 | Длинный тест (> 2× interval keep-alive): сервер принимает keep-alive; Force Work X mid-test нет | | |
| E2 | Нет спама WARN `worker not found` на здоровом worker | | |
| E3 | Detached/shared SS: выход одного worker **не** убивает SS для остальных | | |
| E4 | **Нет** atexit/shutdown-hook, который `terminate`/`Kill` detached SS до внешнего wait (Python CI-модель) | | |
| E5 | Owned-child платформы (если так задумано): wait-completion **только** на process exit, потом destroy | | |

### F. Быстрый smoke (15–20 мин)

Минимум: **A1, B1–B4, C1–C2, D1–D4, E1, E4**.

---

## 3. Чеклист: Namespace / discovery vs api-validator golden

Имеет смысл для репо, где CI гоняет examples + `api-validator-dotnet` Expected.

| # | Проверка | Pass? | Notes |
|---|----------|-------|-------|
| N1 | CI `test_command` и cwd совпадают с тем, как снимали/держите Expected | | |
| N2 | Фактический `AutoTest.Namespace` (и classname при наличии) = Expected байт-в-байт | | |
| N3 | Нет сюрприза `tests.` / `src.` префикса, если эталон короткое имя модуля | | |
| N4 | `CheckAutoTests` и `CheckTestResults` оба зелёные (ошибка часто в nested `actual.AutoTest.Namespace`) | | |
| N5 | При расхождении сначала чинят **discovery/start-dir/cwd** (как `-s tests`), не strip в адаптере | | |
| N6 | README examples и CI-команда согласованы по start-dir | | |

**Python Nose эталон этой ветки:** `nose2 --testit -s tests`.

### Pytest xfail → TMS Outcome (TMS-26367)

| # | Проверка | Pass? | Notes |
|---|----------|-------|-------|
| X1 | `@pytest.mark.xfail` + ожидаемый fail (XFAIL) → Outcome **Passed** (`status_type=Succeeded`) | | |
| X2 | XPASS (прошёл вопреки xfail) → Outcome **Failed** | | |
| X3 | SS cut `status_code` ∈ {Passed, Failed, Skipped, Blocked, InProgress} — нет сырого `xfailed`/`xpassed` | | |

**Контракт:** см. `testit-adapter-pytest/docs/xfail-xpass.md`. Cut нормализует по `status_type` (Succeeded→Passed).

---

## 4. Антирегрессии (не вернуть)

- [ ] Не финализировать статус через `PUT /api/v2/testResults/{id}`
- [ ] Не звать `/wait-completion` на каждый worker `completed` в multi-suite процессе
- [ ] Не `atexit` → kill detached SS (ломает CI wait-completion / Mode 2)
- [ ] Не fail-fast на чужой `testRunId` без попытки port bump
- [ ] Не продолжать прогон «без SS», если в диапазоне bump ещё есть свободный порт
- [ ] Не править Namespace хардкодом `lstrip("tests.")` вместо фикса discovery

---

## 5. Evidence к отчёту

- Лог адаптера: preferred/effective port, ATTACH/START/TRY_NEXT, register, completed  
- Лог SS: Work X, keep-alive  
- TMS: test run id(s), outcomes ≠ InProgress  
- Env: `SYNC_STORAGE_PORT`, `SYNC_STORAGE_PORT_MAX_BUMP`, adapter mode  
- Для N*: фрагмент Expected + фактический `namespace` / команда CI  

---

## 6. Вне скоупа адаптера (баги sync-storage)

| Симптом | Куда |
|---------|------|
| HTTP 500 в TMS при «Work X completed», результат InProgress | sync-storage |
| Orphan registered worker без keep-alive дольше orphan timeout | sync-storage config/bug |
| Idle timeout / master lifetime до конца Work X | sync-storage (≥ 0.4.x) |
