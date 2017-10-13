# -*- coding: utf-8 -*- 

import pymysql
 
conn = pymysql.connect(
    host='127.0.0.1', 
    user='hello', 
    password='0000',
    db='edxapp'
)
  
curs = conn.cursor()

### QUERY STORE ###  
sql1 = """
CREATE TABLE `tb_notice`
(
   `seq`      int(11) NOT NULL AUTO_INCREMENT,
   `title`    varchar(200) DEFAULT NULL,
   `link`     varchar(200) DEFAULT NULL,
   `sdate`    varchar(8) DEFAULT NULL,
   `stime`    varchar(4) DEFAULT NULL,
   `edate`    varchar(8) DEFAULT NULL,
   `etime`    varchar(4) DEFAULT NULL,
   `useyn`    char(1) CHARACTER SET latin1 DEFAULT NULL,
   PRIMARY KEY(`seq`)
)
ENGINE = InnoDB
AUTO_INCREMENT = 16
DEFAULT CHARSET = utf8
COMMENT = 'notice'
"""

sql2 = """
CREATE TABLE `edxapp`.`vw_copykiller`
(
   `uri`                  VARCHAR(40) NOT NULL COMMENT '표절검사 대상 문서 PK',
   `year_id`              VARCHAR(40) NULL COMMENT '학년 ID',
   `year_name`            VARCHAR(40) NULL COMMENT '학년명',
   `term_id`              VARCHAR(40) NULL COMMENT '학기 ID',
   `term_name`            VARCHAR(40) NULL COMMENT '학기명',
   `class_id`             VARCHAR(40) NULL COMMENT '과목(수업)ID',
   `class_name`           VARCHAR(100) NULL COMMENT '과목(수업)명',
   `report_id`            VARCHAR(100) NULL COMMENT '과제 ID',
   `report_name`          VARCHAR(100) NULL COMMENT '과제명',
   `student_id`           VARCHAR(40) NULL COMMENT '학습자(과제 제출자)ID',
   `student_name`         VARCHAR(40)
                          NULL
                          COMMENT '학습자(과제 제출자) 이름',
   `student_number`       VARCHAR(40)
                          NULL
                          COMMENT '학습자(과제 제출자) 번호',
   `student_dept_name`    VARCHAR(40)
                          NULL
                          COMMENT '학습자(과제 제출자) 학과명',
   `start_date`           VARCHAR(40)
                          NULL
                          COMMENT '과제 제출 시작일(YYYYMMDDhhmmss)',
   `end_date`             VARCHAR(40)
                          NULL
                          COMMENT '과제 제출 마감일(YYYYMMDDhhmmss)',
   `submit_date`          VARCHAR(40)
                          NULL
                          COMMENT '과제 제출일(YYYYMMDDhhmmss)',
   `update_date`          VARCHAR(40)
                          NULL
                          COMMENT '과제 수정일(YYYYMMDDhhmmss)',
   `title`                VARCHAR(100)
                          NULL
                          COMMENT '제출한 과제물의 제목',
   `content`              VARCHAR(20000)
                          NULL
                          COMMENT '제출한 과제물의 본문',
   `attach_file_name`     VARCHAR(100)
                          NULL
                          COMMENT '제출한 과제물 첨부문서 파일명',
   `attach_file_path`     VARCHAR(100)
                          NULL
                          COMMENT '제출한 과제물 첨부문서 파일경로',
   PRIMARY KEY(`uri`)
)
"""

sql3 = """
CREATE TABLE tb_copykiller_copyratio
(
   uri                      varchar(128) NOT NULL,
   check_type               varchar(128) NOT NULL,
   total_copy_ratio         integer(5) NOT NULL DEFAULT '-100',
   disp_total_copy_ratio    varchar(16) NOT NULL DEFAULT '검사중',
   complete_status          char(1) NOT NULL DEFAULT 'N',
   complete_date            varchar(14) NULL
)
"""

sql4 = """
CREATE UNIQUE INDEX idx_tb_ck_copyratio_key
   ON tb_copykiller_copyratio(uri, check_type)
"""

sql5 = """
CREATE INDEX idx_tb_ck_copyratio_complete
   ON tb_copykiller_copyratio(complete_status)
"""

sql6 = """
CREATE TABLE tb_copykiller_delete
(
   uri             varchar(128) NOT NULL,
   is_deleted      char(1) DEFAULT 'N' NOT NULL,
   deleted_date    datetime NULL
)
"""

sql7 = """
CREATE INDEX idx_tb_ck_delete_key
   ON tb_copykiller_delete(uri)
"""

sql8 = """
CREATE INDEX idx_tb_ck_delete_deleted
   ON tb_copykiller_delete(is_deleted)
"""

sql9 = """
CREATE TABLE `edxapp`.`tb_tmp_answer`
(
   `course_id`     VARCHAR(100) NULL,
   `uuid`          VARCHAR(100) NULL,
   `raw_answer`    VARCHAR(20000) NULL,
   `item_type`     VARCHAR(100) NULL
)
"""

sql10 = """
CREATE TABLE drmt_auth_user
(
   id int(11),
   password varchar(128),
   last_login datetime(6),
   is_superuser tinyint(1),
   username varchar(30),
   first_name varchar(30),
   last_name varchar(30),
   email varchar(254),
   is_staff tinyint(1),
   is_active tinyint(1),
   date_joined datetime(6),
   dormant_mail_cd varchar(2),
   dormant_yn varchar(1),
   dormant_dt datetime(6)
)
"""

sql11 = """
CREATE TABLE drmt_auth_userprofile
(
   id int(11),
   name varchar(255),
   meta longtext,
   courseware varchar(255),
   language varchar(255),
   location varchar(255),
   year_of_birth int(11),
   gender varchar(6),
   level_of_education varchar(6),
   mailing_address longtext,
   city longtext,
   country varchar(2),
   goals longtext,
   allow_certificate tinyint(1),
   bio varchar(3000),
   profile_image_uploaded_at datetime(6),
   user_id int(11)
)
"""

sql12 = """
CREATE TABLE drmt_social_auth_usersocialauth
(
   id int(11),
   provider varchar(32),
   uid varchar(255),
   extra_data longtext,
   user_id int(11)
)
"""

sql13 = """
ALTER TABLE edxapp.auth_user
   ADD dormant_mail_cd varchar(2)
"""

sql14 = """
ALTER TABLE edxapp.auth_user
   ADD dormant_yn varchar(1)
"""

sql15 = """
ALTER TABLE edxapp.auth_user
   ADD dormant_dt datetime(6)
"""

sql16 = """
CREATE TABLE faq_request
(
   id          int(11) PRIMARY KEY AUTO_INCREMENT,
   student_email varchar(50),
   response_email varchar(50),
   head_title varchar(50),
   question text,
   reg_date    datetime DEFAULT now()
)
"""

sql17 = """
CREATE TABLE tb_board
(
   board_id    int(11) PRIMARY KEY AUTO_INCREMENT,
   head_title varchar(50),
   subject     text NOT NULL,
   content longtext,
   reg_date    datetime DEFAULT now() NOT NULL,
   mod_date    datetime DEFAULT now() NOT NULL,
   section     varchar(10) NOT NULL,
   use_yn      varchar(1) DEFAULT "Y" NOT NULL,
   odby        int(11) DEFAULT "0",
   INDEX ind (section)
)
"""

sql18 = """
CREATE TABLE tb_board_attach
(
   attatch_id           int(11) PRIMARY KEY AUTO_INCREMENT,
   board_id             int(11) NOT NULL,
   attatch_file_name    varchar(255) NOT NULL,
   attatch_file_ext     varchar(50) NOT NULL,
   attatch_file_size    varchar(50) NOT NULL,
   del_yn               varchar(1) DEFAULT "Y" NOT NULL,
   INDEX ind (board_id)
)
"""

sql19 = """
CREATE TABLE drmt_auth_user_process
(
   email        varchar(50) NOT NULL,
   send_date    datetime DEFAULT now() NOT NULL,
   success      int(1) DEFAULT '0'
)
"""

sql20 = """
CREATE TABLE edxapp.course_review(
id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, 
content VARCHAR(200) NOT NULL,                               
point INT NOT NULL DEFAULT 1,                                    
reg_time DATETIME NOT NULL DEFAULT NOW(),         
user_id INT NOT NULL,                                                    
course_id VARCHAR(100) NOT NULL                             
)
"""

sql21 = """
CREATE TABLE edxapp.course_review_user(
id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, 
review_id INT NOT NULL,                                                 
user_id INT NOT NULL,                                                    
good_bad VARCHAR(10) NOT NULL,                              
reg_time DATETIME NOT NULL DEFAULT NOW()         
)
"""

### QUERY STORE ###  

curs.execute(sql1)
curs.execute(sql2)
curs.execute(sql3)
curs.execute(sql4)
curs.execute(sql5)
curs.execute(sql6)
curs.execute(sql7)
curs.execute(sql8)
curs.execute(sql9)
curs.execute(sql10)
curs.execute(sql11)
curs.execute(sql12)
curs.execute(sql13)
curs.execute(sql14)
curs.execute(sql15)
curs.execute(sql16)
curs.execute(sql17)
curs.execute(sql18)
curs.execute(sql19)
curs.execute(sql20)
curs.execute(sql21)

conn.close()
