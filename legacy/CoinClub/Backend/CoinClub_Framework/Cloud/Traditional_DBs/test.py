from RDS import MySQL

class test:
    def __init__(self):
        #MySQL.Connection(host,user,password,database,Table)
        Conn = MySQL.Connection("qsbackup.c9iouglvkg67.us-west-2.rds.amazonaws.com",
                      "admin",
                      "Quincy2222",
                      "QSDB2")

        #MySQL.SQL_READ(Connection,Table)
        DATA = MySQL.SQL_Query(Conn,"SELECT * FROM actioncodes;","dataframe")


        #MySQL.SQL_READ_Table(Connection,Table)
        READ_DATA = MySQL.SQL_READ_Table(Conn,"actioncodes","csv")

        #Download(File_Name,DATA)
        MySQL.Download("test.csv",str(READ_DATA))

        #Recursive_Pull(Conn,DBname,Table_List)
        Table_List = ["actioncodes","actionreason","actionreason_todolist"]
        MySQL.Recursive_Pull(Conn,"Test",Table_List,"csv")

if __name__ == '__main__':
    test()
