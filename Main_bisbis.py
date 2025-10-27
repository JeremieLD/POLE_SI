import customtkinter as ctk
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk

# Configuration de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """Application pour visualiser les projets."""
    
    def __init__(self):
        super().__init__()
        
        self.sort_column = None
        self.sort_reverse = False

        # Configuration de la fenêtre
        self.title("Gestion de Projets")
        self.geometry("1000x700")
        
        # Connexion à la base de données
        self.connexion = sqlite3.connect("BDD_projets.db")
        self.cursor = self.connexion.cursor()
        
        # Créer la table si elle n'existe pas
        self.creer_table()
        
        # Créer l'interface
        self.creer_interface()
        
        # Afficher les projets au démarrage
        self.afficher_projets()
        
        # Fermer proprement la BDD quand on ferme l'app
        self.protocol("WM_DELETE_WINDOW", self.fermer_app)


    def creer_table(self):
        """
        Crée la table 'projets' si elle n'existe pas.
        Les dates sont facultatives.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS projets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                date_creation DATE,
                date_expiration DATE
            )
        """)
        self.connexion.commit()
    
    def creer_interface(self):
        """Crée tous les éléments visuels."""
        
        # Titre
        titre = ctk.CTkLabel(self,text="📋 Gestion de Projets",font=("Arial", 24, "bold"))
        titre.pack(pady=15)
        
        # Frame pour la barre de recherche
        frame_recherche = ctk.CTkFrame(self)
        frame_recherche.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(frame_recherche, text="🔍 Rechercher :").pack(side="left", padx=5)
        
        # Entry pour la recherche
        self.entree_recherche = ctk.CTkEntry(frame_recherche, width=300)
        self.entree_recherche.pack(side="left", padx=5)
        
        # Bouton rechercher
        ctk.CTkButton(frame_recherche,text="Rechercher",command=self.rechercher_projet,width=100).pack(side="left", padx=5)
        
        # Bouton pour réinitialiser (afficher tout)
        ctk.CTkButton(frame_recherche,text="Tout afficher",command=self.afficher_projets,width=100).pack(side="left", padx=5)
        
        # Frame pour le tableau style Excel
        frame_tableau = ctk.CTkFrame(self)
        frame_tableau.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Créer le Treeview (tableau)
        # Treeview = widget de tkinter pour faire des tableaux
        # On utilise ttk.Treeview car CustomTkinter n'a pas de tableau
        self.tableau = ttk.Treeview(frame_tableau,columns=("ID", "Nom", "Création", "Expiration", "État"),show="headings",  # Afficher seulement les en-têtes, pas la colonne par défaut
              height=15
        )
        
        # Définir les en-têtes
        self.tableau.heading("ID", text="ID", command=lambda: self.sort_by("ID"))
        self.tableau.heading("Nom", text="Nom du projet", command=lambda: self.sort_by("Nom"))
        self.tableau.heading("Création", text="Date de création", command=lambda: self.sort_by("Création"))
        self.tableau.heading("Expiration", text="Date d'expiration", command=lambda: self.sort_by("Expiration"))
        self.tableau.heading("État", text="État")
        
        # Définir la largeur des colonnes
        self.tableau.column("ID", width=50, anchor="center")
        self.tableau.column("Nom", width=300, anchor="w")
        self.tableau.column("Création", width=120, anchor="center")
        self.tableau.column("Expiration", width=120, anchor="center")
        self.tableau.column("État", width=120, anchor="center")
        
        # Scrollbar pour le tableau
        scrollbar = ttk.Scrollbar(frame_tableau, orient="vertical", command=self.tableau.yview)
        self.tableau.configure(yscrollcommand=scrollbar.set)
        
        self.tableau.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Double-clic sur une ligne pour voir les détails
        self.tableau.bind("<Double-Button-1>", self.voir_details_ligne)
        
        # Frame pour les boutons d'action en bas
        frame_boutons = ctk.CTkFrame(self)
        frame_boutons.pack(pady=15)
        
        # Bouton Ajouter
        ctk.CTkButton(frame_boutons,text="➕ Ajouter",command=self.ouvrir_fenetre_ajouter,fg_color="green",hover_color="darkgreen",width=130).pack(side="left", padx=10)
        
        # Bouton Modifier (modifie la ligne sélectionnée)
        ctk.CTkButton(frame_boutons,text="✏️ Modifier",command=self.modifier_ligne_selectionnee,fg_color="orange",hover_color="darkorange",width=130).pack(side="left", padx=10)
        
        # Bouton Supprimer (supprime la ligne sélectionnée)
        ctk.CTkButton(frame_boutons,text="🗑️ Supprimer",command=self.supprimer_ligne_selectionnee,fg_color="red",hover_color="darkred",width=130).pack(side="left", padx=10)
    
    def calculer_etat(self, date_expiration):
        """
        Calcule l'état du projet en fonction de sa date d'expiration.
        Si pas de date, retourne "Non défini".
        """
        if not date_expiration:  # Si la date est vide ou None
            return "⚪ Non défini"
        
        try:
            date_exp = datetime.strptime(date_expiration, "%Y-%m-%d").date()
            aujourd_hui = datetime.now().date()
            jours_restants = (date_exp - aujourd_hui).days
            
            if jours_restants < 0:
                return "❌ Expiré"
            elif jours_restants <= 7:
                return "⚠️ Urgent"
            else:
                return "✅ Actif"
        except:
            return "⚪ Non défini"
    
    def afficher_projets(self, projets=None):
        """
        Affiche tous les projets dans le tableau.
        
        Si projets est None, on récupère tout depuis la BDD.
        Sinon, on affiche les projets fournis (pour la recherche).
        """
        # Vider le tableau
        # get_children() retourne toutes les lignes du tableau
        for item in self.tableau.get_children():
            self.tableau.delete(item)
        
        # Si aucun projet fourni, on les récupère tous
        if projets is None:
            self.cursor.execute("SELECT * FROM projets ORDER BY id")
            projets = self.cursor.fetchall()
        
        # Afficher chaque projet
        for projet in projets:
            id_projet = projet[0]
            nom = projet[1]
            date_creation = projet[2] if projet[2] else "-"  # "-" si vide
            date_expiration = projet[3] if projet[3] else "-"
            
            # Calculer l'état
            etat = self.calculer_etat(projet[3])
            
            # Insérer la ligne dans le tableau
            # insert("", "end", ...) ajoute une ligne à la fin
            self.tableau.insert("", "end", values=(id_projet, nom, date_creation, date_expiration, etat))
    
    def sort_by(self,column):
        """Tri le tableau par colonne"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        items = [(self.tableau.set(child, column), child) for child in self.tableau.get_children()]

        # Tri numérique pour certaines colonnes
        if column in ["ID"]:
            items.sort(key=lambda x: float(str(x[0]).replace(" ", "")), reverse=self.sort_reverse)
        else:
            items.sort(key=lambda x: str(x[0]).lower(), reverse=self.sort_reverse)

        for index, (_, iid) in enumerate(items):
            self.tableau.move(iid, "", index)

    def rechercher_projet(self):
        """
        Recherche un projet par son nom.
        
        LIKE en SQL permet de chercher avec des caractères joker.
        % = n'importe quels caractères
        Exemple : "%site%" trouve "Mon site web", "Site perso", etc.
        """
        terme_recherche = self.entree_recherche.get()
        
        if not terme_recherche:
            self.afficher_projets()  # Si vide, afficher tout
            return
        
        # Recherche dans la BDD
        self.cursor.execute(
            "SELECT * FROM projets WHERE nom LIKE ? ORDER BY id",
            (f"%{terme_recherche}%",)  # Les % permettent de trouver le terme n'importe où dans le nom
        )
        resultats = self.cursor.fetchall()
        
        # Afficher les résultats
        self.afficher_projets(resultats)
    
    def voir_details_ligne(self, event):
        """
        Appelé quand on double-clique sur une ligne.
        Affiche une fenêtre avec les détails du projet.
        """
        # Récupérer la ligne sélectionnée
        selection = self.tableau.selection()
        if not selection:
            return
        
        # Récupérer les valeurs de la ligne
        # item() retourne un dictionnaire avec les infos de la ligne
        valeurs = self.tableau.item(selection[0])["values"]
        
        # Créer une fenêtre de détails
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Détails du projet")
        fenetre.geometry("400x300")
        
        ctk.CTkLabel(fenetre, text="📄 Détails du Projet", font=("Arial", 18, "bold")).pack(pady=15)
        
        # Afficher les infos
        ctk.CTkLabel(fenetre, text=f"ID : {valeurs[0]}", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(fenetre, text=f"Nom : {valeurs[1]}", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(fenetre, text=f"Date de création : {valeurs[2]}", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(fenetre, text=f"Date d'expiration : {valeurs[3]}", font=("Arial", 14)).pack(pady=5)
        ctk.CTkLabel(fenetre, text=f"État : {valeurs[4]}", font=("Arial", 14)).pack(pady=5)
        
        ctk.CTkButton(fenetre, text="Fermer", command=fenetre.destroy).pack(pady=20)
    
    def ouvrir_fenetre_ajouter(self):
        """Ouvre une fenêtre pour ajouter un projet."""
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Ajouter un projet")
        fenetre.geometry("400x320")
        
        ctk.CTkLabel(fenetre, text="➕ Nouveau Projet", font=("Arial", 18, "bold")).pack(pady=15)
        
        # Champ : Nom (obligatoire)
        ctk.CTkLabel(fenetre, text="Nom du projet * :").pack(pady=5)
        entree_nom = ctk.CTkEntry(fenetre, width=300)
        entree_nom.pack(pady=5)
        
        # Champ : Date de création (facultatif)
        ctk.CTkLabel(fenetre, text="Date de création (YYYY-MM-DD, facultatif) :").pack(pady=5)
        entree_date_creation = ctk.CTkEntry(fenetre, width=300)
        entree_date_creation.insert(0, datetime.now().strftime("%Y-%m-%d"))
        entree_date_creation.pack(pady=5)
        
        # Champ : Date d'expiration (facultatif)
        ctk.CTkLabel(fenetre, text="Date d'expiration (YYYY-MM-DD, facultatif) :").pack(pady=5)
        entree_date_expiration = ctk.CTkEntry(fenetre, width=300)
        entree_date_expiration.pack(pady=5)
        
        def ajouter_projet():
            nom = entree_nom.get().strip()
            date_creation = entree_date_creation.get().strip() or None
            date_expiration = entree_date_expiration.get().strip() or None
            
            if not nom:
                print("❌ Le nom est obligatoire")
                return
            
            # Si les dates sont vides, on met None (NULL en SQL)
            date_creation = date_creation if date_creation else None
            date_expiration = date_expiration if date_expiration else None
            
            self.cursor.execute(
                "INSERT INTO projets (nom, date_creation, date_expiration) VALUES (?, ?, ?)",
                (nom, date_creation, date_expiration)
            )
            self.connexion.commit()
            
            print(f"✅ Projet '{nom}' ajouté")
            fenetre.destroy()
            self.afficher_projets()
        
        ctk.CTkButton(fenetre, text="Ajouter", command=ajouter_projet, fg_color="green").pack(pady=20)
    
    def modifier_ligne_selectionnee(self):
        """
        Modifie le projet sélectionné dans le tableau.
        Pré-remplit les champs avec les valeurs actuelles.
        """
        selection = self.tableau.selection()
        if not selection:
            print("❌ Veuillez sélectionner une ligne à modifier")
            return
        
        # Récupérer les valeurs de la ligne sélectionnée
        valeurs = self.tableau.item(selection[0])["values"]
        id_projet = valeurs[0]
        nom_actuel = valeurs[1]
        date_creation_actuelle = valeurs[2] if valeurs[2] != "-" else ""
        date_expiration_actuelle = valeurs[3] if valeurs[3] != "-" else ""
        
        # Créer la fenêtre de modification
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Modifier un projet")
        fenetre.geometry("400x320")
        
        ctk.CTkLabel(fenetre, text=f"✏️ Modifier le projet ID {id_projet}", font=("Arial", 18, "bold")).pack(pady=15)
        
        ctk.CTkLabel(fenetre, text="Nom du projet * :").pack(pady=5)
        entree_nom = ctk.CTkEntry(fenetre, width=300)
        entree_nom.insert(0, nom_actuel)  # Pré-remplir avec la valeur actuelle
        entree_nom.pack(pady=5)
        
        ctk.CTkLabel(fenetre, text="Date de création (facultatif) :").pack(pady=5)
        entree_date_creation = ctk.CTkEntry(fenetre, width=300)
        entree_date_creation.insert(0, date_creation_actuelle)
        entree_date_creation.pack(pady=5)
        
        ctk.CTkLabel(fenetre, text="Date d'expiration (facultatif) :").pack(pady=5)
        entree_date_expiration = ctk.CTkEntry(fenetre, width=300)
        entree_date_expiration.insert(0, date_expiration_actuelle)
        entree_date_expiration.pack(pady=5)
        
        def modifier():
            nom = entree_nom.get().strip()
            date_creation = entree_date_creation.get().strip()
            date_expiration = entree_date_expiration.get().strip()
            
            if not nom:
                print("❌ Le nom est obligatoire")
                return
            
            date_creation = date_creation if date_creation else None
            date_expiration = date_expiration if date_expiration else None
            
            self.cursor.execute(
                "UPDATE projets SET nom = ?, date_creation = ?, date_expiration = ? WHERE id = ?",
                (nom, date_creation, date_expiration, id_projet)
            )
            self.connexion.commit()
            
            print(f"✅ Projet ID {id_projet} modifié")
            fenetre.destroy()
            self.afficher_projets()
        
        ctk.CTkButton(fenetre, text="Modifier", command=modifier, fg_color="orange").pack(pady=20)
    
    def supprimer_ligne_selectionnee(self):
        """Supprime le projet sélectionné dans le tableau."""
        selection = self.tableau.selection()
        if not selection:
            print("❌ Veuillez sélectionner une ligne à supprimer")
            return
        
        # Récupérer l'ID du projet
        valeurs = self.tableau.item(selection[0])["values"]
        id_projet = valeurs[0]
        nom_projet = valeurs[1]
        
        # Fenêtre de confirmation
        fenetre = ctk.CTkToplevel(self)
        fenetre.title("Confirmer la suppression")
        fenetre.geometry("400x200")
        
        ctk.CTkLabel(
            fenetre, 
            text=f"⚠️ Supprimer le projet ?\n\n'{nom_projet}' (ID: {id_projet})", 
            font=("Arial", 14)
        ).pack(pady=30)
        
        def confirmer():
            self.cursor.execute("DELETE FROM projets WHERE id = ?", (id_projet,))
            self.connexion.commit()
            print(f"✅ Projet ID {id_projet} supprimé")
            fenetre.destroy()
            self.afficher_projets()
        
        frame_boutons = ctk.CTkFrame(fenetre)
        frame_boutons.pack(pady=10)
        
        ctk.CTkButton(frame_boutons, text="Oui, supprimer", command=confirmer, fg_color="red").pack(side="left", padx=10)
        ctk.CTkButton(frame_boutons, text="Annuler", command=fenetre.destroy).pack(side="left", padx=10)
    
    def fermer_app(self):
        """Ferme proprement la connexion à la BDD puis l'application."""
        self.connexion.close()
        self.destroy()


# Lancement de l'application
if __name__ == "__main__":
    app = App()
    app.mainloop()