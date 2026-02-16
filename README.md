# b24-excel-exporter

Микросервис на Python (FastAPI) для интеграции с роботами Bitrix24.
Сервис принимает Webhook робота (событие в виде исходящего WebHook'а) и далее по списку:
* Получает данные риквиза со списком сделок (в виде массива)
* Запрашивает полные данные по сделкам через API Bitrix24
* Генерирует плоский Excel-отчет
* Возвращает прямую ссылку на отчет.

## 🚀 Features

*   **REST API:** Обработка GET и POST запросов.
*   **Асинхронность:** Быстрая работа благодаря `FastAPI` и `httpx`.
*   **Безопасность:** Работает исключительно по HTTPS (SSL).
*   **Валидация:** Строгая проверка входящих данных и конфигурации через `Pydantic`.
*   **Docker:** Полная готовность к развертыванию через docker-compose.
*   **Статика:** Встроенный сервер для раздачи сгенерированных файлов.

---

## 🛠 Установка и Запуск

Для запуска сервиса используется Docker. Следуйте шагам ниже.

### Шаг 0. Клонирование репозитория

Клонируем репозиторий и проваливаемся в рабочую папку

```bash
git clone https://github.com/FreeGMan/b24-excel-exporter
cd b24-excel-exporter
```

### Шаг 1. Генерация SSL сертификатов

Сервис требует наличия SSL сертификатов для работы по HTTPS.
Создайте папку `certs` в корне проекта и сгенерируйте самоподписанные сертификаты (или положите свои):

**Linux / macOS / Git Bash:**
```bash
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/CN=localhost"
```

### Шаг 2. Конфигурация

Создайте в корне проекта файл `serviceProperties.json`.
Используйте пример ниже, заменив `b24_webhook_url` на ваш реальный вебхук из Bitrix24, а `smart_process_type_id` и `sp_deals_uf` на соответствующие ID из Bitrix24.
Так же необходимо изменить внешний IP или домен в `host`. 

**Пример `serviceProperties.json`:**

```json
{
    "host": "127.0.0.1",
    "port": 8000,
    "files_dir": "files",
    "ssl_keyfile": "certs/key.pem",
    "ssl_certfile": "certs/cert.pem",
    "b24_webhook_url": "https://ВАШ_ПОРТАЛ.bitrix24.ru/rest/1/ВАШ_КЛЮЧ/",
    "smart_process_type_id" : "1040",
    "sp_deals_uf" : "ufCrm8_1770008727"
}
```

**Описание параметров:**
*   `host`: IP-адрес или домен, который будет использоваться для генерации ссылок на скачивание файла.
*   `port`: Порт, на котором работает сервис.
*   `files_dir`: Папка внутри контейнера для хранения отчетов.
*   `ssl_keyfile`: Путь к файлу ключа сертификата.
*   `ssl_certfile`: Путь к файлу сертификата.
*   `b24_webhook_url`: URL входящего вебхука (права: CRM).
*   `smart_process_type_id`: ID типа смарт-процесса в Bitrix24.
*   `sp_deals_uf`: ID пользовательского реквизита, в котором расположен массив связанных сделок.

### Шаг 3. Запуск в Docker

Убедитесь, что Docker и Docker Compose установлены.

1.  **Сборка и запуск:**
    ```bash
    docker-compose up --build
    ```
    После запуска сервис будет доступен по адресу: `https://127.0.0.1:8000` (или на том хосте, где запущен Docker).
    *Примечание: Браузер может предупредить о небезопасном соединении, так как сертификат самоподписанный. Это нормально.*

2.  **Остановка:**
    ```bash
    docker-compose down
    ```

---

## 📡 API Методы

### 1. Health Check

Тестовый callback. В случае доступности, вернет отправленное

*   **URL:** `/test`
*   **Метод:** `GET`
*   **Ответ:**
    ```json
    {
      "status": "success",
      "version": "v1",
      "received_data": ""
    }
    ```

### 2. Основной Webhook (GET/POST)

Основной метод для подключения робота смарт-процесса в Bitrix24

*   **URL:** `/api/v1/sendDealData`
*   **Метод:** `POST`
*   **Тело запроса (JSON) (или параметыр GET):**
    ```json
    {
      "smart_process_id": 10
    }
    ```
*   **Ответ:**
    ```json
    {
      "status": "success",
      "message": "Deal processed and Excel generated",
      "smart_process_id": 10,
      "download_url": "https://127.0.0.1:8000/files/deal_10.xlsx"
    }
    ```

### 3. Документация (Swagger UI)

Интерактивная документация доступна автоматически после запуска:
*   **URL:** `https://127.0.0.1:8000/docs`

---

## 📂 Структура проекта

```text
b24-excel-exporter/
├── app/                    # Основной код приложения
│   ├── api/                # Маршруты и схемы данных (Pydantic)
│   ├── services/           # Бизнес-логика (Bitrix, Excel, Workflow)
│   ├── config.py           # Загрузка и валидация настроек
│   └── logger.py           # Настройка логирования
├── certs/                  # SSL сертификаты (не пушить в git!)
├── files/                  # Сгенерированные отчеты
├── main.py                 # Точка входа
├── serviceProperties.json  # Конфигурация (не пушить в git!)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```