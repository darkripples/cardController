# coding:utf8
# V1.0   2015/5/24 10:25  by fls

from conf import configs

DB_TYPE = configs.DB_TYPE

USE_TIMES = 10
import re
import threading, _thread
from .attrdict import AttrDict
from .fmt_utils import formatter

import psycopg2 as db2api


class Dummy:
    pass


if db2api.threadsafety == 0:
    DB_POOL = Dummy()
else:
    DB_POOL = Dummy()  # threading.local()
LOCKED = threading.local()  # 用于标记线程是否已申请数据库
# thread_not_safe_lock = threading.Lock()
operator_lock = threading.Lock()


def get():
    global DB_POOL
    with operator_lock:
        if not hasattr(DB_POOL, 'lock'):
            DB_POOL.lock = threading.Lock()

    if getattr(LOCKED, 'locked', False):
        # 在同一线程中是不应该重复请求连接的
        raise RuntimeError("同一线程[%s]中不应该重复申请连接，代码有错误，请查找" % _thread.get_ident())

    DB_POOL.lock.acquire()  # 锁定当前请求，直到连接可用
    LOCKED.locked = True

    if getattr(DB_POOL, 'conn', None) is None:
        DB_POOL.conn = None
        DB_POOL.use_times = 0  # 为了避免创建数据库连接失败导致的put异常
        try:
            DB_POOL.conn = db2api.connect(database=configs.DBNAME, user=configs.USER,
                                          password=configs.PWD, host=configs.HOST, port=configs.PORT)

            DB_POOL.use_times = USE_TIMES or 10  # 若未设置，则按10次
        except:
            # 创建连接失败，应恢复线程状态
            put()
            import traceback2
            traceback2.print_exc()
            # raise
    else:
        # 超过28800s不使用数据库连接，mysql会报错，可采用ping重新连接的方式应用
        if DB_TYPE == 'mysql':
            DB_POOL.conn.ping(reconnect=True)
    DB_POOL.use_times -= 1
    return DB_POOL.conn


def put():
    global DB_POOL
    try:
        if DB_POOL.use_times <= 0:  # 使用次数结束
            if DB_POOL.conn:
                try:
                    DB_POOL.conn.close()
                except:
                    pass  # 关闭不成功则丢弃
                DB_POOL.conn = None
    finally:
        LOCKED.locked = False
        # if db2api.threadsafety == 0:
        #    thread_not_safe_lock.release()
        DB_POOL.lock.release()  # 释放线程级锁


class DBConnection(object):
    def __init__(self):
        self.con = get()
        self.cursors = []

    def cursor(self):
        return self.cursors[0] if len(self.cursors) else self.con.cursor()

    def has_table(self, tname, schema=None):
        """
        检查时直接连接数据库select，没有异常就说明存在，有异常就说明表不存在
        """
        cur = self.cursor()
        rs = bool(0)
        if DB_TYPE == 'postgresql':
            if schema is None:
                cur.execute(
                    """select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname=current_schema() and lower(relname)=%(name)s""",
                    {'name': tname.lower()});
            else:
                cur.execute(
                    """select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname=%(schema)s and lower(relname)=%(name)s""",
                    {'name': tname.lower(), 'schema': schema});
            rs = bool(cur.rowcount)
        elif DB_TYPE == 'oracle':
            try:
                # 这里是因为oracle的处理方式同postgresql不一样，直接使用查询比较简单
                cur.execute("""select * from %(name)s where rownum = 1""" % {
                    'name': (tname if schema is None else '%s.%s' % (schema, tname))})
                rs = bool(1)
            except:
                rs = bool(0)
        else:
            try:
                cur.execute("""select count(0) from %(name)s """ % {
                    'name': (tname if schema is None else '%s.%s' % (schema, tname))})
                rs = bool(1)
            except:
                rs = bool(0)
        return rs

    def execute(self, sql, params=None):
        cur = self.cursor()
        # 去掉开头的注释
        sql = re.sub(r'^\s*--.*', '', sql)
        kind = sql.strip()[:6].lower()
        if type(params) in (tuple, list):
            if len(params) and type(params[0]) in (tuple, list, dict):
                cur.executemany(sql, params)
                return cur
            if kind != 'select':
                cur.execute(sql, params)
                return cur
        elif type(params) in (dict,):
            if kind != 'select':
                cur.execute(sql, params)
                return cur
        else:
            if kind != 'select':
                cur.execute(sql)
                return cur
            # 剩下的全是查询
        return sql_execute(cur, sql, params)

    #    函数 execute_sql
    #        参数：  sql 字符串 可以直接执行的sql语句
    #        返回值：类对象列表
    #        功能描述：
    #            执行sql语句，并组织一个类对象列表返回
    #            select类型的直接返回处理后的数据集
    #            非select类型的返回被转换为类对象的[{'rs':0}]
    def execute_sql(self, sql, params={}, dicorobj="class", hump=True, page=None, limit=10):
        # 直接执行sql，不传入参数，不管是select还是insert都提供一个列表字典的返回值
        # 非select类的返回[{'rs':0}]
        cur = self.cursor()
        # 去掉开头的注释
        sql = re.sub(r'^\s*--.*', '', sql)

        # 找出所有的占位
        params_find = re.findall(r'%\(\s*(.+?)\s*\)s', sql)
        # 去掉多余的键值对
        params_removed = {k: v for k, v in params.items() if k not in params_find}
        if params_removed:
            print('SQL参数已去掉多余的键值-->', params_removed)
        params = {k: v for k, v in params.items() if k in params_find}

        if DB_TYPE == 'oracle':
            # 替换SQL百分号为冒号形式：%( id )s, %( ywbm)s --> :id, :ywbm
            sql = re.sub(r'%\(\s*(.+?)\s*\)s', r':\1', sql)

        kind = sql.strip()[:6].lower()
        if kind != 'select':
            if params and isinstance(params, dict):
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            rs = [{'rs': 0}]
        else:
            # 剩下的全是查询
            sql_page = ""
            if page != None:
                sql_page = " limit {0} offset {1}".format(limit, (int(page) - 1) * int(limit))
            rs = sql_execute(cur, sql + sql_page, params, hump=hump)
            rs = rs.fetchall()

        if dicorobj == "dict":
            return rs
        elif dicorobj == "class":
            # 返回时提供类对象，不是字典
            return [AttrDict(tk) for tk in rs]
        else:
            return rs

    def rollback(self):
        # 抛异常后，应清理数据库连接，避免该线程下的数据库操作一直异常
        global DB_POOL
        DB_POOL.use_times = 0
        try:
            self.con.rollback()
        except:
            pass  # rollback的异常不予处理

    def commit(self):
        self.con.commit()

    def _close(self):
        try:
            list(map(lambda x: x.close(), self.cursors))
        except:
            # 任何异常都应该导致数据库连接重置
            global DB_POOL
            DB_POOL.use_times = 0
        put()


def connect():
    return DBConnection()


from contextlib import contextmanager


@contextmanager
def connection():
    """
    用在with语句中，用于提供数据库连接对象。线程安全
    用法：
        with connection() as con:
            cur = con.cursor()
            cur.execute( "select * from gl_jddy where mc = '银联'" )
            rs = cur.fetchone()
            ...
    """
    con = None
    try:
        con = DBConnection()
        yield con
        con.commit()
    except:
        if con:
            con.rollback()
        raise
    finally:
        if con:
            con._close()


def sql_execute(cur, sql, params=None, encoding=None, hump=True):
    return ResultSet(cur, sql, params, encoding, hump)


class ResultSet(object):
    """
        将cur的select返回结果转换为可按字段名称访问的格式
    """

    def __init__(self, cur, sql, params=None, encoding=None, hump=True):
        """
            @param:cur   数据库引擎
            @param:sql   sql语句  变量用%s或%d的形式代替  例如:select * from gl_hydy where hydm ='%s' and jgdm =%d
            @param:params   参数列表(数据类型为列表),sql语句所需要的参数顺序组成的列表,接上面的例子,参数列表为: ['admin' ,10]
            @param:encoding  编码形式
        """
        self.__cursor = cur
        self.fields = {}
        self.encoding = encoding
        self.hump = hump
        try:
            if params:
                self.__cursor.execute(sql.encode(encoding) if encoding else sql, params)
            else:
                self.__cursor.execute(sql.encode(encoding) if encoding else sql)
            if self.__cursor.description == None:
                return
        except:
            raise
        for i in range(0, len(self.__cursor.description)):
            self.fields[self.__cursor.description[i][0].lower()] = i
        self.row_cache = []

    @property
    def rowcount(self):
        """
            返回sql结果记录条数
        """
        self.fetchall()
        return self.__cursor.rowcount

    def printFieldName(self):
        """
            打印查询结果各字段的字段名
        """
        for i in self.fields.keys():
            print(i)

    def next(self):
        """
            顺序取下一条记录，直到取尽
        """
        if not self.row_cache:
            self.row_cache = self.__cursor.fetchmany(100)
        if self.row_cache:
            if DB_TYPE == 'mysql':
                self.row_cache = list(self.row_cache)
            self.item = self.row_cache.pop(0)
        else:
            self.item = None

        return self if self.item is not None else None

    fetchone = next

    def __iter__(self):
        while self.next():
            yield self

    def fetchall(self):
        """
            取所有数据
        """
        rows = []
        while self.next():
            rows.append(self.to_dict())
        return rows

    def getValue(self, key):
        """
            获取某个字段的值，是什么类型就返回什么类型
        """
        if isinstance(key, int):
            v = self.item[key]
        else:
            idx = self.fields[key.lower()]
            v = self.item[idx]
        return v

    def to_dict(self):
        """
            将查询结果转化成字典的形式，键为字段名，实际值
        """
        d = {}
        for key, i in self.fields.items():
            if self.hump:
                d[formatter(key)] = self.item[i]
            else:
                d[key] = self.item[i]
        return d

    def __getitem__(self, key):
        """
            获取某个字段的值
        """
        return self.getValue(key)

    def __getattr__(self, key):
        return self.getValue(key)

    def close(self):
        try:
            self.__cursor.close()
        except:
            pass


def dbbinary(s):
    """
    用于pgsql的Binary对象生成函数
    """
    return db2api.Binary(s)
