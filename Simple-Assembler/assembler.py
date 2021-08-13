error = ''
linenumber = 1
linenumber_pass2 = 0
commands = []
binary = []

registers = {
    'R0':'000',
    'R1':'001',
    'R2':'010',
    'R3':'011',
    'R4':'100',
    'R5':'101',
    'R6':'110',
    'FLAGS':'111'
}

opcode = {
    'add': ("00000",'A',3),
    'sub': ("00001",'A',3),
    'mov': ("00010",'B',2),
    'mov2': ("00011",'C',2),  #fix this somehow
    'ld': ("00100",'D',2),
    'st': ("00101",'D',2),
    'mul': ("00110",'A',3),
    'div': ("00111",'C',2),
    'rs': ("01000",'B',2),
    'ls': ("01001",'B',3),
    'xor': ("01010",'A',3),
    'or': ("01011",'A',3),
    'and': ("01100",'A',3),
    'not': ("01101",'C',2),
    'cmp': ("01110",'C',2),
    'jmp': ("01111",'E',1),
    'jlt': ("10000",'E',1),
    'jgt': ("10001",'E',1),
    'je': ("10010",'E',1),
    'hlt': ("10011",'F',0)
}

variablesymbols =  {}
labelsymbols = {}

errorlist = {
    'a':'ERROR: Typos in instruction name or register name at',
    'b': 'ERROR: Use of undefined variables at',
    'c': 'ERROR: Use of undefined labels at',
    'd': 'ERROR: Illegal use of FLAGS register at',
    'e': 'ERROR: Illegal Immediate values (less than 0 or more than 255) at',
    'f': 'ERROR: Misuse of label as variable at',
    'f2': 'ERROR: Misuse of variable as label at',
    'g': 'ERROR: Variables not declared at the beginning at',
    'h': 'ERROR: Missing hlt instruction after',
    'i': 'ERROR: hlt not being used as the last instruction at',
    'j': 'ERROR: Wrong syntax used for instructions at',
    'k': 'ERROR: General Syntax Error at',
    'l': 'ERROR: Misuse of label as reserved key words at'
}


"""To accept till EOF and store each line in a list commands[]"""
def readdata():
    while True:                         
            try:
                line=input()
                commands.append(line)       
            except EOFError:
                break

def toBinary(n):
    b = bin(n).replace("0b", "")
    if len(b) < 8:
        b = '0'*(8-len(b)) + b
    return b

def pass1():

    pc=0
    
    global error
    global variablesymbols
    global labelsymbols
    notvar=0

    global linenumber

    for line in commands:
        if line=='':
            linenumber+=1
            continue

        words=line.split()
        
        if words[0] =='var':    #check for variables
            if len(words) !=2:
                error='k'
                return
            elif not(words[1].replace('_', 'U').isalnum()):
                error='k'
                return

            elif notvar==1: # if its 1, it means variable is defined in middle
                error='g'
                return
            else:
                variablesymbols[words[1]]=None
                linenumber+=1
        

        elif words[0][-1]==':':
            if not(words[0][0:-1].replace('_', '').isalnum()):
                error='k'
                return
        
            elif words[1] not in opcode:
                error='a'
                return
            
            else:
                labelsymbols[words[0]]=pc
                notvar=1
                pc+=1
                linenumber+=1
                                           

        elif words[0] in opcode:
            notvar=1
            pc+=1          
            linenumber+=1 
      
        else:
        
            error='a'
            return
    
    for x in variablesymbols:
        variablesymbols[x]=pc
        pc+=1

def pass2():

    global linenumber_pass2
    global error
    global binary
    flag = 0

    for line in commands:
        #line = commands[i]
        linenumber_pass2 += 1

        if line == '':      # remove?
            continue
        
        if flag == 1:
            linenumber_pass2 -= 1
            error = 'i'
            return

        words = line.split()
        #print(words)

        if words[0] =='var':
            continue

        if words[0] in labelsymbols:        #-------((DO))) ALSO MAKE ERROR TO CHECK IF label is a var instead
            if words[0][:-1] in variablesymbols:
                error = 'f2'   # Changed to f2
                return
            if words[0][:-1] in opcode or words[0][:-1] in registers:
                error = 'l'
                return
            for i in range(len(words)-1):
                words[i] = words[i+1]
            words.pop() #------ Fixed your Error here by adding this statement, since it was causing problems in hard testcase 2, length of words list also needed to be decreased

        if words[0] in opcode:
            if words[0] == 'add':       #add
                #try:
                #    x = words[3]
                #except:            ------commented
                #    error = 'j'
                #    return

                if len(words)!=4:
                    error = 'j'     #--------added by me
                    return

                if words[1] in registers and words[2] in registers and words[3] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS" or words[3] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("00000" + "00" + registers[words[1]] + registers[words[2]] + registers[words[3]])
                else:
                    error = 'a'
                    return
            
            elif words[0] == 'sub':     #sub
                #try:
                #    x = words[3]
                #except:
                #    error = 'j'
                #   return

                if len(words)!=4:
                    error = 'j'     #--------added by me
                    return
                    
                if words[1] in registers and words[2] in registers and words[3] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS" or words[3] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("00001" + "00" + registers[words[1]] + registers[words[2]] + registers[words[3]])
                else:
                    error = 'a'
                    return

            elif words[0] == 'mov':     #mov
                if len(words)!=3:       #------added
                    error='j'           #------by
                    return              #------me

                if words[1] in registers:
                    if words[1] == "FLAGS":
                        error = 'd'
                        return
                    if words[2] in registers:
                        binary.append("00011" + "00000" + registers[words[1]] + registers[words[2]])
                    else:
                        if words[2][0] != '$':
                            error = 'k'         # or a?
                            return
                        words[2] = words[2][1:]
                        try:
                            imm = int(words[2])
                            if imm >= 0 and imm <= 255:
                                binary.append("00010" + registers[words[1]] + toBinary(imm))
                            else:
                                error = 'e'
                                return
                        except:
                            error = 'a' #---------- or k, need to check???
                            return
                else:
                    error = 'a'
                    return
            
            elif words[0] == 'ld':      #ld
                if len(words) != 3:
                    error = 'j'
                    return
                if words[2] in registers or words[2][0] == '$':
                    error = 'j'
                    return
                if words[1] in registers:
                    if words[1] == "FLAGS":
                        error = 'd'
                        return
                    if words[2] in variablesymbols:
                        binary.append("00100" + registers[words[1]] + toBinary(variablesymbols[words[2]]))
                    elif words[2] + ':' in labelsymbols:
                        error = 'f' #-----newnewnewedit
                        return
                    elif words[2].replace('_', 'U').isalnum():
                        error = 'b'
                        return
                    else:
                        error = 'k'
                        return
                else:
                    error = 'a'
                    return

            elif words[0] == 'st':      #st
                if len(words) != 3:
                    error = 'j'
                    return
                if words[2] in registers or words[2][0] == '$':
                    error = 'j'
                    return
                if words[1] in registers:
                    if words[1] == "FLAGS":
                        error = 'd'
                        return
                    if words[2] in variablesymbols:
                        binary.append("00101" + registers[words[1]] + toBinary(variablesymbols[words[2]]))
                    elif words[2] + ':' in labelsymbols:
                        error = 'f'
                        return
                    elif words[2].replace('_', 'U').isalnum():
                        error = 'b'
                        return
                    else:
                        error = 'k'
                        return
                else:
                    error = 'a'
                    return

            elif words[0] == 'mul':     #mul
                #try:
                #    x = words[3]
                #except:
                #    error = 'j'
                #    return

                if len(words)!=4:
                    error = 'j'     #--------added by me
                    return
                
                if words[1] in registers and words[2] in registers and words[3] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS" or words[3] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("00110" + "00" + registers[words[1]] + registers[words[2]] + registers[words[3]])
                else:
                    error = 'a'
                    return

            elif words[0] == 'div':     #div
                if len(words) != 3:
                    error = 'j'
                    return
                if words[2] in variablesymbols or words[2][0] == '$':
                    error = 'j'
                    return
                if words[1] in registers and words[2] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("00111" + "00000" + registers[words[1]] + registers[words[2]])
                else:
                    error = 'a'
                    return

            elif words[0] == 'rs':      #rs
                if len(words) != 3:
                    error = 'j'
                    return
                if words[2] in registers or words[2] in variablesymbols:
                    error = 'j'
                    return
                if words[1] in registers:
                    if words[1] == "FLAGS":
                        error = 'd'
                        return
                    if words[2][0] != '$':
                        error = 'k'         # or a?
                        return
                    words[2] = words[2][1:]
                    try:
                        imm = int(words[2])
                        if imm >= 0 and imm <= 255:
                            binary.append("01000" + registers[words[1]] + toBinary(imm))
                        else:
                            error = 'e'
                            return
                    except:
                        error = 'a' #---------- or k, need to check???
                        return
                else:
                    error = 'a'

            elif words[0] == 'ls':      #ls
                if len(words) != 3:
                    error = 'j'
                    return
                if words[2] in registers or words[2] in variablesymbols:
                    error = 'j'
                    return
                if words[1] in registers:
                    if words[1] == "FLAGS":
                        error = 'd'
                        return
                    if words[2][0] != '$':
                        error = 'k'         # or a?
                        return
                    words[2] = words[2][1:]
                    try:
                        imm = int(words[2])
                        if imm >= 0 and imm <= 255:
                            binary.append("01001" + registers[words[1]] + toBinary(imm))
                        else:
                            error = 'e'
                            return
                    except:
                        error = 'a' #---------- or k, need to check???
                        return
                else:
                    error = 'a'

            elif words[0] == 'xor':     #xor
                #try:
                #    x = words[3]
                #except:
                #    error = 'j'
                #   return

                if len(words)!=4:
                    error = 'j'     #--------added by me
                    return

                if words[1] in registers and words[2] in registers and words[3] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS" or words[3] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("01010" + "00" + registers[words[1]] + registers[words[2]] + registers[words[3]])
                else:
                    error = 'a'
                    return
            
            elif words[0] == 'or':      #or
                #try:
                #    x = words[3]
                #except:
                #    error = 'j'
                #   return

                if len(words)!=4:
                    error = 'j'     #--------added by me
                    return
                
                if words[1] in registers and words[2] in registers and words[3] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS" or words[3] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("01011" + "00" + registers[words[1]] + registers[words[2]] + registers[words[3]])
                else:
                    error = 'a'
                    return

            elif words[0] == 'and':     #and
                #try:
                #    x = words[3]
                #except:
                #    error = 'j'
                #   return

                if len(words)!=4:
                    error = 'j'     #--------added by me
                    return
                if words[1] in registers and words[2] in registers and words[3] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS" or words[3] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("01100" + "00" + registers[words[1]] + registers[words[2]] + registers[words[3]])
                else:
                    error = 'a'
                    return

            elif words[0] == 'not':     #not
                if len(words) != 3:
                    error = 'j'
                    return
                if words[2][0] == '$' or words[2] in variablesymbols:
                    error = 'j'
                    return
                if words[1] in registers and words[2] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("01101" + "00000" + registers[words[1]] + registers[words[2]])
                else:
                    error = 'a'
                    return

            elif words[0] == 'cmp':     #cmp
                if len(words) != 3:
                    error = 'j'
                    return
                if words[2][0] == '$' or words[2] in variablesymbols:
                    error = 'j'
                    return
                if words[1] in registers and words[2] in registers:
                    if words[1] == "FLAGS" or words[2] == "FLAGS":
                        error = 'd'
                        return
                    binary.append("01110" + "00000" + registers[words[1]] + registers[words[2]])
                else:
                    error = 'a'
                    return

            elif words[0] == 'jmp':     #jmp
                #try:
                #    x = words[1]
                #except:
                #    error = 'j'
                #   return

                if len(words)!=2:
                    error = 'j'     #--------added by me
                    return
                if words[1] + ':' in labelsymbols:
                    binary.append("01111" + "000" + toBinary(labelsymbols[words[1] + ':']))
                elif words[1] in variablesymbols:
                    error = 'f2'   # Changed to f2
                    return
                elif words[1].replace('_', 'U').isalnum():
                    error = 'c'
                    return
                else:
                    error = 'a'   #-------- or k?? check once
                    return

            elif words[0] == 'jlt':     #jlt
                #try:
                #    x = words[1]
                #except:
                #    error = 'j'
                #   return

                if len(words)!=2:
                    error = 'j'     #--------added by me
                    return

                if words[1] + ':' in labelsymbols:
                    binary.append("10000" + "000" + toBinary(labelsymbols[words[1] + ':']))
                elif words[1] in variablesymbols:
                    error = 'f2'  # Changed to f2
                    return
                elif words[1].replace('_', 'U').isalnum():
                    error = 'c'
                    return
                else:
                    error = 'a'   #-------- or k?? check once
                    return
            
            elif words[0] == 'jgt':     #jgt
                #try:
                #    x = words[1]
                #except:
                #    error = 'j'
                #   return

                if len(words)!=2:
                    error = 'j'     #--------added by me
                    return

                if words[1] + ':' in labelsymbols:
                    binary.append("10001" + "000" + toBinary(labelsymbols[words[1] + ':']))
                elif words[1] in variablesymbols:
                    error = 'f2'   # Changed to f2
                    return
                elif words[1].replace('_', 'U').isalnum():
                    error = 'c'
                    return
                else:
                    error = 'a'  #-------- or k?? check once
                    return

            elif words[0] == 'je':      #je
                #try:
                #    x = words[1]
                #except:
                #    error = 'j'
                #   return

                if len(words)!=2:
                    error = 'j'     #--------added by me
                    return

                if words[1] + ':' in labelsymbols:
                    binary.append("10010" + "000" + toBinary(labelsymbols[words[1] + ':']))
                elif words[1] in variablesymbols:
                    error = 'f2'   # Changed to f2
                    return
                elif words[1].replace('_', 'U').isalnum():
                    error = 'c'
                    return
                else:
                    error = 'a'  #-------- or k?? check once
                    return

            elif words[0] == 'hlt':     #hlt
                
                if len(words) > 1 and len(words) <= 4:
                    error = 'j'
                    return
                flag = 1
                binary.append("1001100000000000")
        else:
            error = 'a'     # or k
    if flag == 0:
            error = 'h'
            return
            

def main():
    
    # Read all data first
    readdata()
    pass1()         # First pass to set the variables and labels & check some errors

    if error=='':
        #print(variablesymbols)
        #print(labelsymbols)

        pass2()     # Second Pass
        
        if error != '':
            print(errorlist[error],"line",linenumber_pass2)
        else:
            for x in binary:
                print(x)

    else:
        print(errorlist[error],"line",linenumber)


if __name__ == "__main__":
    main()

