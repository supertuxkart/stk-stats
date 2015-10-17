try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    print('FATAL ERROR: pymysql is not installed')
