"""
demosql.py

This script should demo sqlalchemy.

https://www.sqlalchemy.org/
https://bitbucket.org/zzzeek/sqlalchemy

Ubuntu Demo:
sudo apt-get install postgresql postgresql-server-dev-all libpq-dev
sudo su - postgres
psql
create database tkrapi;
create role tkrapi with login superuser password 'tkrapi';
\q
exit

wget https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh
bash Anaconda3-4.4.0-Linux-x86_64.sh
conda install sqlalchemy
export PGURL='postgres://tkrapi:tkrapi@127.0.0.1/tkrapi'
~/anaconda3/bin/python demosql.py

heroku demo:
Install heroku client
mkdir myapp2017abc
cd    myapp2017abc
echo  Hello > README.md
git init;git add .;git commit -am hello
heroku create myapp2017abc
heroku addons:create heroku-postgresql:hobby-dev
heroku config
export PGURL='postgres://afizipm:33abc8@ec2-23-13-220-251.compute-1.amazonaws.com:5432/ddrpugf'
~/anaconda3/bin/python demosql.py
heroku pg:psql --app myapp2017abc
select * from dropme;

"""

import os
import sqlalchemy as sql

# I should connect to the DB
#db_s = os.environ['PGURL']
db_s = 'postgres://toajntlqojxjry:71c0c4fb8aa900d1a49f31465c051baaf950f32050cdb702c451811a178b2078@ec2-54-163-240-7.compute-1.amazonaws.com:5432/df66rrrphefqmk'
conn = sql.create_engine(db_s).connect()

sql_s = "drop table if exists dropme"
conn.execute(sql_s)

sql_s = "create table dropme(name VARCHAR, rank INTEGER)"
conn.execute(sql_s)

sql_s = "insert into dropme(name,rank)values( %s, %s )"

conn.execute(sql_s,['Dan',0])
conn.execute(sql_s,['Dano',1])
conn.execute(sql_s,['Daniel',2])
conn.execute(sql_s,['Danny',3])
conn.execute(sql_s,['Danster',4])
conn.execute(sql_s,['Mucho Danero',5])

# From psql type:
# select * from dropme;

sql_s = "select name,rank from dropme where rank > %s "

result = conn.execute(sql_s,[2])

print("I should see some names:")
for row in result:
    print(row.name)

sql_s = "update dropme set rank = (rank + %s) where rank > %s "

conn.execute(sql_s,[1,2])

sql_s = "select name,rank from dropme"

result = conn.execute(sql_s)

print("I should see some rows:")
for row in result:
    print(row.name,row.rank)

sql_s = "delete from dropme where name like %s"

conn.execute(sql_s,['%Danero'])

sql_s = "select name,rank from dropme"

result = conn.execute(sql_s)

print("I should see some rows:")
for row in result:
    print(row.name,row.rank)

'bye'
