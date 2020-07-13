"""CPU functionality."""

import sys


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

    def load(self):
        """Load a program into memory."""
        # Index (address) of current instruction ==> the Program Counter
        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010,  # LDI R0,8-> 3 bytes
            0b00000000,
            0b00001000,
            0b01000111,  # PRN R0
            0b00000000,
            0b00000001,  # HLT
        ]

        for instruction in program:
            # Current instruction just got out of RAM
            self.ram[address] = instruction
            address += 1

    # Added Context for both read and write funcs:
    #Inside the CPU, there are two internal registers used for memory operations:
    #the _Memory Address Register_(MAR) and the _Memory Data Register_(MDR)
    # The MAR contains the address that is being read or written to
    # The MDR contains the data that was read or the data to write
    # both names would make handy parameter names for both funcs

    # TODO: Add RAM function: `ram_read()`
    # Read data from an address in memory
    # Returns the value of what is stored at that address
    #mar param: contains address from memory that is being read 
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
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

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

    
    #TODO: 
        #CPU's run method
        # It reads the memory address that's stored in register `PC`
        # and stores that result in `IR`, (instruction register)
        # IR is just a local variable in this method 
        # Not all instructions use one byte of data
        # Also sometimes the byte value is the registers number, other times it's a constant value (in the case of `LDI`)
        # Use our ram_read func
        # Carry out operations for each instruction

    def run(self):
        """Run the CPU."""
        # Instructions to run
        
        #This is similar to py's exit(), stop whatever we are doing, wherever we are
        HLT = 0b00000001
        # This instruction sets register 0 to value of 8
        LDI = 0b10000010  # LDI R0,8
        #Prints numeric value stored in the given register
        #Print to console the decimal integer value -> converted from binary to decimal 
        PRN = 0b01000111  # PRN R0

        # Local running variable so this function stops running instructions when this variable is set to false
        running = True

        # While running is true
        while running:
            # Set up the IR
            # The memory we need to access is stored in the self.pc
            # We can use our self.ram_read to read the address that we need to access in self.pc, we pass in as params the address of the data we need to read, which is in self.pc
            # Assign result of data we got from our self.pc to IR
            # IR holds copy of instruction we are on/fufilling
            instruc_register = self.ram_read(self.pc)

            # As well as acessing the desired address in self.pc, we have some instructions that use the next 2 bytes of data (the next two indexes along from the initial desired address in the self.pc) as we want to perform operations on this data 
            # The values at these extra addresses could be either a register number, or a constant value (latter for LDI instruction)
            # Use the 2 ram methods to read the values (bytes) at these extra addresses (we can access location of these addresses by simply using pc+1 and pc+2)

            instruc_a = self.ram_read(self.pc + 1)
            # print(instruc_a, 'a, this data/value is a register number')
            instruc_b = self.ram_read(self.pc + 2)
            # print(instruc_b,  'b, this is a value')

            # Doing stuff according to our instructions
                #HLT: causes while loop to break, halts the CPU, so to do this set running to False 
            if instruc_register == HLT:
                running = False
                sys.exit(1)
            
            # Store value of 8 (held at instruc_b) at register one (register one held at instruc_a as has value of 0)
            elif instruc_register == LDI:
                self.reg[instruc_a] = instruc_b
                # Increment by 3 as 3 byte instructions
                self.pc+=3
                
            # Prints the value (8) held at register one (instruc_a)
            elif instruc_register == PRN:
                print(self.reg[instruc_a])
                # Increment by 2 as 2 byte instructions
                self.pc+=2


            # Always have
            else:
                # Stop running the func
                running = False
                sys.exit(1)




