# Homework Tracker API — Пара 9, API-first

**Зачем этот API:** чтобы учитель мог выдавать домашние задания классу, а ученики в одном месте видели, что и к какому сроку сделать.

## Что в репозитории

| Путь | Что это |
|---|---|
| `api.yaml` | Спецификация OpenAPI 3.0.3 — источник правды |
| `service/` | Сервис, сгенерированный по спеке (python-flask + connexion) |
| `README.md` | Этот файл |

## Часть 1 · Спецификация

5 эндпоинтов, 5 разных операций:

| Метод | Путь | Что делает | Успех | Ошибки |
|---|---|---|---|---|
| GET | `/homeworks` | список с фильтрами `grade`, `status`, пагинация `page`/`size` | 200 | 400, 401 |
| GET | `/homeworks/{homeworkId}` | одно задание | 200 | 401, 404 |
| POST | `/homeworks` | создать (только учитель) | 201 | 400, 401, 403 |
| PATCH | `/homeworks/{homeworkId}` | частично изменить (только учитель) | 200 | 400, 401, 403, 404 |
| DELETE | `/homeworks/{homeworkId}` | удалить (только учитель) | 204 | 401, 403, 404 |

**401 vs 403:**
- **401 Unauthorized** — «не знаю, кто ты»: токена нет или он неверный.
- **403 Forbidden** — «знаю, кто ты, но нельзя»: ученик с валидным токеном пытается создать, изменить или удалить задание.

**DTO в `components/schemas`** — внутреннее наружу не едет:
- `HomeworkCreateRequest` — то, что присылает клиент: без `id`, `status`, `createdAt` (их ставит сервер).
- `HomeworkUpdateRequest` — для PATCH, все поля необязательные.
- `HomeworkResponse` — то, что отдаёт сервер. Внутренние поля сущности (`teacher_id`, флаг мягкого удаления `deleted`) в схеме отсутствуют и в ответ не попадают.
- `HomeworkPage` — обёртка списка, `Error` — единый формат ошибки.

Общие ответы об ошибках вынесены в `components/responses` и переиспользуются через `$ref`.

Проверка валидности:
```bash
openapi-spec-validator api.yaml                 # api.yaml: OK
openapi-generator-cli validate -i api.yaml      # No validation issues detected.
```
Также спека открывается без ошибок в editor.swagger.io и импортируется в Postman (Import → OpenAPI).

## Часть 2 · Кодогенерация

```bash
pip install openapi-generator-cli
openapi-generator-cli generate -i api.yaml -g python-flask -o service \
  --additional-properties=packageName=homework_service
```
Генератор: **python-flask**, openapi-generator 7.27.0.

Сгенерировались модели по каждой DTO, контроллеры с функцией на каждую операцию (`list_homeworks`, `get_homework`, `create_homework`, `update_homework`, `delete_homework`) и заглушка проверки токена. Тела контроллеров — `return 'do some magic!'`.

### Запуск
```bash
cd service
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m homework_service
```
Swagger UI: http://localhost:8080/api/v1/ui/

Тестовые токены: `teacher-token` (учитель), `student-token` (ученик).

```bash
curl -X POST localhost:8080/api/v1/homeworks \
  -H "Authorization: Bearer teacher-token" -H "Content-Type: application/json" \
  -d '{"subject":"English","grade":8,"title":"ex. 3 p. 45","dueDate":"2026-11-20"}'
```

### Проверено вручную (curl)

| Сценарий | Ожидали | Получили |
|---|---|---|
| GET список без токена | 401 | 401 |
| POST от учителя | 201 | 201 |
| POST от ученика | 403 | 403 |
| POST без обязательного `dueDate` | 400 | 400 |
| GET список / одно задание | 200 | 200 |
| GET несуществующего id | 404 | 404 |
| PATCH статуса учителем | 200 | 200 |
| DELETE от ученика | 403 | 403 |
| DELETE от учителя | 204 | 204 |
| GET после удаления | 404 | 404 |

## Часть 3 · Как делали

**С агентом:** Claude (модель Claude Opus 5.5) в чате claude.ai с доступом к терминалу — агент сам писал спеку, запускал валидатор, генератор и curl-проверки.

**Порядок работы:**
1. Написали `api.yaml`, прогнали через `openapi-spec-validator` и `openapi-generator-cli validate` — ошибок нет.
2. Сгенерировали сервис генератором `python-flask`.
3. Запустили и проверили все эндпоинты curl-запросами (таблица выше).

**Что поправили руками после генерации**:
1. `controllers/homework_controller.py` — вместо `'do some magic!'` написана логика: хранилище в памяти, проверка роли (403), поиск по id (404), PATCH только переданных полей, перевод внутренней сущности в `HomeworkResponse`.
2. `controllers/security_controller.py` — заглушка пускала любой токен; теперь неизвестный токен даёт 401, а из токена берётся роль.
3. `requirements.txt` — добавлен `werkzeug < 2.2`.

**Известное отличие от спеки:** ошибки 400 и 401 формирует сама библиотека connexion при валидации запроса, поэтому их тело приходит в формате `{status, title, detail}`, а не в нашей схеме `Error`. Коды при этом правильные. Ошибки 403 и 404 возвращаются точно по схеме `Error`.
