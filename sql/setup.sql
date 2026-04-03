-- ============================================================
-- ÉTAPE 1 : CONFIGURATION DE L'ENVIRONNEMENT SNOWFLAKE
-- À exécuter dans un Snowflake Worksheet, en tant qu'ACCOUNTADMIN
-- ============================================================

-- 1.1 Création du rôle dédié au projet
USE ROLE ACCOUNTADMIN;

CREATE ROLE IF NOT EXISTS HOUSE_PRICE_ROLE
    COMMENT = 'Rôle dédié au workshop House Price ML';

GRANT ROLE HOUSE_PRICE_ROLE TO ROLE SYSADMIN;

-- Remplacez YOUR_USER par votre nom d'utilisateur Snowflake
GRANT ROLE HOUSE_PRICE_ROLE TO USER YOUR_USER;

-- 1.2 Création du Virtual Warehouse (puissance de calcul)
CREATE WAREHOUSE IF NOT EXISTS HOUSE_PRICE_WH
    WAREHOUSE_SIZE = 'MEDIUM'
    AUTO_SUSPEND = 120          -- S'éteint après 2 min d'inactivité
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse pour le pipeline ML House Price';

GRANT USAGE ON WAREHOUSE HOUSE_PRICE_WH TO ROLE HOUSE_PRICE_ROLE;

-- 1.3 Création de la base de données et du schéma
CREATE DATABASE IF NOT EXISTS HOUSE_PRICE_DB
    COMMENT = 'Base de données du workshop House Price ML';

CREATE SCHEMA IF NOT EXISTS HOUSE_PRICE_DB.RAW
    COMMENT = 'Données brutes ingérées depuis S3';

CREATE SCHEMA IF NOT EXISTS HOUSE_PRICE_DB.ANALYTICS
    COMMENT = 'Données transformées et features engineerées';

CREATE SCHEMA IF NOT EXISTS HOUSE_PRICE_DB.ML
    COMMENT = 'Modèles, prédictions et artefacts ML';

-- 1.4 Attribution des droits sur la base et les schémas
GRANT ALL PRIVILEGES ON DATABASE HOUSE_PRICE_DB TO ROLE HOUSE_PRICE_ROLE;
GRANT ALL PRIVILEGES ON ALL SCHEMAS IN DATABASE HOUSE_PRICE_DB TO ROLE HOUSE_PRICE_ROLE;
GRANT ALL PRIVILEGES ON FUTURE SCHEMAS IN DATABASE HOUSE_PRICE_DB TO ROLE HOUSE_PRICE_ROLE;
GRANT ALL PRIVILEGES ON ALL TABLES IN DATABASE HOUSE_PRICE_DB TO ROLE HOUSE_PRICE_ROLE;
GRANT ALL PRIVILEGES ON FUTURE TABLES IN DATABASE HOUSE_PRICE_DB TO ROLE HOUSE_PRICE_ROLE;

-- 1.5 Privilèges nécessaires pour Snowpark ML et le Model Registry
GRANT CREATE STAGE ON SCHEMA HOUSE_PRICE_DB.ML TO ROLE HOUSE_PRICE_ROLE;
GRANT CREATE MODEL ON SCHEMA HOUSE_PRICE_DB.ML TO ROLE HOUSE_PRICE_ROLE;
GRANT CREATE FUNCTION ON SCHEMA HOUSE_PRICE_DB.ML TO ROLE HOUSE_PRICE_ROLE;
GRANT CREATE PROCEDURE ON SCHEMA HOUSE_PRICE_DB.ML TO ROLE HOUSE_PRICE_ROLE;

-- 1.6 Création du stage externe pointant vers S3
USE ROLE HOUSE_PRICE_ROLE;
USE DATABASE HOUSE_PRICE_DB;
USE SCHEMA RAW;
USE WAREHOUSE HOUSE_PRICE_WH;

CREATE STAGE IF NOT EXISTS S3_HOUSE_PRICE_STAGE
    URL = 's3://logbrain-datalake/datasets/house_price/'
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
        NULL_IF = ('NULL', 'null', '')
        EMPTY_FIELD_AS_NULL = TRUE
    )
    COMMENT = 'Stage S3 vers le dataset House Price';

-- Vérification que le stage est bien connecté
LIST @S3_HOUSE_PRICE_STAGE;

-- 1.7 Création de la table cible pour l'ingestion
CREATE OR REPLACE TABLE HOUSE_PRICE_DB.RAW.HOUSE_PRICES (
    PRICE          NUMBER(12, 2)   COMMENT 'Prix de vente de la maison',
    AREA           NUMBER(10, 2)   COMMENT 'Surface totale en m²',
    BEDROOMS       NUMBER(3)       COMMENT 'Nombre de chambres',
    BATHROOMS      NUMBER(3)       COMMENT 'Nombre de salles de bain',
    STORIES        NUMBER(3)       COMMENT 'Nombre d étages',
    MAINROAD       VARCHAR(5)      COMMENT 'Accès route principale (yes/no)',
    GUESTROOM      VARCHAR(5)      COMMENT 'Chambre d amis (yes/no)',
    BASEMENT       VARCHAR(5)      COMMENT 'Sous-sol (yes/no)',
    HOTWATERHEATING VARCHAR(5)     COMMENT 'Chauffage eau chaude (yes/no)',
    AIRCONDITIONING VARCHAR(5)     COMMENT 'Climatisation (yes/no)',
    PARKING        NUMBER(3)       COMMENT 'Places de stationnement',
    PREFAREA       VARCHAR(5)      COMMENT 'Zone privilégiée (yes/no)',
    FURNISHINGSTATUS VARCHAR(20)   COMMENT 'État ameublement (furnished/semi-furnished/unfurnished)',
    _INGESTED_AT   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP() COMMENT 'Timestamp d ingestion'
);

-- 1.8 Chargement des données depuis S3
COPY INTO HOUSE_PRICE_DB.RAW.HOUSE_PRICES (
    PRICE, AREA, BEDROOMS, BATHROOMS, STORIES,
    MAINROAD, GUESTROOM, BASEMENT, HOTWATERHEATING,
    AIRCONDITIONING, PARKING, PREFAREA, FURNISHINGSTATUS
)
FROM @S3_HOUSE_PRICE_STAGE
FILE_FORMAT = (
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
)
ON_ERROR = 'CONTINUE'
PURGE = FALSE;

-- Vérification du chargement
SELECT COUNT(*) AS NB_LIGNES FROM HOUSE_PRICE_DB.RAW.HOUSE_PRICES;
SELECT * FROM HOUSE_PRICE_DB.RAW.HOUSE_PRICES LIMIT 10;

-- ============================================================
-- ✅ RÉSULTAT ATTENDU : ~545 lignes chargées
-- ============================================================
