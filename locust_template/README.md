# Locust Template - Шаблон для нагрузочного тестирования

## 📋 Общее описание

Проект представляет собой шаблон для нагрузочного тестирования на основе фреймворка **Locust**. Проект предназначен для тестирования веб-приложения **WebTours** (демонстрационное приложение для тестирования). 

Архитектура проекта построена на модульном принципе с четким разделением на конфигурацию, сценарии тестирования, утилиты и кастомные профили нагрузки.

---

## 📁 Структура проекта

```
locust_template/
├── locustfile.py              # Точка входа, импорт сценариев
├── requirements.txt           # Зависимости проекта
├── test_logs.log              # Файл логов
├── config/
│   └── config.py             # Система конфигурации и логирования
├── user_classes/
│   ├── wt_base_scenario.py   # Базовый сценарий (работает)
│   └── wt_cancel_scenario.py # Сценарий отмены (заготовка)
├── custom_shape/
│   └── custom_load_shapes.py # Кастомные профили нагрузки
├── utils/
│   ├── assertion.py          # Заготовка для проверок
│   └── non_test_methods.py   # Заготовка для утилит
├── test_data/                # Директория для тестовых данных
└── reports/                   # Директория для отчетов
```

---

## 🔧 Компоненты проекта

### 1. `locustfile.py` - Точка входа

**Назначение:** Главный файл, который Locust использует для запуска тестов.

**Как работает:**
- Читает конфигурацию из `config.config`
- Условно импортирует и активирует сценарии на основе конфигурации
- Устанавливает вес (`weight`) для каждого класса пользователей
- Логирует активацию сценариев

**Пример кода:**
```python
from config.config import cfg, logger

if cfg.webtours_base.included:
    from user_classes.wt_base_scenario import WebToursBaseUserClass
    WebToursBaseUserClass.weight = cfg.webtours_base.weight
    logger.info("WebToursBaseUserClass started")
```

---

### 2. `config/config.py` - Система конфигурации

#### Основные компоненты:

##### a) `ScenarioConfig` (базовый класс)
```python
class ScenarioConfig(BaseModel):
    included: bool  # Включен ли сценарий
    url: str        # URL для тестирования
    weight: int     # Вес сценария (вероятность выбора)
```

##### b) Конфигурации сценариев
- `WebToursBaseScenarioConfig` - для базового сценария WebTours
- `WebToursCancelScenarioConfig` - для сценария отмены (заготовка)

##### c) `Config` (основной класс настроек)
```python
class Config(BaseSettings):
    webtours_base: WebToursBaseScenarioConfig
    webtours_cancel: WebToursCancelScenarioConfig
    url: str = Field('http://localhost:1080', env="URL")
    locust_locustfile: str = Field("./locustfile.py", env="LOCUST_LOCUSTFILE")
    pacing: int = Field(5, env="PACING")
    loadshape_type: str = Field('baseline', env="LOADSHAPE_TYPE")
```

**Параметры:**
- `webtours_base`, `webtours_cancel` - конфигурации сценариев
- `url` - базовый URL тестируемого приложения (по умолчанию `http://localhost:1080`)
- `locust_locustfile` - путь к файлу locustfile
- `pacing` - интервал между итерациями в секундах
- `loadshape_type` - тип профиля нагрузки (`baseline` или `stages`)

##### d) `LogConfig` - Система логирования
```python
class LogConfig():
    logger = logging.getLogger('demo_logger')
    logger.setLevel('DEBUG')
    file = logging.FileHandler(filename='test_logs.log')
    file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(file)
    logger.propagate = False
```

**Особенности:**
- Логирование в файл `test_logs.log`
- Уровень логирования: `DEBUG`
- Формат: дата/время, уровень, сообщение
- `propagate = False` - логи не дублируются в корневой логгер

##### e) Загрузка конфигурации
```python
env_file = Path(__file__).resolve().parent.parent / ".env"
cfg = Config(_env_file=(env_file if env_file.exists() else None), 
             _env_nested_delimiter="__")
```

**Как работает:**
1. Ищет файл `.env` в корне `locust_template/`
2. Если файл существует - загружает переменные оттуда
3. Если файла нет - использует переменные окружения системы
4. `_env_nested_delimiter="__"` позволяет использовать вложенные параметры (например, `WEBTOURS_BASE__INCLUDED=true`)

---

### 3. `user_classes/` - Классы пользователей (сценарии)

#### `wt_base_scenario.py` - Базовый сценарий

##### a) `PurchaseFlightTicket` (SequentialTaskSet)
```python
class PurchaseFlightTicket(SequentialTaskSet):
    @task()
    def uc_00_getHomePage(self):
        r00_01_response = self.client.get('/WebTours/', ...)
        logger.info(f"Статус ответа: {r00_01_response.status_code}, ...")
        print(f"Статус ответа: {r00_01_response.status_code}, ...")
```

**Особенности:**
- Наследуется от `SequentialTaskSet` - задачи выполняются последовательно
- Декоратор `@task()` - стандартный декоратор Locust для задач
- Метод `uc_00_getHomePage()`:
  - Выполняет GET запрос к `/WebTours/`
  - Использует реалистичные заголовки (User-Agent, cookies и т.д.)
  - Логирует ответ в файл
  - Выводит информацию в консоль

##### b) `WebToursBaseUserClass` (HttpUser)
```python
class WebToursBaseUserClass(HttpUser):
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url
    tasks = [PurchaseFlightTicket]
```

**Параметры:**
- `wait_time = constant_pacing(cfg.pacing)` - фиксированная пауза между итерациями
- `host = cfg.url` - базовый URL из конфигурации
- `tasks = [PurchaseFlightTicket]` - список задач для выполнения

#### `wt_cancel_scenario.py`
- Файл пустой (заготовка для будущего сценария отмены)

---

### 4. `custom_shape/custom_load_shapes.py` - Кастомные профили нагрузки

#### Класс `CustomLoadShape`:
```python
class CustomLoadShape(LoadTestShape):
    def __init__(self):
        super().__init__()
        match cfg.loadshape_type:
            case "baseline":
                self.stages = [{"duration": 60, "users": 1, "spawn_rate": 1}]
            case "stages":
                self.stages = [
                    {"duration": 60, "users": 10, "spawn_rate": 1},
                    {"duration": 120, "users": 20, "spawn_rate": 1},
                    {"duration": 180, "users": 30, "spawn_rate": 1},
                    {"duration": 240, "users": 40, "spawn_rate": 1}
                ]
```

**Профили нагрузки:**
- **`baseline`**: 1 пользователь на 60 секунд
- **`stages`**: ступенчатый рост нагрузки:
  - 10 пользователей на 60 секунд
  - 20 пользователей на 120 секунд
  - 30 пользователей на 180 секунд
  - 40 пользователей на 240 секунд

**Метод `tick()`:**
- Определяет текущий этап на основе времени выполнения
- Возвращает `(users, spawn_rate)` для текущего этапа
- Возвращает `None` когда все этапы завершены

---

### 5. `utils/` - Вспомогательные утилиты

#### `assertion.py`
- Файл пустой (заготовка для будущих проверок)

#### `non_test_methods.py`
- Файл пустой (заготовка для вспомогательных методов)

---

## 🚀 Как работает проект (поток выполнения)

### 1. Инициализация
```
locustfile.py → config/config.py → загрузка конфигурации
```

**Шаги:**
1. Locust запускает `locustfile.py`
2. Импортируется `config.config`, создается объект `cfg` и `logger`
3. Конфигурация загружается из `.env` файла или переменных окружения

### 2. Активация сценариев
```
locustfile.py → проверка cfg.webtours_base.included → импорт WebToursBaseUserClass
```

**Шаги:**
1. Проверяется флаг `cfg.webtours_base.included`
2. Если `True`, импортируется класс `WebToursBaseUserClass`
3. Устанавливается вес сценария
4. Логируется активация

### 3. Выполнение теста
```
Locust Master → создает виртуальных пользователей → WebToursBaseUserClass → PurchaseFlightTicket
```

**Шаги:**
1. Locust создает виртуальных пользователей согласно профилю нагрузки
2. Каждый пользователь - это экземпляр `WebToursBaseUserClass`
3. Пользователь выполняет задачи из `PurchaseFlightTicket`
4. Между итерациями - пауза `constant_pacing(cfg.pacing)`

### 4. Выполнение задачи
```
uc_00_getHomePage() → HTTP GET запрос → логирование → ожидание → повтор
```

**Шаги:**
1. Выполняется метод `uc_00_getHomePage()`
2. Отправляется GET запрос к `/WebTours/`
3. Ответ логируется в `test_logs.log` и выводится в консоль
4. Ожидание `pacing` секунд
5. Повтор цикла

---

## ⚙️ Конфигурация через переменные окружения

### Пример файла `.env`:
```env
URL=http://localhost:1080
PACING=5
LOADSHAPE_TYPE=baseline
WEBTOURS_BASE__INCLUDED=true
WEBTOURS_BASE__URL=http://localhost:1080
WEBTOURS_BASE__WEIGHT=1
WEBTOURS_CANCEL__INCLUDED=false
WEBTOURS_CANCEL__URL=http://localhost:1080
WEBTOURS_CANCEL__WEIGHT=1
```

### Или через системные переменные окружения:
```bash
export URL=http://localhost:1080
export PACING=5
export LOADSHAPE_TYPE=stages
export WEBTOURS_BASE__INCLUDED=true
export WEBTOURS_BASE__WEIGHT=1
```

**Важно:** Для вложенных параметров используется двойное подчеркивание `__`:
- `WEBTOURS_BASE__INCLUDED` → `cfg.webtours_base.included`
- `WEBTOURS_BASE__URL` → `cfg.webtours_base.url`
- `WEBTOURS_BASE__WEIGHT` → `cfg.webtours_base.weight`

---

## 📦 Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r locust_template/requirements.txt
```

### 2. Настройка конфигурации

Создайте файл `.env` в директории `locust_template/` или экспортируйте переменные окружения (см. раздел выше).

### 3. Запуск Locust

#### Базовый запуск:
```bash
cd locust_template
locust -f locustfile.py
```

#### Запуск с указанием хоста:
```bash
locust -f locustfile.py --host http://localhost:1080
```

#### Запуск с кастомным профилем нагрузки:
```bash
# Установите LOADSHAPE_TYPE=stages в .env или переменных окружения
locust -f locustfile.py --host http://localhost:1080
```

#### Запуск в headless режиме (без веб-интерфейса):
```bash
locust -f locustfile.py --host http://localhost:1080 --headless -u 10 -r 2 -t 60s
```

**Параметры:**
- `-u 10` - количество пользователей
- `-r 2` - скорость создания пользователей (spawn rate)
- `-t 60s` - время выполнения теста

### 4. Доступ к веб-интерфейсу

После запуска откройте браузер и перейдите по адресу:
```
http://localhost:8089
```

---

## 📊 Зависимости проекта

Проект использует следующие библиотеки:

- **locust** - фреймворк для нагрузочного тестирования
- **pydantic** - валидация данных и моделей
- **pydantic-settings** - управление настройками из переменных окружения

Все зависимости указаны в файле `requirements.txt`.

---

## 🏗️ Архитектурные особенности

### Преимущества:
1. ✅ **Модульность** - четкое разделение конфигурации, сценариев и утилит
2. ✅ **Гибкость** - настройка через переменные окружения
3. ✅ **Расширяемость** - легко добавлять новые сценарии
4. ✅ **Логирование** - централизованное логирование в файл
5. ✅ **Профили нагрузки** - кастомные профили через `CustomLoadShape`

### Текущие ограничения:
1. ⚠️ `wt_cancel_scenario.py` пустой (заготовка)
2. ⚠️ `utils/assertion.py` и `utils/non_test_methods.py` пустые (заготовки)
3. ⚠️ В `PurchaseFlightTicket` только одна задача
4. ⚠️ Нет обработки ошибок и проверок ответов

---

## 📝 Примеры использования

### Пример 1: Базовый тест с 1 пользователем
```bash
# .env
LOADSHAPE_TYPE=baseline
PACING=5
WEBTOURS_BASE__INCLUDED=true
WEBTOURS_BASE__WEIGHT=1

# Запуск
locust -f locustfile.py --host http://localhost:1080
```

### Пример 2: Ступенчатый рост нагрузки
```bash
# .env
LOADSHAPE_TYPE=stages
PACING=3
WEBTOURS_BASE__INCLUDED=true
WEBTOURS_BASE__WEIGHT=1

# Запуск
locust -f locustfile.py --host http://localhost:1080
```

### Пример 3: Headless режим с отчетом
```bash
locust -f locustfile.py \
  --host http://localhost:1080 \
  --headless \
  -u 20 \
  -r 5 \
  -t 5m \
  --html reports/report.html \
  --csv reports/stats
```

---

## 🔍 Мониторинг и логирование

### Логи тестирования
Все логи сохраняются в файл `test_logs.log` в корне проекта `locust_template/`.

**Формат логов:**
```
2026-01-09 23:30:14,127 INFO: WebToursBaseUserClass started
2026-01-09 23:36:28,855 INFO: Статус ответа: 304, Тело ответа: ...
```

### Веб-интерфейс Locust
После запуска доступен веб-интерфейс по адресу `http://localhost:8089` с:
- Статистикой в реальном времени
- Графиками производительности
- Детальной информацией о запросах
- Возможностью остановки/перезапуска теста

---

## 🛠️ Расширение проекта

### Добавление нового сценария:

1. Создайте новый файл в `user_classes/`, например `wt_new_scenario.py`
2. Создайте класс сценария, наследуясь от `SequentialTaskSet`
3. Создайте класс пользователя, наследуясь от `HttpUser`
4. Добавьте конфигурацию в `config/config.py`:
   ```python
   class WebToursNewScenarioConfig(ScenarioConfig):
       ...
   ```
5. Добавьте в класс `Config`:
   ```python
   webtours_new: WebToursNewScenarioConfig
   ```
6. Импортируйте в `locustfile.py`:
   ```python
   if cfg.webtours_new.included:
       from user_classes.wt_new_scenario import WebToursNewUserClass
       WebToursNewUserClass.weight = cfg.webtours_new.weight
   ```

### Добавление нового профиля нагрузки:

Отредактируйте `custom_shape/custom_load_shapes.py` и добавьте новый `case` в `match`:
```python
case "custom_profile":
    self.stages = [
        {"duration": 120, "users": 50, "spawn_rate": 10},
        {"duration": 300, "users": 100, "spawn_rate": 20}
    ]
```

---

## 📚 Дополнительная информация

### Документация Locust:
- [Официальная документация Locust](https://docs.locust.io/)
- [Примеры использования](https://docs.locust.io/en/stable/writing-a-locustfile.html)

### Структура проекта:
- Проект следует принципам модульной архитектуры
- Каждый компонент имеет четко определенную ответственность
- Конфигурация централизована и легко настраивается

---

## 📄 Лицензия

Проект представляет собой шаблон для нагрузочного тестирования.

---

## 👥 Авторы

Шаблон проекта для нагрузочного тестирования на основе Locust.

---

## 🔄 Версия

Версия проекта: 1.0.0

---

## 📞 Поддержка

При возникновении вопросов или проблем, проверьте:
1. Правильность настройки переменных окружения
2. Доступность тестируемого приложения
3. Логи в файле `test_logs.log`
4. Документацию Locust
