"""CPU functionality."""

import sys
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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        # Adding multiple operation
            # Store result of values of regA * regB in regA, so we access regsiter A's addresses in self.reg to store the result
            # we need to do self.reg[reg_a] and same with b to access the values in those registers in order to multiply
        elif op == "MUL":
            # self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
            self.reg[reg_a] *= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")
    
    
    # Clean-up if/else block, modular functions which carries out an action for each instruction 
    # HLT FUNC
    def HLT(self):
        # Action: sets running to False
            # running was local on run() func, so setting it as an attribute on CPU class
        self.running = False

    # LDI func
    #Stores value (constant integer value) of 8 (held at instruc_b) at register one (register one held at instruc_a as has console num is 0)
    def LDI(self):
        # As well as acessing the desired address in self.pc, we have some instructions that use the next 2 bytes of data (the next two indexes along from the initial desired address in the self.pc) as we want to perform operations on this data
        # The values at these extra addresses could be either a register number, or a constant value 
        # Use the 2 ram methods to read the values (bytes) at these extra addresses (we can access location of these addresses by simply using pc+1 and pc+2)
        # instruc_a is our reg number (reg0)
        instruc_a = self.ram_read(self.pc + 1)
        # print(instruc_a, 'a, this data/value is a register number')
        # instruc_b is our value we want to want to store at reg0 (instruc_a), this value is a constant number
        instruc_b = self.ram_read(self.pc + 2)
        self.reg[instruc_a] = instruc_b
        self.pc += 3

    # PRN func
    # Prints the value (8) held at register 0 (instruc_a)
    def PRN(self):
        # instruc_a is our reg number (reg0)
        instruc_a = self.ram_read(self.pc + 1)
        print(self.reg[instruc_a])
        # Increment by 2 as 2 byte instructions
        self.pc += 2
    
    # MUL func
    # Calls the alu() func (carries out maths)
    def MUL(self):
        instruc_a = self.ram_read(self.pc + 1)
        instruc_b = self.ram_read(self.pc + 2)
        # Pass in type of operation (MUL), registerA(instrucA), registerB(instrucB)
        self.alu("MUL", instruc_a, instruc_b)
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
            # print(instruc_register, 'the value of currently executing instruction')

            # Depending on which program (filename) we run in the command line, the instruc_register variable refers to the key of the instruction (key of the instructor gives us its instruction number)
                #e.g if we run the program python3 ls8.py examples/mult.ls8 --> runs the 'mult.ls8' file this gets put into the load() func: which has the LDI, MUL, PRN and HLT instructions, each of these key's (and these keys point to the instruction number) are pointed to by instruc_register when we run this file (when run() func gets called - this happens after we call load())
                # The result of accessing each of these instruction keys/numbers one at a time from our branch_table dict, is that each instruction calls/returns its function(altogether 4 functions) and resulting in our answer--> 72
                #e.g when print8.ls file gets typed into comand line, the load func opens this file reads the instructions, saves each instruction number in memory, then when the run() func gets called, each instruction in this file: which has LDI, PRN and HLT, gets assigned as the value of instruc_register (to become the key to our branch_table) which calls one-by-one each of the LDI, PRN and HLT funcions, resulting in our answer --> 8
            self.branchtable[instruc_register]()
            # print(self.branchtable[instruc_register])


            # Check if the instruc_register is not in our branch_table dict
            if instruc_register not in self.branchtable:
                print('Invalid Instruction')
                sys.exit(0)

