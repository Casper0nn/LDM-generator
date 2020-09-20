# Вспомогательный модуль, достает информацию о структуре данных из postgresql
# Оогащает её дополнительными данными
# Рисует структуру базы по обогащенным данным
import psycopg2, copy, json, os.path, yedraw, datetime


class LDM:
    def __init__(self):
        """ """
        self.model = {}
        self.info = {}

    def select_from_postgres(self, connection_str):
        """
        Получает модель данных из всех схем в БД postgres кроме служебных
        :param connection_str:строка с параметрами для коннекта см. https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
        :return: структура с перечнем таблиц и связей в данной БД
        """
        self.model = {}
        conn = psycopg2.connect(connection_str)
        with conn:
            with conn.cursor() as cur:
                # селектим список полей, в запросе вытаскиваются только таблицы
                cur.execute("""SELECT
        n.nspname,
        c.relname::varchar AS tab_name,
        a.attnum::integer,
        a.attname::varchar AS field,
        t.typname::varchar AS type,
        a.attnotnull::boolean AS isnotnull,
        (SELECT 't'::boolean
         FROM pg_index
         WHERE c.oid = pg_index.indrelid
           AND pg_index.indkey[0] = a.attnum
           AND pg_index.indisprimary = 't'
        ) AS pri,
        (SELECT pg_attrdef.adsrc::varchar
         FROM pg_attrdef
         WHERE c.oid = pg_attrdef.adrelid AND pg_attrdef.adnum=a.attnum
        ) AS default_adsrc,
        (SELECT pg_description.description::varchar
         FROM pg_description WHERE pg_description.objoid = c.oid AND a.attnum = pg_description.objsubid
        ) AS comment
    FROM pg_attribute a, pg_class c, pg_type t, pg_namespace n
    WHERE
            n.nspname <> 'information_schema' AND n.nspname <> 'pg_catalog' AND n.nspname <> 'pg_toast'
      AND c.relname <> 'databasechangeloglock' AND c.relname<>'databasechangelog' AND c.relname <>'databasechangeloglock_pkey'
    --  AND ins.table_name is not null
        AND
      a.attnum > 0
    AND c.relkind in ('r','c','t') --r = ordinary table, i = index, S = sequence, v = view, c = composite type, s = special, t = TOAST table
      AND a.attrelid = c.oid
      AND a.atttypid = t.oid
      AND n.oid = c.relnamespace
    ORDER BY  c.relname, a.attnum""")
                for row in cur:
                    tab_schema = row[0]
                    tab_name = row[1]
                    attnum = row[2]
                    attname = row[3]
                    typname = row[4]
                    attnotnull = row[5]
                    pri = row[6]
                    default_adsrc = row[7]
                    comment = row[8]
                    if tab_schema not in self.model:
                        self.model[tab_schema] = {"tables": {}, "relations": {}}
                    if tab_name not in self.model[tab_schema]["tables"]:
                        self.model[tab_schema]["tables"][tab_name] = {'columns': {}}

                    self.model[tab_schema]["tables"][tab_name]['columns'][attname] = {}
                    self.model[tab_schema]["tables"][tab_name]['columns'][attname]['n'] = attnum
                    self.model[tab_schema]["tables"][tab_name]['columns'][attname]['type'] = typname
                    self.model[tab_schema]["tables"][tab_name]['columns'][attname]['notnull'] = attnotnull
                    self.model[tab_schema]["tables"][tab_name]['columns'][attname]['pk'] = pri
                    self.model[tab_schema]["tables"][tab_name]['columns'][attname]['comment'] = comment
                # селектим внешние ключи
                cur.execute("""SELECT
        tc.table_schema,
        tc.constraint_name,
        tc.table_name,
        kcu.column_name,
        ccu.table_schema AS foreign_table_schema,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM
        information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                 ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                 ON ccu.constraint_name = tc.constraint_name
                     AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'""")
                for row in cur:
                    table_schema = row[0]
                    constraint_name = row[1]
                    table_name = row[2]
                    column_name = row[3]
                    foreign_table_schema = row[4]
                    foreign_table_name = row[5]
                    foreign_column_name = row[6]
                    self.model[tab_schema]["relations"][constraint_name] = {}
                    self.model[tab_schema]["relations"][constraint_name]["column"] = column_name
                    self.model[tab_schema]["relations"][constraint_name]["from_schema"] = table_schema
                    self.model[tab_schema]["relations"][constraint_name]["from_table"] = table_name
                    self.model[tab_schema]["relations"][constraint_name]["to_schema"] = foreign_table_schema
                    self.model[tab_schema]["relations"][constraint_name]["to_table"] = foreign_table_name
        return self.model

    def save(self, path):
        """
        Сохраняет модель в JSON файл
        :param path:путь к файлу
        :return: None
        """
        with open(path, "w", encoding="utf-8") as write_file:
            json.dump(self.model, write_file, ensure_ascii=False)

    def load(self, path):
        """
        Загружает модель из JSON файла
        :param path:путь к файлу
        :return: None
        """
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                self.model = json.load(file)

    def load_info(self, path):
        """
        Загружает дополнительные данные из JSON файла 
        :param path:путь к файлу
        :return: None
        """

    def enrich(self, path, refresh=True):
        """
        Обогащает модель данными из информационного файла (дополнительные связи, дополнительные таблицы, локализация и бизнес-наименования)
        Предварительно модель данных должна быть получена из БД (например при помощи collect_from_postgres) или загружена из файла (load)
        :param path: JSON файл с дополнительной информацией
        :param refresh: флаг необходимости обновить файл, добавив в него пометки по удаленным и новым таблицам и их атрибутам
        :return: сводные данные для дальнейшей обработки
        """
        # получаем данные
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                self.info = json.load(file)
        # обогащаем
        for iscm in self.model:
            if iscm in self.info:  # в метаданных есть нужная схема
                for itable in self.model[iscm]["tables"]:
                    if itable in self.info[iscm]["tables"]:  # есть таблица
                        if 'info' in self.info[iscm]["tables"][itable]:
                            self.model[iscm]["tables"][itable]['info'] = self.info[iscm]["tables"][itable]['info']
                        if 'name_ru' in self.info[iscm]["tables"][itable]:
                            self.model[iscm]["tables"][itable]['name_ru'] = self.info[iscm]["tables"][itable]['name_ru']
                        if 'ghost_rel' in self.info[iscm]["tables"][itable]:
                            self.model[iscm]["tables"][itable]['ghost_rel'] = self.info[iscm]["tables"][itable][
                                'ghost_rel']
                        for iattr in self.model[iscm]["tables"][itable]['columns']:
                            if iattr in self.info[iscm]["tables"][itable]['columns']:  # есть атрибут
                                if 'name_ru' in self.info[iscm]["tables"][itable]['columns'][iattr]:
                                    self.model[iscm]["tables"][itable]['columns'][iattr]['name_ru'] = \
                                        self.info[iscm]["tables"][itable]['columns'][iattr]['name_ru']
                                if 'dsc' in self.info[iscm]["tables"][itable]['columns'][iattr]:
                                    self.model[iscm]["tables"][itable]['columns'][iattr]['dsc'] = \
                                        self.info[iscm]["tables"][itable]['columns'][iattr]['dsc']
            if 'ghost_tables' in self.info[iscm]:
                self.model[iscm]['ghost_tables'] = copy.deepcopy(self.info[iscm]['ghost_tables'])
            if 'ghost_relations' in self.info[iscm]:
                self.model[iscm]['ghost_relations'] = copy.deepcopy(self.info[iscm]['ghost_relations'])
        # обновляем метаданные
        if refresh:
            self.refresh_info(path)

    def refresh_info(self, path):
        """
        Перезаписывает JSON файл с информацией, сохраняя данные о удаленных и новых таблицах и их атрибутах
        Предварительно должна быть выполнена функция enrich
        :param path:путь к файлу
        :return: None
        """
        # сначала обходим все схемы, таблицы и атрибуты в info и помечаем их как удаленные
        for iscm in self.info:
            self.info[iscm]['DELETED'] = True
            for itable in self.info[iscm]["tables"]:
                self.info[iscm]["tables"][itable]['DELETED'] = True
                for iattr in self.info[iscm]["tables"][itable]['columns']:
                    self.info[iscm]["tables"][itable]['columns'][iattr]['DELETED'] = True
        # теперь бежим по модели и снимаем флаг удаления в info и добавляем новые схемы, таблицы и иатрибуты
        for iscm in self.model:
            if iscm in self.info:  # в метаданных есть нужная схема
                self.info[iscm].pop('DELETED', None)
            else:
                self.info[iscm] = {"tables": {}, "relations": {}}
            for itable in self.model[iscm]["tables"]:
                if itable in self.info[iscm]["tables"]:
                    self.info[iscm]["tables"][itable].pop('DELETED', None)
                    if 'name_ru' not in self.info[iscm]["tables"][itable]:
                        self.info[iscm]["tables"][itable]['name_ru'] = ''
                    if 'info' not in self.info[iscm]["tables"][itable]:
                        self.info[iscm]["tables"][itable]['info'] = ''
                else:
                    self.info[iscm]["tables"][itable] = {'name_ru': '', 'info': '', 'columns': {}}
                for iattr in self.model[iscm]["tables"][itable]['columns']:
                    if iattr in self.info[iscm]["tables"][itable]['columns']:
                        self.info[iscm]["tables"][itable]['columns'][iattr].pop('DELETED', None)
                    else:
                        self.info[iscm]["tables"][itable]['columns'][iattr] = {}
                        self.info[iscm]["tables"][itable]['columns'][iattr]['name_ru'] = ''
                        self.info[iscm]["tables"][itable]['columns'][iattr]['info'] = ''
                        # скидываем обновленные данные на диск
        with open(path, "w", encoding="utf-8") as write_file:
            json.dump(self.info, write_file, ensure_ascii=False)

    def export_yed(self, path, dbname=''):
        """
        Сохраняет модель в виде графа в формате .graphml, после создания нужно открыть файл в yEd и расставить таблицы. 
        Проще всего делать расстановку автоматически через меню Layout.
        :param path: путь для сохранения файла (.graphml)
        :param dbname: опционально имя базы, если указано, то добавляется как префикс к именам таблиц и схем
        :return:
        """
        GHOST_NODE_STYLE = {"Fill": {"color": "#C0C0C0", "color2": "#C0C0C0"}, "BorderStyle": {"type": "dashed"},
                            "NodeLabel": {"backgroundColor": "#C0C0C0"}}
        yed_file = yedraw.YedFile()
        for iscm in self.model:
            if dbname != '':
                yed_file.add_group(dbname + '.' + iscm, dbname + '.' + iscm)
            else:
                yed_file.add_group(iscm, iscm)
            for itable in self.model[iscm]["tables"]:
                text = ''
                # TODO добавить сортировку в json
                sorted_attr = sorted(self.model[iscm]["tables"][itable]['columns'].items(), key=lambda x: x[1]['n'])
                flag_change = False
                for iattr, attr in sorted_attr:
                    if attr['name_ru'] == '':
                        text += iattr
                        flag_change = True  # в таблице есть неописанные атрибуты
                    else:
                        text += attr['name_ru']
                    text += ':' + attr['type']
                    if attr['pk']:
                        text += ' (PK)'
                    if not attr['notnull']:
                        text += ' [0..1]'
                    text += '\n'
                if 'name_ru' in self.model[iscm]["tables"][itable] and self.model[iscm]["tables"][itable][
                    'name_ru'] != '':
                    label = itable + '\n' + self.model[iscm]["tables"][itable]['name_ru']
                    flag_new = False
                else:
                    label = itable
                    flag_new = True
                if dbname != '':
                    node_id = dbname + '.' + iscm + '.' + itable
                    yed_file.add_node(node_id, label, text, group=dbname + '.' + iscm)
                else:
                    node_id = iscm + '.' + itable
                    yed_file.add_node(node_id, label, text, group=iscm)
                # перекрашиваем
                if "DELETED" in self.model[iscm]["tables"][itable]:  # удаленная таблица
                    yed_file.change_node_style(node_id, {"Fill": {"color": "#ffffff", "color2": "#ffffff"},
                                                         "NodeLabel": {"backgroundColor": "#ff0000"}})
                elif flag_new:  # новая таблица
                    yed_file.change_node_style(node_id, {"Fill": {"color": "#ffcc99", "color2": "#ffcc99"},
                                                         "NodeLabel": {"backgroundColor": "#ffcc99"}})
                elif flag_change:  # изменения в атрибутах
                    # print('node_id',node_id)
                    # yed_file.save('error.graphml')
                    yed_file.change_node_style(node_id, {"Fill": {"color": "#ffcc99", "color2": "#ffcc99"}})

            for iedge, edge in self.model[iscm]["relations"].items():
                if dbname != '':
                    yed_file.add_edge(dbname + '.' + edge['from_schema'] + '.' + edge['from_table'],
                                      dbname + '.' + edge['to_schema'] + '.' + edge['to_table'])
                else:
                    yed_file.add_edge(edge['from_schema'] + '.' + edge['from_table'],
                                      edge['to_schema'] + '.' + edge['to_table'])

            # добавляем несуществующие объекты
            if 'ghost_tables' in self.model[iscm]:
                for itable in self.model[iscm]["ghost_tables"]:
                    label = self.model[iscm]["ghost_tables"][itable]["name_ru"]
                    text = self.model[iscm]["ghost_tables"][itable]["text"]
                    if dbname != '':
                        yed_file.add_node(dbname + '.' + iscm + '.' + itable, label, text, group=dbname + '.' + iscm,
                                          style=GHOST_NODE_STYLE)
                    else:
                        yed_file.add_node(iscm + '.' + itable, label, text, group=iscm, style=GHOST_NODE_STYLE)

        for iscm in self.model:
            # добавляем несуществующие связи из общего описания
            if 'ghost_relations' in self.model[iscm]:
                for iedge, edge in self.model[iscm]["ghost_relations"].items():
                    if dbname != '':
                        yed_file.add_edge(dbname + '.' + edge['from_schema'] + '.' + edge['from_table'],
                                          dbname + '.' + edge['to_schema'] + '.' + edge['to_table'], line_type='dashed')
                    else:
                        yed_file.add_edge(edge['from_schema'] + '.' + edge['from_table'],
                                          edge['to_schema'] + '.' + edge['to_table'], line_type='dashed')
            # добавляем несуществующие связи - новый вариант (из описаний таблицы)
            for itable in self.model[iscm]["tables"]:
                if "ghost_rel" in self.model[iscm]["tables"][itable]:
                    for ghost_rel_item in self.model[iscm]["tables"][itable]["ghost_rel"]:
                        if "schema" in ghost_rel_item:
                            scm = ghost_rel_item["schema"]
                        else:
                            scm = iscm
                        if dbname != '':
                            yed_file.add_edge(dbname + '.' + iscm + '.' + itable,
                                              dbname + '.' + scm + '.' + ghost_rel_item["table"], line_type='dashed')
                        else:
                            yed_file.add_edge(iscm + '.' + itable,
                                              scm + '.' + ghost_rel_item["table"], line_type='dashed')
        yed_file.save(path)

    def export_wiki(self, path, dbname=''):
        """
        Сохраняет модель в виде файла с разметкой для wiki.
        :param path: путь для сохранения файла (.txt)
        :param dbname: опционально имя базы, если указано, то добавляется как префикс к именам таблиц и схем
        :return:
        """
        conf_base = 'Внимание! Содержимое данной страницы создано автоматически, все ручные исправления будут стерты при следующей генерации. Для внесения изменений обратитесь к архитекторам.' + '\n'
        conf_base += 'Дата последнего обновления: ' + datetime.datetime.now().strftime("%d-%m-%Y") + '\n'
        conf_base += 'h1. База ' + dbname + "\n"
        for i_scm in self.model:
            conf_base += "h2. Схема " + i_scm + "\n"

            for i_tab in self.model[i_scm]['tables']:
                if 'name_ru' in self.model[i_scm]['tables'][i_tab] and self.model[i_scm]['tables'][i_tab][
                    "name_ru"] != "":
                    conf_base += "h3. Таблица " + i_tab + " (" + self.model[i_scm]['tables'][i_tab]["name_ru"] + ")\n"
                else:
                    conf_base += "h3. Таблица " + i_tab + "\n"
                if 'info' in self.model[i_scm]['tables'][i_tab] and self.model[i_scm]['tables'][i_tab]["info"] != "":
                    conf_base += self.model[i_scm]['tables'][i_tab]["info"] + "\n"
                conf_base += "||Системное имя||Имя||Тип||Кратность||Описание||PK||\n"
                for i_col in self.model[i_scm]['tables'][i_tab]['columns']:
                    col = self.model[i_scm]['tables'][i_tab]['columns'][i_col]
                    conf_base += '|' + i_col + '|'
                    if 'name_ru' in col and col["name_ru"] != "":
                        conf_base += col["name_ru"] + '|'
                    else:
                        conf_base += ' |'
                    conf_base += col["type"] + '|'
                    if col["notnull"]:
                        conf_base += "1|"
                    else:
                        conf_base += "0..1|"
                    if 'comment' in col and col["comment"] != "" and col["comment"] is not None:
                        conf_base += col["comment"] + '|'
                    else:
                        conf_base += ' |'
                    if col["pk"]:
                        conf_base += "PK|"
                    else:
                        conf_base += " |"
                    conf_base += "\n"
            f = open(path, 'w')
            f.write(conf_base)
            f.close()
