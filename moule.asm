extern printf, atoi, strcat, strlen

section .data
FMT
argc : dq 0
argv : dq 0
DECL_VARS
DECL_CLASS

section .text
global main
main:
  push rbp
  mov [argc], rdi
  mov [argv], rsi
  INIT_VARS
  BODY
  RETURN
  mov rdi, fmt
  mov rsi, rax
  call printf
  pop rbp
  ret