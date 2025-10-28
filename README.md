# Gestion de projets

## Description :
L'application de bureau réalisée permet de gérer une liste de projets avec leurs dates de création, d'expiration et état d'avancement.\
L'interface est issu de CustomTKinter et l'application s'appuie sur une base de donnée SQLite pour stocker les données.

## Installation

Prérequis :  
Python 3.10+\
Module :
```
pip install customtkinter
```
## Lancement

Placer le script gestion_projets.py et le fichier BDD_projets.db dans un même dossier.  
Exécuter le script, une fenêtre s'ouvre avec l'interface principale.

## Fonctionalités principales

Ajouts de projets\
    L'ajout de projet se fait par un bouton "Ajouter" et ouvre une nouvelle fenêtre où doivent être remplies les informations liées au projet :  Noms obligatoires, dates facultatives au format YYYY-MM-DD
    
Modifications de projets
    * La modification d'un projet passe par la sélection d'une ligne dans le tableau principal et le bouton Modifier
    * Toutes les informations sont éditables
    * L'état "Terminé" peut-être appliqué par le bouton "Terminer" mais aussi désappliqué avec le bouton modifier, le calcul de l'état repasse alors automatiquement par les règles de calcul d'état.

Suppression d'un projet avec confirmation
    * La suppression dd'un projet passe par la sélection d'une ligne dans le tableau principal et le bouton Supprimer
    * La suppression demande confirmation.

Marquer un projet comme "Terminé"
    * Le bouton "Terminer" permet de marquer un projet comme "Terminé" pour son état.

Tri par colonnes
    * Toutes les colonnes peuvent être triées par ordre croissant/décroissant à l'exception de la colonne "état"

Calcul automatique de l'état
    * L'état d'un projet est calculé automatiquement en fonction du nombre de jours restants (différence entre date de création et date d'expiration)
    * Si ce nombre (jours_restants) > 7, l'état est "En cours"
    * Si jours_restants <= 7, l'état est "Urgent"
    * Si jours_restants < 0, l'état est "En retard"
    * Sinon l'état est "non défini" (date non précisé)

## Démarche, Choix techniques
CustomTKinter : interface graphique moderne offrant compromis entre simplicité, fonctionnalité et esthétique.   
SQLite : base de données embarquée, idéale pour une application locale  
Classe unique : structure claire, fonctions pour chaque action\
On personalise l'interface en respectant les contraintes et en mettant des boutons associées aux actions requises.

## Limites connues
Pas de système de sauvegarde externe (lié au fichier BDD_projets.db)\
Pas de filtrage combiné (par état ou par date)\
Pas de connexion en simultané pour accéder à la BDD

## Pistes d'amélioration
Ajout de filtrage dynamique\
Exportation vers CSV, Excel, Pdf\
Modifier les fenêtres pop-up pour des notifications plus discrètes\
Système multi-utilisateur avec authentification\
Persistance du tri et des filtres entre les sessions\
Vue calendrier ou timeline des projets