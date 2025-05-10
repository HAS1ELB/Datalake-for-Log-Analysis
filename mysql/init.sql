-- Creation de la base de données
CREATE DATABASE IF NOT EXISTS transactional_db;
USE transactional_db;

-- Table des clients
CREATE TABLE clients (
    client_id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_inscription DATE NOT NULL
);

-- Table des produits
CREATE TABLE produits (
    produit_id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    prix DECIMAL(10, 2) NOT NULL,
    categorie VARCHAR(50) NOT NULL
);

-- Table des ventes
CREATE TABLE ventes (
    vente_id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    date_vente DATETIME NOT NULL,
    montant_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

-- Table des détails des ventes
CREATE TABLE details_ventes (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    vente_id INT NOT NULL,
    produit_id INT NOT NULL,
    quantite INT NOT NULL,
    prix_unitaire DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (vente_id) REFERENCES ventes(vente_id),
    FOREIGN KEY (produit_id) REFERENCES produits(produit_id)
);

-- Insertion de données d'exemple pour les clients
INSERT INTO clients (nom, prenom, email, date_inscription) VALUES
('Dupont', 'Jean', 'jean.dupont@email.com', '2023-01-15'),
('Martin', 'Sophie', 'sophie.martin@email.com', '2023-02-20'),
('Dubois', 'Pierre', 'pierre.dubois@email.com', '2023-03-10'),
('Leroy', 'Marie', 'marie.leroy@email.com', '2023-04-05'),
('Moreau', 'Thomas', 'thomas.moreau@email.com', '2023-05-12');

-- Insertion de données d'exemple pour les produits
INSERT INTO produits (nom, description, prix, categorie) VALUES
('Ordinateur portable', 'Ordinateur portable haute performance', 999.99, 'Informatique'),
('Smartphone', 'Smartphone dernière génération', 699.99, 'Téléphonie'),
('Tablette', 'Tablette tactile 10 pouces', 349.99, 'Informatique'),
('Casque audio', 'Casque audio sans fil', 129.99, 'Audio'),
('Enceinte bluetooth', 'Enceinte bluetooth portable', 79.99, 'Audio'),
('Souris sans fil', 'Souris ergonomique sans fil', 29.99, 'Périphériques'),
('Clavier mécanique', 'Clavier mécanique rétroéclairé', 89.99, 'Périphériques'),
('Moniteur 4K', 'Moniteur 27 pouces résolution 4K', 299.99, 'Écrans'),
('Disque dur externe', 'Disque dur externe 1TB', 59.99, 'Stockage'),
('Imprimante laser', 'Imprimante laser monochrome', 199.99, 'Périphériques');

-- Insertion de données d'exemple pour les ventes
INSERT INTO ventes (client_id, date_vente, montant_total) VALUES
(1, '2023-06-15 10:25:00', 1029.98),
(2, '2023-06-20 14:30:00', 699.99),
(3, '2023-07-05 09:15:00', 479.98),
(4, '2023-07-10 16:45:00', 399.98),
(5, '2023-07-15 11:20:00', 129.99),
(1, '2023-08-05 13:10:00', 359.98),
(2, '2023-08-10 15:30:00', 199.99),
(3, '2023-08-20 10:45:00', 89.99),
(4, '2023-09-01 14:15:00', 299.99),
(5, '2023-09-10 12:30:00', 139.98);

-- Insertion de données d'exemple pour les détails des ventes
INSERT INTO details_ventes (vente_id, produit_id, quantite, prix_unitaire) VALUES
(1, 1, 1, 999.99),
(1, 6, 1, 29.99),
(2, 2, 1, 699.99),
(3, 3, 1, 349.99),
(3, 6, 1, 29.99),
(3, 9, 1, 59.99),
(4, 4, 1, 129.99),
(4, 5, 1, 79.99),
(4, 6, 1, 29.99),
(4, 9, 1, 59.99),
(5, 4, 1, 129.99),
(6, 3, 1, 349.99),
(7, 10, 1, 199.99),
(8, 7, 1, 89.99),
(9, 8, 1, 299.99),
(10, 6, 1, 29.99),
(10, 9, 1, 59.99),
(10, 4, 1, 129.99);

-- Création d'utilisateur pour Sqoop avec les privilèges nécessaires
CREATE USER IF NOT EXISTS 'sqoop_user'@'%' IDENTIFIED BY 'sqoop_password';
GRANT ALL PRIVILEGES ON transactional_db.* TO 'sqoop_user'@'%';
FLUSH PRIVILEGES;
