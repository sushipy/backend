# coding: utf-8
import MySQLdb

class _DataAccess:
    __db_conn = None

    def __init__(self):
        self.__connect()
        _DataAccess.__set_db_conn(self.__db_conn)

    def __connect(self):
        try:
            self.__db_conn = MySQLdb.connect(
                host='localhost',
                db='BMI22',
                user='bmi22',
                passwd='bmi22',
                charset='utf8'
            )
        except MySQLdb.Error, e:
            #ホントはちゃんと実装する
            pass

    @classmethod
    def __set_db_conn(cls, db_conn):
        cls.__db_conn = db_conn

    @classmethod
    def get_db_conn(cls):
        if not cls.__db_conn:
            data_access = _DataAccess()
        return cls.__db_conn

class Event:
    # カラムが追加されたらここに追加する
    model = [
        'id',
        'start_time',
        'end_time',
        'title',
        'room',
        'descri',
        'promotor_name',
        'promotor_mail',
        'capacity'
        ]

    def __init__(self):
        """
        コンストラクタ
        全ての変数の初期値としてNoneを設定

        """
        for column in self.model:
            self.__dict__[column] = None

    @classmethod
    def __get_cols(cls):
        columns = []
        for column in cls.model:
            columns.append(column)
        return columns

    def save(self):
        """
        DBに保存（新規はINSERT、変更はUPDATE)
        @param  self
        @return 採番or更新したID

        """
        db_conn = _DataAccess.get_db_conn()
        c = db_conn.cursor()
        columns = []
        values = []
        binds = []
        # 値の設定されているカラムを保存対象とする
        for k in filter(lambda x: self.__dict__[x], self.model):
            columns.append(k)
            values.append(self.__dict__[k])
            binds.append('%s')
        # idがなければinsert
        if not self.id:
            stmt = 'INSERT INTO event(' + ','.join(columns) + ') VALUES(' + ','.join(binds) + ')'
            c.execute(stmt,values)
            self.id = c.lastrowid
        # idがあればupdate
        else:
            buf = []
            for col in columns:
                 buf.append(col + '=%s')
            stmt = 'UPDATE event SET ' + ','.join(buf) + ' WHERE id = %s'
            values.append(self.id)
            c.execute(stmt,values)
        db_conn.commit()
        return self.id

    @classmethod
    def list(cls, criteria=None, sortkey=None, desc=False, size=None, page=1, capable=False, participate_name=None):
        """
        イベントのリストを返却
        @param  cls
        @param  criteria 検索条件の辞書{"カラム名":[{条件A},{条件B}],"カラム名2:[{条件C},{条件D}]}
                         カラム名でして以下のなものはクラス変数modelに格納されているもののみ
                         個別の検索条件は値(value)と比較演算子(operator)を含む辞書{"value":"10", "operator":"<"}
                         operatorで指定できるのは「=,>,>=,<,<=,like」
                         ex) {
                               "start_time":
                                 [
                                   {
                                     "value":"2015-01-01 00:00:00"
                                     "operator":">="
                                   },
                                   {
                                     "value":"2015-02-01 00:00:00"
                                     "operator":"<"
                                   }
                                 ],
                               "promotor_name":
                                 [
                                   {
                                     "value":"山田%"
                                     "operator":"like"
                                   }
                             }
                        検索条件はすべてAND条件で評価する
        @param  sortkey ソート対象のカラム名(default:None)
        @param  desc    ソートを降順にする場合はTrueを設定(default:False)
        @param  size    件数を制限する場合にして(default:None)
        @param  page    sizeを指定する場合に何ページ目かを指定(default:1)
        @param  capable 残席のあるイベントを検索対象とする場合はTrueを設定(default:None)
        @param  participate_name 指定した参加者が参加登録しているイベントに絞る(default:none)
        @return Eventインスタンスのリスト
        """
        db_conn = _DataAccess.get_db_conn()
        c = db_conn.cursor()
        cols = cls.__get_cols()
        _cols = map(lambda x: 'event.' + x, cols)
        stmt = 'SELECT ' + ','.join(_cols) + ' FROM event'
        where = []
        values = []
        if capable:
            stmt += ' LEFT OUTER JOIN (SELECT id,count(1) as cnt FROM participate_history GROUP BY id) p ON event.id = p.id'
            where.append('ifnull(event.capacity,0) > ifnull(p.cnt,0)')
        if participate_name:
            stmt += ', participate_history'
            where.append('event.id = participate_history.id')
            where.append('participate_history.participant_name = %s')
            values.append(participate_name)
        if criteria:
            for cdt in criteria:
                if cdt not in cls.model:
                    continue
                for cn in criteria[cdt]:
                    if cn['operator'] in ['=', '>', '<', '>=', '<=', 'like']:
                        where.append(cdt + ' '  + cn['operator'] + ' %s')
                        values.append(cn['value'])
        if where:
            stmt += ' WHERE ' + ' AND '.join(where)
        if sortkey:
            stmt += ' ORDER BY event.' + sortkey
            if desc:
                stmt += ' DESC'
        if size:
            stmt += ' LIMIT ' + str(size * (page - 1)) + ',' + str(size * page)
        if values:
            c.execute(stmt,values)
        else:
            c.execute(stmt)
        events = []
        if size:
            rows = c.fetchmany(size)
        else:
            rows = c.fetchall()
        for row in rows:
            e = Event()
            for k,v in zip(cols, row):
                e.__dict__[k] = v
            events.append(e)
        return events

    @classmethod
    def get(cls, id):
        """
        ID指定でEventインスタンスを取得
        @param  cls
        @param  id
        @return Eventインスタンス
        """
        db_conn = _DataAccess.get_db_conn()
        c = db_conn.cursor()
        cols = cls.__get_cols()
        stmt = 'SELECT ' + ','.join(cols) + ' FROM event WHERE id = %s'
        c.execute(stmt,[id])
        e = Event()
        for k,v in zip(cls.model, c.fetchone()):
                e.__dict__[k] = v
        return e

    def attend(self, name, cancel=False, force=False):
        """
        Eventに参加者を登録
        @param  self
        @param  name 参加者名
        @param  cancel キャンセル時はTrueに設定(default:False)
        @param  force 満席時にも登録処理を行う場合はTrueに設定(default:False)
        @return 処理が成功したかどうかのbool値
        """
        if not cancel and not force and not self.is_capable():
            return False
        db_conn = _DataAccess.get_db_conn()
        c = db_conn.cursor()
        if cancel:
          stmt = 'DELETE FROM participate_history WHERE id = %s AND participant_name = %s'
        else:
          stmt = 'INSERT INTO participate_history(id, participant_name) VALUES(%s,%s)'
        c.execute(stmt,[self.id, name])
        db_conn.commit()
        return True

    def list_participate(self):
        """
        参加者のリストを取得
        @param  self
        @return 参加者の一覧タプル
        """
        db_conn = _DataAccess.get_db_conn()
        c = db_conn.cursor()
        stmt = 'SELECT participant_name from participate_history where id = %s'
        c.execute(stmt, [self.id])
        ret = []
        for p in  c.fetchall():
            ret.append(p[0])
        return tuple(ret)

    def get_participate_num(self):
        """
        参加者数を取得
        @param  self
        @return 参加者数
        """
        db_conn = _DataAccess.get_db_conn()
        c = db_conn.cursor()
        stmt = 'SELECT count(1) from participate_history where id = %s'
        c.execute(stmt, [self.id])
        return c.fetchone()[0]

    @classmethod
    def list_from_now(cls, **kwargs):
        """
        まだ終わっていないイベントのリストを取得
        list()のwrapper
        """
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        c = {"operator":">","value":now}
        if 'criteria' in kwargs:
            criteria = dict(kwargs['criteria'])
            del kwargs['criteria']
            if "end_time" in criteria:
                criteria['end_time'].append(c)
            else:
                criteria['end_time'] = [c]
        else:
            criteria = {'end_time':[c]}
        return cls.list(criteria=criteria, **kwargs)

    def is_capable(self):
        """
        残席があるか判定
        @param  self
        @return bool値
        """
        if self.capacity > self.get_participate_num():
            return True
        else:
            return False

