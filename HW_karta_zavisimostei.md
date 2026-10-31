Задание:
1. Найти слои в коде StPlatform, протрассировать одну функцию в формате Файл.метод → Файл.метод.
2. Сделать то же для PetClinic («добавление визита») через агента и указать агента и модель.

---

## Часть 1. StPlatform — «сдать домашку»

Репозиторий: https://gitverse.ru/UnMatty/StPlatform, ветка main
Пакет: src/main/java/ru/urfu/platform/
Пакеты нарезаны по фичам: user, auth, assignment, submission, consent, aicheck, student. Контроллеры вынесены в web/ (страницы) и api/ (REST).

### 1.1 Список слоёв

| Слой | Классы |
|---|---|
| Контроллеры (web/) | AssignmentPageController, CabinetController, ActivateController, LoginController, PasswordResetController, AttachmentController, TeacherAssignmentController, TeacherImportController, TeacherStudentController, AiSettingsPageController, consent/ConsentPageController |
| Контроллеры (api/) | ApiSubmissionController, ApiAssignmentController, ApiAuthController |
| Сервисы | SubmissionService, AssignmentService, UserService, ActivationService, PasswordResetService, ConsentService, AiCheckService, AiSettingsService, StudentRemovalService, PlatformUserDetailsService |
| Репозитории (Spring Data JPA) | SubmissionRepository, SubmissionAttachmentRepository, AssignmentRepository, UserRepository, ConsentRecordRepository, AiCheckRepository, AiSettingsRepository |
| Сущности (@Entity) | Submission, SubmissionAttachment, Assignment, User, ConsentRecord, AiCheck, AiSettings |
| Инфраструктура | AttachmentStorage (файлы на диске), LinkValidator, InviteMailer, PasswordResetMailer, config/, security/ |

### 1.2 Цепочка вызовов

POST /assignments/{id}/submit

```
web/AssignmentPageController.submitWork
 → user/UserService.byId
    → UserRepository.findById
 → submission/SubmissionService.submit
    → assignment/AssignmentRepository.findById
    → Assignment.isPublished
    → SubmissionService.ensureNotAlreadySent
       → SubmissionRepository.findFirstByStudentIdAndAssignmentIdOrderByCreatedAtDesc
    → Assignment.deadlinePassed
    → submission/LinkValidator.isValid
    → SubmissionRepository.save
    → submission/AttachmentStorage.store
    → SubmissionAttachmentRepository.save
    → publishEvent(SubmissionCreatedEvent)
 → redirect:/assignments/{id}


### 1.3 Все ли стрелки идут «вниз»?

Да, все стрелки идут сверху вниз: контроллер → сервис → репозиторий → БД.
- Ни один контроллер не обращается к репозиторию напрямую.
- Ни один сервис не зависит от web/ или api/.


### 1.4 Где провёл бы границу иначе

- Разобрать MultipartFile в контроллере, а в сервис передать нейтральный тип (имя файла).


### 1.5 Зачем граница

Граница нужна, чтобы правило «когда можно сдать работу» жило в одном месте и одинаково работало для веб-формы, REST и тестов, независимо от того, как пришёл запрос.

---

## Часть 2. Spring PetClinic — «добавление визита»

Выполнено агентом: general-purpose 
Модель: Claude Sonnet 5.5 
Репозиторий: https://github.com/spring-projects/spring-petclinic, ветка main

### 2.1 Список слоёв

| Слой | Классы |
|---|---|
| Контроллеры | VisitController, OwnerController, PetController, VetController, WelcomeController, CrashController |
| Сервисы | **нет**: контроллеры работают с репозиториями напрямую |
| Репозитории | OwnerRepository, PetTypeRepository (JpaRepository), VetRepository |
| Сущности | Owner, Pet, Visit, PetType, Vet, Specialty, BaseEntity, NamedEntity, Person |

### 2.2 Цепочка вызовов

POST /owners/{ownerId}/pets/{petId}/visits/new

```
owner/VisitController.loadPetWithVisit
 → OwnerRepository.findById
 → Owner.getPet
 → new Visit()
 → Pet.addVisit

owner/VisitController.processNewVisitForm
 → @Valid Visit + проверка даты
 → Owner.addVisit
    → Owner.getPet
    → Pet.addVisit
 → OwnerRepository.save
 → redirect:/owners/{ownerId}
```

### 2.3 Все ли стрелки идут «вниз»?

Да, все стрелки идут вниз: контроллер → сущности и контроллер → репозиторий. Обратных вызовов нет.

### 2.4 Зачем граница

Граница нужна, чтобы бизнес-правила и транзакции не зависели от HTTP: тогда их можно тестировать и переиспользовать без Spring MVC.

---

## Вывод

StPlatform разделён на слои строже, чем PetClinic. В нём есть сервисный слой, контроллеры не касаются репозиториев, а фичи связаны событиями. PetClinic проще, но контроллер в нём совмещает роль сервиса.
