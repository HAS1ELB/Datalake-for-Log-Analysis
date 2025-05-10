FROM mysql:8.0

ENV MYSQL_DATABASE=transactional_db
ENV MYSQL_USER=sqoop_user
ENV MYSQL_PASSWORD=sqoop_password
ENV MYSQL_ROOT_PASSWORD=root

COPY ./init.sql /docker-entrypoint-initdb.d/

EXPOSE 3306
