extern printf, atoi

section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
car.speed : dq 0
class.Car.speed : dq 0
class.arg.Car.speed : dq 0

class.oarg.Human.Car.speed : dq 0

class.Human.Car.speed : dq 0
human.car.speed : dq 0




section .text
global main

CarInit: 
  
  ; calculus in between with vars
  mov rax, [class.arg.Car.speed]
  mov [class.Car.speed], rax
  ret

Car.acc:
  mov rax, 29
  mov [class.Car.speed], rax
  ret

HumanInit:
  ; calculus in between with vars
  mov rax, [class.oarg.Human.Car.speed]
  mov [class.Human.Car.speed], rax
  ret

main:
  push rbp
  mov [argc], rdi
  mov [argv], rsi
  


  ; init arg of constr just before
  mov rax, 6
  mov [class.arg.Car.speed], rax
  ; make calculus by constr to create attr 
  call CarInit
  ; put the attr value in the attr of the object
  mov rax, [class.Car.speed]
  mov [car.speed], rax

  ; method acc for object car
  call Car.acc
  mov rax, [class.Car.speed]
  mov [car.speed], rax
  
  mov rax, [car.speed]
  mov [class.oarg.Human.Car.speed], rax
  ; Human
  call HumanInit
  mov rax, [class.Human.Car.speed]
  mov [human.car.speed], rax
  
  mov rax, [human.car.speed]
  mov rdi, fmt
  mov rsi, rax
  call printf
  pop rbp
  ret
  
 
