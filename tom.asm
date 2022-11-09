extern printf, atoi, strcat, strlen

section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0
a : dq 0
class.arg.Human.age : dq 0
class.Human.footSize : dq 0
s : dq 0
speed : dq 0
Z : dq 0
h.age : dq 0
X : dq 0
class.arg.Car.speed : dq 0
class.arg.Human.size : dq 0
Y : dq 0
class.Human.age : dq 0
h.footSize : dq 0
class.Car.speed : dq 0
car.speed : dq 0




section .text
global main
main:
  push rbp
  mov [argc], rdi
  mov [argv], rsi
  
    mov rbx, [argv]
    mov rdi, [rbx + 8]
    xor rax, rax 
    call atoi
    mov [X], rax
    
    mov rbx, [argv]
    mov rdi, [rbx + 16]
    xor rax, rax 
    call atoi
    mov [Y], rax
    
    mov rbx, [argv]
    mov rdi, [rbx + 24]
    xor rax, rax 
    call atoi
    mov [Z], rax
    
  

            mov rax, 28

            mov [speed], rax
            
        mov rax, [speed]
        mov [class.arg.Car.speed], rax
        
      call CarInit
      
          mov rax, [class.Car.speed]
          mov [car.speed], rax
          
            mov rax, 1

            mov [s], rax
            
            mov rax, 21

            mov [a], rax
            
        mov rax, [s]
        mov [class.arg.Human.size], rax
        
        mov rax, [a]
        mov [class.arg.Human.age], rax
        
      call HumanInit
      
          mov rax, [class.Human.footSize]
          mov [h.footSize], rax
          
          mov rax, [class.Human.age]
          mov [h.age], rax
          
            mov rax, [h.age]
            mov [Y], rax
            
  mov rax, [Y]

  mov rdi, fmt
  mov rsi, rax
  call printf
  pop rbp
  ret