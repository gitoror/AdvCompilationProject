import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER              -> exp_nombre
| IDENTIFIER                     -> exp_var
| exp OPBIN exp                  -> exp_opbin
| "(" exp ")"                    -> exp_par
|   "\"" STRING "\""           -> exp_str
com : IDENTIFIER "=" exp ";"     -> assignation
| "if" "(" exp ")" "{" bcom "}"  -> if
| "while" "(" exp ")" "{" bcom "}"  -> while
| "print" "(" exp ")"               -> print
| lhs "=" exp ";"                   -> attribut
bcom : (com)*
prg : "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";"  "}"
class : "class" " " IDENTIFIER "{" constructor "}"
constructor : IDENTIFIER "(" var_list ")" "{" bcom "}"
lhs : IDENTIFIER                -> assignation  
| IDENTIFIER "." IDENTIFIER     -> self
var_list :                       -> vide
| IDENTIFIER (","  IDENTIFIER)*  -> aumoinsune
fonction : "len" "(" IDENTIFIER ")"  ->length
IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/
OPBIN : /[+\-*>]/
STRING : /[a-zA-Z][a-zA-Z0-9.,!?]*/
%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""",start="prg")

op = {'+' : 'add', '-' : 'sub'}

list_str = []

def asm_exp(e):
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_var":
        return f"mov rax, [{e.children[0].value}]\n"
    elif e.data == "exp_par":
        return asm_exp(e.children[0])
    elif e.data == "exp_opbin":
        E1 = asm_exp(e.children[0])
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        push rax
        {E1}
        pop rbx
        {op[e.children[1].value]} rax, rbx
        """
    elif e.data == "exp_str":

        return f"mov rax, str{list_str.index(e.children[0].value)} \0\n"

def pp_exp(e):
    if e.data in {"exp_nombre", "exp_var"}:
        return e.children[0].value
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    elif e.data == "exp_opbin":
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"
    elif e.data == "exp_str":
        return f"{e.children[0].value}"


def vars_exp(e):
    if e.data  == "exp_nombre" :
        return set()
    elif e.data ==  "exp_var":
        return { e.children[0].value }
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "exp_opbin":
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        #print(type(e.children[2].value))
        return L | R
    elif e.data == "exp_str":
        #print(e.children[0].value)
       # return { e.children[0].value }
       list_str.append(e.children[0].value)
       return set()

cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

def asm_com(c):
    if c.data == "assignation":
        E = asm_exp(c.children[1])
        #print(E)
        return f"""
        {E}
        mov [{c.children[0].value}], rax        
        """
    elif c.data == "if":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        {E}
        cmp rax, 0
        jz fin{n}
        {C}
fin{n} : nop
"""
    elif c.data == "while":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        debut{n} : {E}
        cmp rax, 0
        jz fin{n}
        {C}
        jmp debut{n}
fin{n} : nop
"""
    elif c.data == "print":
        E = asm_exp(c.children[0])
        return f"""
        {E}
        mov rdi, fmt
        mov rsi, rax
        call printf
        """

def pp_com(c):
    if c.data == "assignation":
        return f"{c.children[0].value} = {pp_exp(c.children[1])};"
    elif c.data == "if":
        x = f"\n{pp_bcom(c.children[1])}"
        return f"if ({pp_exp(c.children[0])}) {{{x}}}"
    elif c.data == "while":
        x = f"\n{pp_bcom(c.children[1])}"
        return f"while ({pp_exp(c.children[0])}) {{{x}}}"
    elif c.data == "print":
        return f"print({pp_exp(c.children[0])})"
    elif c.data == "attribut":
        return f"{pp_attribut(c.children[0])} = {pp_exp(c.children[1])};"



def vars_com(c):
    if c.data == "assignation":
        R = vars_exp(c.children[1])
        #print(R)
        #print(c.children[1])
        return {c.children[0].value} | R
    elif c.data in {"if", "while"}:
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0]) 
        return E | B
    elif c.data == "print":
        return vars_exp(c.children[0])

def asm_bcom(bc):
    return "".join([asm_com(c) for c in bc.children])

def pp_bcom(bc):
    return "\n".join([pp_com(c) for c in bc.children])

def vars_bcom(bc):
    S = set()
    for c in bc.children:
        S = S | vars_com(c)
    return S

def pp_var_list(vl):
    return ", ".join([t.value for t in vl.children])

def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    D += "\n"+"\n".join([f"str{list_str.index(v)} : db \"{v}\", 0" for v in list_str])
    moule = moule.replace("DECL_VARS", D)  # need to write DECL_VARS before asm_exp and asm_bcom to name var str
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    E = asm_exp(p.children[2])
    moule = moule.replace("RETURN", E)
    s = ""
    for i in range(len(p.children[0].children)):
        v = p.children[0].children[i].value
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx + { 8*(i+1)}]
        xor rax, rax
        call atoi
        mov [{v}], rax
        """
        s = s + e
    moule = moule.replace("INIT_VARS", s)    
    return moule

def vars_prg(p):
    L = set([t.value for t in p.children[0].children])
    C = vars_bcom(p.children[1])
    R = vars_exp(p.children[2])
    print(p.children[1])
    #print(C)
    return L | C | R

def pp_prg(p):
    L = pp_var_list(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main( %s ) { %s return(%s);\n}" % (L, C, R)

def pp_constructor(cons):
    #print(cons.children[0])
    I = cons.children[0]
    L = pp_var_list(cons.children[1])
    C = pp_bcom(cons.children[2])
    #print(C)
    return "%s ( %s ) { %s \n}" % (I, L, C)

def pp_attribut(a):
    if a.data == "assignation":
        return f"{a.children[0].value}"
    elif a.data == "self":
        return f"{a.children[0].value}.{a.children[1].value}"

def pp_class(c):
    I = c.children[0]
    CONS = pp_constructor(c.children[1])
    return "class %s{ %s \n}" % (I, CONS)

#ast = grammaire.parse("""main(x,y){
        #while(x){
           # x = x - 1;
           # y = y + 1;
        #}
    #return (y);
#}
#""")
#asm = asm_prg(ast)
#f = open("ouf.asm", "w")
#f.write(asm)
#f.close()


#ast_class = grammaire.parse("""class A {
    #A(x,y,z){
       #self.x = x;
        #y = 1;
        #z = 2;
    #}
#}
#""")


#ast_constructor = grammaire.parse("""
#A(x){
        #self.x = x;
        #x = y;
   # }
#""")
#print(pp_class(ast_class))
#print(pp_constructor(ast_constructor))

ast_string1=grammaire.parse(""" main(x){
 x = "coucou,hello.aaaaaa";
 return (x);}
 
 """)
asm_string1 = asm_prg(ast_string1)
#print(pp_prg(ast_string1))
#print(asm_prg(ast_string1))
f = open("ouf_string1.asm", "w")
f.write(asm_string1)
f.close()