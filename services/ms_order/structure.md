📂 src/

    📄 main.py (Сборка и запуск FastAPI)

    📄 config.py (Настройки из .env)

    📦 domain/ (Бизнес-правила)

        📁 aggregates/ (Агрегат Заказа и его позиции)

        📁 value_objects/ (Цены, адреса)

        📁 interfaces/ (Абстрактные репозитории и UoW)

    📦 application/ (Сценарии использования)

        📁 use_cases/ (Логика: создать заказ, оплатить заказ)

        📁 dto/ (Pydantic схемы)

        📁 interfaces/ (Абстракции брокеров сообщений)

    📦 infrastructure/ (Технические детали)

        📁 database/ (Тут лежит database.py, модели SQLAlchemy и миграции Alembic)

        📁 repositories/ (Реализация репозиториев для Postgres)

        📁 uow/ (Реализация UnitOfWork)

        📁 message_broker/ (Реализация RabbitMQ)

    📦 presentation/ (Внешний интерфейс)

        📁 api/ (Роутеры FastAPI и dependencies.py)