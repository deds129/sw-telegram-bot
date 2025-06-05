# Strong Will Bot 🦾

A Telegram bot for tracking habits and maintaining streaks. Built with Python, Aiogram, and PostgreSQL.

## Features

- Track up to 3 habits simultaneously
- Log relapses with optional reasons
- View current streaks and statistics
- Clean and intuitive interface
- Support for both polling and webhook modes

## Requirements

- Python 3.12+
- PostgreSQL 12+
- Poetry (recommended) or pip

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sw-telegram-bot.git
cd sw-telegram-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a PostgreSQL database

4. Create `.env` file:
```env
BOT_TOKEN=your_bot_token_from_botfather
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
WEBHOOK_ENABLED=false
WEBHOOK_URL=https://your.domain  # Only if WEBHOOK_ENABLED=true
WEBHOOK_PATH=/webhook  # Only if WEBHOOK_ENABLED=true
WEBAPP_HOST=0.0.0.0  # Only if WEBHOOK_ENABLED=true
WEBAPP_PORT=8000  # Only if WEBHOOK_ENABLED=true
```

5. Apply database migrations:
```bash
alembic upgrade head
```

6. Run the bot:
```bash
python main.py
```

## Usage

1. Start the bot: `/start`
2. Add a habit: `/habit_add` or use the "➕ Add Habit" button
3. View your habits: `/habits` or "📊 My Habits"
4. Log a relapse: `/relapse` or "📝 Log Relapse"
5. View progress: Select a habit from the list

## Development

### Running Tests
```bash
pytest
```

### Creating New Migrations
```bash
alembic revision -m "description"
```

### Applying Migrations
```bash
alembic upgrade head
```

## License

MIT
