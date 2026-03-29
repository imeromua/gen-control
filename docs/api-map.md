# API Map — Всі ендпоінти GenControl

Базовий URL: `http://localhost:8080`

## Auth
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| POST | `/auth/login` | Публічний | Логін, повертає JWT |
| POST | `/auth/logout` | Авторизований | Логаут, видаляє токен |
| POST | `/auth/refresh` | Авторизований | Оновити токен |

## Users
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/users` | ADMIN | Список користувачів |
| POST | `/users` | ADMIN | Створити користувача |
| GET | `/users/{id}` | ADMIN | Деталі користувача |
| PUT | `/users/{id}` | ADMIN | Оновити користувача |
| DELETE | `/users/{id}` | ADMIN | Видалити користувача |
| GET | `/users/me` | Авторизований | Поточний користувач |

## Generators
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/generators` | ADMIN + OPERATOR | Список генераторів |
| POST | `/api/generators` | ADMIN | Створити генератор |
| GET | `/api/generators/{id}` | ADMIN + OPERATOR | Деталі генератора |
| PUT | `/api/generators/{id}` | ADMIN | Оновити генератор |
| DELETE | `/api/generators/{id}` | ADMIN | Видалити генератор |
| GET | `/api/generators/{id}/status` | ADMIN + OPERATOR | Статус генератора |
| GET | `/api/generators/{id}/settings` | ADMIN | Налаштування |
| PUT | `/api/generators/{id}/settings` | ADMIN | Оновити налаштування |

## Motohours
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/motohours/{gen_id}` | ADMIN + OPERATOR | Мотогодини генератора |
| GET | `/api/motohours/{gen_id}/maintenance` | ADMIN + OPERATOR | Журнал ТО |
| POST | `/api/motohours/{gen_id}/maintenance` | ADMIN | Зафіксувати ТО |

## Shifts
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/shifts` | ADMIN + OPERATOR | Журнал змін |
| POST | `/api/shifts/start` | ADMIN + OPERATOR | Запустити генератор |
| POST | `/api/shifts/{id}/stop` | ADMIN + OPERATOR | Зупинити генератор |
| GET | `/api/shifts/active` | ADMIN + OPERATOR | Активна зміна |
| GET | `/api/shifts/{id}` | ADMIN + OPERATOR | Деталі зміни |

## System Settings
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/shifts/settings` | ADMIN + OPERATOR | Системні налаштування |
| PUT | `/api/shifts/settings` | ADMIN | Оновити робочий час |

## Fuel
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/fuel/stock` | ADMIN + OPERATOR | Поточний стан складу |
| PUT | `/api/fuel/stock` | ADMIN | Налаштування складу |
| GET | `/api/fuel/deliveries` | ADMIN + OPERATOR | Журнал постачань |
| POST | `/api/fuel/deliveries` | ADMIN + OPERATOR | Прийняти паливо |
| GET | `/api/fuel/refills` | ADMIN + OPERATOR | Журнал заправок |
| POST | `/api/fuel/refills` | ADMIN + OPERATOR | Заправити генератор |

## Oil
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/oil` | ADMIN + OPERATOR | Список запасів мастила |
| POST | `/api/oil` | ADMIN | Додати запас мастила |
| PATCH | `/api/oil/{id}` | ADMIN | Оновити кількість |

## Adjustments
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/adjustments` | ADMIN | Список корекцій |
| POST | `/api/adjustments` | ADMIN | Створити корекцію |
| GET | `/api/adjustments/{id}` | ADMIN | Деталі корекції |

## Outage Schedule
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/outage` | ADMIN + OPERATOR | Графік відключень |
| POST | `/api/outage` | ADMIN | Додати відключення |
| DELETE | `/api/outage/{id}` | ADMIN | Видалити відключення |
| GET | `/api/outage/next` | ADMIN + OPERATOR | Найближче відключення |

## Event Log
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/events` | ADMIN + OPERATOR | Журнал подій |
| GET | `/api/events/{id}` | ADMIN + OPERATOR | Деталі події |

## Dashboard
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/api/dashboard` | ADMIN + OPERATOR | Повна картина |
| GET | `/api/dashboard/summary` | ADMIN + OPERATOR | Легкий polling endpoint |

## Health
| Метод | URL | Доступ | Опис |
|---|---|---|---|
| GET | `/health` | Публічний | Перевірка сервера |

## Swagger UI

`http://localhost:8080/docs` — інтерактивна документація API
