#!/bin/bash

# Attente que le service MySQL soit disponible
echo "Attente que MySQL soit prêt..."
until mysqladmin ping -h mysql -u sqoop_user -p'sqoop_password' --silent; do
  echo "MySQL n'est pas encore disponible - attente..."
  sleep 5
done

# Attente que le namenode HDFS soit disponible
echo "Attente que HDFS soit prêt..."
until hdfs dfsadmin -safemode get | grep -q "Safe mode is OFF"; do
  echo "HDFS n'est pas encore disponible - attente..."
  sleep 5
done

# Attente que Hive soit disponible
echo "Attente que Hive soit prêt..."
until nc -z hive-server 10000; do
  echo "Hive n'est pas encore disponible - attente..."
  sleep 5
done


echo "Tous les services sont prêts. Le container Sqoop est opérationnel."

# Create a directory for Sqoop-generated classes
SQOOP_GEN_CLASSES_DIR="/opt/sqoop/gen-classes"
mkdir -p "${SQOOP_GEN_CLASSES_DIR}"

# Add the generated classes directory to HADOOP_CLASSPATH
export HADOOP_CLASSPATH="${HADOOP_CLASSPATH}:${SQOOP_GEN_CLASSES_DIR}/*"
echo "HADOOP_CLASSPATH in entrypoint is: $HADOOP_CLASSPATH"

# Gardez le conteneur en cours d'exécution
