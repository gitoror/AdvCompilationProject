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
|   "\"" STRING "\""           -> exp_str
| "len" "(" "\"" STRING "\"" ")"     -> exp_fonc_length
| "len" "(" IDENTIFIER ")"     -> exp_fonc_length_var
| STRING "+" STRING             -> exp_fonc_concatenation
| IDENTIFIER "[" SIGNED_NUMBER "]" -> exp_fonc_getletter
com : lhs "=" exp ";"                         -> lhs_assignation
| "if" "(" exp ")" "{" bcom "}"               -> if
| "while" "(" exp ")" "{" bcom "}"            -> while
| "print" "(" exp ")"                         -> print
| lhs "." method "()"                         -> method_call
bcom : (com)*
class : "class" IDENTIFIER "{" constructor methods"}"      -> create_class
constructor : "def" IDENTIFIER "(" var_list ")" "{" bcom "}"
methods : (method)*
method : "def" IDENTIFIER "(" var_list ")" "{" bcom "}"
var_list :                           -> vide
| IDENTIFIER ("," IDENTIFIER)*       -> aumoinsune
classes: -> no_class
| (class)* -> at_least_class
prg : IDENTIFIER " " "main" "(" var_list ")" "{" classes bcom "return" "(" exp ")" ";"  "}"
STRING : /[a-zA-Z][a-zA-Z0-9.,!?; ]*/      
""", 
start="prg")

list_str = []
list_len = []
list_sum = []

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
def asm_exp(e, className=None):
  if e.data == "exp_nombre":
    return f"mov rax, {e.children[0].value}\n"
  elif e.data == "exp_var":
    if className!=None:
      if e.children[0].value in Class_list[f"{className}"]["arg"]:
        arg = e.children[0].value
        return f"mov rax, [class.arg.{className}.{arg}]\n"
    return f"mov rax, [{e.children[0].value}]\n"
  elif e.data == "exp_opbin":

    if (e.children[0].data == "exp_str"):
      list_sum.append(e.children[0].children[0].value)
      list_sum.append(e.children[2].children[0].value)
      return f"""
      mov rdx, {e.children[2].children[0].value}
      mov rax, {e.children[0].children[0].value} 
      mov rsi, rdx
      mov rdi, rax
      call strcat
      """ 
    elif (e.children[0].data == "exp_var"):
      return f"""
      mov rdx, [{e.children[2].children[0].value}]
      mov rax, [{e.children[0].children[0].value}] 
      mov rsi, rdx
      mov rdi, rax
      call strcat
      """                                                              
    else:
      E1 = asm_exp(e.children[0])
      E2 = asm_exp(e.children[2])
      return f"""
      {E2}
      push rax
      {E1}
      pop rbx
      {op[e.children[1].value]} rax, rbx
      """
  elif e.data == "exp_par":
    return asm_exp(e.children[0],className) # Compile ce qu'il y a 
    # a l' interieur des parentheses
  elif e.data == "exp_id_attribute":
    attribute = f"{e.children[0].value}.{e.children[1].value}"
    return f"mov rax, [{attribute}]"
  elif e.data == "exp_call_class_constructor":
    # not here bcs lack name of obj, see in com -> lhs_assignation
    # Update : could have move back the code here bcs of the
    # disctionary Class_list
    pass
  elif e.data == "exp_str":

    return f"mov rax, str{list_str.index(e.children[0].value)} \0\n"
  elif e.data == "exp_fonc_length":
    list_len.append(e.children[0].value)
    #return f"mov rax, len{list_str.index(e.children[0].value)}"
    return f"""
    mov rax, {e.children[0].value}
    mov rdi, rax
    call strlen
    """
  elif e.data == "exp_fonc_length_var":
    return f"""
    mov rax, [{e.children[0].value}]
    mov rdi, rax
    call strlen
    """                                                                
                           

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
    {asm_bcom(Constructor.children[2],Constructor.children[0].value)}
    ret
  """
  # ecrire les meth

def asm_com(c, className=None):
  if c.data == "assignation":
    E = asm_exp(c.children[1],className)
    return f"""
    {E}
    mov [{c.children[0].value}], rax"""
  elif c.data == "if":
    E = asm_exp(c.children[0],className)
    C = asm_bcom(c.children[1],className)
    n = next()
    return f"""
    {E}
    cmp rax, 0
    jz fin{n}
    {C}
fin{n} : nop"""
  elif c.data == "while":
      E = asm_exp(c.children[0],className)
      C = asm_bcom(c.children[1],className)
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
    lhs = c.children[0]
    if c.children[1].data == "exp_call_class_constructor":
      ConstrVars = c.children[1].children[1].children
      ConstrName = c.children[1].children[0].value
      # Load ctr args into class args before calling constructor 
      s=""
      i = 0
      for var in ConstrVars:
        e=f"""
        mov rax, [{var.value}]
        mov [class.arg.{ConstrName}.{Class_list[f"{ConstrName}"]["arg"][i]}], rax
        """
        s+=e
        i+=1
      # Call constructor
      s = s+ f"""
      call {ConstrName}Init
      """
      # Affect class attr to the object attr
      t=""
      for attribute in Class_list[f"{ConstrName}"]["attr"]:
        if lhs.data == "lhs_var":
          g=f"""
          mov rax, [class.{ConstrName}.{attribute}]
          mov [{lhs.children[0].value}.{attribute}], rax
          """
          t+=g
        elif lhs.data == "lhs_id_attribute":
          g=f"""
          mov rax, [class.{ConstrName}.{attribute}]
          mov [{lhs.children[0].value}.{lhs.children[1].value}.{attribute}], rax
          """
          t+=g
      return s+t
    else:
      E = asm_exp(c.children[1],className)
      if lhs.data == "lhs_id_attribute":
        if lhs.children[0].value == "self":
          # if rhs = arg of the constr
          if c.children[1].data == "exp_var" and\
                c.children[1].children[0].value in Class_list[f"{className}"]["arg"]:
            arg = c.children[1].children[0].value
            r = f"""mov rax, [class.arg.{className}.{arg}]
            mov [class.{className}.{lhs.children[1].value}], rax"""
          else:
            r=f"""
            {E}
            mov [class.{className}.{lhs.children[1].value}], rax
            """
        else:
          # if rhs = arg of the constr
          if c.children[1].data == "exp_var" and\
                c.children[1].children[0].value in Class_list[f"{className}"]["arg"]:
            arg = c.children[1].children[0].value
            r = f"""mov rax, [class.arg.{className}.{arg}]
            mov [{lhs.children[0].value}.{lhs.children[1].value}], rax"""
          else:
            r=f"""
            {E}
            mov [{lhs.children[0].value}.{lhs.children[1].value}], rax
            """
      elif lhs.data == "lhs_var":
         # if rhs = arg of the constr
          if c.children[1].data == "exp_var" and\
                c.children[1].children[0].value in Class_list[f"{className}"]["arg"]:
            arg = c.children[1].children[0].value
            r = f"""mov rax, [class.arg.{className}.{arg}]
            mov [{lhs.children[0].value}], rax"""
          else:
            r=f"""
            {E}
            mov [{lhs.children[0].value}], rax
            """
      return r

def asm_bcom(bc,className=None):
  return "\n" + "".join([asm_com(c,className) for c in bc.children])
 
def asm_prg(p):
  f = open("moule.asm")
  moule = f.read()
  if (p.children[0].value == "int"):
      moule = moule.replace("FMT", "fmt : db \"%"+"d\", 10, 0")
  elif(p.children[0].value == "string"):
      moule = moule.replace("FMT", "fmt : db \"%"+"s\", 10, 0")
    
  D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
  D += "\n"+"\n".join([f"str{list_str.index(v)} : db \"{v}\", 0" for v in list_str]) # declaire adress for string
  D += "\n"+"\n".join([f"{v} : db \"{v}\", 0" for v in list_len])
  #D += "\n"+"\n".join([f"len{list_len.index(v)} : equ $ -\"{v}\" " for v in list_len]) # declaire adress for length
  D += "\n"+"\n".join([f"{v} : db \"{v}\", 0" for v in list_sum])
  moule = moule.replace("DECL_VARS", D)  # need to write DECL_VARS before asm_exp and asm_bcom to name var str

  C = asm_bcom(p.children[3])
  moule = moule.replace("BODY", C)
  R = asm_exp(p.children[4])
  moule = moule.replace("RETURN", R)
  DC=""
  for class_ in p.children[2].children:
    DC += f"{asm_class(class_)}\n"
  moule = moule.replace("DECL_CLASS", DC)
  s = ""
  for i in range(len(p.children[1].children)):
    v = p.children[1].children[i].value
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
    return set(f"{lhs.children[0].value}.{lhs.children[1].value}")

def vars_exp(e):
  if e.data == "exp_nombre" :
    return set()
  if e.data == "exp_var":
    return {e.children[0].value}
  elif e.data == "exp_opbin":
    if (e.children[0].data == "exp_str"):
      list_sum.append(e.children[0].children[0].value)
      list_sum.append(e.children[2].children[0].value)
      return set()
    else:
      L = vars_exp(e.children[0])
      R = vars_exp(e.children[2])
      return L | R
  elif e.data == "exp_par":
    return vars_exp(e.children[0])
  elif e.data == "exp_call_class_constructor":
    return set()
  elif e.data =="exp_id_attribute":
    return set()
  elif e.data == "exp_str":
    list_str.append(e.children[0].value)
    return set()
  elif e.data == "exp_fonc_length":
    list_len.append(e.children[0].value)
    return set()

def vars_com(c):
  if c.data == "assignation":
    R = vars_exp(c.children[1])
    return {c.children[0].value} | R
  elif c.data == "lhs_assignation":
    lhs = c.children[0]
    if c.children[1].data == "exp_call_class_constructor":
      if c.children[0].data == "lhs_var":
        ObjectName = c.children[0].children[0].value
        ConstrName = c.children[1].children[0].value
        ObjAttributeSet = set()
        for attribute in Class_list[f"{ConstrName}"]["attr"]:
          ObjAttributeSet.add(f"{ObjectName}.{attribute}")
        return ObjAttributeSet
    else:
      if c.children[0].data == "lhs_var":
        R = vars_exp(c.children[1])
        return {lhs.children[0].value} | R
      if c.children[0].data == "lhs_id_attribute":
        # soit self att
        if lhs.children[0].value == "self":
          return set() # handle in vars_class bcs need class name
        # soit obj att 
        else :
          return set(f"{lhs.children[0].value}.{lhs.children[1].value}")
  
  if c.data == "lhs_assignation":
    if c.children[0].data == "lhs_var":
      R = vars_exp(c.children[1])
      return {c.children[0].children[0].value} | R
    if c.children[0].data == "lhs_id_attribute":
      lhs = c.children[0]
      # soit self att
      if lhs.children[0].value == "self":
        return set() # handle in vars_class bcs need class name
      # soit obj att 
      else :
        return set(f"{lhs.children[0].value}.{lhs.children[1].value}")
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

Class_list = {}

def vars_class(c):
  Class_list[f"{c.children[0].value}"] = {"attr":[],"arg":[],"meth":[]}
  Constructor = c.children[1]
  Args = set([f"class.arg.{c.children[0].value}.{t.value}" for t in Constructor.children[1].children])
  for t in Constructor.children[1].children:
    Class_list[f"{c.children[0].value}"]["arg"].append(t.value)
  C = vars_bcom(c.children[1].children[2])
  ClassAtt = set()
  ConstrBcom = Constructor.children[2]
  for com in ConstrBcom.children:
    if com.data == "lhs_assignation":
      if com.children[0].data == "lhs_id_attribute":
        lhs = com.children[0]
        # if it is a self attribute (= in the constructor)
        if lhs.children[0].value == "self":
          Class_list[f"{c.children[0].value}"]["attr"].append(lhs.children[1].value)
          ClassAtt.add(f"class.{c.children[0].value}.{lhs.children[1].value}")
  print("Le set")
  print(Args | C | ClassAtt)
  print("fin set")
  return Args | C | ClassAtt

def vars_prg(p):
  L = set([t.value for t in p.children[1].children])
  if p.children[2].data == "at_least_class":
     print("OK")
     
     O=set()
     print(p.children[2].children)
     for class_ in p.children[2].children:
      vars_class(class_)
      O = O | vars_class(class_)
  C = vars_bcom(p.children[3])
  R = vars_exp(p.children[4])
  return L | O | C | R

####################################################################################################################
## MAIN                                                                                            
####################################################################################################################
if __name__ == '__main__':
  ast = grammaire.parse("""
 int main(X,Y,Z) {
    class Car {
      def Car(speed) {
        self.speed=speed+1;
      }
    }
    class Human {
      def Human(size,age) {
        self.footSize = size-1;
        self.age=age;
      }
    }
    speed=28;
    car = Car(speed);
    s=1;
    a=21;
    h=Human(s,a);
    Y = h.age;
    return (Y);
  }
  """)
  print(ast)
  
  #print(pp_prg(ast))
  asm = asm_prg(ast)
  f = open("tom.asm", "w")
  f.write(asm)
  f.close()
 
  print(Class_list)  
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