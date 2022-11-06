import lark
grammaire = lark.Lark(r"""
%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/ 
OPBIN : /[+\-*>]/
lhs : IDENTIFIER                         -> lhs_var  
| IDENTIFIER "." IDENTIFIER              -> lhs_id_attribute
exp : IDENTIFIER                           -> exp_var
| SIGNED_NUMBER                            -> exp_nombre
| exp OPBIN exp                            -> exp_opbin
| "(" exp ")"                              -> exp_par
| IDENTIFIER "(" var_list ")"              -> exp_call_class_constructor
| IDENTIFIER "." IDENTIFIER                -> exp_id_attribute
com : IDENTIFIER "=" exp ";"                  -> assignation
| lhs "=" exp ";"                             -> lhs_assignation
| "if" "(" exp ")" "{" bcom "}"               -> if
| "while" "(" exp ")" "{" bcom "}"            -> while
| "print" "(" exp ")"                         -> print
| lhs "." method "()"                         -> method_call
bcom : (com)*
class :                                       -> no_class
| "class" IDENTIFIER "{" constructor methods"}"      -> create_class
constructor : "def" IDENTIFIER "(" var_list ")" "{" bcom "}"
methods : (method)*
method : "def" IDENTIFIER "(" var_list ")" "{" bcom "}"
var_list :                           -> vide
| IDENTIFIER ("," IDENTIFIER)*       -> aumoinsune
prg : "main" "(" var_list ")" "{" class bcom "return" "(" exp ")" ";" "}"
""", 
start="prg")

####################################################################################################################
## pretty printer                                                                                                 
####################################################################################################################
def pp_lhs(lhs):
  if lhs.data == "lhs_var":
      return lhs.children[0].value
  if lhs.data == "lhs_id_attribute":
    return f"{lhs.children[0].value}"+"."+f"{lhs.children[1].value}"

def pp_exp(e):
  # Tree(data, children [ ])
  # Token(Type, value)
  if e.data in {"exp_nombre", "exp_var"}:
    return e.children[0].value
  elif e.data == "exp_opbin":
    return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"
  elif e.data == "exp_par":
    return f"({pp_exp(e.children[0])})"
  if e.data == "exp_call_class_constructor":
    return f"{e.children[0].value}({pp_var_list(e.children[1])})"
  if e.data == "exp_id_attribute":
    return f"{e.children[0].value}"+"."+f"{e.children[1].value}"
  
def pp_class(c):
  if c.data == "no_class":
    return "\n"
  elif c.data == "create_class":
    return f"class {c.children[0].value} " + "{\n" + f"{pp_constructor(c.children[1])}" + "\n}"

def pp_com(c):
  if c.data == "assignation":
    return f"{c.children[0].value} = {pp_exp(c.children[1])};"
  if c.data == "if":
    x = f"\n{pp_bcom(c.children[1])}"
    return f"if ({pp_exp(c.children[0])}) {{{x}}}\n"
  if c.data == "while":
    x = f"\n{pp_bcom(c.children[1])}"
    return f"while ({pp_exp(c.children[0])})"+ " {" +f"{x}" + "\n}"
  if c.data == "print":
    return f"print({pp_exp(c.children[0])})\n"
  if c.data == "lhs_assignation":
    return f"{pp_lhs(c.children[0])} = {pp_exp(c.children[1])};"
  

def pp_bcom(bc):
  return "\n".join([pp_com(c) for c in bc.children])

def pp_constructor(ctr):
  return f"def {ctr.children[0].value}"+"("+f"{pp_var_list(ctr.children[1])}"+") "    \
          +"{\n"+f"{pp_bcom(ctr.children[2])}"+"\n}"

def pp_var_list(vl):
  return ", ".join([t.value for t in vl.children]) # t for token

def pp_prg(p):
  L = pp_var_list(p.children[0])
  CL = pp_class(p.children[1])
  C = pp_bcom(p.children[2])
  R = pp_exp(p.children[3])
  return f"main({L})" + " {\n" + f"{CL}\n" + f"{C}\n"  +  f"return ({R});" + "\n}"
  #return "main( %s ) { %s return(%s);\n}" % (L, C, R)


####################################################################################################################
## asm                                                                                                            
####################################################################################################################
def asm_lhs(lhs):
  #if lhs.data == "lhs_var":
   #   return lhs.children[0].value
  if lhs.data == "lhs_id_attribute":
    return f"{lhs.children[0].value}"+"."+f"{lhs.children[1].value}"

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
  elif e.data == "exp_call_class_constructor":
    # not here bcs lack name of obj, see in com -> lhs_assignation
    pass

cpt = 0
def next():
  global cpt
  cpt+=1
  return cpt





def asm_class(c):
  # ecrire le ctr
  Constructor = c.children[1]
  return f"""
  {c.children[0]}Init:
    {Constructor.children[2]}
    ret
  """
  # ecrire les meth

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
  elif c.data == "lhs_assignation":
    if c.children[1].data == "exp_call_class_constructor":
      ConstrVars = c.children[1].children[1].children
      ConstrName = c.children[1].children[0].value
      # Load args + call constr => creer attr objet
      # Cmt je sais cb d'att l'objet va avoir ????
      s=""
      i = 0
      for var in ConstrVars:
        e=f"""
        mov rax, [{var.value}]
        mov [class.{ConstrName}.{Class_list[0][i]}], rax
        """
        s+=e
        i+=1
      s = s+ f"""
      call {ConstrName}Init
      """
      t=""
      j = 0
      for var in ConstrVars:
        g=f"""
        mov rax, [class.{ConstrName}.{Class_list[0][i]}]
        mov [{ConstrName}.{Class_list[0][i]}], rax
        """
        t+=g
        j+=1
      return s+t
      
   

def asm_bcom(bc):
  return "\n" + "".join([asm_com(c) for c in bc.children])
 
def asm_prg(p):
  f = open("moule.asm")
  moule = f.read()
  C = asm_bcom(p.children[2])
  moule = moule.replace("BODY", C)
  R = asm_exp(p.children[3])
  moule = moule.replace("RETURN", R)
  D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
  moule = moule.replace("DECL_VARS", D)
  DC = f"{asm_class(p.children[1].children[1])}"
  moule = moule.replace("DECL_CLASS", DC)
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

####################################################################################################################
## vars                                                                                                       
####################################################################################################################
def vars_lhs(lhs):
  if lhs.data == "lhs_id_attribute":
    return f"{lhs.children[0].value}.{lhs.children[1].value}"

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
  elif e.data == "exp_call_class_constructor":
    return set()
  elif e.data =="exp_id_attribute":
    return set()

def vars_com(c):
  if c.data == "assignation":
    R = vars_exp(c.children[1])
    return {c.children[0].value} | R
  if c.data == "lhs_assignation":
    if c.children[0].data == "lhs_var":
      R = vars_exp(c.children[1])
      return {c.children[0].value} | R
    if c.children[0].data == "lhs_id_attribute_var":
      lhs = c.children[0].children[0]
      # soit self att
      if lhs.children[0].value == "self":
        return set()
      # soit obj att 
      else :
        return f"{lhs.children[0].value}.{lhs.children[1].value}"
  if c.data in {"if", "while"}:
    B = vars_bcom(c.children[1])
    E = vars_exp(c.children[0])
    return B | E
  if c.data == "print":
    return vars_exp(c.children[0])

def vars_bcom(bc):
  S = set()
  for c in bc.children:
    S = S | vars_com(c)
  return S

Class_list = []

def vars_class(c):
  if c.data == "no_class":
    return set()
  elif c.data == "create_class":
    Class_list.append([c.children[0].value])
    nb = len(Class_list)
    Constructor = c.children[1]
    Args = set([f"class.{c.children[0].value}.{t.value}" for t in Constructor.children[1].children])
    C = vars_bcom(c.children[1].children[2])
    ClassAtt = set()
    ConstrBcom = Constructor.children[2]
    for com in ConstrBcom.children:
      if com.data == "lhs_assignation":
        if com.children[0].data == "lhs_id_attribute":
          lhs = com.children[0]
          # soit self att
          if lhs.children[0].value == "self":
            Class_list[nb].append(lhs.children[1].value)
            ClassAtt = ClassAtt | f"class.{c.children[0]}.{lhs.children[1].value}"
    return Args | C | ClassAtt

def vars_prg(p):
  L = set([t.value for t in p.children[0].children])
  O = vars_class(p.children[0])
  C = vars_bcom(p.children[1])
  R = vars_exp(p.children[2])
  return L | O | C | R

####################################################################################################################
## MAIN                                                                                            
####################################################################################################################
if __name__ == '__main__':
  ast = grammaire.parse("""
  main(X,Y,Z) {
    class Car {
      def Car(speed) {
        self.speed=3;
      }
    }
    speed = 5;
    car = Car(speed);
    
    x = car.speed;
    while(X){
        T = 4;
        X = X-1;
        Y = Y+1;
    }
    return (Y);
  }
  """)
  print(pp_prg(ast))
  asm = asm_prg(ast)
  f = open("tom.asm", "w")
  f.write(asm)
  f.close()
 

####################################################################################################################
## NOTES                                                                                                      
####################################################################################################################
"""
#ast= grammaire.parse("Abcd,  \n x")
  #ast= grammaire.parse(""
  #x=3;
  #print(x);
  #"")

  asm = asm_prg(ast)
  f = open("oufT.asm", "w")
  f.write(asm)
  f.close()

#print(vars_prg(ast))

  #print(pp_prg(ast))
  #ast = grammaire.parse("x = 3; a = 5;")
  #print(ast)
  #print(pp_bcom(ast))
  #print(pp_exp(ast))

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


Tree(
  Token('RULE', 'exp'), 
  [Tree(
    Token('RULE', 'exp'), 
    Token('SIGNED_NUMBER', '12')]), 
    Token('OPBIN', '+'), Tree(Token('RULE', 'exp'), [Token('SIGNED_NUMBER', '3')])])

"""




