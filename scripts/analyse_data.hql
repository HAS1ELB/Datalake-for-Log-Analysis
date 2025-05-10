-- Analyse des données pour valider la migration

USE retail_analytics;

SET textinputformat.record.delimiter='\n';
SET hive.auto.convert.join=false;
SET mapreduce.job.reduces=1; -- Force a single reducer

-- 1. Total des ventes par catégorie de produit
CREATE TABLE IF NOT EXISTS ventes_par_categorie AS
SELECT 
    p.categorie, 
    SUM(dv.quantite) AS total_ventes,
    SUM(dv.quantite * dv.prix_unitaire) AS montant_total
FROM 
    produits p
JOIN 
    details_ventes dv ON p.produit_id = dv.produit_id
GROUP BY 
    p.categorie
ORDER BY 
    montant_total DESC;

-- 2. Top 5 des clients par montant d'achat
CREATE TABLE IF NOT EXISTS top_clients AS
SELECT 
    c.client_id, 
    CONCAT(c.prenom, ' ', c.nom) AS nom_complet,
    SUM(v.montant_total) AS total_achats,
    COUNT(DISTINCT v.vente_id) AS nombre_achats
FROM 
    clients c
JOIN 
    ventes v ON c.client_id = v.client_id
GROUP BY 
    c.client_id, CONCAT(c.prenom, ' ', c.nom)
ORDER BY 
    total_achats DESC
LIMIT 5;

-- 3. Statistiques sur les ventes mensuelles
CREATE TABLE IF NOT EXISTS ventes_mensuelles AS
SELECT 
    SUBSTR(v.date_vente, 1, 7) AS mois,
    COUNT(DISTINCT v.vente_id) AS nombre_ventes,
    SUM(v.montant_total) AS chiffre_affaires,
    AVG(v.montant_total) AS panier_moyen
FROM 
    ventes v
GROUP BY 
    SUBSTR(v.date_vente, 1, 7)
ORDER BY 
    mois;

-- 4. Produits les plus vendus
CREATE TABLE IF NOT EXISTS produits_populaires AS
SELECT 
    p.produit_id,
    p.nom AS nom_produit,
    p.categorie,
    SUM(dv.quantite) AS quantite_vendue,
    SUM(dv.quantite * dv.prix_unitaire) AS montant_total_produit
FROM 
    produits p
JOIN 
    details_ventes dv ON p.produit_id = dv.produit_id
GROUP BY 
    p.produit_id, p.nom, p.categorie
ORDER BY 
    quantite_vendue DESC;

-- Afficher les résultats pour validation
SELECT * FROM ventes_par_categorie;
SELECT * FROM top_clients;
SELECT * FROM ventes_mensuelles;
SELECT * FROM produits_populaires;
