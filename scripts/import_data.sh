#!/bin/bash

# Ce script effectue l'importation des données de MySQL vers HDFS à l'aide de Sqoop

# Set HADOOP_CLASSPATH to include the directory where Sqoop generates JARs
# The wildcard '*' ensures that any JAR files in this directory are picked up.
export HADOOP_CLASSPATH="/opt/sqoop/gen-classes/*"
echo "HADOOP_CLASSPATH in script is now set to: $HADOOP_CLASSPATH"

echo "Début de l'importation des données..."

# Import de la table clients
sqoop import \
  --connect jdbc:mysql://mysql:3306/transactional_db \
  --username sqoop_user \
  --password sqoop_password \
  --table clients \
  --columns "client_id,nom,prenom,email,date_inscription" \
  --map-column-java client_id=Integer,nom=String,prenom=String,email=String,date_inscription=String \
  --target-dir hdfs://namenode:8020/user/sqoop/clients \
  --delete-target-dir \
  --fields-terminated-by ',' \
  --null-string '\\N' \
  --null-non-string '\\N' \
  --bindir /opt/sqoop/gen-classes \
  --hive-drop-import-delims \
  -m 1

# Import de la table produits
sqoop import \
  --connect jdbc:mysql://mysql:3306/transactional_db \
  --username sqoop_user \
  --password sqoop_password \
  --table produits \
  --columns "produit_id,nom,description,prix,categorie" \
  --map-column-java produit_id=Integer,nom=String,description=String,prix=java.math.BigDecimal,categorie=String \
  --target-dir hdfs://namenode:8020/user/sqoop/produits \
  --delete-target-dir \
  --fields-terminated-by ',' \
  --null-string '\\N' \
  --null-non-string '\\N' \
  --bindir /opt/sqoop/gen-classes \
  --hive-drop-import-delims \
  -m 1

# Import de la table ventes
sqoop import \
  --connect jdbc:mysql://mysql:3306/transactional_db \
  --username sqoop_user \
  --password sqoop_password \
  --table ventes \
  --columns "vente_id,client_id,date_vente,montant_total" \
  --map-column-java vente_id=Integer,client_id=Integer,date_vente=String,montant_total=java.math.BigDecimal \
  --target-dir hdfs://namenode:8020/user/sqoop/ventes \
  --delete-target-dir \
  --fields-terminated-by ',' \
  --null-string '\\N' \
  --null-non-string '\\N' \
  --bindir /opt/sqoop/gen-classes \
  --hive-drop-import-delims \
  -m 1

# Import de la table details_ventes
sqoop import \
  --connect jdbc:mysql://mysql:3306/transactional_db \
  --username sqoop_user \
  --password sqoop_password \
  --table details_ventes \
  --columns "detail_id,vente_id,produit_id,quantite,prix_unitaire" \
  --map-column-java detail_id=Integer,vente_id=Integer,produit_id=Integer,quantite=Integer,prix_unitaire=java.math.BigDecimal \
  --target-dir hdfs://namenode:8020/user/sqoop/details_ventes \
  --delete-target-dir \
  --fields-terminated-by ',' \
  --null-string '\\N' \
  --null-non-string '\\N' \
  --bindir /opt/sqoop/gen-classes \
  --hive-drop-import-delims \
  -m 1

echo "Importation des données terminée avec succès!"
