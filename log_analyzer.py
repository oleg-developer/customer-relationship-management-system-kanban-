from collections import defaultdict
from typing import Union, Generator, Iterable

import sqlparse.sql
import sqlparse.tokens


def is_subselect(parsed: sqlparse.sql.IdentifierList) -> bool:
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is sqlparse.tokens.DML and item.value.upper() == 'SELECT':
            return True
    return False


def extract_from_statement(statement: sqlparse.sql.Statement) -> Generator[
    Union[sqlparse.sql.Identifier, sqlparse.sql.IdentifierList],
    None,
    None
]:
    from_seen = False
    for item in statement.tokens:
        if is_subselect(item):
            yield from extract_from_statement(item)
        if from_seen:
            if item.ttype is sqlparse.tokens.Keyword:
                if item.value.upper() in ['ORDER', 'GROUP', 'BY', 'HAVING']:
                    raise StopIteration
            else:
                yield item
        elif item.ttype is sqlparse.tokens.Keyword and item.value.upper() == 'FROM':
            from_seen = True


def extract_table_identifiers(token_stream: Iterable[Union[sqlparse.sql.IdentifierList, sqlparse.sql.Identifier]]) \
        -> Generator[str, None, None]:
    for item in token_stream:
        if isinstance(item, sqlparse.sql.IdentifierList):
            for identifier in item.get_identifiers():
                yield identifier.get_name()
        elif isinstance(item, sqlparse.sql.Identifier):
            yield item.get_name()
        # It's a bug to check for Keyword here, but in the example
        # above some tables names are identified as keywords...
        elif item.ttype is sqlparse.tokens.Keyword:
            yield item.value


def extract_tables(sql: Union[str, sqlparse.sql.Statement]) -> Iterable[str]:
    stream = extract_from_statement(sqlparse.parse(sql)[0] if type(sql) is str else sql)
    return extract_table_identifiers(stream)


def log_record_mapper(statement: sqlparse.sql.Statement):
    token = statement.tokens[0]
    i = 0
    while True:
        if isinstance(token, sqlparse.sql.Comment):
            break
        i += 1
        if i < len(statement.tokens):
            token = statement.tokens[i]
        else:
            return 0, ()
    date, ms = str(token).strip()[2:].split()
    tables = extract_tables(statement)
    return float(ms), tables


def analyze_log(log_file_name="log.sql"):
    file = open(log_file_name, "r")
    statements = sqlparse.parse(file.read())
    file.close()
    stat = filter(lambda ms_tables: ms_tables[0] and ms_tables[1], map(log_record_mapper, statements))
    tables_ms = defaultdict(lambda: .0)
    tables_count = defaultdict(lambda: 0)
    for ms, itable in stat:
        itable = list(itable)
        for table in set(itable):
            tables_ms[table] += ms
        for table in itable:
            tables_count[table] += 1
    return {table: (tables_ms[table], tables_count[table]) for table in tables_ms}


if __name__ == '__main__':
    out = open("log.sql.csv", "w")
    LOGS = (
        ("1", "log.sql"),
        ("2", "./docker/rasa-board-server/log.sql"),
        ("3", "./docker/rasa-board-server-dev/log.sql"),
    )
    promt = "Log file: \n{}\n".format("\n".join(map(lambda k_v: "{}) {}".format(*k_v), LOGS)))
    log = dict(LOGS).get(input(promt), None)
    print("Processing...")
    for table, (ms, count) in sorted(
            analyze_log(log).items(),
            key=lambda t__ms_count: t__ms_count[1][0], reverse=True
    ):
        out.write("{:f};{:>d};{}\n".format(ms, count, table))
        print("{:>7.2f}\t{:>5d}\t{}".format(ms, count, table))
    out.close()
