COMPILO

Général

Seulement les int sont acceptés pour l'entrée du main
remarque:
si on veut les entrée soient de string, il faut remplace ligne call atoi par mov rax, rdi lorsqu'on traite les entrées(dans fonction asm_prog() de script .py, variable s)

Partie Class (par Tom Marini):

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
i = len("coucoua"); 
return (i);}

ex2.

int main(x){ 
x = "coucou"; 
y = len[x]; 
return (y);}

"


Partie typage dynamique (Kamal Mohamed Amine)

