# Projet compilation

# Tom : extension objets
Voici un exemples de fonctionnement du compilo pour la programmation d'objets proches de python : 

- Définir une classe toujours avant le bloc de commandes du main. 
- Une classe contient un constructeur dans lequel sont initialisés des attributs et des méthodes. 
- Création d'un objet en appelant le constructeur. 
- Appel de méthodes, avec la particularité de devoir mettre le nom de la classe avec un espace après l'appel. 
- Affectation d'attirbuts à des variables.

```
main(X,Y,Z) {
      class Car {
        def Car(speed) {
          self.speed=speed+1;
        }
        method accelerate() {
          self.speed = self.speed + 50;
        }
        method brake() {
          self.speed = 0;
        }
      }
      speed=28;
      car = Car(speed);
      car.brake() Car;
      car.accelerate() Car;    
      Y = car.speed;
      return (Y);
    }
```
Vous pouvez essayer d'exécuter le programme `compiloTom.py` avec l'ast1 et d'exécuter `tom.asm` :
```
nasm -f elf64 tom.asm
gcc -np-pie -fno-pie tom.o
./a.out
```
Autre exemple fonctionnel à l'écexution :
- Affectation d'un objet à l'attribut d'une classe. Attention, il faut déclarer les classes dans le bon ordre.
- Arguments pouvant être des objets dans le constructeur.
- Affectation de l'attribut d'un attribut.
- Conception limitée à un niveau. On ne peut pas faire une 3ème classe qui aurait un attribut égal à un objet qui a déjà un objet en attribut.
- Impossible de mettre en argument d'un constructeur d'une classe un objet issu de la même la classe. (pas de Tree(value,left,right). Le problème vient de l'initalisation. (manque de temps pour réaliser un élément null, difficile à intégrer)

```
main(X,Y,Z) {
      class Car {
        def Car(speed) {
          self.speed=speed+1;
        }
      }
      class Human {
        def Human(Car car) {
          self.mycar=car;
        }
      }
      speed=28;
      car = Car(speed);
      h=Human(Car car);
      h.car.speed = 2;
      Y = h.car.speed;
      return (Y);
    }
```

## Travail d'équipe 
Les objets sont censés fonctionner avec les strings, extension du compilo réalisée par Xinhao. Une tentative a été effectuée mais elle ne permet pas du tout d'exploiter les objets, voir `compiloTom_Xinhao.py`.

## Organisation du code
Il y a beaucoup de lignes car je n'ai pas eu le temps d'optimiser mon code ... 

## Pistes d'amélioration 
Je suis définitivement limité par le fait que dans ma conception un objet n'existe que via ses attributs. Cela rend compliqué les choses mais on voit qu'on peut déjà s'en sortir pour faire des objets simples qui ont des méthodes et des attributs. Si je devais continuer le projet, j'essaierais de passer par les pointeurs.

## Résultat assembleur
Si on a analyse le résulat produit par le compilo en assembleur, on voit que la déclaration des variables n'est pas parfaite (lettres qui trainent, variables inutiles). Sinon le reste est cohérent.

## Tom : fin

# Xinhao : extension string

# Mohamed Amine : extension typage dynamique
