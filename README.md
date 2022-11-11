COMPILO

Général

Seulement les int sont acceptés pour l'entrée du main

structure de main est sous la forme

<int/string> main(<var_list>){
  classes (initialisation des classes)
  bcom
  return <(exp)>
}

remarque:
si on veut les entrées soient de string, il faut remplace ligne call atoi par mov rax, rdi lorsqu'on traite les entrées(dans fonction asm_prog() de script .py, variable s)

Partie Class (Tom Marini):

L'objectif de cette partie est d'apporter une extension au compilateur fait en cours. Cette extension est l'implémentation des objets. Cependant elle ne fonctionne pas encore. Il y a toutes les fonctions permettant d'écrire le programme.asm pour les classes, mais les erreurs sont dues à une mauvaise manipulation de l'ast. J'ai des erreurs du type : 'Token' object has no attribute 'data'. En observant l'ast je me rend bien comtpe du problème. Un moyen pour le résoudre serait de modifier la grammaire pour que l'ast soit comme je le souhaite, mais je n'y arrive pas.

Les pretty printer marchent au moins pour la déclaration de la classe sans méthodes, l'instanciation d'une classe (appel constructeur) et l'appel à des attributs.
Le fichier class.asm produit un code fonctionnel. Il montre comment je comptais créer les objets en assembleur. On y voit notamment l'appel de fonctions pour le constructeur et les méthodes. Les attributs sont des variables. Lorsque l'attribut d'un objet doit changer de valeur, on demande à l'attribut de la classe de changer de valeur puis on affecte l'attribut de la classe à l'attribut de l'objet. L'attribut de la classe est unique et il sert uniquement d'intermédiaire pour les méthodes et le contructeur. On aurait sûrement pu faire sans en mettant des arguments dans des registres ou dans la pile.

J'ai une diffulté lors de l'appel du contructeur pour créer un objet : je dois passer par des listes python pour stocker le nom des attributs que l'objet devra avoir car une fois la classe déclarée je ne vois pas comment on peut relire le nom des attributs. Ils doivent être déclarés avant le lancement de l'éxecution et par conséquent on ne peut pas faire appel à la fonction constructeur dans le code assembleur... Peut être que la grammaire est mal conçue.
La syntaxe choisie :
class Voiture {
  def Voiture(vitesse, NbEnfants, NbParents) {
    self.vitesse = vitesse;
    self.NbPassager = NbEnfants + NbParents;
  }
  def arret() {
    self.vitesse = 0;
  }
  def accelere() {
    self.vitesse = 30;
  }
}

voiture = Voiture(10,1,1)
voiture.accelere()
v = voiture.vitesse
print(v)



Partie String (Xinhao ZHAO):
Objectif de cette partie est d'apporter une extension au compilateur fait en cours, qui est expression string. Cette partie permet de réaliser 
1°) printer un string
2°) concaténation (soit directement entre les chaînes, ex. "coucou"+"hello", soit entre les variables)
3°) trouver la taille d'une chaîne de caractère (soit avec une chaine, ex len["coucou"], soit avec une variable)

Un inconvénient dans le code est d'utiliser 3 listes pour gérer les données string: 
1°)je stock les chaînes dans list_str (une liste python) lors d'affectation (ex. x = "coucou", et je stock "coucou" dans list_str pour ensuite construire une adresse pour "coucou" dans .asm).
2°)je stock les chaînes dans list_sum (une liste python) lors de concaténation entre deux string (ex. z = "coucou" + "hello", et je stock "coucou" et "hello" dans list_sum pour ensuite construire des adresses dans .asm).
3°)je stock les chaînes dans list_len (une liste python) lorsqu'on veut la taille d'une chaîne (ex. z = len["coucou"], et je stock "coucou" dans list_str pour ensuite construire une adresse).
Ce sera pas mal si l'on peut stocker les chaînes dans une liste, mais je n'ai pas de temps. En plus si on fait (x = "coucou", y = len["coucou"], ça va générer deux adresses "coucou" et ça fonctionne dans .asm). 

Pour éviter le conflit entre class et length, je décide de changer syntaxe length comme (len["coucou"], et len[x]).


Fonctionnement et syntaxe (avec exemple d'utilisation)

1°) Pouvoir affichier un string sans ou avec espace:

ex. 

string main(x){

z = "coucou Abc.DEf?" ;
return (z);}

""")


2°) Concaténation:

ex.1

string main(x){

z = "coucou" + "a"; 
return (z);}


ex.2

string main(x){ x = "coucou"; 
z = "hello"; 
y = x + z; 
return (y);}



3°) Length:

ex.1

int main(x){
i = len["coucoua"]; 
return (i);}

ex2.

int main(x){ 
x = "coucou"; 
y = len[x]; 
return (y);}

"


Partie typage dynamique (Kamal Mohamed Amine)
Ce mini-compilateur a été conçu dans l'optique de venir apporter une extension au Compilateur de Xinhao Zhao en introduisant le typage dynamique. En premier lieu, il s'agissait de rajouter le type des variables au sein même de exp_var en faisant en sorte de garder la variable cachée et de ne l'expliciter que lors de l'appel au prettyprinter de exp_var. Un choix ayant été fait au préalable avant d'avoir accès au mini-compilateur avec les strings d'implémentés était de définir le type des variables avec un entier pouvant prendre les valeurs "0" pour un entier, "1" pour un string. Pour généraliser aux classes également, une serait d'introduire un compteur avec le nombre de classes, en assignant à chaque classe définie un entier n. On serait donc en mesure de reconnaitre la classe de la variable en associant à chaque nombre au delà de 2 une classe. En deuxième lieu, il s'agissait d'introduire l'équivalent des fonctions int() et str() dans Python : il s'agit des 2 fonctions atoi et itoa. Une première idée était de les définir sous formes de fonctions comme elles le sont concrètement. Mais n'ayant aucune personne dans le groupe traitant des fonctions, et après une tentative d'implémentation avec beaucoup de difficultés, j'ai plutôt choisi de les définir en tant que commandes, tout en les introduisant dans les blocs de commandes qui nécessiteraient une modification.

Contraintes rencontrées : Suite à des contraintes liées au temps, le problème principal était de bien comprendre le fonctionnement de print et d'adapter mon implémentation à celle des strings, les erreurs s'empilaient et je n'ai pas réussi à obtenir un résultat concret. La 2ème contrainte était lié aux manques et à la complexité des exemples de compilateurs introduisants le typage dynamique, il fallait donc trouver une solution qui pourrait simplifier l'implémentation quitte à perdre en pertinence et beaucoup de mémoire.

Une solution pratique qu'il fallait adapter était d'éliminer les commandes de string qui s'avéraient problématiques plutôt que de chercher à les affronter de face. Ce qui aurait réduit la quantité de nouvelles informations auxquelles j'étais confrontée et qui aurait permis une implémentation fonctionnelle.

