# ChainSignalPulse Advanced

📡 **ChainSignalPulse Advanced** — это мощный инструмент для мониторинга Ethereum в реальном времени с визуализацией, уведомлениями и логированием.

## 🔍 Возможности

- Обнаружение аномалий активности
- Telegram-уведомления
- Веб-интерфейс через Streamlit
- Логирование всех событий
- Настройки через `.env`

## 🚀 Быстрый старт

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Создайте `.env` файл на основе `.env.example`:
   ```
   ETHERSCAN_API_KEY=your_etherscan_key
   TELEGRAM_BOT_TOKEN=your_telegram_token
   TELEGRAM_CHAT_ID=your_chat_id
   ANOMALY_THRESHOLD_MULTIPLIER=3.5
   ```

3. Запустите мониторинг:
   ```bash
   streamlit run chain_signal_pulse_advanced.py
   ```

## 🛠 Необходимые ключи

- [Etherscan API](https://etherscan.io/myapikey)
- [Telegram Bot](https://t.me/BotFather)

## 📄 License

MIT
