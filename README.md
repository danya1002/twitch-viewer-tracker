# Twitch & YouTube Viewer Tracker Bot

Python-бот для отслеживания статистики зрителей на Twitch и YouTube в реальном времени.

## Возможности

- Получение количества зрителей с Twitch API (Helix)
- Получение количества зрителей с YouTube API (Data API v3)
- Логирование статистики с временными метками в CSV
- Отображение статистики в реальном времени в консоли

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

1. Скопируйте `config.example.py` в `config.py`
2. Заполните параметры:

### Twitch
- Зарегистрируйте приложение на https://dev.twitch.tv/console/apps
- Получите `CLIENT_ID` и `CLIENT_SECRET`

### YouTube
- Включите YouTube Data API v3 в https://console.cloud.google.com/
- Создайте API-ключ

## Запуск

```bash
python src/main.py
```

## Структура проекта

```
├── src/
│   ├── main.py           # Точка входа
│   ├── twitch_client.py  # Клиент Twitch API
│   ├── youtube_client.py # Клиент YouTube API
│   ├── tracker.py        # Логирование статистики
│   └── config.py         # Конфигурация
├── config.example.py     # Пример конфигурации
├── requirements.txt      # Зависимости
└── .gitignore
```
