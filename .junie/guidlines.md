# Project Guidelines

##  What the Project Does

This project implements a **habit tracking Telegram bot** called **Strong Will 🦾**. Users can create habits (good or bad), track their adherence or abstinence over time, and log relapses. The bot motivates users to maintain their streaks, analyze past periods, and stay accountable.

Core features:
- Habit creation and management
- Period tracking (abstinence or adherence)
- Relapse logging with optional reason
- Viewing progress history and minimal analytics
- Clean Telegram bot UX with inline buttons

---

##  Backend Technologies

- **Python 3.12+**
- **[Aiogram 3.20.0](https://aiogram.dev/)** – Async Telegram bot framework
- **PostgreSQL** – Relational database
- **SQLAlchemy 2.0 (Declarative ORM)** – Async DB access
- **Alembic** – Database migrations
- **Pydantic** – Data validation and schemas
- **Logging** – Standard `logging` module with structured logs
- **APScheduler** – Optional scheduled jobs (e.g., periodic reminders)

---

##  Frontend/Client Technologies

- **Telegram Bot Interface**
- **Inline Keyboards / Reply Keyboards**
- FSM-powered conversational flows
- Optional: future clients (Web, VK, Mini-apps)

---

##  Testing Stack

- **pytest** – Core testing framework
- **pytest-asyncio** – Async test support
- **aiogram test utilities** – For simulating bot updates
- **Factory Boy** – For mock data factories
- **Docker + Testcontainers** – For integration testing with real PostgreSQL

---

##  Project Structure

```
bot/
├── handlers/ # FSM & command handlers
│ ├── init.py # Centralized router registration
│ ├── common.py # Start/help/menu handlers
│ └── habit_create.py# FSM flow for adding habits
│
├── keyboards/ # Inline/Reply keyboard layouts
├── middlewares/ # Optional custom middlewares
├── models/ # Pydantic models and schemas
├── db/ # SQLAlchemy models & database logic
│ ├── base.py
│ ├── models/
│ └── migrations/ # Alembic
│
├── services/ # Business logic
├── utils/ # Helpers & utilities
├── config.py # Settings via pydantic.BaseSettings
├── main.py # Bot entrypoint
└── constants.py # Static constants and enums
```


---

##  Technologies to Avoid

- `telebot`, `pyTelegramBotAPI`, `python-telegram-bot` – avoid non-async libraries
- Django / Flask – unnecessary overhead for bot-only architecture
- Hard-coded state machines – use `aiogram.fsm`
- SQLite in production – use PostgreSQL
- Global mutable state – always scope per session/user

---

##  Architectural Patterns

- **Ports and Adapters (Hexagonal Architecture)** for future client integration
- **Service Layer** – business logic is separated from handler logic
- **Repository Pattern** – database access is abstracted from logic

---

##  Design Patterns

- **FSM (Finite State Machine)** – user dialog management
- **Dependency Injection** – lightweight pattern using async context in handlers
- **Factory Pattern** – for keyboard creation and service objects
- **DTOs (Data Transfer Objects)** – via Pydantic

---

##  Scalability Guidelines

- All business logic must be client-agnostic
- Telegram is the first client; others should use the same API/backend
- Use UUIDs as primary keys for portability
- Avoid tight coupling between FSM states and DB models
- Use routers per domain (habit, user, etc.) for separation of concerns

---

##  Security Considerations

- Use Telegram user ID as the core identifier, with optional OAuth for cross-platform linking
- Sanitize all user inputs
- Protect against replay attacks on webhook if used

---

##  MVP Scope

1. Create/view/delete habit (up to 3 at a time)
2. Track current abstinence/adherence period
3. Log relapse (optional reason)
4. Show history (past periods)
5. Show minimal analytics (avg duration, relapse count)

---

##  Extensibility

- Easy addition of gamification (XP, badges)
- Integration with Google/Fit/Notion
- Admin dashboard (via web)
- Scheduled reminders via APScheduler/Celery

---

##  Deployment Notes

- Use `.env` with `pydantic.BaseSettings` for config
- Log with `logging.config.dictConfig` and JSON output
- Dockerized deployment (Bot + Postgres + Redis optional)
- Use webhook or polling based on deployment target

---

##  Final Notes for AI Coding Agent

- Follow existing handler and router architecture
- Use async/await properly, no blocking code
- Every service function must be testable in isolation
- Keep user flows minimal and intuitive
- Prefer declarative logic and keyboard-driven UX
