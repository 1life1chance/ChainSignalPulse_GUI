import os
import threading
import requests
import time
import statistics
import logging
from tkinter import *
from email.mime.text import MIMEText
from dotenv import load_dotenv
from smtplib import SMTP

# Загрузка конфигурации
load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ANOMALY_THRESHOLD_MULTIPLIER = float(os.getenv("ANOMALY_THRESHOLD_MULTIPLIER", 3.5))

# Логирование
logging.basicConfig(filename="monitoring.log", level=logging.INFO, format='%(asctime)s - %(message)s')

# Telegram уведомление
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=payload)
        if not response.ok:
            logging.warning(f"Telegram error: {response.text}")
    except Exception as e:
        logging.error(f"Telegram exception: {str(e)}")

# Email уведомление
def send_email_message(text):
    msg = MIMEText(text)
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = "Ethereum Anomaly Alert"
    try:
        with SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
    except Exception as e:
        logging.error(f"Email exception: {str(e)}")

def get_block_number():
    url = f"https://api.etherscan.io/api?module=proxy&action=eth_blockNumber&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    return int(response['result'], 16)

def get_tx_count(block_number):
    url = f"https://api.etherscan.io/api?module=proxy&action=eth_getBlockTransactionCountByNumber&tag={hex(block_number)}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url).json()
    return int(response['result'], 16)

def get_latest_blocks(n=20):
    latest = []
    for i in range(n):
        block = get_block_number() - i
        count = get_tx_count(block)
        latest.append(count)
        time.sleep(0.2)
    return list(reversed(latest))

def detect_anomaly(data):
    if len(data) < 5:
        return False
    mean = statistics.mean(data[:-1])
    stdev = statistics.stdev(data[:-1])
    current = data[-1]
    return current > mean + ANOMALY_THRESHOLD_MULTIPLIER * stdev

# GUI логика
class App:
    def __init__(self, master):
        self.master = master
        master.title("ChainSignalPulse Monitor")
        master.geometry("400x300")

        self.label = Label(master, text="Нажмите 'Старт' для мониторинга", font=("Helvetica", 12))
        self.label.pack(pady=20)

        self.start_btn = Button(master, text="Старт", command=self.start_monitoring, width=20, bg="green", fg="white")
        self.start_btn.pack(pady=10)

        self.stop_btn = Button(master, text="Стоп", command=self.stop_monitoring, width=20, bg="red", fg="white")
        self.stop_btn.pack(pady=10)

        self.status = Label(master, text="Остановлено", fg="grey")
        self.status.pack(pady=10)

        self.running = False
        self.thread = None

    def monitor_loop(self):
        self.status.config(text="Мониторинг...")
        history = get_latest_blocks()
        while self.running:
            block = get_block_number()
            tx_count = get_tx_count(block)
            history.append(tx_count)
            if len(history) > 20:
                history.pop(0)
            if detect_anomaly(history):
                msg = f"🚨 Аномалия в блоке {block} с {tx_count} транзакциями"
                logging.info(msg)
                send_telegram_message(msg)
                send_email_message(msg)
                self.status.config(text=msg)
            time.sleep(15)

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.monitor_loop)
            self.thread.start()

    def stop_monitoring(self):
        self.running = False
        self.status.config(text="Остановлено")

root = Tk()
app = App(root)
root.mainloop()
