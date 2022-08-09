import sqlite3
from hashlib import md5
from cryptography.fernet import Fernet
class Connection:
    __salt1 = -91
    __salt2 = "id6KHUjbTs".encode("utf-8")
    def __init__(self):
        self.conn = sqlite3.connect("properties/__secret_code.db")
        self.cn = self.conn.cursor()
        #创建函数
        self.conn.create_function('enc',1,self.__encode)
        self.conn.create_function('md5',1,self.enmd5)
        self.cn.execute("select * from sqlite_master where type='table'")
        self.users = list()
        #获取所有账号
        while True:
            line = self.cn.fetchone()
            if not line:
                break
            user = line[1]
            if user.startswith("code"):
                self.users.append(user[4:])
    def add_user(self,name,code,questions):
        if name in self.users:
            raise Exception("账号名已存在")
        if name == "":
            raise Exception("账号名不能为空")
        if len(questions) != 3:
            raise Exception("问题必须是三个")
        #创建账号
        self.cn.execute("""create table code{}(
                    _id integer primary key autoincrement,
                    name text,
                    user text,
                    pass text)""".format(name))
        self.users.append(name)
        cipher_key = Fernet.generate_key()
        #设置密码
        self.cn.execute("insert into code{} values(null,?,?,md5(?))"\
                        .format(name),("",cipher_key.decode("utf-8"),code))
        #设置问题
        for question in questions:
            self.cn.execute("insert into code{} values(null,?,?,md5(?))"\
                        .format(name),("",question[0],question[1]))
        self.conn.commit()
        #登录账号
        self.login(name,code)
    def __decode(self,code):
        return self.mainuserFernet.decrypt(code.encode("utf-8"))\
               .decode("utf-8")
    def __encode(self,string):
        return self.mainuserFernet.encrypt(string.encode("utf-8"))\
               .decode("utf-8")
    @classmethod
    def enmd5(cls,string):
        obj = md5()
        obj.update(string.encode("utf-8"))
        obj.update(cls.__salt2)
        return obj.hexdigest()
    def getusers(self):
        return self.users.copy()
    def get_questions(self,user_name):
        if user_name not in self.users:
            raise Exception("没有该账户")
        questions = list()
        for i in range(3):
            self.cn.execute("select * from code{} where _id=?"\
                            .format(user_name),(i+2,))
            questions.append(self.cn.fetchone()[2])
        return questions
    #用于登录账户的方法
    def login(self,user_name,user_code):
        if user_name not in self.users:
            raise Exception("没有该账户")
        self.cn.execute("select * from code{} where _id=?"\
                            .format(user_name),(1,))
        attrs = self.cn.fetchone()
        if attrs[3] == self.enmd5(user_code):
            self.main_user = user_name
            self.mainuserFernet = Fernet(attrs[2])
            self.names = list()
            self.cn.execute("select * from code{} where _id>?"\
                            .format(self.main_user),(4,))
            while True:
                line = self.cn.fetchone()
                if not line:
                    break
                self.names.append(line[1])
            return True
        else:
            return False
    #忘记密码
    def login_by_answers(self,user_name,answers,new_code):
        if user_name not in self.users:
            raise Exception("没有该账户")
        if len(answers) != 3:
            raise Exception("答案必须是三个")
        for i in range(3):
            self.cn.execute("select * from code{} where _id=?"\
                            .format(user_name),(i+2,))
            if self.cn.fetchone()[3] != self.enmd5(answers[i]):
                return i+1
        self.cn.execute("select * from code{} where _id=?"\
                            .format(user_name),(1,))
        attrs = self.cn.fetchone()
        self.main_user = user_name
        self.mainuserFernet = Fernet(attrs[2])
        self.names = list()
        self.cn.execute("select * from code{} where _id>?"\
                            .format(self.main_user),(4,))
        while True:
            line = self.cn.fetchone()
            if not line:
                break
            self.names.append(line[1])
        self.change(new_code)
        return 0
    #修改登录进的账户的密码的方法
    def change(self,new_code):
        self.cn.execute("update code{} set pass=md5(?) where _id=?"\
                        .format(self.main_user),(new_code,1))
        self.conn.commit()
    def have_logined(self):
        if not hasattr(self,"main_user"):
            raise Exception("您还未登录")
    def getnames(self):
        return self.names.copy()
    def insert(self,line):
        self.have_logined()
        if line[0] in self.names or line[0] == "":
            return False
        self.cn.execute("insert into code{} values(null,?,?,enc(?))"\
                        .format(self.main_user),line)
        self.names.append(line[0])
        self.conn.commit()
        return True
    def update(self,line):
        self.have_logined()
        if line[0] not in self.names:
            return False
        self.cn.execute("update code{} set user=?,pass=enc(?) where name=?"\
                        .format(self.main_user),(line[1],line[2],line[0]))
        self.conn.commit()
        return True
    def select(self,name):
        self.have_logined()
        if name not in self.names:
            return None
        self.cn.execute("select * from code{} where name=?"\
                        .format(self.main_user),(name,))
        result = list(self.cn.fetchone()[2:])
        result[1] = self.__decode(result[1])
        return result
    def delete(self,name):
        self.have_logined()
        if name not in self.names:
            return False
        self.cn.execute("delete from code{} where name=?"\
                        .format(self.main_user),(name,))
        self.conn.commit()
        self.names.remove(name)
        return True
    def set_questions(self,questions):
        self.have_logined()
        if len(questions) != 3:
            raise Exception("问题必须是三个")
        for i in range(3):
            self.cn.execute("update code{} set user=?,pass=md5(?) where _id=?"\
                        .format(self.main_user),\
                        (questions[i][0],questions[i][1],i+2))
        self.conn.commit()
    def close(self):
        self.cn.close()
        self.conn.close()
    def __del__(self):
        self.close()
