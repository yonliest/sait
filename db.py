import psycopg2

with psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="Genandrey9009") as conn:
   with conn.cursor() as cursor:
       cursor.execute('SELECT * FROM \"Products\"')
       result = cursor.fetchall()
       for i in result:
           print(i)