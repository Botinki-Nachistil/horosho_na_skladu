# Хорошо на складу

Первый запуск.
'''bash
git clone <repo_name>
cd <repo_name>

# Поставить uv, если нет
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установить все зависимости
uv sync
'''

Обязательно активирвать pre-commit после установки зависимостей
'''bash
pre-commit run
'''
