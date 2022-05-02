MSG_PIOCHE1 = "Voici vos deux premières cartes: "
MSG_PIOCHE2 = "Voici les trois cartes du flop: "
MSG_PIOCHE3 = "Voici la carte du turn: "
MSG_PIOCHE4 = "Voici la carte de la river: "
MSG_RECAP_CARTES = "Vous avez donc à votre disposition les cartes suivantes:"
MSG_QUESTION_MISE = "Voulez-vous miser quelque chose [O/N]?"
MSG_ERREUR_MISE = "Veuillez répondre par Oui ou par Non:"
MSG_PARI_MISE = "Sur quel résultat voulez-vous miser [p/dp/b/s/c/f/ca/sc] ?"
MSG_ERREUR_PARI = "Veuillez entrer un résultat valable : p/dp/b/s/c/f/ca/sc ?"
MSG_RESTE_MISE = "Combien voulez-vous miser?"
MSG_BITCOIN = "Ƀ"
MSG_ERREUR_MONTANT = "Veuillez entrer un montant entier positif inférieur à "
MSG_SOLDE = "Il vous reste "
MSG_CONTINUER = "Voulez-vous continuer à jouer [O/N]? "
MSG_FIN_1 = "Merci d'avoir joué. Vous repartez avec "
MSG_FIN_2 = " Ƀ. Bye"
MSG_GAIN_PARI_1 = "Votre pari "
MSG_GAIN_PARI_2 = " vous a rapporté "
import random

paris_possibles = ['p','dp','b','s','c','f','ca','sc']

def carte_to_string(carte):
    """Cree la chaine de caracteres correspondant a la carte."""
    symboles = [str(i+1) for i in range(10)] + ["V", "D", "R"]
    couleurs = ["♥", "♦", "♣", "♠"]
    res = symboles[carte[0] - 1] + couleurs[carte[1] - 1]
    return res

def creer_jeu():
    """Cree un jeu de cartes."""
    jeu = []
    for i in range(1,  14):
        for j in range(1, 5):
            jeu.append((i, j))
    return jeu

def question_mise():
    x = input(MSG_QUESTION_MISE)
    while x != 'O' and x != 'N':
        x = input(MSG_ERREUR_MISE)
    return x

def pari():
    x = input(MSG_PARI_MISE)
    while x not in paris_possibles:
        x = input(MSG_ERREUR_PARI)
    return x

def valeur_mise(solde):
    print(MSG_SOLDE,solde,MSG_BITCOIN + '.', MSG_RESTE_MISE)
    x = int(input())
    while x > solde:
        print(MSG_ERREUR_MONTANT,solde)
        x = int(input())
    return x
    
def pari_juste(x, cartes):
    if x == 'p':
        res = paire(cartes)
    elif x == 'dp':
        res = double_paire(cartes)
    elif x == 'b':
        res = brelan(cartes)
    elif x == 'c':
        res = couleur(cartes)
    elif x == 'f':
        res = full(cartes)
    elif x == 'ca':
        res = carre(cartes)
    else:
        res = False
    return res

def pioche2(cartes):
    print(MSG_PIOCHE2, cartes[2], cartes[3], cartes[4])
    print(MSG_RECAP_CARTES, cartes[0], cartes[1], cartes[2], cartes[3], cartes[4])
    return

def pioche3(cartes):
    print(MSG_PIOCHE3, cartes[5])
    print(MSG_RECAP_CARTES, cartes[0], cartes[1], cartes[2], cartes[3], cartes[4], cartes[5])
    return

def pioche4(cartes):
    print(MSG_PIOCHE4, cartes[6])
    print(MSG_RECAP_CARTES, cartes[0], cartes[1], cartes[2], cartes[3], cartes[4], cartes[5], cartes[6])
    return

def paire(cartes):
    dico = {}
    for i in cartes:
        dico[i[0]] = dico.get(i[0], 0) + 1
    if max(dico.values()) > 1:
        return True
        
def brelan(cartes):
    dico = {}
    for i in cartes:
        dico[i[0]] = dico.get(i[0], 0) + 1
    if max(dico.values()) > 2:
        return True

def carre(cartes):
    dico = {}
    for i in cartes:
        dico[i[0]] = dico.get(i[0], 0) + 1
    if max(dico.values()) > 3:
        return True

def double_paire(cartes):
    dico = {}
    for i in cartes:
        dico[i[0]] = dico.get(i[0], 0) + 1
    x = list(filter(lambda x : x != 1 ,dico.values()))
    if len(x) > 1:
        return True

def full(cartes):
    dico = {}
    res = False
    for i in cartes:
        dico[i[0]] = dico.get(i[0], 0) + 1
    x = list(filter(lambda x : x != 1 ,dico.values()))
    if len(x) > 1 and 3 in dico.values():
        res = True
    elif len(x) > 1 and 4 in dido.values():
        res = True
    return res

def couleur(cartes):
    dico = {}
    for i in cartes:
        dico[i[1]] = dico.get(i[1], 0) + 1
    if max(dico.values()) > 4:
        return True

def probabilites(pari):
    f = open('Users\Julien\Documents\projets infos\probabilites.txt')
    liste = []
    for line in f:
        liste.append(line.split(' '))
    for i in range(len(liste)):
        if pari == liste[i][0]:
            return (float(liste[i][1].strip())/100)

def gain(mise, pari, i):
    bitcoins_gagnes = int(mise * (1/(probabilites(pari)*i)))
    return bitcoins_gagnes

def continue_or_not():
    x = input(MSG_CONTINUER)
    while x != 'O' and x != 'N':
        x = input(MSG_CONTINUER)
    return x
    

def cartes_propres(cartes):
    liste = []
    for i in range(len(cartes)):
        liste.append(carte_to_string(cartes[i]))
    return liste

def poker_un_joueur(s):
    random.seed(s)
    playagain = 'yes'
    solde = 100
    while playagain == 'yes':
        deck = creer_jeu()
        cartes = random.sample(deck, 7)
        jolies_cartes = cartes_propres(cartes)
        gain1, gain2, gain3 = 0, 0, 0
        print(MSG_PIOCHE1, jolies_cartes[0], jolies_cartes[1])
        if question_mise() == 'O':
            choix1 = pari()
            argent_mise1 = valeur_mise(solde)
            solde -= argent_mise1
            if pari_juste(choix1, cartes):
                gain1 = gain(argent_mise1, choix1, 1) - argent_mise1
                
        pioche2(jolies_cartes)
        if question_mise() == 'O':
            choix2 = pari()
            argent_mise2 = valeur_mise(solde)
            solde -= argent_mise2
            if pari_juste(choix2, cartes):
                gain2 = gain(argent_mise2, choix2, 2) - argent_mise2
                
        pioche3(jolies_cartes)
        if question_mise() == 'O':
            choix3 = pari()
            argent_mise3 = valeur_mise(solde)
            solde -= argent_mise3
            if pari_juste(choix3, cartes):
                gain3 = gain(argent_mise3, choix3, 3) - argent_mise3
                
        pioche4(jolies_cartes)
        if gain1 != 0:
            print(MSG_GAIN_PARI_1, choix1,':',argent_mise1, MSG_GAIN_PARI_2, gain1,MSG_BITCOIN)
            solde += gain1 + argent_mise1
        if gain2 != 0:
            print(MSG_GAIN_PARI_1, choix2,':',argent_mise2, MSG_GAIN_PARI_2, gain2,MSG_BITCOIN)
            solde += gain2 + argent_mise2
        if gain3 != 0:
            print(MSG_GAIN_PARI_1, choix3,':',argent_mise3, MSG_GAIN_PARI_2, gain3,MSG_BITCOIN)
            solde += gain3 + argent_mise3
        print(MSG_SOLDE, solde)

        if continue_or_not() == 'N':
            playagain = 'game over'

            print(MSG_FIN_1, solde,MSG_FIN_2)
        return

poker_un_joueur(1)