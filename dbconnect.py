import pymysql.cursors

MAIL_SERVER='mail.cloudaccess.net'
MAIL_USER = 'info@bitesofjoy.in'
MAIL_PASS = '3idiots@123'
# mysql --user=root -p
def connection():
    conn = pymysql.connect(host='104.37.86.29', # your host, usually localhost
                     user="xdenachw", # your username
                      passwd="1k)72C2ojaMR(Z", # your password
                      port = 3306,
                      db="xdenachw") # name of the data base
    c = conn.cursor()

    return c, conn


