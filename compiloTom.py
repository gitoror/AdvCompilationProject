import lark
grammaire = lark.Lark(r"""
%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/ 
OPBIN : /[+\-*>]/
lhs : IDENTIFIER                         -> lhs_var  
| IDENTIFIER "." IDENTIFIER              -> lhs_id_attribute
| IDENTIFIER "." exp                     -> lhs_id_follow_attr
exp : IDENTIFIER                           -> exp_var
| SIGNED_NUMBER                            -> exp_nombre
| exp OPBIN exp                            -> exp_opbin
| "(" exp ")"                              -> exp_par
| IDENTIFIER "(" var_list ")"              -> exp_call_class_constructor
| IDENTIFIER "." IDENTIFIER                -> exp_id_attribute
| IDENTIFIER "." exp                       -> exp_id_follow_attr
com : lhs "=" exp ";"                         -> lhs_assignation
| "if" "(" exp ")" "{" bcom "}"               -> if
| "while" "(" exp ")" "{" bcom "}"            -> while
| "print" "(" exp ")"                         -> print
| lhs "." IDENTIFIER "(" var_list ")" IDENTIFIER ";"     -> method_call
bcom : (com)*
class : "class" IDENTIFIER "{" constructor methods"}"      -> create_class
constructor : "def" IDENTIFIER "(" var_list ")" "{" bcom "}"
methods : (method)*
method : "method" IDENTIFIER "(" var_list ")" "{" bcom "}"
var_list :                           -> vide
| var ("," var)*       -> aumoinsune
var : IDENTIFIER -> var 
| IDENTIFIER " " IDENTIFIER -> object_var
| "null" -> null
classes: -> no_class
| (class)* -> at_least_class
prg : "main" "(" var_list ")" "{" classes bcom "return" "(" exp ")" ";" "}"
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
def asm_exp(e, className=None):
  if e.data == "exp_nombre":
    return f"mov rax, {e.children[0].value}\n"
  elif e.data == "exp_var":
    if className!=None:
      if e.children[0].value in Class_dic[f"{className}"]["arg"]:
        arg = e.children[0].value
        return f"mov rax, [class.arg.{className}.{arg}]\n"
      elif e.children[0].value in Class_dic[f"{className}"]["oarg"]:
        arg = e.children[0].value
        return f"mov rax, [class.arg.{className}.{arg}]\n"
    return f"mov rax, [{e.children[0].value}]\n"
  elif e.data == "exp_opbin":
    E1 = asm_exp(e.children[0],className) # E1 = 'gamma de E1'
    E2 = asm_exp(e.children[2],className)
    # l'indentation sera visible dans le code assembleur
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
    if e.children[0].value == "self":
      return f"mov rax, [class.{className}.{e.children[1].value}]"
    else:
      attribute = f"{e.children[0].value}.{e.children[1].value}"
      return f"mov rax, [{attribute}]"
  elif e.data =="exp_id_follow_attr":
    attribute = f"{e.children[0].value}.{e.children[1].children[0].value}.{e.children[1].children[1].value}"
    return f"mov rax, [{attribute}]"
  elif e.data == "exp_call_class_constructor":
    # not here bcs lack name of obj, see in com -> lhs_assignation
    # Update : could have moved back the code here bcs of the
    # disctionary Class_dic
    pass

cpt = 0
def next():
  global cpt
  cpt+=1
  return cpt

def asm_class(c):
  s=""
  # ecrire le ctr
  Constructor = c.children[1]
  s+= f"""
  {c.children[0]}Init:
    {asm_bcom(Constructor.children[2],Constructor.children[0].value)}
    ret
  """
  # ecrire les meth
  for meth in c.children[2].children:
    s+=f"""
  {c.children[0]}.{meth.children[0]}:
    {asm_bcom(meth.children[2],Constructor.children[0].value)}
    ret
  """
  return s


def asm_com(c, className=None):
  if c.data == "if":
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
  
  elif c.data == "method_call":
    # hyp : lhs is only identifier (object) for the moment
    lhs = c.children[0]
    methName = f"{c.children[1].value}"
    methVars = c.children[2].children
    className = c.children[3];
    # Load arg
    m=""
    i=0
    for var in methVars:
      m+=f"""
      mov rax, [{var.children[0].value}]
      mov [class.arg.{className}.{Class_dic[f"{className}"]["meth"][{methName}][i]}], rax
      """
      i+=1
    # Call meth
    m+=f"""
    call {className}.{methName}
    """
    # Reaffect class attr to object attr
    for attribute in Class_dic[f"{className}"]["attr"]:
      m+=f"""
      mov rax, [class.{className}.{attribute}]
      mov [{lhs.children[0].value}.{attribute}], rax
      """
    return m
  elif c.data == "lhs_assignation":
    lhs = c.children[0]
    if c.children[1].data == "exp_call_class_constructor":
      ConstrVars = c.children[1].children[1].children
      ConstrName = c.children[1].children[0].value
      # Load ctr args into class args before calling constructor 
      s=""
      i = 0
      for var in ConstrVars:
        if var.data == "object_var":
          #class.oarg.Human.Car.speed
          otherClassName = var.children[0].value
          for attribute in Class_dic[f"{otherClassName}"]["attr"]:
           
            s+=f"""
            mov rax, [{var.children[1].value}.{attribute}]
            mov [class.oarg.{ConstrName}.{otherClassName}.{attribute}], rax
            """
        elif var.data == "var":
          s+=f"""
          mov rax, [{var.children[0].value}]
          mov [class.arg.{ConstrName}.{Class_dic[f"{ConstrName}"]["arg"][i]}], rax
          """
        i+=1
      # Call constructor
      s = s+ f"""
      call {ConstrName}Init
      """
      # Affect class attr to the object attr
      t=""
      for objArg in Class_dic[f"{ConstrName}"]["oarg"]:
        otherClassName = Class_dic[f"{ConstrName}"]["oarg"][f"{objArg}"]
        for attribute in Class_dic[f"{otherClassName}"]["attr"]:
          if lhs.data == "lhs_var":
            t+=f"""
            mov rax, [class.{ConstrName}.{otherClassName}.{attribute}]
            mov [{lhs.children[0].value}.{objArg}.{attribute}], rax
            """
          elif lhs.data == "lhs_id_attribute":
            t+=f"""
            mov rax, [class.{ConstrName}.{otherClassName}.{attribute}]
            mov [{lhs.children[0].value}.{lhs.children[1].value}.{attribute}], rax
            """
      for attribute in Class_dic[f"{ConstrName}"]["attr"]:
        if lhs.data == "lhs_var":
          t+=f"""
          mov rax, [class.{ConstrName}.{attribute}]
          mov [{lhs.children[0].value}.{attribute}], rax
          """
        elif lhs.data == "lhs_id_attribute":
          t+=f"""
          mov rax, [class.{ConstrName}.{attribute}]
          mov [{lhs.children[0].value}.{lhs.children[1].value}.{attribute}], rax
          """
      return s+t
    
    else:
      E = asm_exp(c.children[1],className)
      if lhs.data == "lhs_id_attribute":
        if lhs.children[0].value == "self":
          # if rhs = arg of the constr
          if c.children[1].data == "exp_var" and\
                c.children[1].children[0].value in Class_dic[f"{className}"]["arg"]:
            arg = c.children[1].children[0].value
            r = f"""mov rax, [class.arg.{className}.{arg}]
            mov [class.{className}.{lhs.children[1].value}], rax
            """
            return r
          # rhs = object arg ctr
          if c.children[1].data == "exp_var" and\
                c.children[1].children[0].value in Class_dic[f"{className}"]["oarg"]:
       
            
            arg = c.children[1].children[0].value
            otherClassName = Class_dic[f"{className}"]["oarg"][f"{arg}"]
         
            r=""
            for attribute in Class_dic[f"{otherClassName}"]["attr"]:
            
              r += f"""
              mov rax, [class.oarg.{className}.{otherClassName}.{attribute}]
              mov [class.{className}.{otherClassName}.{attribute}], rax
              """
            return r
          if c.children[1].data == "exp_id_attribute":
            r=""
            if c.children[1].children[0].value == "self":
              className = className
              for attr in Class_dic[f"{className}"]["attr"]:
                if attr == f"{c.children[1].children[1].value}":
                  r += f"""
                  mov rax, [class.{className}.{c.children[1].children[1].value}]
                  mov [class.{className}.{lhs.children[1].value}], rax
                  """
                  return r
            else:
              r += f"""
              mov rax, [{c.children[1].children[1].value}.{c.children[1].children[1].value}]
              mov [{lhs.children[0].value}.{lhs.children[1].value}], rax
              """
              return r
          else:
            r=f"""
            {E}
            mov [class.{className}.{lhs.children[1].value}], rax
            """
            return r
        else:
          # if rhs = arg of the constr
          if c.children[1].data == "exp_var" and\
                c.children[1].children[0].value in Class_dic[f"{className}"]["arg"]:
            arg = c.children[1].children[0].value
            r = f"""
            mov rax, [class.arg.{className}.{arg}]
            mov [{lhs.children[0].value}.{lhs.children[1].value}], rax
            """
            return r
          if c.children[1].data == "exp_id_attribute":
            r=""
            if c.children[1].children[0].value == "self":
              className = className
              for attr in Class_dic[f"{className}"]["attr"]:
                if attr == f"{c.children[1].children[1].value}":
                  r += f"""
                  mov rax, [class.{className}.{c.children[1].children[1].value}]
                  mov [{lhs.children[0].value}.{lhs.children[1].value}], rax
                  """
                  return r
            else:
              r += f"""
              mov rax, [{c.children[1].children[1].value}.{c.children[1].children[1].value}]
              mov [{lhs.children[0].value}.{lhs.children[1].value}], rax
              """
              return r
          else:
            r=f"""
            {E}
            mov [{lhs.children[0].value}.{lhs.children[1].value}], rax
            """
            return r
      elif lhs.data == "lhs_id_follow_attr":
        r=f"""
        {E}
        mov [{lhs.children[0].value}.{lhs.children[1].children[0]}.{lhs.children[1].children[1]}], rax
        """
        return r
      elif lhs.data == "lhs_var":
        if c.children[1].data == "exp_id_attribute":
            r=""
            if c.children[1].children[0].value == "self":
              
              className = className
              for attr in Class_dic[f"{className}"]["attr"]:
                if attr == f"{c.children[1].children[1].value}":
                  r += f"""
                  mov rax, [class.{className}.{c.children[1].children[1].value}]
                  mov [{lhs.children[0].value}], rax
                  """
                  return r
            else:
              r += f"""
                  mov rax, [{c.children[1].children[0].value}.{c.children[1].children[1].value}]
                  mov [{lhs.children[0].value}], rax
                  """
              return r
        else:
          r=f"""
          {E}
          mov [{lhs.children[0].value}], rax
          """
          return r
      
      return r

def asm_bcom(bc,className=None):
  return "\n" + "".join([asm_com(c,className) for c in bc.children])
 
def asm_prg(p):
  f = open("mouleTom.asm")
  moule = f.read()
  
  D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
  moule = moule.replace("DECL_VARS", D)
  DC=""
  for class_ in p.children[1].children:
    DC += f"{asm_class(class_)}\n"
  moule = moule.replace("DECL_CLASS", DC)
  C = asm_bcom(p.children[2])
  moule = moule.replace("BODY", C)
  R = asm_exp(p.children[3])
  moule = moule.replace("RETURN", R)
  
  s = ""
  for i in range(len(p.children[0].children)):
    v = p.children[0].children[i].children[0].value
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
    S=set()
    S.add(f"{e.children[0].value}")
    return S
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
  elif e.data == "exp_id_follow_attr":
    return set(f"{e.children[0].value}.{e.children[1].children[0].value}.{e.children[1].children[1].value}")

def vars_com(c):
  if c.data == "method_call":
    return set()
  elif c.data == "lhs_assignation":
    lhs = c.children[0]
    if c.children[1].data == "exp_call_class_constructor":
      if c.children[0].data == "lhs_var":
        ObjectName = c.children[0].children[0].value
        ConstrName = c.children[1].children[0].value
        ObjAttributeSet = set()
        for attribute in Class_dic[ConstrName]["attr"]:
          ObjAttributeSet.add(f"{ObjectName}.{attribute}")
        for objArg in Class_dic[ConstrName]["oarg"]:
          otherClassName = Class_dic[ConstrName]["oarg"][objArg]
          for attribute in Class_dic[f"{otherClassName}"]["attr"]:
            ObjAttributeSet.add(f"{ObjectName}.{objArg}.{attribute}")
        return ObjAttributeSet
    else:
      if c.children[0].data == "lhs_var":
        R = vars_exp(c.children[1])
        S = set()
        S.add(f"{lhs.children[0].value}")
        return S | R
      elif c.children[0].data == "lhs_id_attribute":
        S = set()
        # soit self att
        if lhs.children[0].value == "self":
          return set() # handle in vars_class bcs need class name
        # soit obj att 
        else :
          S.add(f"{lhs.children[0].value}.{lhs.children[1].value}")
          return S
      elif c.children[0].data == "lhs_id_follow_attr":
        S = set()
        S.add((f"{lhs.children[0].value}.{lhs.children[1].children[0].value}.{lhs.children[1].children[1].value}"))
        return S
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

Class_dic = {}


def vars_class(c):
  Class_dic[f"{c.children[0].value}"] = {"attr":[],"arg":[],"meth":{},"oarg":{},"oattr":[]}
  Constructor = c.children[1]
  Args = set()
  OArgs = set()
  OAttr = set()
  for t in Constructor.children[1].children:
     if t.data == "object_var":
       otherClassName = t.children[0].value
       # stocke la classe cet arg du ctr 
       Class_dic[f"{c.children[0].value}"]["oarg"][f"{t.children[1].value}"]=t.children[0].value 
      
       for attribute in Class_dic[f"{otherClassName}"]["attr"]:
          # class.oarg.Human.Car.speed
          OArgs.add(f"class.oarg.{c.children[0].value}.{t.children[0].value}.{attribute}")
          # class.Human.Car.speed
          OAttr.add(f"class.{c.children[0].value}.{t.children[0].value}.{attribute}")
          Class_dic[f"{c.children[0].value}"]["oattr"].append(attribute)
     else:
        
        Args.add(f"class.arg.{c.children[0].value}.{t.children[0].value}")
        Class_dic[f"{c.children[0].value}"]["arg"].append(t.children[0].value)
  
  C = vars_bcom(c.children[1].children[2])
  ClassAtt = set()
  ConstrBcom = Constructor.children[2]
  for com in ConstrBcom.children:
    if com.data == "lhs_assignation":
      if com.children[0].data == "lhs_id_attribute":
        lhs = com.children[0]
        # if it is a self attribute (= in the constructor)
        if lhs.children[0].value == "self":
          Class_dic[f"{c.children[0].value}"]["attr"].append(lhs.children[1].value)
          ClassAtt.add(f"class.{c.children[0].value}.{lhs.children[1].value}")
  
  # methods
  # declare the vars in arg of meth
  for meth in c.children[2].children:
    Class_dic[f"{c.children[0].value}"]["meth"][f"{meth.children[0].value}"] = [] # method arg list
    className = f"{c.children[0].value}"
    C = C | vars_bcom(meth.children[2])
    for arg in meth.children[1].children:
      methName = meth.children[0].value
      argName = arg.children[0].value
      Args.add(f"class.arg.{c.children[0].value}.{methName}.{arg.children[0].value}")
      Class_dic[f"{c.children[0].value}"]["meth"][f"{meth.children[0].value}"].append(argName)
  
  return Args | OArgs | OAttr | C | ClassAtt 

def vars_prg(p):
  L = set([t.children[0].value for t in p.children[0].children])
  O=set()
  if p.children[1].data == "at_least_class":
     for class_ in p.children[1].children:
      O = O | vars_class(class_)
  C = vars_bcom(p.children[2])
  R = vars_exp(p.children[3])
  return L | O | C | R

####################################################################################################################
## MAIN                                                                                            
####################################################################################################################
if __name__ == '__main__':
  
  ast1 = grammaire.parse("""
    main(X,Y,Z) {
      class Car {
        def Car(speed) {
          self.speed=speed+1;
        }
        method accelerate() {
          self.speed = self.speed + 50;
        }
      }
        
      speed=28;
      car = Car(speed);
      car.accelerate() Car;
      Y = car.speed;
      return (Y);
    }
  """)

  ast2 = grammaire.parse("""
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
  """)

  
 
  asm = asm_prg(ast1)
  print(Class_dic)
  f = open("tom.asm", "w")
  f.write(asm)
  f.close()

  
  
 
####################################################################################################################
## NOTES                                                                                                      
####################################################################################################################
"""

if __name__ == '__main__':
  
  ast = grammaire.parse(
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
  )

  #print(ast)
  
  #print(pp_prg(ast))
  asm = asm_prg(ast)
  f = open("tom.asm", "w")
  f.write(asm)
  f.close()
 
ast = grammaire.parse(
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

    Y = car.speed;
    return (Y);
  }
  )

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




