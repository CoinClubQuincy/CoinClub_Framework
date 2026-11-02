import mysql.connector


class MySQL:
    def Connection(host,user,password,database):
        mydb = mysql.connector.connect(
          host="%s" % host,
          user="%s" % user,
          password="%s" % password,
          database="%s" % database
        )

        return mydb

    def SQL_READ_Table(Connection,Table,Type):
        print("Start Read")

        mycursor = Connection.cursor()
        mycursor.execute("SELECT * FROM %s" % Table)
        myresult = mycursor.fetchall()

        myresult = str(myresult)
        if Type == "csv":
            # Know its Trash But whatever
            #its to get rid of all the extra framing
            X = myresult.replace('(', '')
            X = X.replace('),', '\n')
            X = X.replace('[,', '')
            X = X.replace('],', '')
            X = X.replace(')', '')
            X = str(X)
            X = X.replace(']', '')
            X = X.replace('[', '')

            return X

        elif Type == "dataframe":
            return myresult
        else:
            print("Error: Enter data type")

    def SQL_Query(Connection,Query,Type):
        print("Start Query")

        cursor = Connection.cursor()
        cursor.execute(Query)
        results = cursor.fetchall()
        results = str(results)

        if Type == "csv":
            # I KNOW I KNOW SHOOT ME
            X = results.replace('(', '')
            X = X.replace('),', '\n')
            X = X.replace('[,', '')
            X = X.replace('],', '')
            X = X.replace(')', '')
            X = str(X)
            X = X.replace(']', '')
            X = X.replace('[', '')

            return X

        elif Type == "dataframe":
            return results
        else:
            print("Error: Enter data type")

    def Recursive_Pull(Connection,DBname,Table_List,Type):
        print("Start Write")

        for i in Table_List:
            DATA = MySQL.SQL_READ_Table(Connection,i,Type)
            Filename = "%s-%s.csv" % (DBname,i)
            MySQL.Download(Filename,str(DATA))

            print("Download %s" % Filename)

    def Download(File_Name,DATA):
        print("Start Downloads")
        f = open(File_Name, "w")
        f.write(DATA)

        print("Download Complete")
