#Compilateur : Mohamed Amine KAMAL

Ce mini-compilateur a été conçu dans l'optique de venir apporter une extension au Compilateur de Xinhao Zhao en introduisant le typage dynamique. 
En premier lieu, il s'agissait de rajouter le type des variables au sein même de exp_var en faisant en sorte de garder la variable cachée et de ne l'expliciter que lors de l'appel au prettyprinter de exp_var. Un choix ayant été fait au préalable avant d'avoir accès au mini-compilateur avec les strings d'implémentés était de définir le type des variables avec un entier pouvant prendre les valeurs "0" pour un entier, "1" pour un string. Pour généraliser aux classes également, une serait d'introduire un compteur avec le nombre de classes, en assignant à chaque classe définie un entier n. On serait donc en mesure de reconnaitre la classe de la variable en associant à chaque nombre au delà de 2 une classe.
En deuxième lieu, il s'agissait d'introduire l'équivalent des fonctions int() et str() dans Python : il s'agit des 2 fonctions atoi et itoa. Une première idée était de les définir sous formes de fonctions comme elles le sont concrètement. Mais n'ayant aucune personne dans le groupe traitant des fonctions, et après une tentative d'implémentation avec beaucoup de difficultés, j'ai plutôt choisi de les définir en tant que commandes, tout en les introduisant dans les blocs de commandes qui nécessiteraient une modification.

Contraintes rencontrées :
Suite à des contraintes liées au temps, le problème principal était de bien comprendre le fonctionnement de print et d'adapter mon implémentation à celle des strings, les erreurs s'empilaient et je n'ai pas réussi à obtenir un résultat concret.
La 2ème contrainte était lié aux manques et à la complexité des exemples de compilateurs introduisants le typage dynamique, il fallait donc trouver une solution qui pourrait simplifier l'implémentation quitte à perdre en pertinence et beaucoup de mémoire.

Une solution pratique qu'il fallait adapter était d'éliminer les commandes de string qui s'avéraient problématiques plutôt que de chercher à les affronter de face. Ce qui aurait réduit la quantité de nouvelles informations auxquelles j'étais confrontée et qui aurait permis une implémentation fonctionnelle.
