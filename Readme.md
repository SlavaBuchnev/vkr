## Источник данных

Все тестовые экземпляры задачи квадратичного назначения взяты из общедоступной библиотеки [**QAPLIB**](https://qaplib.mgi.polymtl.ca/).

план тестов:
запуск + 14 тестов, делать по 5 запусков каждого варианта:
```json
{
    "pop_size": 500, // 250, 500, 1000
    "gens": 150, // 50, 100, 150, 300
    "cross_rate": 0.8, // 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1
    "mut_rate": 0.3, // 0.1, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5
    "tourn_size": 10, // 2, 5, 10, 20
    "elitism": 10, // 0, 1, 2, 5, 10, 25, 30
    "use_local_search": true, // true, false
    "ls_freq": 10, // 1, 5, 10, 20
    "strategy": "generational", // "generational", "plus", "comma"
    "init_method":"clustering_sa" // "random", "clustering_sa"
}
```

## Установка зависимостей
Рекомендуется предварительно создать и активировать виртуальное окружение:
```shell

pip install -r requirements.txt
```
## Разработка LaTeX
```shell

cd latex; make run
```
## Структура проекта
```
.
├── main/                       
│   ├── cycle_crossover_support.py   # Реализация циклического кроссинговера и вспомогательных функций
│   ├── algo_ea.py                   # Эволюционный алгоритм для QAP
│   └── manufacturing.py             # Загрузка данных, вычисление стоимости, чтение конфигов
│
├── test/
│   ├── run_tests_unit.py            # Запуск unit тестов
│   ├── unit/                        # папка с unit тестами
│   └── integration/                 # папка с integration тестами
│
├── configs/                         # Папка с конфигурационными файлами
│   ├── ea_results.csv               # Результаты
│   ├── opt_values.json              # Известные оптимальные значения для тестовых экземпляров
│   └── ea_params.json               # Параметры эволюционного алгоритма
│
├── latex/                           # LaTeX
│
└── files/                           # папка с данными
```