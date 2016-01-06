#!/bin/bash

# mysqlコンテナ準備待ち
sleep 10 

# BMI22データベース作成
tempSqlFile='/init.sql'
cat > "$tempSqlFile" <<-EOSQL
	CREATE DATABASE BMI22 character set utf8;
	GRANT ALL ON BMI22.* TO 'bmi22'@'172.17.%' IDENTIFIED BY 'bmi22' WITH GRANT OPTION;
	GRANT ALL ON BMI22.* TO 'bmi22'@'localhost' IDENTIFIED BY 'bmi22' WITH GRANT OPTION;
	FLUSH PRIVILEGES;
EOSQL
mysql -u root -h ${MYSQL_PORT_3306_TCP_ADDR} -P ${MYSQL_PORT_3306_TCP_PORT} < $tempSqlFile

# BMI22用DDL流し込み
mysql BMI22 -u bmi22 -pbmi22 -h ${MYSQL_PORT_3306_TCP_ADDR} -P ${MYSQL_PORT_3306_TCP_PORT} < /src/DDL
 
# アプリ起動用ライブラリインストール
pip install -r /src/requirements.txt

# アプリ起動
cd /src ; python ddd.py
