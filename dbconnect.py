import pymysql.cursors

MAIL_SERVER=''
MAIL_USER = ''
MAIL_PASS = ''
# mysql --user=root -p
def connection():
    conn = pymysql.connect(host='', # your host, usually localhost
                     user="", # your username
                      passwd="", # your password
                      port = ,
                      db="") # name of the data base
    c = conn.cursor()

    return c, conn


