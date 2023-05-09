**07.04.2023**  
План:  
- [x] Добавить функционал кнопки "Не нашли проект в списке?"   
- [x] Отображение последних 5 добавленных записей на странице добавления записей
- [x] Починка авторизации после разрыва сессии
# "Не нашли проект в списке?"   

  "Не нашли проект в списке?" - по нажатию на кнопку, переводится на страницу добавления проекта.  
  На этой странице будет форма добавления проекта, которая будет состоять из следующих полей:  
- Код проекта, например, "21П18" или "23В01"  
- Название проекта, например, "Балтика СПб Термоупаковщик-5"

## Детали backend части:
--- 
Код проекта должен быть формата: `dd[А-Я]dd`, например, "23В01"  
Код и название проекта должны быть склеены следующим образом:  
`"dd[А-Я]dd project_name"`, то есть между ними д.б. пробел.  
### Зависимость проекта->статей расходов->задач
---
- Когда создается проект, под ним нет статей затрат. Их надо добавить. 
- Когда создается статья затрат, под ней **автоматически** добавляется задача `blank_task`  
- Когда создаётся проект через эту кнопку, в проекте, ГИПом будет **mar** (gip_id = 9)

# Отображение последних 5 добавленных записей  
Эти записи могут быть размещены сбоку или под формой. В мобильной версии под формой.
## Детали backend части:
---
В классе `Records` можно создать `classmethod` - под названием `get_last_5_records`.  

    class Records(...):  
      @classmethod  
      def get_last_5_records(cls):
        session = db.session
        select = db.select
        execute = db.execute
        stmt = select(cls).order_by(cls.time_created).limit(5)
        res = execute(stmt).fetchall()
        return res

- [x] Тест этого метода  
Этот метод выдаёт только 5 первых с начала (id=1,2...) и т.д.   
Корректнее работает этот код:  

      @classmethod  
      def get_last_5_records(cls):
          session = db.session
          select = db.select
          execute = session.execute
          stmt = select(cls).order_by(cls.id.desc(), cls.time_created).limit(5)
          res = execute(stmt).scalars().fetchmany()
          return res
Он возвращает 5 последних (с конца по id) записей. Данные в списке типа объекта Records.

Теперь надо:  
- [x] заменить id людей на логины, а id статей затрат на их именования, имя задачи пока не отображать  
- [x] Отобразить эти 5 записей на HTML

COLUMNS
---
| Field | Type | Null | Key | Default | Extra | 
| --- | --- | --- | --- | --- | --- | 
| id | int(11) | NO | PRI | \N | auto_increment | 
| time_created | datetime | YES |  | current_timestamp() |  | 
| employee_id | int(11) | YES | MUL | \N |  | 
| project_id | int(11) | YES | MUL | \N |  | 
| cost_id | int(11) | YES | MUL | \N |  | 
| task_id | int(11) | YES | MUL | \N |  | 
| hours | int(11) | YES |  | \N |  | 
| minuts | int(11) | YES |  | \N |  | 

`employee_id` вторичный ключ т. `employees`  - в этой т. можно достать логин напрямую  
`project_id` вторичный ключ т. `projects`  - в этой т. можно достать код проекта/имя проекта напрямую    
`cost_id` вторичный ключ т. `project_costs` - в этой т. нельзя достать имя проетка напрямую    
`task_id` вторичный ключ т. `costs_tasks` -  в этой т. нельзя достать имя проекта напрямую  
### Там, где нельзя достать имя проекта напрямую:
---
По вторичному ключу достаем объект связанной таблице, по ней достаем вторичный ключ названия, по этому ключу достаем нужное имя
#### **Решение:**  
    def replace_ids_to_names(
            self, EmployeesObj,
            ProjectsObj, ProjectCostObj, 
            CostsTasksObj, CostsObj, TasksObj):
        emp_login = db.session.get(EmployeesObj, self.employee_id).login
        project_name = db.session.get(ProjectsObj, self.project_id).project_name
        project_cost_name_fk_id = ProjectCostObj.query.filter_by(id=self.cost_id).first().cost_name_fk
        cost_name = db.session.get(CostsObj, project_cost_name_fk_id).cost_name
        project_cost_tasks_name_fk_id = CostsTasksObj.query.filter_by(cost_id=self.cost_id).first().task_name_fk
        task_name = db.session.get(TasksObj, project_cost_tasks_name_fk_id).task_name
        return (self.id, self.time_created, emp_login, project_name, cost_name, task_name, self.hours, self.minuts)

`blank_task` - это костыль!


## Починка авторизации после разрыва сессии
---
Эту проблему решил код ниже:  

    @main.before_app_first_request
    def ping_connect():
        try:
            logger.info("Ping DB")
            res = execute(
                select(Records)
            ).first()
        except:
            logger.warning("Ping DB")
Выбираем первую запись в БД в таблице `records`, тем самым инициируя подключение к БД перед обработкой первого запроса.