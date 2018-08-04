#!/usr/bin/python3

# Todo:
# eax -> ax -> ah/al
# op code jg/jl
# opcode hex/dec,hex/dec
# corriger list func 

import os, sys, re

TAB_SIZE = 4
TAB = 4 * " "

DUMP_CMD="objdump -d -M intel --no-show-raw-insn --prefix-addresses"

RE_FUNC_HDR = r'^[0-9a-f]+ <[a-zA-Z_]*>'
RE_FUNC = r'^[0-9a-f]+ <[a-zA-Z_]*>'

offset_index = {}

def wr_newline(txt, tab=0, nl=0):
    return tab * TAB + txt + "\n" + nl * "\n"

def gen_header(filename, funcname):
    
    header = wr_newline("#!/usr/bin/python3\n")
    header += wr_newline("# Generated by Asm2py")
    header += wr_newline("# Binary : " + filename)
    header += wr_newline("# Function : " + funcname, 0, 2)

    header += wr_newline("import sys",0,1)

    header += wr_newline("#Create Stack")
    header += wr_newline("stack = list()",0,1)

    header += wr_newline("#Create flags")
    flags = ["FZ","FN"]
    header += wr_newline( "=".join(flags) + "=0",0,1)
    
    header += wr_newline("def cmp(x,y):")
    header += wr_newline("global FZ",1)
    header += wr_newline("FZ = True if x == y else False",1)
    header += wr_newline("FN = True if ( (x-y) < 0) else False",1,1)

    header += wr_newline("test = cmp")

    header += wr_newline("def jg(addr):")
    header += wr_newline("global FN",1)
    header += wr_newline("if(not FN):",1)
    header += wr_newline("goto(addr-1)",2)

    header += wr_newline("def jl(addr):")
    header += wr_newline("global FN",1)
    header += wr_newline("if(FN):",1)
    header += wr_newline("goto(addr-1)",2)

    header += wr_newline("def je(addr):")
    header += wr_newline("global FZ",1)
    header += wr_newline("if(FZ):",1)
    header += wr_newline("goto(addr-1)",2)
    header += wr_newline("jz = je",0,1)

    header += wr_newline("def jne(addr):")
    header += wr_newline("global FZ",1)
    header += wr_newline("if(not FZ):",1)
    header += wr_newline("goto(addr-1)",2)

    header += wr_newline("nop = lambda : None",0,1)

    header += wr_newline("#Create registers")
    # manage AL, AH...
    regs = ["eax","ebx","ecx","edx",
            "edi","esi","eip","esp","ebp"]

    header += wr_newline( "=".join(regs) + "=0",0,1)

    header += wr_newline("def print_regs():")
    header += wr_newline("print('Registers Dump')",1)
    header += wr_newline("for reg in " + str(regs) + ":",1)
    header += wr_newline("print(reg, '=', eval(reg))",2,1)

    header += wr_newline("#Debug exemple for line 0 :")
    header += wr_newline("debug_instructions = { 0 : 'print(\"Debug starts\")'}",0,1)


    header += wr_newline("def come_from(ceip):")
    header += wr_newline("eval(debug_instructions.get(ceip,'nop()'))",1,1)

    header += wr_newline("#Create .text")
    header += wr_newline("ins = [")

    return header


def gen_runner():

    runner = ""
    runner += wr_newline("def goto(i): #i know i'll go to hell for that")
    runner += wr_newline("global eip",1)
    runner += wr_newline("eip = i",1,1)

    runner += wr_newline("jmp = call = goto")

    runner += wr_newline("while(eip < len(ins)):")
    runner += wr_newline("print('eip : ', eip, 'inst: ', ins[eip])",1)
    runner += wr_newline("come_from(eip)",1)
    runner += wr_newline("exec(ins[eip])",1)
    runner += wr_newline("eip+=1",1,1)

    runner += wr_newline("print_regs()")
    return runner


def create_script(filename, funcname):
    output_name = filename + "::" + funcname + ".py"
    file = open(output_name, "w")
    file.write(gen_header(filename,funcname))
    return file

def get_func_list(raw_asm):
    re_find_func = re.compile(RE_FUNC_HDR, re.M)
    func = re_find_func.findall(raw_asm)
    func_list = []
    i = 1
    for func_found in func :
        func_name = func_found.replace('<','').replace('>','')
        func_name = func_name.split()[1]
        func_list.append(func_name)
        print(i, ":", func_name)
        i += 1
    return func_list

def choose_func(funcs):

    good_choice = False
    maxf = len(funcs)
    input_str = "Function to pythonize ? [1-" + str(maxf) + "]"
    while(not good_choice):
        try:
            choice = int(input(input_str))
            if(choice > 0 and choice <= maxf):
                good_choice = True
        except ValueError:
            print("Bad value")
    return funcs[choice-1]

def bind_offset_index(raw):
    
    global offset_index
    index = -1
    
    offset_re = r'[0-9a-f]+ <[a-z0-9_\-]+\+(0x[0-9a-f]+)>'

    for line in raw.split('\n'):
        index += 1
        if (index == 0) or (line==""):
            continue
        print(line)
        offset_s = re.search(offset_re, line).group(1)
        offset_index[offset_s] = index

def get_raw_func(raw_asm,func_name):

    raw = ""

    regex_func = r'^[0-9a-f]+ <'+ func_name +'([\+0x[a-f0-9]*)?>'
    regex_find = re.compile(regex_func, re.M)
    
    for line in raw_asm.split("\n"):
        if(regex_find.search(line)):
            raw += line + "\n"
    bind_offset_index(raw)
    return raw

space_padding = lambda line : 40 - len(line)

def analyze(raw_func, ofile):

    global cur_func

    raw_func = bulk_transform(raw_func)
    instructions = ""
    line_nr = 0
    for line in raw_func.split("\n"):
        if line == "":
            continue
        
        opcodes = " ".join(line.split()[2:]) # default (copy)
        
        instructions += TAB + "'"+ opcodes + "',"
        instructions += " " * space_padding(opcodes)
        instructions += "#" + str(hex(line_nr))
        instructions += " (" + str(line_nr) +")"+"\n"
        line_nr += 1
    instructions += "]\n" # end of ins
    ofile.write(instructions)


def bulk_transform(raw_func):

    global cur_func
    raw_func = re.sub(r"( |\t){2,}"," ", raw_func)

    bulk_dict = [

        # Pre-format
        {"from": r"r([0-9]{2})[a-z]([ ,]?)", "to":r"r\1\2"},

        # General 
        {"from" : r"mov ([a-z]+),([0-9a-z]*)", "to":r"\1 = \2"},
        {"from" : r"xchg ([a-z]+),([a-z]+)", "to":r"\1, \2 = \2, \1"},
        {"from" : r"ret", "to":r"sys.exit(0)"},
        {"from" : r"lea ([a-z]+),\[([0-9a-z\-\*\+]+)\]","to":r"\1 = \2"},
        {"from" : r"(cmp|test) ([a-z]+),([0-9a-z]+)","to":r"cmp(\2,\3)"},
        #Control flow
        
        # Hexa
        {
            "from" : r"(call|jmp|jne|je|jz|jg|jl) [0-9a-f]+ <"+cur_func+"\+(0x[0-9a-f]+)>",
            #"to": lambda m: m.group(1) + "(" + str( int(m.group(2),16) - 2) + ")" # -2 pour ajuster eip
           "to": lambda m: m.group(1) + "(" + str( offset_index.get(m.group(2),m.group(2))) + ")"
        },
        #Decimal
        #{
        #   "from" : r"(call|jmp|jne|je|jz) [0-9a-f]+ <"+cur_func+"\+([0-9]+)>",
        #   "to": lambda m: m.group(1) + "(" + str( int(m.group(2)) - 2) + ")" # -2 pour ajuster eip
        #}, 

        #Bitwise
        {"from" : r"shr ([a-z]+),([x0-9a-z]*)", "to":r"\1 = \1 >> \2"},
        {"from" : r"shl ([a-z]+),([x0-9a-z]*)", "to":r"\1 = \1 << \2"},
        {"from" : r"xor ([a-z]+),([x0-9a-z]*)", "to":r"\1 ^= \2"},
        {"from" : r"and ([a-z]+),([x0-9a-z]*)", "to":r"\1 &= \2"},
        {"from" : r"or ([a-z]+),([x0-9a-z]*)", "to":r"\1 \|= \2"},

        #Basic operations
        {"from" : r"add ([a-z]+),([0-9a-z]*)", "to":r"\1 += \2"},
        {"from" : r"sub ([a-z]+),([0-9a-z]*)", "to":r"\1 -= \2"},
        {"from" : r"inc ([a-z]+)", "to":r"\1 += 1"},
        {"from" : r"dec ([a-z]+)", "to":r"\1 -= 1"},

        # Stack
        {"from" : r"push ([a-z0-9]+)", "to": r"stack.append(\1)"},
        {"from" : r"pop ([a-z0-9]+)", "to": r"\1 = stack.pop()"}
    #   {"from": "a", "to": "d"}
]

    for item in bulk_dict:
        raw_func = re.sub(item["from"], item["to"], raw_func)

    return raw_func


if(len(sys.argv) < 2):
    print("usage ./", sys.argv[0], ' binary')
    sys.exit(1)

raw_asm = os.popen(DUMP_CMD + " " + sys.argv[1])
raw_asm = raw_asm.read()

cur_func = choose_func(get_func_list(raw_asm))
print("Function :", cur_func)

raw_func = get_raw_func(raw_asm,cur_func)
#print(raw_func)

output_file = create_script(sys.argv[1], cur_func)

analyze(raw_func, output_file)


output_file.write(gen_runner())
output_file.close()


# convertir write en printf

#dump strings dans un tableau data= { [offset] = "string" }