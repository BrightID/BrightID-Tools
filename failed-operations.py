import time, datetime
from arango import ArangoClient

def check(f, t):
    f = time.mktime(datetime.datetime.strptime(f, "%Y/%m/%d").timetuple())*1000
    t = time.mktime(datetime.datetime.strptime(t, "%Y/%m/%d").timetuple())*1000
    db = ArangoClient().db('_system')
    cursor = db.aql.execute(
      '''FOR op IN operations
            FILTER
                op.state == "failed" AND
                op.timestamp > @f AND
                op.timestamp < @t
            SORT op.timestamp
            RETURN op
        ''',
        bind_vars={'f': f, 't': t}
    )

    for op in cursor:
        t = op['timestamp'] / 1000
        t = time.strftime('%Y/%m/%d', time.localtime(t))
        print(f'{t}\t{op["result"]}\t{op}')

if __name__ == '__main__':
    check('2020/01/01', '2021/01/01')
