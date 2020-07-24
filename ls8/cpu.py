"""CPU functionality."""

import sys
import datetime
# Instructions to run
# HLT:
# similar to py's exit(), stop whatever we are doing, wherever we are
HLT = 0b00000001
# LDI
# Sets register 0 to value of 8
LDI = 0b10000010  # LDI R0,8
# PRN
# Takes in a register number as its argument and prints a numeric value stored in that register
# It prints to console that numeric value as decimal integer value
PRN = 0b01000111  # PRN R0

# MUL
# Instruction is handled by ALU
# Takes in 2 arguments: regA and regB: multiplies the values stored in both registers and stores the result in regA
MUL = 0b10100010

# PUSH
# Takes in 1 argument: given register for copying value from this register to add to the stack
PUSH = 0b01000101

# POP
# Pops the value at top of the stack into given register
# Takes in 1 argument: the given stack the value gets put into
POP = 0b01000110

# CALL
# Calls a subroutine (function) at the address stored in the register
# Takes in one argument: the register that stores the address of the subroutine
CALL = 0b01010000

# RET
# Pops the value from the top of the stack and stores it in the `PC` so the PC goes to where we last left off
# Takes no arguments
RET = 0b00010001

# ADD: part of call.ls8 program
# Instruction is handled by the ALU
# Adds the value in two registers and store the result in regA
ADD = 0b10100000

# ST: part of timer interupt
# Storing the value in regB in the address stored in regA
# 2 arguments
ST = 0b10000100

# JEQ
# Jumps to an address in given register if the equal flag is set (1)
# Takes one argument: the register number
JEQ = 0b01010101

# CMP: Instruction is handled by the ALU
# Compares values in two registers (arguments) and sets flag status accordingly based on the comparison of the values in the registers
# Has two arguments
CMP = 0b10100111

# JMP: Jumps to a address which is stored in given register AND sets PC to that address in the register (how it jumps there)
# Takes one argument (register number)
JMP = 0b01010100

# JNE
# Jumps to an address in given register if the equal flag is clear (0: not true)
# Takes one argument: the register number
JNE = 0b01010110

# AND
    # Takes in 2 arguments 
    # Handled by ALU
AND = 0b10101000

# OR
    # Takes in 2 arguments
    # Handled by ALU
OR = 0b10101010

# XOR
    # Takes in 2 arguments
    # Handled by ALU
XOR = 0b10101011


#NOT
    # Does a bitwise-NOT on the value in a register, storing the result in the register
    # Takes in one argument
    # Handled by ALU
NOT = 0b01101001

# SHL
    # Shifts the value in regA left by the number of bits specified in regB, filling the low bits with 0
    # Takes in 2 arguments
    # Handled by ALU
SHL = 0b10101100

# SHR
    # Shift the value in regA right by the number of bits specified in regB, filling the high bits with 0
    # Takes in 2 arguments
    # Handled by ALU
SHR = 0b10101101

# MOD 
    # Divides the value in regA by the value in regB, stores the remainder (the modulo) of the result in regA
    # Handled by ALU
    # Takes in 2 arguments
MOD = 0b10100100




class CPU:
    """Main CPU class."""

    # TODO: Add list properties to the CPU class to hold 256 bytes of memory and 8 general-purpose registers
    def __init__(self):
        """Construct a new CPU."""
        # Attribute: RAM -> memory storage
        # RAM holds 256 bytes of memory
        self.ram = [0] * 256
        # Attribute: REG: registers in CPU
        # need lists of 8 registers
        self.reg = [0] * 8
        # Attribute: PC: program counter-> is a special purpose register
        # the PC is the index/address into the RAM array of the current instruction, initialise it to 0
        self.pc = 0
        # Adding running (decides whether our CPU runs or not) as attribute so its availble for our modular func instruction methods
        self.running = True
        # Adding our Stack pointer so both PUSH and POP functions can use this attribute
        # remember: the SP points to the address in memory and this address holds our most recently element of the stack
        # Setting the number 7 which is the register_number that holds the address of our SP
        self.stack_pointer = 7
        # Register 7 holds the address of our SP if the stack is empty: we assign R7 to the SP's address which is F4
        self.reg[self.stack_pointer] = 0xf4

        # Setting up my branchtable to beautify my run() if/else chains
        # Each key in this branchtable for all the instructions is the instruction number (decimal of the binary string)
        self.branchtable = {}
        # Passing in HLT as key to branch_table dict with value as the function for HLT
        self.branchtable[HLT] = self.HLT
        # Passing in LDI as key to branch_table dict with value as the function for LDI
        self.branchtable[LDI] = self.LDI
        # Passing in PRN as key to branch_table dict with value as the function for PRN
        self.branchtable[PRN] = self.PRN
        # Passing in MUL as key to branch_table dict with value as the function for MUL
        self.branchtable[MUL] = self.MUL
        # print(self.branchtable, 'BT')
        # Passing in PUSH as key to branch_table dict with value as the function for PUSH
        self.branchtable[PUSH] = self.PUSH
        # Passing in POP as key to branch_table dict with value as the function for POP
        self.branchtable[POP] = self.POP
        # Passing in CALL as key to branch_table dict with value as the function for CALL
        self.branchtable[CALL] = self.CALL
        # Passing in RET as key to branch_table dict with value as the function for RET
        self.branchtable[RET] = self.RET
        # Passing in ADD as key to branch_table dict with value as the function for ADD
        self.branchtable[ADD] = self.ADD

        # Timer interupt: ST instruction
        self.branchtable[ST] = self.ST
        # Timer interupt: IS held in reg number 6, status of interrupt
        self.IS = 6
        # Timer interupt: IM held in reg number 5
        self.IM = 5
        # No interrupt so no data, starts with 0 - nothing to interrupt
        self.reg[self.IM] = 0
        self.reg[self.IS] = 0
        # FL bits (flag bits) as attribute so this can be changed depending on the values stored in regA and regB
        # Flags is a special purpose register
        self.flag_bits = 0b00000000
        # Passing in JEQ as key to branch_table dict with value as the function for JEQ
        self.branchtable[JEQ] = self.JEQ
        # Passing in CMP as key to branch_table dict with value as the function for CMP
        self.branchtable[CMP] = self.CMP
        # Passing in JMP as key to branch_table dict with value as the function for JMP
        self.branchtable[JMP] = self.JMP
        # Passing in JNE as key to branch_table dict with value as the function for JNE
        self.branchtable[JNE] = self.JNE
        # Passing in AND as key to branch_table dict with value as the function for AND
        self.branchtable[AND] = self.AND
        # Passing in OR as key to branch_table dict with value as the function for OR
        self.branchtable[OR] = self.OR
        # Passing in XOR as key to branch_table dict with value as the function for XOR
        self.branchtable[XOR] = self.XOR
        # Passing in NOT as key to branch_table dict with value as the function for NOT
        self.branchtable[NOT] = self.NOT
        # Passing in SHL as key to branch_table dict with value as the function for SHL
        self.branchtable[SHL] = self.SHL
        # Passing in SHR as key to branch_table dict with value as the function for SHR
        self.branchtable[SHR] = self.SHR
        # Passing in MOD as key to branch_table dict with value as the function for MOD
        self.branchtable[MOD] = self.MOD




    def load(self, filename):
        """Load a program into memory."""

        # # For now, we've just hardcoded a program:
        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8-> 3 bytes
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     # Current instruction set within specific index/address in RAM
        #     self.ram[address] = instruction
        #     address += 1

        if len(sys.argv) != 3:
            # Filename comes in from sys.argv[1] when this func is called
            with open(filename) as f:
                # Index (address) of current instruction ==> the Program Counter
                address = 0
                for line in f:
                    # print(line)
                    # Split string at hash so the comment isnt included
                    line = line.split("#")
                    try:
                        # Passing in our base-2 as its binary number base in our programs, we need to convert this binary string to an integer
                        # Selecting first part of split string which is our binary string
                        value = int(line[0], 2)
                    # Deals with blank lines, comment lines etc.. we carry on with loop over these lines
                    except ValueError:
                        continue

                    # Store each value we read in address in RAM,
                    self.ram[address] = value
                    address += 1
        # If filename is not put: print error and exit
        else:
            print('No filename written, ERROR')
            sys.exit(0)
            # Run python3 ls8.py examples/print8.ls8 to test it prints 8

    # Added Context for both read and write funcs:
    # Inside the CPU, there are two internal registers used for memory operations:
    # the _Memory Address Register_(MAR) and the _Memory Data Register_(MDR)
    # The MAR contains the address that is being read or written to
    # The MDR contains the data that was read or the data to write
    # both names would make handy parameter names for both funcs

    # TODO: Add RAM function: `ram_read()`
    # Read data from an address in memory
    # Returns the value of what is stored at that address
    # mar param: contains address from memory that is being read

    def ram_read(self, mar):
        # Value accesses the value at the address (mar) in memory we want to read
        value = self.ram[mar]
        return value

    # TODO: Add RAM function: `ram_write()`
    # Takes in a value to write (mdr), and the address to write it to in RAM memory(mar)

    def ram_write(self, mdr, mar):
        # The value we want to store in the address in RAM
        write_value = mdr
        # Assigning the value to the address passed into this func in RAM
        self.ram[mar] = write_value

    #reg_b optional arg to cater for NOT instruction
    def alu(self, op, reg_a, reg_b=None):
        """ALU operations."""
        # ADD operation
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        # Adding multiple operation
            # Store result of values of regA * regB in regA, so we access regsiter A's addresses in self.reg to store the result
            # we need to do self.reg[reg_a] and same with b to access the values in those registers in order to multiply
        elif op == "MUL":
            # self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            # If the value at regA is less than regB, add 1's to the 'L' bits on the FL bits (third to last)
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag_bits = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                # If the value at regA is greater than regB, add 1's to the 'G' bits on the FL bits (second to last)
                self.flag_bits = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                # If the value at regA is equal to regB, add 1's to the 'E' bits on the FL bits (end)
                self.flag_bits = 0b00000001
        
        elif op == "AND":
        # Uses bitwise '&' operator: compares regA and regB values and stores result in regA
        # Compares each column of value of both: any time the value for both is '1' it returns 1 as result for that column
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        
        elif op == "OR":
        # Uses bitwise '|' operator: compares regA and regB values and stores result in regA
        # Compares each column of value of both: any time the value for either or both is '1' it returns 1 as result for that column
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]

        
        elif op == "XOR":
        # Uses bitwise '^' operator: compares regA and regB values and stores result in regA
        # Compares each column of value of both: any time the value for either is '1' it returns 1 as result for that column
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        
        elif op == "NOT":
        # Does a bitwise-NOT on the value in the given register, storing the result in the same register
        # Uses bitwise '~' operator
            self.reg[reg_a] = ~self.reg[reg_a]
        
        elif op == "SHL":
        # Shifts the value in regA left by the number of bits specified in regB (filling the low bits with 0)
        # Uses bitwise '<<' operator
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        
        elif op == "SHR":
        # Shifts the value in regA right by the number of bits specified in regB (filling the low bits with 0)
        # Uses bitwise '>>' operator
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]

        
        elif op == "MOD":
        # Divides the value in regA by the value in regB, stores the remainder (the modulo) of the result in regA
        # Uses modulo operator: %
        # If the value in the second register is 0, the system should print an error message and halt (self.HLT)
            if self.reg[reg_b] == 0:
                print('Error')
            # Get the CPU to halt by calling our HLT function which sets running to false
                self.HLT()
        # Else, if the value in reg_b is not 0
            self.reg[reg_a] %= self.reg[reg_b]


        else:
            raise Exception("Unsupported ALU operation")

    # Clean-up if/else block, modular functions which carries out an action for each instruction
    # HLT FUNC

    def HLT(self):
        # Action: sets running to False
        # running was local on run() func, so setting it as an attribute on CPU class
        self.running = False

    # LDI func
    # Stores value (constant integer value) of 8 (held at instruc_b) at register one (register one held at instruc_a as has console num is 0)
    def LDI(self):
        # When carrying out this instruction, self.pc will point to this instruction number
        # This instruction has two arguments (3 bytes long inluding the instruction number)
        # So to access its other two arguments, they can be found at pc+1 for the first arg and pc+2 for the second argument as both values held at these addresses are needed for this isntruction
        # One value gives us the register number (instrucA)
        # The other value we need is a constant value (instrucB)

        # instruc_a is our reg number (reg0)
        instruc_a = self.ram_read(self.pc + 1)
        # print(instruc_a, 'a, this data/value is a register number')
        # instruc_b is our value we want to want to store at the register number (instruc_a)
        instruc_b = self.ram_read(self.pc + 2)
        self.reg[instruc_a] = instruc_b
        self.pc += 3

    # PRN func
    # Prints the value (8) held at register 0 (instruc_a)
    def PRN(self):
        # When carrying out this instruction, self.pc will point to this instruction number
        # This instruction has one argument, which is the register number(reg0), which can be accessed by pc+1, which gives us the value stored at that reg0's address
        instruc_a = self.ram_read(self.pc + 1)
        print(self.reg[instruc_a])
        # Increment by 2 as 2 byte instructions
        self.pc += 2

    # MUL func
    # Calls the alu() func (carries out maths)
    def MUL(self):
        # When carrying out this instruction self.pc will point to this instruction number
        # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (MUL), registerA(instrucA), registerB(instrucB)
        self.alu("MUL", instruc_a, instruc_b)
        # It's 2 arguments plus instruction so have to increment pc by 3
        self.pc += 3

    # PUSH func
        # Pushes a value in the given register on the stack

    def PUSH(self):
        # 1. Decrement SP
        # Register 7 which points to our SP (the address), the SP's address gets decremented
        self.reg[self.stack_pointer] -= 1
        # We need to find the register that we need to copy value from
        # We do this by finding the register number from our RAM
        # as self.pc points to our instruction (PUSH) so self.pc + 1 gets the one/only argument the instruction has, which is the register number
        reg_num = self.ram[self.pc + 1]
        # Now we have the number as the index to put into our self.reg, which gets us the value that this particular register stores (as we want to add this value to the stack)
        value = self.reg[reg_num]

        # The address of the top of the stack is register7 (where we want to insert our value into), the address is

        # The address at the top of the stack is what register7 points too (F3), so our top_stack_adress = F3, as this is the address that the SP points too and this address stores the value of the element at top of stack
        # It's now F3 as we decremented the SP from F4 -> F3
        top_of_stack_address = self.reg[self.stack_pointer]
        # print(top_of_stack_address)
        # Assign the address F4 in RAM to the value we want to add which is the value we got from our specified register
        self.ram[top_of_stack_address] = value
        # 2 byte instruction:
        self.pc += 2

    # POP func
        # Pops the value at the top of the stack into the given register
    def POP(self):
        # The address at the top of the stack is what register7 points too (F3), so our top_stack_adress = F3, as this is the address that the SP points too and this address stores the value of the element at top of stack
        top_of_stack_address = self.reg[self.stack_pointer]
        # Get the value that is stored at this address in RAM (value being the last element added to the stack)
        value_at_sp = self.ram[top_of_stack_address]
        # print(value_at_sp)
        # Get the address of the given register to put our value in
        # self.pc + 1 points to the register number we need to put this value we pop off the stack into
        reg_num = self.ram[self.pc + 1]
        # Assining this value to the given register
        self.reg[reg_num] = value_at_sp

        # Increment SP: the address in memory that the SP points to gets incremented
        # Our register number that holds the address that the SP points too, now this register holds the new incremented address that the SP points to
        self.reg[self.stack_pointer] += 1

        # 2 byte instruction
        self.pc += 2

    # CALL func
        # Calls a subroutine (function) at the address stored in the register

    def CALL(self):
        # 1. Get the address of the next instruction (after CALL), to push onto the stack so when we can return to this instruction's address when the subroutine func finishes
        # The address is pc + 2 as CALL is a 2 byte instruction
        next_instruc_address = self.pc + 2
        # Decrement the SP as pushing to stack
        self.reg[self.stack_pointer] -= 1
        # Get address for top of stack (where SP is)
        top_of_stack_address = self.reg[self.stack_pointer]
        # Get this address in memory and store this next_instr_address at the top of the stack
        self.ram[top_of_stack_address] = next_instruc_address

    # 2. Need to set the PC to the address of our subroutine address so the PC can jump to this address when we hit the CALL instruction
        # This subroutine address is held in a given register
        # We can find this register from our instruction's argument which tells us the register number by pc + 1
        reg_num = self.ram[self.pc + 1]
        # We get the value (address of subroutine) out of this register
        address_subroutine = self.reg[reg_num]
        # Set the PC to this address
        self.pc = address_subroutine

    # RET func
        # Pops the value from the top of the stack and stores it in the `PC` so the PC goes to where we last left off

    def RET(self):
        # Get address of top of stack
        top_of_stack_address = self.reg[self.stack_pointer]
        # Get value held at top of stack
        value_at_sp = self.ram[top_of_stack_address]
        # Increment SP: the address in memory that the SP points to gets incremented
        self.reg[self.stack_pointer] += 1
        # Assign pc to this value
        self.pc = value_at_sp

     # ADD func
    # Calls the alu() func (carries out maths)

    def ADD(self):
        # When carrying out this instruction self.pc will point to this instruction number
        # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (ADD), registerA(instrucA), registerB(instrucB)
        self.alu("ADD", instruc_a, instruc_b)
        # It's 2 arguments plus instruction so have to increment pc by 3
        self.pc += 3

    # ST func
        # Store the value held in regB in the address stored in regA
    def ST(self):
        # When carrying out this instruction self.pc will point to this instruction number
        # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)

        # Get the value out of regB
        reg_b_value = self.reg[instruc_b]

        # Get the value (address) out of regA
        # reg_a_value is an address in RAM
        reg_a_value = self.reg[instruc_a]

        self.ram[reg_a_value] = reg_b_value


# JEQ func
    # Jumps to an address in given register if the equal flag is set (true/1)
    def JEQ(self):
        # Get the reg number self.pc + 1 points too
        reg_num = self.ram_read(self.pc + 1)
        # Get this register's value as it holds the address that we need to jump too if equal flag has a '1'
        address_value = self.reg[reg_num]
        # Check if the equal flag has been set to 1 (last bit in our flag_bits)
        if self.flag_bits == 0b00000001:
            self.pc = address_value
        else:
            # Go to next instruction (this one is 2 bytes long)
            self.pc += 2

    # CMP func
        # Calls the alu() func (carries out maths)
    def CMP(self):
        # When carrying out this instruction self.pc will point to this instruction number
        # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        self.alu("CMP", instruc_a, instruc_b)
        # 3 byte instruction
        self.pc += 3

    # JMP func
        # Jump to the address stored in the given register and sets PC to that address
    def JMP(self):
        # self.pc points to this instruction number
        # self.pc + 1 (this instructions first and only argument) will give us the register number, which contains the address we want to the CPU to jump too
        # First get the reg number
        reg_num = self.ram_read(self.pc + 1)
        # Then access this register's value it holds (address)
        address_value = self.reg[reg_num]
        # Set the PC to it
        self.pc = address_value

    # JNE func
    # Jumps to an address in given register if the equal flag is clear (false/0)
    def JNE(self):
        # Get the reg number self.pc + 1 points too
        reg_num = self.ram_read(self.pc + 1)
        # Get this register's value as it holds the address that we need to jump too if equal flag has a '0'
        address_value = self.reg[reg_num]
        # Check if the equal flag is not equal to 1, not set (last bit in flag_bits)
        if self.flag_bits != 0b00000001:
            self.pc = address_value
        else:
            # Go to next instruction (this one is 2 bytes long)
            self.pc += 2

    # AND func  
    # Calls the alu() func (carries out maths)
    def AND(self):
    # When carrying out this instruction self.pc will point to this instruction number
            # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers 
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (AND), registerA(instrucA), registerB(instrucB)
        self.alu("AND", instruc_a, instruc_b)
        # It's 2 arguments plus instruction so have to increment pc by 3
        self.pc += 3


    # OR func  
    # Calls the alu() func (carries out maths)
    def OR(self):
    # When carrying out this instruction self.pc will point to this instruction number
            # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers 
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (OR), registerA(instrucA), registerB(instrucB)
        self.alu("OR", instruc_a, instruc_b)
        # It's 2 arguments plus instruction so have to increment pc by 3
        self.pc += 3

    # XOR func  
    # Calls the alu() func (carries out maths)
    def XOR(self):
    # When carrying out this instruction self.pc will point to this instruction number
            # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers 
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (XOR), registerA(instrucA), registerB(instrucB)
        self.alu("XOR", instruc_a, instruc_b)
        # It's 2 arguments plus instruction so have to increment pc by 3
        self.pc += 3

    
    # NOT func  
    # Calls the alu() func (carries out maths)
    def NOT(self):
    # When carrying out this instruction self.pc will point to this instruction number
            # the 1 arg that follow this instruc. numb in the spec are regA which is  accessed by doing pc+1 so instruc_a  gives us the value held at both the register number 
        instruc_a = self.ram_read(self.pc + 1)
        # Pass in type of operation (NOT), registerA(instrucA)
        self.alu("NOT", instruc_a)
        # It's 1 arguments plus instruction so have to increment pc by 2
        self.pc += 2

    
    # SHL func  
    # Calls the alu() func (carries out maths)
    def SHL(self):
    # When carrying out this instruction self.pc will point to this instruction number
            # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers 
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (shl), registerA(instrucA), registerB(instrucB)
        self.alu("SHL", instruc_a, instruc_b)
        # It's 2 arguments plus instruction so have to increment pc by 3
        self.pc += 3
    
    # SHR func  
    # Calls the alu() func (carries out maths)
    def SHR(self):
    # When carrying out this instruction self.pc will point to this instruction number
            # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers 
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (SHR), registerA(instrucA), registerB(instrucB)
        self.alu("SHR", instruc_a, instruc_b)
        # It's 2 arguments plus instruction so have to increment pc by 3
        self.pc += 3

    
    # MOD func  
    # Calls the alu() func (carries out maths)
    def MOD(self):
    # When carrying out this instruction self.pc will point to this instruction number
            # the 2 args that follow this instruc. numb in the spec are regA and regB, which can be accessed by doing pc+1 and pc+2, so both instruc variables gives us the value held at both of these registers 
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (MOD), registerA(instrucA), registerB(instrucB)
        self.alu("MOD", instruc_a, instruc_b)
        # It's 2 arguments plus instruction so have to increment pc by 3
        self.pc += 3

    
    




    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # TODO:
        # CPU's run method
        # It reads the memory address that's stored in register `PC`
        # and stores that result in `IR`, (instruction register)
        # IR is just a local variable in this method
        # Not all instructions use one byte of data
        # Also sometimes the byte value is the registers number, other times it's a constant value (in the case of `LDI`)
        # Use our ram_read func
        # Carry out operations for each instruction

    # def run(self):
    #     """Run the CPU."""
    #     # Instructions to run
    #     # HLT:
    #     # similar to py's exit(), stop whatever we are doing, wherever we are
    #     HLT = 0b00000001
    #     # LDI
    #     # Sets register 0 to value of 8
    #     LDI = 0b10000010  # LDI R0,8
    #     # PRN
    #     # Takes in a register number as its argument and prints a numeric value stored in that register
    #     # It prints to console that numeric value as decimal integer value
    #     PRN = 0b01000111  # PRN R0

    #     # MUL
    #     # Instruction is handled by ALU
    #     # Takes in 2 arguments: regA and regB: multiplies the values stored in both registers and stores the result in regA
    #     MUL = 0b10100010

    #     # Local running variable so this function stops running instructions when this variable is set to false
    #     running = True

    #     # While running is true
    #     while running:
    #         # Set up the IR
    #         # The memory we need to access is stored in the self.pc
    #         # We can use our self.ram_read to read the address that we need to access in self.pc, we pass in as params the address of the data we need to read, which is in self.pc (self.pc tells us the address of the current instruction running)
    #         # Assign result of data we got from our self.pc to IR
    #         # IR holds copy of instruction we are on/fufilling
    #         instruc_register = self.ram_read(self.pc)

    #         # As well as acessing the desired address in self.pc, we have some instructions that use the next 2 bytes of data (the next two indexes along from the initial desired address in the self.pc) as we want to perform operations on this data
    #         # The values at these extra addresses could be either a register number, or a constant value (latter for LDI instruction)
    #         # Use the 2 ram methods to read the values (bytes) at these extra addresses (we can access location of these addresses by simply using pc+1 and pc+2)

    #         instruc_a = self.ram_read(self.pc + 1)
    #         # print(instruc_a, 'a, this data/value is a register number')
    #         instruc_b = self.ram_read(self.pc + 2)
    #         # print(instruc_b,  'b, this is a value')

    #         # Doing stuff according to our instructions
    #         # HLT: causes while loop to break, halts the CPU, so to do this set running to False
    #         if instruc_register == HLT:
    #             running = False
    #             sys.exit(1)

    #         # Stores value (constant integer value) of 8 (held at instruc_b) at register one (register one held at instruc_a as has console num is 0)
    #         elif instruc_register == LDI:
    #             self.reg[instruc_a] = instruc_b
    #             # Increment by 3 as 3 byte instructions
    #             self.pc += 3

    #         # Prints the value (8) held at register 0 (instruc_a)
    #         elif instruc_register == PRN:
    #             print(self.reg[instruc_a])
    #             # Increment by 2 as 2 byte instructions
    #             self.pc += 2

    #         # Call the alu() so instruction gets carried out by ALU func
    #         elif instruc_register == MUL:
    #             # Pass in type of operation (MUL), registerA(instrucA), registerB(instrucB)
    #             self.alu("MUL", instruc_a, instruc_b)
    #             # It's 2 arguments plus instruction so have to increment pc by 3
    #             self.pc += 3

    #         # Always have
    #         else:
    #             # Stop running the func
    #             running = False
    #             sys.exit(1)

    # Cleaner runfunc!!

    def run(self):
        # Using attribute on CPU class to start running CPU which is set to True, unless we encounter the HLT func which switches running to False
        while self.running:
            # We can use our self.ram_read to read the address that we need to access in self.pc, we pass in as params the address of the data we need to read, which is in self.pc (self.pc tells us the address of the current instruction running)
            # Using ram_read assign the result of data we got from our self.pc to IR (the IR holds copy of instruction we are on/fufilling)

            # When we run the run() func, the value that gets assigned to instruc_register changes depending on what file we are running, AND this variable refers to the current instruction value (will be a number) that is being run in this particular file
            # e.g if we run print8.ls8, the IR would refer to the first instruction in the file: the LDI instruction (3 instructions long)
            instruc_register = self.ram_read(self.pc)

            # Depending on which program (filename) we run in the command line, the instruc_register variable refers to the key of the instruction (key of the instructor gives us its instruction number)
            # e.g if we run the program python3 ls8.py examples/mult.ls8 --> runs the 'mult.ls8' file this gets put into the load() func: which has the LDI, MUL, PRN and HLT instructions, each of these key's (and these keys point to the instruction number) are pointed to by instruc_register when we run this file (when run() func gets called - this happens after we call load())
            # The result of accessing each of these instruction keys/numbers one at a time from our branch_table dict, is that each instruction calls/returns its function(altogether 4 functions) and resulting in our answer--> 72
            # e.g when print8.ls file gets typed into comand line, the load func opens this file reads the instructions, saves each instruction number in memory, then when the run() func gets called, each instruction in this file: which has LDI, PRN and HLT, gets assigned as the value of instruc_register (to become the key to our branch_table) which calls one-by-one each of the LDI, PRN and HLT funcions, resulting in our answer --> 8

            self.branchtable[instruc_register]()

            # Check if the instruc_register is not in our branch_table dict
            if instruc_register not in self.branchtable:
                print('Invalid Instruction')
                sys.exit(0)


# # # ======================================================
# # INTERRUPT: in run func
#     while datetime.datetime.now() == 1000:
#     # Fire an interrupt
#     # 1. set bit 0 of the self.reg[6] to 1
#         self.reg[self.IS] = 10000000
# # 2. Check to see if bit 0 of the IS register is set
#         if self.reg[self.IS] = 10000000:
# # 3. IF yes:
#     # The IM register  is bitwise AND-ed with the IS register and the results stored as `maskedInterrupts`. This masks out all the interrupts we're not interested in, leaving the ones we are interested in:
#      # Each bit of maskedInterrupts is checked, starting from 0 and going up to the 7th bit, one for each interrupt 
#             masked_interrupts = self.reg[self.IM] & self.reg[self.IS]

#         # To see which interrupts are set
#         for i in range(8):
#     # Right shift interrupts down by i, then mask with 1 to see if that bit was set
#         interrupt_happened = ((masked_interrupts >> i) & 1) == 1

#     #  4. Push the registers on the stack, look up the IH address in the interupt vector table at address '0xF8' and set the PC to it
#     # Value to grt address --> self.ram[0xF8]



# # 4. When hit IRET instruction: signals a return from IH, the registers and PC are popped off the stack and execution continues
