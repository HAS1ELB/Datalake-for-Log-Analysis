-- Création des tables Hive pour les données importées

-- Création de la base de données
CREATE DATABASE IF NOT EXISTS retail_analytics;
USE retail_analytics;

-- Table des clients
CREATE EXTERNAL TABLE IF NOT EXISTS clients (
    client_id INT,
    nom STRING,
    prenom STRING,
    email STRING,
    date_inscription STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/sqoop/clients'
TBLPROPERTIES ('serialization.format'='1', 'serialization.null.format'='\\N', 'escape.delim'='\\', 'textinputformat.ignore.errors'='true');

-- Table des produits
CREATE EXTERNAL TABLE IF NOT EXISTS produits (
    produit_id INT,
    nom STRING,
    description STRING,
    prix DECIMAL(10, 2),
    categorie STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/sqoop/produits'
TBLPROPERTIES ('serialization.format'='1', 'serialization.null.format'='\\N', 'escape.delim'='\\', 'textinputformat.ignore.errors'='true');

-- Table des ventes
CREATE EXTERNAL TABLE IF NOT EXISTS ventes (
    vente_id INT,
    client_id INT,
    date_vente STRING,
    montant_total DECIMAL(10, 2)
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/sqoop/ventes'
TBLPROPERTIES ('serialization.format'='1', 'serialization.null.format'='\\N', 'escape.delim'='\\', 'textinputformat.ignore.errors'='true');

-- Table des détails des ventes
CREATE EXTERNAL TABLE IF NOT EXISTS details_ventes (
    detail_id INT,
    vente_id INT,
    produit_id INT,
    quantite INT,
    prix_unitaire DECIMAL(10, 2)
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/sqoop/details_ventes'
TBLPROPERTIES ('serialization.format'='1', 'serialization.null.format'='\\N', 'escape.delim'='\\', 'textinputformat.ignore.errors'='true');
