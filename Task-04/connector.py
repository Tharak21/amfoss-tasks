import csv
import mysql.connector
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="thmarvel",
    database="cinescope",
)
cursor=mydb.cursor()

file=open("movies.csv","r")
reader=csv.reader(file)
header=next(reader)
for row in reader:
    query = "INSERT INTO movies1 (Series_Title, Released_Year, Genre, IMDB_Rating, Director, Star1, Star2, Star3) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7])
    cursor.execute(query,val)
mydb.commit()
file.close()

print("succesful")