import matplotlib.pyplot as plt
import time;

commands=[]
memory=['0000000000000000']*256

registers={
    0:'0000000000000000',
    1:'0000000000000000',
    2:'0000000000000000',
    3:'0000000000000000',
    4:'0000000000000000',
    5:'0000000000000000',
    6:'0000000000000000',
    7:'0000000000000000'
}

pc=0
cycle=0

cycle_x=[]
address_y=[]

#---------------------------------------------------------------------------------

def toBinary_8bit(n):
    b = bin(n).replace("0b", "")
    if len(b) < 8:
        b = '0'*(8-len(b)) + b
    return b

def toBinary_16bit(n):
    b = bin(n).replace("0b", "")
    if len(b) < 16:
        b = '0'*(16-len(b)) + b
    if len(b) > 16: # To ignore overflow digits
        b = b[-16:]
    return b

def readdata():
    while True:                         
            try:
                line=input()
                commands.append(line)       
            except EOFError:
                break

def mem_dump():
    for i in memory:
        print(i)

def pc_dump():
    print(toBinary_8bit(pc),end=" ")

def registers_dump():
    for num in registers:
        print(registers[num],end=" ")


def initialise_mem():
    i=0
    global memory
    for words in commands:
        memory[i]=words
        i+=1


def execute(instruction):

    global registers
    
    if instruction[0:5]=='00000':  #add

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[7:10],2)
        decimal_register2=int(instruction[10:13],2)
        decimal_register3=int(instruction[13:],2)

        sum = int(registers[decimal_register2],2) + int(registers[decimal_register3],2)
        

        if sum>65535:  # if sum > 2^16 -1   (overflow)
            registers[7]='0000000000001000' # set overflow
            registers[decimal_register1]=toBinary_16bit(sum)

            return False,pc+1
        else:
            registers[decimal_register1]=toBinary_16bit(sum)

            registers[7]='0000000000000000' # reset flags
            return False,pc+1

    elif instruction[0:5]=='00001':  #subtract

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[7:10],2)
        decimal_register2=int(instruction[10:13],2)
        decimal_register3=int(instruction[13:],2)

        sub = int(registers[decimal_register2],2) - int(registers[decimal_register3],2)

        if sub<0:  # if Reg3 > Reg2
            registers[7]='0000000000001000' # set overflow
            registers[decimal_register1]='0000000000000000' # set Reg1 to 0 

            return False,pc+1
        else:
            registers[decimal_register1]=toBinary_16bit(sub)

            registers[7]='0000000000000000' # reset flags
            return False,pc+1

    elif instruction[0:5]=='00010':    # for mov (imm type)

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register=int(instruction[5:8],2)
        registers[decimal_register]='00000000'+instruction[8:]

        registers[7]='0000000000000000' # reset flags
        return False,pc+1

    elif instruction[0:5]=='00011':    # for mov (reg type)
        
        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[10:13],2)
        decimal_register2=int(instruction[13:],2)

        registers[decimal_register1]=registers[decimal_register2]  # performs Reg1 = Reg2

        registers[7]='0000000000000000' # reset flags
        return False,pc+1
    
    elif instruction[0:5]=='00100':  # for ld

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register=int(instruction[5:8],2)
        decimal_memory=int(instruction[8:],2)

        cycle_x.append(cycle)
        address_y.append(decimal_memory)  # accessing memory

        registers[decimal_register]=memory[decimal_memory]

        registers[7]='0000000000000000' # reset flags
        return False,pc+1

    elif instruction[0:5]=='00101':  # for st

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register=int(instruction[5:8],2)
        decimal_memory=int(instruction[8:],2)

        cycle_x.append(cycle)
        address_y.append(decimal_memory) # accesing memory

        memory[decimal_memory]=registers[decimal_register]

        registers[7]='0000000000000000' # reset flags
        return False,pc+1

    elif instruction[0:5]=='00110':  # multiply

        cycle_x.append(cycle)
        address_y.append(pc)
        
        decimal_register1=int(instruction[7:10],2)
        decimal_register2=int(instruction[10:13],2)
        decimal_register3=int(instruction[13:],2)

        mul = int(registers[decimal_register2],2) * int(registers[decimal_register3],2)

        if mul>65535:  # if mul > 2^16 -1   (overflow)
            registers[7]='0000000000001000' # set overflow
            registers[decimal_register1]=toBinary_16bit(mul)

            return False,pc+1
        else:
            registers[decimal_register1]=toBinary_16bit(mul)

            registers[7]='0000000000000000' # reset flags
            return False,pc+1

    elif instruction[0:5]=='00111':   # for divide

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[10:13],2)
        decimal_register2=int(instruction[13:],2)

        quotient = int(registers[decimal_register1],2) // int(registers[decimal_register2],2)
        remainder = int(registers[decimal_register1],2) % int(registers[decimal_register2],2)

        registers[0] = toBinary_16bit(quotient) # stores quotient in R0
        registers[1] = toBinary_16bit(remainder) # stores remainder in R1

        registers[7]='0000000000000000' # reset flags
        return False,pc+1

    elif instruction[0:5]=='01000':  # for right shift  

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register = int(instruction[5:8],2)
        imm = int(instruction[8:],2)

        registers[decimal_register] = toBinary_16bit(int(registers[decimal_register],2) >> imm)

        registers[7]='0000000000000000' # reset flags
        return False,pc+1
    
    elif instruction[0:5]=='01001':  # for left shift

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register = int(instruction[5:8],2)
        imm = int(instruction[8:],2)

        registers[decimal_register] = toBinary_16bit(int(registers[decimal_register],2) << imm)

        registers[7]='0000000000000000' # reset flags
        return False,pc+1

    elif instruction[0:5]=='01010':  # xor

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[7:10],2)
        decimal_register2=int(instruction[10:13],2)
        decimal_register3=int(instruction[13:],2)

        bitxor = int(registers[decimal_register2],2) ^ int(registers[decimal_register3],2)     # bitwise xor
        registers[decimal_register1]=toBinary_16bit(bitxor)

        registers[7]='0000000000000000' # reset flags
        return False,pc+1

    elif instruction[0:5]=='01011':  # OR

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[7:10],2)
        decimal_register2=int(instruction[10:13],2)
        decimal_register3=int(instruction[13:],2)

        bitor = int(registers[decimal_register2],2) | int(registers[decimal_register3],2)     # bitwise OR
        registers[decimal_register1]=toBinary_16bit(bitor)

        registers[7]='0000000000000000' # reset flags
        return False,pc+1

    elif instruction[0:5]=='01100':  # and

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[7:10],2)
        decimal_register2=int(instruction[10:13],2)
        decimal_register3=int(instruction[13:],2)

        bitand = int(registers[decimal_register2],2) & int(registers[decimal_register3],2)     # bitwise and
        registers[decimal_register1]=toBinary_16bit(bitand)

        registers[7]='0000000000000000' # reset flags
        return False,pc+1

    elif instruction[0:5]=='01101':   # for invert (not)  # FIXED BUGG HERE !!!!

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[10:13],2)
        decimal_register2=int(instruction[13:],2)

        #bitnot=~int(registers[decimal_register2],2) #bitnot

        bitnot=''
        for i in registers[decimal_register2]:
            if i=='0':
                bitnot=bitnot+'1'
            elif i=='1':
                bitnot=bitnot+'0'        

        registers[decimal_register1] = bitnot
    

        registers[7]='0000000000000000' # reset flags
        return False,pc+1
    
    elif instruction[0:5]=='01110':   # for compare (cmp)

        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_register1=int(instruction[10:13],2)
        decimal_register2=int(instruction[13:],2)

        if int(registers[decimal_register1],2) < int(registers[decimal_register2],2):
            registers[7]='0000000000000100'
        elif int(registers[decimal_register1],2) > int(registers[decimal_register2],2):
            registers[7]='0000000000000010'
        elif int(registers[decimal_register1],2) == int(registers[decimal_register2],2):
            registers[7]='0000000000000001'    

        
        return False,pc+1

    elif instruction[0:5]=='01111':  # for jmp
        
        cycle_x.append(cycle)
        address_y.append(pc)

        decimal_memory=int(instruction[8:],2)
        

        registers[7]='0000000000000000' # reset flags
        return False,decimal_memory  # pc = jump location

    elif instruction[0:5]=='10000':  # for jlt

        cycle_x.append(cycle)
        address_y.append(pc)
        
        decimal_memory=int(instruction[8:],2)
        
        if registers[7] == '0000000000000100': #check if less than flag is set
            registers[7]='0000000000000000' # reset flags
            return False, decimal_memory  # pc = jump location
        else:
            registers[7]='0000000000000000' # reset flags
            return False, pc+1    

    elif instruction[0:5]=='10001':  # for jgt

        cycle_x.append(cycle)
        address_y.append(pc)
        
        decimal_memory=int(instruction[8:],2)
        
        if registers[7] == '0000000000000010': #check if greater than flag is set
            registers[7]='0000000000000000' # reset flags
            return False, decimal_memory  # pc = jump location
        else:
            registers[7]='0000000000000000' # reset flags
            return False, pc+1  

    elif instruction[0:5]=='10010':  # for je

        cycle_x.append(cycle)
        address_y.append(pc)
        
        decimal_memory=int(instruction[8:],2)
        
        if registers[7] == '0000000000000001': #check if greater than flag is set
            registers[7]='0000000000000000' # reset flags
            return False, decimal_memory  # pc = jump location
        else:
            registers[7]='0000000000000000' # reset flags
            return False, pc+1          
        
    elif instruction[0:5]=='10011':  # for hlt
        
        cycle_x.append(cycle)
        address_y.append(pc)

        registers[7]='0000000000000000' # reset flags
        return True,pc+1

    


def main():

    global pc
    global cycle
    readdata()
    initialise_mem()

    halted = False

    while not halted:
        instruction=memory[pc]

        halted,new_pc=execute(instruction)
        pc_dump()
        registers_dump()
        print()

        pc=new_pc
        cycle+=1  # increment cycle (for plotting)

    mem_dump()

    plt.scatter(cycle_x, address_y)
    plt.title("Memory Access Trace")
    plt.xlabel('Cycle')
    plt.ylabel('Memory Address')
    plt.show()
    #plt.savefig('plot.png')

    localtime = time.asctime( time.localtime(time.time()) )[11:19]
    plt.savefig('plot_images/{} plot.png'.format(localtime))  # folder path (modify later if needed)
    time.sleep(1)

        
    
if __name__ == "__main__":
    main()





