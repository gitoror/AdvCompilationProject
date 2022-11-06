# AdvCompilationProject

COMPIL

avoir fait les pretty printer

exemple type qui rend compte de l’interet du compilo 
doc qui decrit est la syntaxe du langage pour que le prof puisse ecrire des prog et essaie de compiler 
dossier : compilo, readme, doc de syntaxe, transparents de la présentation

Fonctionnement String:

remarque: lorsque l'on veut afficher un string, il faut remplacer "%d" par "%s" dans fmt (moule.asm)

1°) Pouvoir affichier un string sans espace:

remarque: 

bug: on ne peut pas afficher l'entrée (en string) de la fonction à cause de moule.asm (à résoudre)

ex. 
ast_string1=grammaire.parse(""" string main(x){
 
 z = "coucouAbc.DEf?" ;
 return (z);}
 
 """)
 
 
 2°) Concaténation:
 
 ex.
 
 ast_string1=grammaire.parse(""" string main(x){
 
 z = "coucou" + "a";
 return (z);}
 
 """)

 3°) Length:

 ex.

 ast_string1=grammaire.parse(""" int main(x){
 
 z = "coucou";
 i = len("coucoua");
 return (i);}
 
 """)
 
 
