extern printf, atoi

section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
list_length : dq 0
list : dq 0
a : dq 0
c : dq 0
class.car.var1 : dq 0
class.car.var2 : dq 0
car.speed : dq 0
car.nbppl : dq 0
class.car.speed : dq 0
class.car.nbppl : dq 0

section .text
global main

ctrCar: 
  ; calculus in between with vars
  mov rax, [class.car.var1]
  mov [class.car.speed], rax
  mov rax, [class.car.var2]
  mov [class.car.nbppl], rax
  ret

Car.acc:
  mov rax, 29
  mov [class.car.speed], rax
  ret

Car.SetNbPpl:
  mov rax, 2
  mov [class.car.nbppl], rax
  ret


main:
  push rbp
  mov [argc], rdi
  mov [argv], rsi
  
  mov rbx, [argv]
  mov rdi, [rbx + 8]
  xor rax, rax
  call atoi
  mov [list_length], rax

  mov rax, 3
  mov [a], rax 

  ; init arg of constr just before
  mov rax, 6
  mov [class.car.var1], rax
  mov rax, 9
  mov [class.car.var2], rax
  ; make calculus by constr to create attr 
  call ctrCar
  ; put the attr value in the attr of the object
  mov rax, [class.car.speed]
  mov [car.speed], rax
  mov rax, [class.car.nbppl]
  mov [car.nbppl], rax

  ; method acc for object car
  call Car.acc
  mov rax, [class.car.speed]
  mov [car.speed], rax
  
  ; method SetNbPpl for object car
  call Car.SetNbPpl
  ; cmt le code est censé savoir que c'est tel arg qui est changé ??
  ; faire : tous les arg de l'obj = tous ceux de la classe (avec speed donc..)
  ; mais c'est pas très opti
  ; et si la meth retourne qqch ? => pour plus tard
  mov rax, [class.car.nbppl]
  mov [car.nbppl], rax

  
  mov rax, [car.speed]
  mov rdi, fmt
  mov rsi, rax
  call printf
  pop rbp
  ret
  
 