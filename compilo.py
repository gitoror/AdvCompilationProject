from os import cpu_count
import lark

###############
## grammaire ##
###############



grammaire = lark.Lark(r"""

exp : SIGNED_NUMBER                  -> exp_nombre
| IDENTIFIER                         -> exp_var
| exp OPBIN exp                      -> exp_opbin
| "(" exp ")"                        -> exp_par

com : IDENTIFIER "=" exp ";"         -> assignation
| "if" "(" exp ")" "{" bcom "}"      -> if
| "while" "(" exp ")" "{" bcom "}"   -> while
| "print" "(" exp ")"                -> print

bcom : (com)*

prg : "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}"

var_list :                           -> vide
| IDENTIFIER ("," IDENTIFIER)*       -> aumoinsune

IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/ 

OPBIN : /[+\-*>]/

%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", 
start="prg")

####################
## pretty printer ##
####################

# exp

def pp_exp(e):
  # Tree(data, children [ ])
  # Token(Type, value)
  if e.data in {"exp_nombre", "exp_var"}:
    return e.children[0].value
  elif e.data == "exp_opbin":
    return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"
  elif e.data == "exp_par":
    return f"({pp_exp(e.children[0])})"

def vars_exp(e):
  if e.data == "exp_nombre" :
    return set()
  if e.data == "exp_var":
    return {e.children[0].value}
  elif e.data == "exp_opbin":
    L = vars_exp(e.children[0])
    R = vars_exp(e.children[2])
    return L | R # union de L et R
  elif e.data == "exp_par":
    return vars_exp(e.children[0])

op = {'+':"add", '-':"sub"}
def asm_exp(e):
  if e.data == "exp_nombre":
    return f"mov rax, {e.children[0].value}\n"
  elif e.data == "exp_var":
    return f"mov rax, [{e.children[0].value}]\n"
  elif e.data == "exp_opbin":
    E1 = asm_exp(e.children[0]) # E1 = 'gamma de E1'
    E2 = asm_exp(e.children[2])
    # l'indentation sera visible dans le code assembleur
    return f"""
    {E2}
    push rax
    {E1}
    pop rbx
    {op[e.children[1].value]} rax, rbx
    """
  elif e.data == "exp_par":
    return asm_exp(e.children[0]) # Compile ce qu'il y a 
    # a l' interieur des parentheses

# com

def pp_com(c):
  if c.data == "assignation":
    return f"{c.children[0].value} = {pp_exp(c.children[1])};"
  if c.data == "if":
    x = f"\n{pp_bcom(c.children[1])}"
    return f"if ({pp_exp(c.children[0])}) {{{x}}}\n"
  if c.data == "while":
    x = f"\n  {pp_bcom(c.children[1])}"
    return f"while ({pp_exp(c.children[0])})"+ " {" +f"{x}" + "\n}"
  if c.data == "print":
    return f"print({pp_exp(c.children[0])})\n"

def vars_com(c):
  if c.data == "assignation":
    R = vars_exp(c.children[1])
    return {c.children[0].value} | R
  if c.data in {"if", "while"}:
    B = vars_bcom(c.children[1])
    E = vars_exp(c.children[0])
    return B | E
  if c.data == "print":
    return vars_exp(c.children[0])


cpt = 0
def next():
  global cpt
  cpt+=1
  return cpt

def asm_com(c):
  if c.data == "assignation":
    E = asm_exp(c.children[1])
    return f"""
    {E}
    mov [{c.children[0].value}], rax"""
  elif c.data == "if":
    E = asm_exp(c.children[0])
    C = asm_bcom(c.children[1])
    n = next()
    return f"""
    {E}
    cmp rax, 0
    jz fin{n}
    {C}
fin{n} : nop"""
  elif c.data == "while":
      E = asm_exp(c.children[0])
      C = asm_bcom(c.children[1])
      n = next()
      return f"""
      debut{n} :
        {E}
        cmp rax, 0
        jz fin{n}
        {C}
        jmp debut{n}
fin{n} : nop"""
  if c.data == "print":
    E = asm_exp(c.children[0])
    return f"""
    {E}
    mov rdi, fmt
    mov rsi, rax
    call printf"""

# bcom

def pp_bcom(bc):
  return "\n".join([pp_com(c) for c in bc.children])

def vars_bcom(bc):
  S = set()
  for c in bc.children:
    S = S | vars_com(c)
  return S

def asm_bcom(bc):
  return "\n" + "".join([asm_com(c) for c in bc.children])
 
# var_list

def pp_var_list(vl):
  return ", ".join([t.value for t in vl.children]) # t for token


# prg

def pp_prg(p):
  L = pp_var_list(p.children[0])
  C = pp_bcom(p.children[1])
  R = pp_exp(p.children[2])
  return f"main({L})" + " {\n" + f"{C}\n"  +  f"return ({R});" + "\n}"
  #return "main( %s ) { %s return(%s);\n}" % (L, C, R)

def asm_prg(p):
  f = open("moule.asm")
  moule = f.read()
  C = asm_bcom(p.children[1])
  moule = moule.replace("BODY", C)
  R = asm_exp(p.children[2])
  moule = moule.replace("RETURN", R)
  D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
  moule = moule.replace("DECL_VARS", D)
  s = ""
  for i in range(len(p.children[0].children)):
    v = p.children[0].children[i].value
    e = f"""
    mov rbx, [argv]
    mov rdi, [rbx + { 8*(i+1) }]
    xor rax, rax 
    call atoi
    mov [{v}], rax
    """
    s = s + e
  moule  = moule.replace("INIT_VARS", s)
  return moule

def vars_prg(p):
  L = set([t.value for t in p.children[0].children])
  C = vars_bcom(p.children[1])
  R = vars_exp(p.children[2])
  return L | C | R


##########
## main ##
##########

if __name__ == '__main__':
  #ast= grammaire.parse("Abcd,  \n x")
  #ast= grammaire.parse("""
  #x=3;
  #print(x);
  #""")
  

  ast = grammaire.parse("""main(X,Y,Z){
    while(X){
        T = 4;
        X = X-1;
        Y = Y+1;
    }
    return (Y);
  }
  """)

  #print(asm_bcom(ast))
  
  asm = asm_prg(ast)
  f = open("ouf.asm", "w")
  f.write(asm)
  f.close()

  #print(vars_prg(ast))

  #print(pp_prg(ast))
  #ast = grammaire.parse("x = 3; a = 5;")
  #print(ast)
  #print(pp_bcom(ast))
  #print(pp_exp(ast))




###########
## notes ##
###########



# Exp :: N | V | Exp op Exp
# Com :: V = Exp";" | if(Exp) {Bcom} | while(Exp) {Bcom}
# Bcom = block de commade :: (com)*
# Pgm
# 
# -> vide sert à voir quelle règle on applique quand on affiche
# %ignore /[ ]/  sans White Space
# OPBIN = operation binaire
# OPBIN : /[+\-*]/    le \ sert a dire que ce n'est pas toutes 
# les operations de + à * comme de a à z (a-z)

# faire loperation inverse 




"""

Tree(
  Token('RULE', 'exp'), 
  [Tree(
    Token('RULE', 'exp'), 
    Token('SIGNED_NUMBER', '12')]), 
    Token('OPBIN', '+'), Tree(Token('RULE', 'exp'), [Token('SIGNED_NUMBER', '3')])])

"""
