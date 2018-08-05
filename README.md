# Asm2py - Assembly to python converter

/!\ Experimental prototype. 32 bits only. It doesn't cover all opcodes, all registers (or sub registers) or some memory manipulations (there is not stack yet, no .data section, etc...). Some adjustements may be required in the source code of the target binary to make the conversion easier (like register variables if C is used).

# Wut ?

Asm2py converts assembly functions (dumped from an ELF binary via objdump) to python instructions. The program allows you to select a function to analyze and converts it to python. The generated python instructions take place inside a new file. Once the python script is generated you can execute and debug it. It can help to understand some (simple) assembly pieces of code for a better understanding or reverse engineering purposes.


# Dependancies

This program runs under python3, you need the objdump program ( "binutils" package).

# Exemple

## Compile the fibbo sample

```
gcc -o fibbo sample/fibbo.c
```

This simple program computes a Fibonacci serie.


## Run main.py

```
python3 main.py fibbo
or
chmod +x main.py
./main.py fibbo
```

When the following list appears, select fibbo's function number :

```
$ python3 main.py fibbo
1 : _init
2 : _start
3 : deregister_tm_clones
4 : register_tm_clones
5 : __do_global_dtors_aux
6 : frame_dummy
7 : main
8 : fibbo
9 : __libc_csu_init
10 : __libc_csu_fini
11 : _fini
Function to pythonize ? [1-11]8
Selected function : fibbo
```

## Read and edit fibbo::fibbo.py

This file contains assembly instructions converted to python :

```python
ins = [

	...

    'edi = 0x1',                               #0x8 (8)
    'ebx = 0x0',                               #0x9 (9)
    'jmp(20)',                                 #0xa (10)
    'cmp(ebx,0x1)',                            #0xb (11)
    'jg(15)',                                  #0xc (12)
    
    ...
]
```

## Breakpoint/Debug

You can execute some piece of code when a line is reached during execution with the ```debug_instructions``` var.

```
debug_instructions = { REACHED_LINE: 'STR_PAYLOAD'}
```

### Exemple :

```
debug_instructions = { 0 : 'print("Debug starts")'}
```

It prints "Debug start" before executing line 0. If you want to inspect registers before a comparison :

```'cmp(ebx,0x1)',                            #0xb (11)```

Write this :

```
debug_instructions = { 11 : 'print_regs()'}
```

## Execute the generated script

```python3 fibbo::fibbo.py```

Output (with a debug instruction placed before execution of ```cmp``` opcode):

```
eip :  0 inst:  stack.append(ebp)
eip :  1 inst:  ebp = esp
eip :  2 inst:  stack.append(edi)
eip :  3 inst:  stack.append(esi)
eip :  4 inst:  stack.append(ebx)
eip :  5 inst:  eax += 0x2e0b
eip :  6 inst:  eax = 0xf
eip :  7 inst:  edx = 0x0
eip :  8 inst:  edi = 0x1
eip :  9 inst:  ebx = 0x0
eip :  10 inst:  jmp(20)
eip :  20 inst:  cmp(ebx,eax)
eip :  21 inst:  jl(11)
eip :  11 inst:  cmp(ebx,0x1)
Registers Dump
eax = 15
ebx = 0
ecx = 0
edx = 0
edi = 1
esi = 0
eip = 11
esp = 0
ebp = 0
eip :  12 inst:  jg(15)
eip :  13 inst:  esi = ebx
eip :  14 inst:  jmp(19)
eip :  19 inst:  ebx += 0x1
eip :  22 inst:  eax = esi
eip :  23 inst:  ebx = stack.pop()
eip :  24 inst:  esi = stack.pop()
eip :  25 inst:  edi = stack.pop()
eip :  26 inst:  ebp = stack.pop()
eip :  27 inst:  print('End')
End
Registers Dump
eax = 610
ebx = 0
ecx = 0
edx = 377  
edi = 0
esi = 0
eip = 28
esp = 0
ebp = 0
```

edx contains the result of the ```fibbo()``` function.

## Functions Parameters

Some functions need parameters (```fibbo``` doesn't, ```pgcd``` does) to run you can set them in the generated script :

```
# Local variables
locvar1=768
locvar2=128
locvar3=0
```

## Blacklist call/addresses/lines

You can disable the conversion of some opcodes, jumps or everything else that is present in the assembly code. It will not appear in the generated python script.

Use the trash_funcs array :

```
trash_funcs = [
    "__x86.get_pc_thunk.ax"
]
```

# Other examples

A ```pgcd.c``` example is available is ```sample/```. It uses function with arguments.