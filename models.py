import mysql.connector
from datetime import datetime
from flask import flash
import pymysql

class DBManager:
    def __init__(self):
        # MySQL 데이터베이스 연결
        self.connection = None
        self.cursor = None
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
            host='10.0.66.20',
            user='sejong',
            password='1234',
            database='board_db2'
            )
            self.cursor = self.connection.cursor(dictionary=True)
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS `posts` (
                                `id` INT(11) NOT NULL AUTO_INCREMENT,
                                `title` VARCHAR(200) NOT NULL,
                                `content` TEXT NOT NULL,
                                `filename` VARCHAR(255) DEFAULT NULL,
                                `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
                                `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
                                `views` INT(11) DEFAULT 0,
                                `userid` VARCHAR(255) NOT NULL,
                                `username` VARCHAR(255) NOT NULL,
                                PRIMARY KEY (`id`)
                                )
                                """)
            self.cursor.execute("""
                                CREATE TABLE IF NOT EXISTS `users` (
                                `idx` INT(11) NOT NULL AUTO_INCREMENT,
                                `name` VARCHAR(255) NOT NULL,
                                `id` VARCHAR(255) NOT NULL,
                                `password` VARCHAR(255) NOT NULL,
                                `user_ip` VARCHAR(45) NOT NULL,
                                `reg_date` DATETIME DEFAULT CURRENT_TIMESTAMP(),
                                PRIMARY KEY (`idx`)
                                ) 
                                """)
            
        except mysql.connector.Error as error:
            print(f"데이터베이스 연결 실패: {error}")
            
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
#--------------------------기본값으로 설정--------------------------------★    
    def get_all_posts(self):
        try:
            self.connect()
            sql = f"SELECT * FROM posts order by views desc"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"게시글 조회 실패: {error}")
            return []
        finally:
            self.disconnect()
            
    def insert_post(self, title, content, filename, userid, username):
        try:
            self.connect()
            sql = f"INSERT INTO posts (title, content, filename, created_at, userid, username) values (%s, %s, %s, %s, %s, %s)"
            values = (title, content, filename, datetime.now(), userid, username)  # 튜플형태
            self.cursor.execute(sql, values)
            
            '''
            ##  executemany() : list로 묶어서 한번에 입력 가능
            values = [(title, content, filename, datetime.now().date().strftime('%Y-%m-%d')),(title, content, filename, datetime.now().date().strftime('%Y-%m-%d'))]
            self.cursor.executemany(sql, values)
            '''
            
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시글 추가 실패: {error}")
            return False
        finally:
            self.disconnect()
            
    def get_post_by_id(self, id):
        try:
            self.connect()
            sql = f"SELECT * FROM posts WHERE id = %s"
            value = (id,) # 튜플에 값이 한개만 들어갈때 ,해줘야됨 
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"데이터베이스 연결 실패: {error}")
            return None
        finally:
            self.disconnect()
            
    def update_post(self, id, title, content, filename):
        try:
            self.connect()
            if filename:
                sql = f"UPDATE posts SET title = %s, content =%s, filename= %s WHERE id =%s"
                values = (title, content, filename, id)  # 튜플형태
            else:
                sql = f"UPDATE posts SET title = %s, content =%s WHERE id =%s"
                values = (title, content, id)  # 튜플형태
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            self.connection.rollback()
            print(f"게시글 정보 수정 실패: {error}")
            return False
        finally:
            self.disconnect()
            
    def delete_post(self, id):
        try:
            self.connect()
            sql = f"DELETE FROM posts WHERE id = %s"
            value = (id,) # 튜플에 값이 한개만 들어갈때 ,해줘야됨 
            self.cursor.execute(sql, value)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시글 삭제 실패: {error}")
            return False
        finally:
            self.disconnect()
            
    def increment_hits(self, id):
        try:
            self.connect()
            sql = f"UPDATE posts SET views = views +1 WHERE id = %s"
            value = (id,) # 튜플에 값이 한개만 들어갈때 ,해줘야됨 
            self.cursor.execute(sql, value)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시글 조회수 증가 실패: {error}")
            return False
        finally:
            self.disconnect()        
        
            
    def regsiter_user(self, name, id, password,user_ip):
        try:
            self.connect()
            sql = f"INSERT INTO users (name, id, password, user_ip) values (%s, %s, password(%s), %s)"
            values = (name, id, password, user_ip)  # 튜플형태
            self.cursor.execute(sql, values)

            self.connection.commit()

            flash("계정등록이 성공적으로 완료되었습니다!", "success")
            return True
        except mysql.connector.Error as error:
        # except pymysql.IntegrityError as e:    
            print(f"계정 등록 실패: {error}")
            # flash("중복된 아이디가 존재 합니다.", "error")
            return False
        finally:  
            self.disconnect() 
    
    def login_user(self, id, password):
        try:
            self.connect()
            sql = f"SELECT * FROM users where id = %s and password=password(%s)"
            values = (id, password)
            self.cursor.execute(sql,values)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            flash("계정 조회 실패", "error")
            print(f"계정 조회 실패: {error}")
            return []
        finally:
            self.disconnect()
    
    def duplicate_user(self,id):
        try:
            self.connect()
            sql = f"SELECT * FROM users where id = %s"
            value = (id,)
            self.cursor.execute(sql,value)
            result = self.cursor.fetchone()
            if result:
                return True
            else:
                return False
        except mysql.connector.Error as error:
            print(f"게시글 조회 실패: {error}")
            return []
        finally:
            self.disconnect()
    
    def get_user_by_id(self,id):
        try:
            self.connect()
            sql = f"SELECT * FROM users WHERE id = %s"
            value = (id,) # 튜플에 값이 한개만 들어갈때 ,해줘야됨 
            self.cursor.execute(sql, value)
            return self.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"데이터베이스 연결 실패: {error}")
            return None
        finally:
            self.disconnect()       
            
    def delete_user(self, id):
        try:
            self.connect()
            sql = f"DELETE FROM users WHERE id = %s"
            value = (id,) # 튜플에 값이 한개만 들어갈때 ,해줘야됨 
            self.cursor.execute(sql, value)
            self.connection.commit()
            flash("회원 탈퇴 성공!",'success')
            return True
        except mysql.connector.Error as error:
            print(f"유저 삭제 실패: {error}")
            return False
        finally:
            self.disconnect()
            
    def get_user_edit_password(self, id, password):
        try:
            self.connect()
            sql = f"UPDATE users SET `password` = PASSWORD(%s) WHERE `id`=%s"
            value = (password,id) # 튜플에 값이 한개만 들어갈때 ,해줘야됨 
            self.cursor.execute(sql, value)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시글 조회수 증가 실패: {error}")
            return False
        finally:
            self.disconnect()    