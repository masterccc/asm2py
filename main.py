#!/usr/bin/python3

import os, sys, re

def gen_instruction(txt, tab=0, nl=0):
	return tab * "\t" + txt + "\n" + nl * "\n"

def gen_header(filename, funcname):
	
	header = gen_instruction("#!/usr/bin/python3\n")
	header += gen_instruction("# Generated by Asm2py")
	header += gen_instruction("# Binary : " + filename)
	header += gen_instruction("# Function : " + funcname, 0, 2)

	header += gen_instruction("import sys",0,1)

	header += gen_instruction("#Create Stack")
	header += gen_instruction("stack = list()",0,1)

	header += gen_instruction("#Create registers")

	# manage AL, AH...
	regs = ["eax","ebx","ecx","edx",
			"edi","esi","eip","esp","ebp"]

	header += gen_instruction( "=".join(regs) + "=0",0,1)

	header += gen_instruction("def print_regs():")
	header += gen_instruction("print('Registers Dump')",1)
	header += gen_instruction("for reg in " + str(regs) + ":",1)
	header += gen_instruction("print(reg, '=', eval(reg))",2,1)

#	header += gen_instruction("# user defined functions")

	header += gen_instruction("#Create .text")
	header += gen_instruction("ins = [")

	return header


def gen_runner():

	runner = ""
	runner += gen_instruction("def goto(i): #i know i'll go to hell for that")
	runner += gen_instruction("\tglobal eip",1)
	runner += gen_instruction("\teip += 1",1,1)

	runner += gen_instruction("while(eip < len(ins)):")
	runner += gen_instruction("print('eip : ', eip, 'inst: ', ins[eip])",1)
	runner += gen_instruction("exec(ins[eip])",1)
	runner += gen_instruction("eip+=1",1,1)

	runner += gen_instruction("print_regs()")
	return runner


def create_script(filename, funcname):
	output_name = filename + "::" + funcname + ".py"
	file = open(output_name, "w")
	file.write(gen_header(filename,funcname))
	return file

def get_func_list(raw_asm):
	re_find_func = re.compile(RE_FUNC)
	func = re_find_func.findall(raw_asm)
	func_list = []
	i = 1
	for func_found in func :
		func_name =	func_found.replace('<','').replace('>','')
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
	
def get_raw_func(raw_asm,func_name):

	raw = ""
	regex_func = r'<'+func_name+'([\+0x[a-f0-9]*)?>'
	regex_find = re.compile(regex_func)
	
	for line in raw_asm.split("\n"):
		if(regex_find.search(line)):
			raw += line + "\n"
	return raw


def analyze(raw_func, ofile):

	global cur_func

	jmp_re = r'<' + cur_func +'+0x[0-9a-z]+>'
	jmp_re_c = re.compile(jmp_re)

	raw_func = bulk_transform(raw_func)
	instructions = ""
	for line in raw_func.split("\n"):
		if line == "":
			continue
		
		opcodes = " ".join(line.split()[2:]) # default (copy)
		
		#if(jmp_re_c.search() != False):
		# opcode like 'call 00001040 <strcmp@plt>'
		#je     10f8 <deregister_tm_clones+0x38>
		#call   1050 <__libc_start_main@plt>
		#cur_func
		
		instructions += "\t'" + opcodes + "',\n"
	instructions += "]\n" # end of ins
	ofile.write(instructions)


def bulk_transform(raw_func):

	global cur_func
	raw_func = re.sub(r"( |\t){2,}"," ", raw_func)

	bulk_dict = [

		# General 
		{"from" : r"mov ([a-z]+),([0-9a-z]*)", "to":r"\1 = \2"},
		{"from" : r"xchg ([a-z]+),([a-z]+)", "to":r"\1, \2 = \2, \1"},
		{"from" : r"ret", "to":r"sys.exit(0)"},
		
		#Control flow
		{
			"from" : r"(call|jmp) [0-9a-f]+ <"+cur_func+"\+(0x[0-9a-f]+)>",
			"to":r"goto(\2)"
		},
		#jmp 000012b9 <main+0xd0>
		# opcode like 'call 00001040 <strcmp@plt>'
		#je     10f8 <deregister_tm_clones+0x38>
		#call   1050 <__libc_start_main@plt>

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
		{"from" : r"pop ([a-z]+)", "to": r"\1 = stack.pop()"}
	#	{"from": "a", "to": "d"}
	]

	for item in bulk_dict:
		raw_func = re.sub(item["from"], item["to"], raw_func)

	return raw_func

DUMP_CMD="objdump -d -M intel --no-show-raw-insn --prefix-addresses"

RE_FUNC = r'<[a-zA-Z_]*>'


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