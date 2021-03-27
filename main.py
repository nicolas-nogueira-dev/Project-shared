#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#|  Auteur : Nicolas Nogueira  |#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
from flask import *
from datetime import datetime
from werkzeug.security import *
from werkzeug.utils import *
import os
from os.path import join
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from random import *
from uuid import uuid4
import operator

def verif_mdp(pseudo,mdp):
    connexion = mysql.connect()
    curseur = connexion.cursor(cursor=DictCursor)
    curseur.execute("SELECT pseudonyme, mot_de_passe_chiffre FROM membre WHERE pseudonyme = %s", (pseudo))
    myresult = curseur.fetchone()
    curseur.close()
    if myresult == None or check_password_hash(myresult["mot_de_passe_chiffre"], mdp) == False:
        return False
    else:
        return True

def verif_nom_img(titre):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM `images` WHERE nom_image = %s", (titre))
    myresult = curseur.fetchone()
    curseur.close()
    if myresult == None :
        return True
    else:
        return False

def verif_pseudo(pseudo):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM `membre` WHERE pseudonyme = %s", (pseudo))
    myresult = curseur.fetchone()
    curseur.close()
    if myresult == None :
        return True
    else:
        return False

def avoir_img_actu():
    connexion = mysql.connect()
    curseur = connexion.cursor(cursor=DictCursor)
    curseur.execute("SELECT * FROM `images`")
    myresult = curseur.fetchall()
    curseur.close()
    shuffle(myresult)
    myresult_last = []
    count = 0
    for i in myresult:
        if count < 3 :
            myresult_last += [i]
            count += 1
        else:
            break
    return myresult_last

def avoir_img_top():
    connexion = mysql.connect()
    curseur = connexion.cursor(cursor=DictCursor)
    curseur.execute("SELECT * FROM `images`")
    myresult = curseur.fetchall()
    curseur.close()
    if myresult == () :
        return ()
    else :
        for i in myresult:
            i["nb_like"] = nb_like(i["nom_image"])
        myresult.sort(key=operator.itemgetter('nb_like'), reverse=True)
        myresult_last = []
        count = 0
        for i in myresult:
            if count < 3 :
                myresult_last += [i]
                count += 1
            else:
                break
        return myresult_last

def avoir_img_all():
    connexion = mysql.connect()
    curseur = connexion.cursor(cursor=DictCursor)
    curseur.execute("SELECT * FROM `images` ORDER BY date DESC")
    myresult = curseur.fetchall()
    curseur.close()
    return myresult

def avoir_image(id):
    connexion = mysql.connect()
    curseur = connexion.cursor(cursor=DictCursor)
    curseur.execute("SELECT * FROM `images` WHERE id = %s", (id))
    myresult = curseur.fetchone()
    curseur.close()
    return myresult

def avoir_image_pseudo(pseudo):
    connexion = mysql.connect()
    curseur = connexion.cursor(cursor=DictCursor)
    curseur.execute("SELECT * FROM `images` WHERE auteur = %s ORDER BY date DESC", (pseudo))
    myresult = curseur.fetchall()
    curseur.close()
    return myresult

def avoir_com(nom_img):
    connexion = mysql.connect()
    curseur = connexion.cursor(cursor=DictCursor)
    curseur.execute("SELECT * FROM `commentaire` WHERE nom_image = %s", (nom_img))
    myresult = curseur.fetchall()
    curseur.close()
    return myresult

def ajout_membre(pseudo,mdp):
    mdp_sec = generate_password_hash(mdp)
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO `membre`(`pseudonyme`, `mot_de_passe_chiffre`) VALUES (%s,%s)", (str(pseudo),str(mdp_sec)))
    curseur.close()
    connexion.commit()
    connexion.close()

def ajout_image(auteur,titre,nom_fichier):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO `images`(`auteur`, `nom_image`, `nom_fichier`) VALUES (%s,%s,%s)", (auteur, titre, nom_fichier))
    curseur.close()
    connexion.commit()
    connexion.close()

def remove_image(id):
    connexion = mysql.connect()
    curseur = connexion.cursor(cursor=DictCursor)
    curseur.execute("SELECT * FROM `images` WHERE id = %s", (id))
    last = curseur.fetchone()
    curseur.close()
    path = "stock/" + str(last["nom_fichier"])
    os.remove(path)
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("DELETE FROM `images` WHERE `images`.`id` = %s", (id))
    curseur.close()

def ajout_like(auteur,titre,nom_fichier):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO `coeur`(`auteur`, `titre`, `nom_fichier`) VALUES (%s,%s,%s)", (auteur, titre, nom_fichier))
    curseur.close()

def remove_like(auteur,titre,nom_fichier):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("DELETE FROM `coeur` WHERE `coeur`.`auteur` = %s AND `coeur`.`titre` = %s AND `coeur`.`nom_fichier` = %s", (auteur, titre, nom_fichier))
    curseur.close()

def ajout_commentaire(auteur,contenu,nom_img):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO `commentaire`(`auteur`, `contenu`, `nom_image`) VALUES (%s,%s,%s)", (auteur, contenu, nom_img ))
    curseur.close()

def remove_com(id):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("DELETE FROM `commentaire` WHERE `commentaire`.`id` = %s", (id))
    curseur.close()

def modification_com(contenu,id):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("UPDATE `commentaire` SET `contenu`=%s WHERE `id`=%s", (contenu,id))
    curseur.close()

def sauv_fichier(fichier,nom_fichier):
    fichier.save(join(app.config['UPLOAD_FOLDER'], nom_fichier))

def extension_autorisee(nom_du_fichier):
    return '.' in nom_du_fichier and \
        nom_du_fichier.rsplit('.', 1)[1].lower() in EXTENSIONS_AUTORISEES

def nb_like(nom):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM `coeur` WHERE titre = %s", (nom))
    myresult = curseur.fetchall()
    curseur.close()
    return len(myresult)

def savoir_si_like(auteur,titre,nom_fichier):
    connexion = mysql.connect()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM `coeur` WHERE auteur = %s AND titre = %s AND nom_fichier = %s", (auteur,titre,nom_fichier))
    myresult = curseur.fetchall()
    curseur.close()
    if myresult == () :
        return False
    else:
        return True


app = Flask(__name__)

app.config.from_json('config.json')

mysql = MySQL()
mysql.init_app(app)

EXTENSIONS_AUTORISEES = ['png', 'jpg', 'jpeg', 'gif']

app.secret_key = b'KfKkH48u1FZ24_r#g'
app.config['UPLOAD_FOLDER'] = join(os.getcwd(), 'stock')

@app.route("/")
def accueil():
    img_top = avoir_img_top()
    img = avoir_img_actu()
    return render_template("main.html", list_img=img, list_img_top=img_top, nb_like=nb_like, savoir_si_like=savoir_si_like)

@app.route("/toute_les_images")
def all_image():
    list_img = avoir_img_all()
    return render_template("all.html", list_img=list_img, nb_like=nb_like, savoir_si_like=savoir_si_like)

@app.route("/connexion", methods=['GET', 'POST'])
def connecting():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        mdp = request.form['mdp']
        if verif_mdp(pseudo,mdp):
            session['pseudo'] = pseudo
            return redirect('/')
        else:
            return render_template("erreur_connexion.html")
    elif "pseudo" in session:
        return redirect('/')
    return render_template("connexion.html")

@app.route("/inscription", methods=['GET', 'POST'])
def inscrip():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        mdp = request.form['mdp']
        if verif_pseudo(pseudo):
            ajout_membre(pseudo,mdp)
            return render_template("suc_inscription.html")
        else:
            print("problème connexion")
            return render_template("erreur_inscription.html")
    return render_template("inscription.html")

@app.route("/mon-profil")
def infos_moi():
    return render_template("moi.html")

@app.route("/profil")
def infos_profil():
    pseudo = request.args["pseudo"]
    img = avoir_image_pseudo(pseudo)
    return render_template("profil.html", pseudo=pseudo, list_img=img, nb_like=nb_like, savoir_si_like=savoir_si_like)

@app.route("/image")
def infos_image():
    id = request.args["id"]
    nom_img = request.args["nom_img"]
    img = avoir_image(id)
    commentaires = avoir_com(nom_img)
    return render_template("image.html", i=img, com=commentaires, nb_like=nb_like, savoir_si_like=savoir_si_like)

@app.route("/ajout_image", methods=['GET', 'POST'])
def ad_content():
    if request.method == 'POST':
        titre = request.form['titre']
        fichier = request.files['fichier']
        if extension_autorisee(fichier.filename):
            if verif_nom_img(titre) == True:
                prefixe = uuid4().hex
                nom_fichier = secure_filename(fichier.filename)
                nom_final = prefixe + '_' + nom_fichier
                sauv_fichier(fichier,nom_final)
                ajout_image(session['pseudo'],titre,nom_final)
                return render_template("envoie_image_win.html")
            else:
                return render_template("erreur_ajout_image.html", erreur=2)
        else:
            return render_template("erreur_ajout_image.html", erreur=1)
    return render_template("ajout_image.html")

@app.route("/ajout_commentaire", methods=['GET', 'POST'])
def ad_com():
    auteur = request.form["auteur"]
    contenu = request.form["contenu"]
    nom_img = request.form["nom_image"]
    ajout_commentaire(auteur,contenu,nom_img)
    return redirect("/")

@app.route("/suprimer_com")
def rem_com():
    id = request.args["id"]
    remove_com(id)
    return redirect("/")

@app.route("/modification_com", methods=['GET', 'POST'])
def change_com():
    if request.method == 'POST':
        id = request.form["id"]
        contenu = request.form["contenu"]
        modification_com(contenu,id)
        return redirect("/")
    else:
        id = request.args["id"]
        return render_template("modif_com.html", id=id)

@app.route("/ajout_like")
def ad_like():
    auteur = request.args["a"]
    titre = request.args["b"]
    nom_fichier = request.args["c"]
    ajout_like(auteur,titre,nom_fichier)
    return redirect("/")

@app.route("/dislike")
def rem_like():
    auteur = request.args["a"]
    titre = request.args["b"]
    nom_fichier = request.args["c"]
    remove_like(auteur,titre,nom_fichier)
    return redirect("/")

@app.route("/suprimer_image")
def rem_image():
    id = request.args["id"]
    remove_image(id)
    return redirect("/")

@app.route('/avoir_image')
def affiche_image():
    nom_image = request.args['nom_image']
    return send_from_directory(app.config['UPLOAD_FOLDER'], nom_image)

@app.route("/deconnexion")
def deconnexion():
    if "pseudo" in session:
        del session["pseudo"]
        return redirect("/")


app.run(debug=True)
