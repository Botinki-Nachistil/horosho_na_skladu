# Git Workflow — horosho_na_skladu

## Ветки

Репозиторий живёт на двух постоянных ветках:

| Ветка | Назначение | Кто пушит |
|-------|-----------|-----------|
| `main` | Стабильная версия, инфраструктура, релизы | Только через PR |
| `dev`  | Активная разработка, интеграция фич | Только через PR |

Никогда не коммить напрямую в `main` или `dev`. Весь код идёт через feature-ветки.

---

## Жизненный цикл задачи

```
Issue (#12)  →  ветка  →  коммиты  →  PR в dev  →  merge  →  PR в main (релиз)
```

### 1. Берёшь issue

Открываешь GitHub, назначаешь себя на issue, ставишь статус "In Progress".

### 2. Создаёшь ветку от `dev`

```bash
git checkout dev
git pull origin dev
git checkout -b feat/16-serializers
```

**Формат названия ветки:** `<тип>/<номер-issue>-<короткое-описание>`

| Тип | Когда использовать |
|-----|-------------------|
| `feat/` | Новая функциональность |
| `fix/` | Исправление бага |
| `refactor/` | Рефакторинг без изменения поведения |
| `chore/` | Зависимости, конфиги, CI |
| `docs/` | Документация |

**Примеры для текущих задач:**
```
feat/16-serializers
feat/12-viewsets
feat/10-auth
```

### 3. Работаешь и коммитишь

```bash
git add accounts/serializers.py warehouse/serializers.py
git commit -m "feat(#16): add DRF serializers for accounts and warehouse"
```

**Формат коммит-сообщения:**
```
<тип>(#<issue>): <что сделано в настоящем времени>

[опционально: подробности через пустую строку]
```

| Тип | Пример |
|-----|--------|
| `feat` | `feat(#16): add InventorySerializer with read-only available_qty` |
| `fix` | `fix(#16): exclude pin_code from UserSerializer output` |
| `refactor` | `refactor(#12): extract permission class to shared/permissions.py` |
| `chore` | `chore: add djangorestframework to pyproject.toml` |
| `test` | `test(#12): add viewset integration tests for warehouse CRUD` |
| `docs` | `docs: update GIT_WORKFLOW with branch naming` |

Коммить **часто и маленькими кусками** — по одной логической единице за раз. Не нужно делать один большой коммит на всю задачу.

### 4. Проверяешь pre-commit локально

Pre-commit запускается автоматически при каждом `git commit`, но можно запустить вручную:

```bash
# Установить один раз
pip install pre-commit
pre-commit install

# Запустить вручную на всех файлах
pre-commit run --all-files

# Или только на изменённых
pre-commit run
```

Что проверяет pre-commit в этом проекте:
- **ruff** — линтинг и форматирование Python
- **mypy** — статическая типизация
- **bandit** — проверка безопасности
- **detect-secrets** — защита от случайного коммита секретов
- **check-yaml / check-toml / check-json** — синтаксис конфигов
- **end-of-file-fixer / trailing-whitespace** — форматирование файлов

### 5. Пушишь ветку и открываешь PR

```bash
git push origin feat/16-serializers
```

Открываешь PR на GitHub: **base: `dev`**, **compare: `feat/16-serializers`**.

**Шаблон описания PR:**
```
## Что сделано
- Добавлены DRF-сериализаторы для accounts, warehouse, inventory, orders
- pin_code помечен write_only, available_qty — read_only

## Связанный issue
Closes #16

## Как проверить
1. `docker compose up django`
2. GET /api/v1/warehouses/ — вернуть список складов
3. POST /api/v1/users/ — проверить, что pin_code не возвращается в ответе
```

### 6. Code review и merge

- Минимум **1 approve** от другого участника перед merge
- Все pre-commit проверки и CI должны быть зелёными
- Merge стратегия: **Squash and merge** в `dev` (чистая история)
- После merge — удалить feature-ветку

---

## Порядок задач и зависимости

Текущий спринт требует строгого порядка выполнения:

```
#16 serializers  →  #12 viewsets  →  #10 auth
     (база)            (использует #16)    (использует #12 + #16)
```

Не начинай #12, пока не смёрджен #16. Не начинай #10, пока не смёрджен #12.

---

## Синхронизация с `dev`

Если `dev` обновился пока ты работаешь в своей ветке:

```bash
# Вариант 1 — rebase (предпочтительно, история чище)
git fetch origin
git rebase origin/dev

# Вариант 2 — merge (если ветка уже в PR)
git merge origin/dev
```

При конфликтах — разрешаешь, коммитишь, продолжаешь работу.

---

## Релиз в `main`

После завершения спринта (все issue закрыты, `dev` стабилен):

```bash
# PR: dev → main
# Название: "Release: Sprint 1"
# Merge стратегия: Merge commit (сохраняет историю спринта)
```

Тег релиза:
```bash
git tag -a v0.1.0 -m "Sprint 1: models, serializers, viewsets, auth"
git push origin v0.1.0
```

---

## Быстрый старт для новой задачи

```bash
# 1. Обновить dev
git checkout dev && git pull origin dev

# 2. Создать ветку (пример для #12)
git checkout -b feat/12-viewsets

# 3. Работать, коммитить часто
git add <файлы>
git commit -m "feat(#12): add WarehouseViewSet with CRUD"

# 4. Пушить и открыть PR
git push origin feat/12-viewsets
```

---

## Чего не делать

- ❌ `git push origin main` — никогда напрямую
- ❌ `git commit -m "fix"` — коммит без контекста
- ❌ `git add .` — без проверки что именно добавляется (`git diff --staged` перед коммитом)
- ❌ Один огромный коммит на всю задачу
- ❌ Мёрдж `dev → main` без тега релиза
- ❌ Работа в `dev` напрямую (только feature-ветки)
