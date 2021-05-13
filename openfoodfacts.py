"""
Ce module permet de récupérer les données du site web OpenFoodFacts ("https://fr.openfoodfacts.org/").
Le module contient une fonction de scraping de données récupérant diverses informations sur tous les produits recensés sur le site.
Il est aussi accompagné d'une mesure du temps de computation vous indiquant en combien de temps l'opération a eu lieu.
Attention, en fonction du nombre de pages web à scrapper, le temps de computation peut vite exploser.
"""


def scrap_openfoodfacts(nb_pages = 50) :
    """ Il s'agit de la fonction principale du module.
    Cette dernière crée dans votre espace de travail un DataFrame Pandas contenant les informations scrapées sur le site OpenFoodFacts.
    L'argument "nb_pages" permet de régler le nombre de page à scraper.
    Veuillez ne pas trop l'augmenter afin que l'opération prenne un temps raisonnable.
    Il faut compter environ 30 secondes pour scraper une page (25 minutes pour les 50 pages par défaut).
    27 variables sont scrapées pour chaque nouvelle donnée.
    """
    # Importation des modules
    import time
    from time import sleep
    import numpy as np
    import requests
    import re
    from bs4 import BeautifulSoup
    
    # Mesure du temps
    start_time = time.time()
    
    # Initialisation de la liste records récoltant nos données
    records = []
    #Initialisation de la valeur des erreurs à implémenter dans le DataSet
    error = np.NaN
    
    # On récupère l'url de chaque produit sur le nombre de pages souhaitées
    for i in range(1,nb_pages+1) :

        r = requests.get(('https://fr.openfoodfacts.org/' + str(i)))
        soup = BeautifulSoup(r.text, 'html.parser')

        products = soup.find_all('ul', {'class' : "products"})

        products = products[0].find_all('a')

        liste_url = ['https://fr.openfoodfacts.org/' + elt['href'] for elt in products]

        # Pour chaque produit on place dans des variables les données que l'on souhaite scraper
        for url in liste_url :
                s = requests.get(url)
                soup = BeautifulSoup(s.text, 'html.parser')
                
                # Si la donnée peut être récupérée, on la place dans notre variable, sinon on la replace par une erreur
                try :            
                    name = soup.title.text[:-2]
                except :
                    name = error

                try :
                    code_barre = soup.find('span', attrs = {'style' : "speak-as:digits;"}).text
                except :
                    code_barre = error

                try:
                    nutri_score = soup.find('div', attrs = {'id' : 'nutriscore_drop'}).contents[-2].text[-1]
                except : 
                    nutri_score = error

                try :
                    nova = soup.find(style = "margin-bottom:1rem;max-width:100%")['alt'][0]
                    nova = [float(elt) for elt in nova.split() if elt.replace('.', '').isdigit()].pop()
                except :
                    nova = error

                try :
                    caractéristiques = soup.find(itemprop="description").text
                except :
                    caractéristiques = error

                try :
                    ingrédients  = soup.find(property="food:ingredientListAsText").text
                except : 
                    ingrédients = error

                try :
                    palme = soup.find('span', {'class' : "alert round label ingredients_analysis green"}).contents[-1][:-3]
                except :
                    palme = error
                    
                try :
                    palme2 = soup.find(href="/ingredients-issus-de-l-huile-de-palme/huile-de-palme").text
                except : 
                    palme2 = error
                 
                try :
                    repères_nutritionnels = soup.find_all('div', {'class' : "small-12 xlarge-6 columns"})[1].text.split("\n")[-5:-1]
                except : 
                    repère_nutritionnels = error
                    
                # On découpe les repères nutritionnels en 4 variabes distinctes (matière grasse, acide gras, sucre et sel)
                # Puis on les transforme en float pour faciliter l'analyse
                liste_repères_nutri = repères_nutritionnels
                
                try :
                    matière_grasse = liste_repères_nutri[0]
                    matière_grasse = [float(elt) for elt in matière_grasse.split() if elt.replace('.', '').isdigit()].pop()
                except :
                    matière_grasse = error
                    
                try :    
                    acide_gras = liste_repères_nutri[1]
                    acide_gras = [float(elt) for elt in acide_gras.split() if elt.replace('.', '').isdigit()].pop()
                except : 
                    acide_gras = error
                                    
                try :
                    sucre = liste_repères_nutri[2]
                    sucre = [float(elt) for elt in sucre.split() if elt.replace('.', '').isdigit()].pop()
                except :
                    sucre = error
                
                try :
                    sel = liste_repères_nutri[3]
                    sel = [float(elt) for elt in sel.split() if elt.replace('.', '').isdigit()].pop()
                except : 
                    sel = error
                
                # On utilise la même méthode sur les KJ et les KCAL pour les transformer en float
                try :
                    kj = soup.find(id="nutriment_energy-kj_tr").find('td', {'class' : 'nutriment_value'}).text[9: 13]
                    kj = [float(elt) for elt in kj.split() if elt.replace('.', '').isdigit()].pop()
                except : 
                    kj = error

                try :
                    kcal = soup.find(id="nutriment_energy-kcal_tr").find('td', {'class' : 'nutriment_value'}).text[9:15]
                    kcal = [float(elt) for elt in kcal.split() if elt.replace('.', '').isdigit()].pop()
                except : 
                    kcal = error
                    
                try : 
                    eco_score = soup.find(id="ecoscore_drop").contents[-2].text[-1]
                except :
                    eco_score = error

                #Pour toutes les variables suivantes; l'utilisation de Regex va nous permettre d'extraire la donnée
                info = soup.find('div',{ 'class':'medium-12 large-8 xlarge-8 xxlarge-8 columns'})
                infos = []

                for el in info:
                    try:
                        infos.append(el.text)
                    except: 
                        pass

                try :             
                    r = re.compile('^Quan.*$')
                    quantity = list(filter(r.match, infos))[0].split(':')[-1]
                except : 
                    quantity = error

                try :
                    r = re.compile('^Conditionnement.*$')
                    conditionnement = list(filter(r.match, infos))[0].split(':')[-1]
                except :
                    conditionnement = error

                try :
                    r = re.compile('^Marques.*$')
                    marques = list(filter(r.match, infos))[0].split(':')[-1]
                except :
                    marques = error

                try :
                    r = re.compile('^Catégories.*$')
                    catégories = list(filter(r.match, infos))[0].split(':')[-1]
                except : 
                    catégoris = error

                try :
                    r = re.compile('^Labels.*$')
                    labels = list(filter(r.match, infos))[0].split(':')[-1]
                except :
                    labels = error

                try : 
                    r = re.compile('^Lieux.*$')
                    lieux = list(filter(r.match, infos))[0].split(':')[-1]
                except :
                    lieux = error

                try :
                    r = re.compile('^Code.*$')
                    code = list(filter(r.match, infos))[0].split(':')[-1]
                except :
                    code = error

                try : 
                    r = re.compile('^Lien.*$')
                    lien = list(filter(r.match, infos))[0].split(':')[-1]
                except :
                    lien = error

                try :
                    r = re.compile('^Magasins.*$')
                    magasins = list(filter(r.match, infos))[0].split(':')[-1]
                except :
                    magasins = error

                try :
                    r = re.compile('^Origine.*$')
                    origine = list(filter(r.match, infos))[0].split(':')[-1]
                except :
                    origine = error

                try :
                    r = re.compile('^Pays.*$')
                    pays = list(filter(r.match, infos))[0].split(',')[1:]
                except :
                    pays = error
                    
                nb_pays = len(pays)

                #On place nos différentes variables dans la liste records
                records.append((name, code_barre, nutri_score, nova, caractéristiques, ingrédients, palme, palme2,
                                kj, kcal, eco_score, quantity, conditionnement, marques, catégories, labels, lieux, code, lien, magasins,
                                origine, pays, nb_pays, matière_grasse, acide_gras, sucre, sel))

        i+=1
        
        # On laisse un temps d'attente entre chaque itération pour ne pas provoquer une erreur dû au trop grand nombre de requêtes envoyées 
        # vers Open Fact Food
        sleep(1)

    # On construit le DataFrame, puis on l'exporte dans l'espace de travail
    import pandas as pd
    df = pd.DataFrame(records, columns = ['Produit', 'CodeBarre', 'NutriScore', 'Nova', 'Caractéristiques', 'Ingrédients', 
                                      'NoPalme','Palme', 'KJ', 'KCAL', 'Eco-Score', 'Quantité', 'Conditionnement', 
                                      'Marque', 'Catégorie', 'Label', 'Lieux', 'Code', 'Lien', 'Magasin', 
                                      'Origine', 'Pays', 'NbPays', 'MatGrasse', 'AcideGras', 'Sucre', 'Sel'])

    df.to_csv('openfoodfacts.csv', index=False, encoding='utf-8')

    # On affiche le temps d'éxecution de la fonction
    print("Temps d'éxecution : "+"--- %s seconds ---" % (time.time() - start_time))
    print("Merci pour votre patience !")