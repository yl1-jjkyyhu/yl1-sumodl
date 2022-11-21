from os import path as ospath, makedirs
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# from bot import DB_URI, AUTHORIZED_CHATS, SUDO_USERS, AS_DOC_USERS, AS_MEDIA_USERS, rss_dict, LOGGER, botname, LEECH_LOG, PRE_DICT, LEECH_DICT, PAID_USERS, CAP_DICT, REM_DICT, SUF_DICT, CFONT_DICT
from bot import DB_URI, user_data, rss_dict, botname, LOGGER


class DbManger:
    def __init__(self):
        self.__err = False
        self.__db = None
        self.__conn = None
        self.__connect()

    def __connect(self):
        try:
            self.__conn = MongoClient(DB_URI)
            self.__db = self.__conn.mltb
        except PyMongoError as e:
            LOGGER.error(f"Error in DB connection: {e}")
            self.__err = True

    def db_load(self):
        if self.__err:
            return
        # User Data
        if self.__db.users.find_one():
            rows = self.__db.users.find({})  # return a dict ==> {_id, is_sudo, is_auth, as_media, as_doc, thumb}
            for row in rows:
                uid = row['_id']
                del row['_id']
                path = f"Thumbnails/{uid}.jpg"
                if row.get('thumb'):
                    if not ospath.exists('Thumbnails'):
                        makedirs('Thumbnails')
                    with open(path, 'wb+') as f:
                        f.write(row['thumb'])
                    row['thumb'] = True
                user_data[uid] = row
            LOGGER.info("Users data has been imported from Database")
        # Rss Data
        if self.__db.rss.find_one():
            rows = self.__db.rss.find({})  # return a dict ==> {_id, link, last_feed, last_name, filters}
            for row in rows:
                title = row['_id']
                del row['_id']
                rss_dict[title] = row
            LOGGER.info("Rss data has been imported from Database.")

    def update_user_data(self, user_id):
        if self.__err:
            return
        data = user_data[user_id]
        if data.get('thumb'):
            del data['thumb']
        self.__db.users.update_one({'_id': user_id}, {'$set': data}, upsert=True)

    def update_thumb(self, user_id, path=None):
        if self.__err:
            return
        if path is not None:
            image = open(path, 'rb+')
            image_bin = image.read()
        else:
            image_bin = False
        self.__db.users.update_one({'_id': user_id}, {'$set': {'thumb': image_bin}}, upsert=True)

    def update_prefix(self, user_id, value=None):
        if self.__err:
            return
        if value is not None:
            dbval = value
        else:
            dbval = False
        self.__db.users.update_one({'_id': user_id}, {'$set': {'prefix': dbval}}, upsert=True)

    def rss_update(self, title):
        if self.__err:
            return   
        self.__db.rss.update_one({'_id': title}, {'$set': rss_dict[title]}, upsert=True)

    def rss_delete(self, title):
        if self.__err:
            return
        self.__db.rss.delete_one({'_id': title})

    def add_incomplete_task(self, cid, link, tag):
        if self.__err:
            return
        self.__db.tasks[botname].insert_one({'_id': link, 'cid': cid, 'tag': tag})

    def rm_complete_task(self, link):
        if self.__err:
            return
        self.__db.tasks[botname].delete_one({'_id': link})

    def get_incomplete_tasks(self):
        notifier_dict = {}
        if self.__err:
            return notifier_dict
        if self.__db.tasks[botname].find_one():
            rows = self.__db.tasks[botname].find({})  # return a dict ==> {_id, cid, tag}
            for row in rows:
                if row['cid'] in list(notifier_dict.keys()):
                    if row['tag'] in list(notifier_dict[row['cid']]):
                        notifier_dict[row['cid']][row['tag']].append(row['_id'])
                    else:
                        notifier_dict[row['cid']][row['tag']] = [row['_id']]
                else:
                    usr_dict = {}
                    usr_dict[row['tag']] = [row['_id']]
                    notifier_dict[row['cid']] = usr_dict
        self.__db.tasks[botname].drop()
        return notifier_dict # return a dict ==> {cid: {tag: [_id, _id, ...]}}

    def trunc_table(self, name):
        if self.__err:
            return
        self.__db[name].drop()

    def __exit__(self):
        try:
            self.__conn.close()
        except:
            pass

if DB_URI is not None:
    DbManger().db_load()






    

#     def user_auth(self, chat_id: int):
#         if self.err:
#             return "Error in DB connection, check log for details"
#         elif not self.user_check(chat_id):
#             sql = 'INSERT INTO users (uid, auth) VALUES ({}, TRUE)'.format(chat_id)
#         else:
#             sql = 'UPDATE users SET auth = TRUE WHERE uid = {}'.format(chat_id)
#         self.cur.execute(sql)
#         self.conn.commit()
#         self.disconnect()
#         return 'Authorized successfully'

#     def user_unauth(self, chat_id: int):
#         if self.err:
#             return "Error in DB connection, check log for details"
#         elif self.user_check(chat_id):
#             sql = 'UPDATE users SET auth = FALSE WHERE uid = {}'.format(chat_id)
#             self.cur.execute(sql)
#             self.conn.commit()
#             self.disconnect()
#             return 'Unauthorized successfully'

#     def user_addsudo(self, user_id: int):
#         if self.err:
#             return "Error in DB connection, check log for details"
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (uid, sudo) VALUES ({}, TRUE)'.format(user_id)
#         else:
#             sql = 'UPDATE users SET sudo = TRUE WHERE uid = {}'.format(user_id)
#         self.cur.execute(sql)
#         self.conn.commit()
#         self.disconnect()
#         return 'Successfully Promoted as Sudo'

#     def user_rmsudo(self, user_id: int):
#         if self.err:
#             return "Error in DB connection, check log for details"
#         elif self.user_check(user_id):
#             sql = 'UPDATE users SET sudo = FALSE WHERE uid = {}'.format(user_id)
#             self.cur.execute(sql)
#             self.conn.commit()
#             self.disconnect()
#             return 'Successfully removed from Sudo'

#     def user_media(self, user_id: int):
#         if self.err:
#             return
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (uid, media) VALUES ({}, TRUE)'.format(user_id)
#         else:
#             sql = 'UPDATE users SET media = TRUE, doc = FALSE WHERE uid = {}'.format(user_id)
#         self.cur.execute(sql)
#         self.conn.commit()
#         self.disconnect()

#     def user_doc(self, user_id: int):
#         if self.err:
#             return
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (uid, doc) VALUES ({}, TRUE)'.format(user_id)
#         else:
#             sql = 'UPDATE users SET media = FALSE, doc = TRUE WHERE uid = {}'.format(user_id)
#         self.cur.execute(sql)
#         self.conn.commit()
#         self.disconnect()

#     def user_pre(self, user_id: int, user_pre):
#         if self.err:
#             return
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (pre, uid) VALUES (%s, %s)'
#         else:
#             sql = 'UPDATE users SET pre = %s WHERE uid = %s'
#         self.cur.execute(sql, (user_pre, user_id))
#         self.conn.commit()
#         self.disconnect()
        

#     def user_cfont(self, user_id: int, user_cfont):
#         if self.err:
#             return
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (cfont, uid) VALUES (%s, %s)'
#         else:
#             sql = 'UPDATE users SET cfont = %s WHERE uid = %s'
#         self.cur.execute(sql, (user_cfont, user_id))
#         self.conn.commit()
#         self.disconnect()

        
        
#     def user_suf(self, user_id: int, user_suf):
#         if self.err:
#             return
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (suf, uid) VALUES (%s, %s)'
#         else:
#             sql = 'UPDATE users SET suf = %s WHERE uid = %s'
#         self.cur.execute(sql, (user_suf, user_id))
#         self.conn.commit()
#         self.disconnect()



#     def user_cap(self, user_id: int, user_cap):
#         if self.err:
#             return
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (cap, uid) VALUES (%s, %s)'
#         else:
#             sql = 'UPDATE users SET cap = %s WHERE uid = %s'
#         self.cur.execute(sql, (user_cap, user_id))
#         self.conn.commit()
#         self.disconnect()  


#     def user_dump(self, user_id: int, user_dump):
#         if self.err:
#             return
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (dump, uid) VALUES (%s, %s)'
#         else:
#             sql = 'UPDATE users SET dump = %s WHERE uid = %s'
#         self.cur.execute(sql, (user_dump, user_id))
#         self.conn.commit()
#         self.disconnect()


#     def user_rem(self, user_id: int, user_rem):
#         if self.err:
#             return
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (rem, uid) VALUES (%s, %s)'
#         else:
#             sql = 'UPDATE users SET rem = %s WHERE uid = %s'
#         self.cur.execute(sql, (user_rem, user_id))
#         self.conn.commit()
#         self.disconnect()

#     def user_addpaid(self, user_id: int):
#         if self.err:
#             return "Error in DB connection, check log for details"
#         elif not self.user_check(user_id):
#             sql = 'INSERT INTO users (uid, paid) VALUES ({}, TRUE)'.format(user_id)
#         else:
#             sql = 'UPDATE users SET paid = TRUE WHERE uid = {}'.format(user_id)
#         self.cur.execute(sql)
#         self.conn.commit()
#         self.disconnect()
#         return 'Successfully Promoted as Paid Member'

#     def user_rmpaid(self, user_id: int):
#         if self.err:
#             return "Error in DB connection, check log for details"
#         elif self.user_check(user_id):
#             sql = 'UPDATE users SET paid = FALSE WHERE uid = {}'.format(user_id)
#             self.cur.execute(sql)
#             self.conn.commit()
#             self.disconnect()
#             return 'Successfully removed from Paid Membership'


#     def user_save_thumb(self, user_id: int, path):
#         if self.err:
#             return
#         image = open(path, 'rb+')
#         image_bin = image.read()
#         if not self.user_check(user_id):
#             sql = 'INSERT INTO users (thumb, uid) VALUES (%s, %s)'
#         else:
#             sql = 'UPDATE users SET thumb = %s WHERE uid = %s'
#         self.cur.execute(sql, (image_bin, user_id))
#         self.conn.commit()
#         self.disconnect()

#     def user_rm_thumb(self, user_id: int, path):
#         if self.err:
#             return
#         elif self.user_check(user_id):
#             sql = 'UPDATE users SET thumb = NULL WHERE uid = {}'.format(user_id)
#         self.cur.execute(sql)
#         self.conn.commit()
#         self.disconnect()

#     def addleech_log(self, chat_id: int):
#         if self.err:
#             return "Error in DB connection, check log for details"
#         elif not self.user_check(chat_id):
#             sql = 'INSERT INTO users (uid, leechlog) VALUES ({}, TRUE)'.format(chat_id)
#         else:
#             sql = 'UPDATE users SET leechlog = TRUE WHERE uid = {}'.format(chat_id)
#         self.cur.execute(sql)
#         self.conn.commit()
#         self.disconnect()
#         return 'Successfully added to leech logs'

#     def rmleech_log(self, chat_id: int):
#         if self.err:
#             return "Error in DB connection, check log for details"
#         elif self.user_check(chat_id):
#             sql = 'UPDATE users SET leechlog = FALSE WHERE uid = {}'.format(chat_id)
#             self.cur.execute(sql)
#             self.conn.commit()
#             self.disconnect()
#             return 'Removed from leech logs successfully'

#     def user_check(self, uid: int):
#         self.cur.execute("SELECT * FROM users WHERE uid = {}".format(uid))
#         res = self.cur.fetchone()
#         return res

#     def rss_add(self, name, link, last, title, filters):
#         if self.err:
#             return
#         q = (name, link, last, title, filters)
#         self.cur.execute("INSERT INTO rss (name, link, last, title, filters) VALUES (%s, %s, %s, %s, %s)", q)
#         self.conn.commit()
#         self.disconnect()

#     def rss_update(self, name, last, title):
#         if self.err:
#             return
#         q = (last, title, name)
#         self.cur.execute("UPDATE rss SET last = %s, title = %s WHERE name = %s", q)
#         self.conn.commit()
#         self.disconnect()

#     def rss_delete(self, name):
#         if self.err:
#             return
#         self.cur.execute("DELETE FROM rss WHERE name = %s", (name,))
#         self.conn.commit()
#         self.disconnect()

#     def add_incomplete_task(self, cid: int, link: str, tag: str):
#         if self.err:
#             return
#         q = (cid, link, tag)
#         self.cur.execute("INSERT INTO {} (cid, link, tag) VALUES (%s, %s, %s)".format(botname), q)
#         self.conn.commit()
#         self.disconnect()

#     def rm_complete_task(self, link: str):
#         if self.err:
#             return
#         self.cur.execute("DELETE FROM {} WHERE link = %s".format(botname), (link,))
#         self.conn.commit()
#         self.disconnect()

#     def get_incomplete_tasks(self):
#         if self.err:
#             return False
#         self.cur.execute("SELECT * from {}".format(botname))
#         rows = self.cur.fetchall()  # return a list ==> (cid, link, tag)
#         notifier_dict = {}
#         if rows:
#             for row in rows:
#                 if row[0] in list(notifier_dict.keys()):
#                     if row[2] in list(notifier_dict[row[0]].keys()):
#                         notifier_dict[row[0]][row[2]].append(row[1])
#                     else:
#                         notifier_dict[row[0]][row[2]] = [row[1]]
#                 else:
#                     usr_dict = {}
#                     usr_dict[row[2]] = [row[1]]
#                     notifier_dict[row[0]] = usr_dict
#         self.cur.execute("TRUNCATE TABLE {}".format(botname))
#         self.conn.commit()
#         self.disconnect()
#         return notifier_dict # return a dict ==> {cid: {tag: [mid, mid, ...]}}


#     def trunc_table(self, name):
#         if self.err:
#             return
#         self.cur.execute("TRUNCATE TABLE {}".format(name))
#         self.conn.commit()
#         self.disconnect()

# if DB_URI is not None:
#     DbManger().db_init()
