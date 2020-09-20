# LDM-generator
This is a simple LDM (logical data model) generator written in Python.

Это простой генератор логических моделей данных, написанный на Python.

##Концепция
Существующие инструменты для документирования БД позволяют создавать очень подробные описания физических моделей данных. Данный скрипт не заменяет их, он генерирует упрощенную логическую модель данных, которая
* Концентрируется на сущностях, их атрибутах и связях. 
* Использует бизнес-названия вместо технических - значит она понятна аналитику и может обсуждаться с бизнесом.
* Выгружается в простом редактируемом формате - это значит можно скопировать часть таблиц, добавить несколько своих и через 5 минут идти обсуждать это с команджой или заказчиком.   
* Может быть обогащена данными о несуществующих в физической модели сущностях и связях.

## Пример использования

    import LDM    
    # Создаем пустую модель
    model = LDM.LDM()    
    # Извлекаем модель из базы mybase
    model.select_from_postgres("dbname=mybase user=mybase password=mybase host=localhost port=5432")
    # опционально - сохраняем модель в файл, нужно для того, чтобы разделить логику извлечения и обработки
    model.save("mybase.json")
    # опционально - извлекаем ранее сохраненную модель из файла
    model.load("mybase.json")
    # опционально - обогащаем модель 
    model.enrich("mybase_info.json", refresh=False )
    # опционально - обновляем mybase_info в отдельном файле, либо не указываем refresh=False тогдп будет изменен mybase_info.json
    model.refresh_info("mybase_info_new.json")
    # Экспорт в картинку
    model.export_yed('mybase.graphml','pteam')
    # Экспорт описания в wiki
    model.export_wiki('mybase.txt','pteam')
    
## Пример дополнительных данных для обогащения mybase_info.json    
    {
      "public": {
        "tables": {...},
        "relations": {...},
        "ghost_tables": {
          "ghost_1": {
            "name_ru": "Несуществующая таблица",
            "text": "Текстовое описание\nтаблицы"
          }
        },
        "ghost_relations": {
          "edge_1": {
            "column": "fk_col",
            "from_schema": "public",
            "from_table": "table_1",
            "to_schema": "public",
            "to_table": "table_2"
          }
        }
      }
    }