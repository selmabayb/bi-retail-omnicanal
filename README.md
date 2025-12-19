# 📊 BI Retail Omnicanal — Power BI Project

## 🎯 Objectif
Ce projet a pour objectif de démontrer mes compétences en **Business Intelligence** à travers la conception complète d’un dashboard Power BI orienté **pilotage retail omnicanal (Online + Magasins)**.

Le projet couvre l’ensemble de la chaîne BI :
- Modélisation des données (schéma en étoile)
- Création de KPIs business en DAX
- Visualisation et data storytelling
- Recommandations business actionnables

---

## 🏢 Contexte métier
Entreprise fictive : **OMNI RETAIL CO**

Activité :
- Vente de produits retail
- Canaux : Online & Magasins physiques
- Analyse multi-axes : temps, canal, catégorie, client, région

---

## 🧩 Modèle de données
Architecture en **schéma en étoile** :

- **Table de faits**
  - `fact_sales` (ventes, revenus, quantités, remises)

- **Dimensions**
  - `dim_date`
  - `dim_customers`
  - `dim_products`
  - `dim_stores`
  - `dim_channel`

📌 Voir : `model/star_schema.png`

---

## 📈 KPIs principaux
### Performance commerciale
- Chiffre d’Affaires (CA)
- Nombre de commandes
- Panier moyen (AOV)
- Prix moyen par unité
- CA Online / Store
- Part Online %

### Analyse temporelle
- CA YTD
- CA LY
- Croissance YoY %
- Croissance MoM %

### Clients
- Clients actifs
- Nouveaux clients
- Taux de nouveaux clients
- CA par client (ARPC)

📄 Détails complets dans : `report/KPI_Book_Retail_Omnicanal.pdf`

---

## 📊 Dashboards Power BI
Le rapport Power BI contient **5 pages** :

1. **Executive Overview**  
   KPIs globaux & vision synthétique

2. **Channel & Omnichannel**  
   Comparaison Online vs Store

3. **Produits & Performance**  
   Analyse par catégorie et top produits

4. **Clients & Géographie**  
   Analyse client et répartition régionale

5. **Business Insights & Recommandations**  
   Synthèse décisionnelle orientée management

📸 Aperçus : dossier `screenshots/`

---

## 🌐 Accès au rapport Power BI
🔗 **Rapport Power BI (lecture)**  
👉 *(nécessite un compte Microsoft)*  
Lien :  


https://app.powerbi.com/groups/me/reports/ada73cc8-82aa-480e-ad4f-b5b99c519a33
