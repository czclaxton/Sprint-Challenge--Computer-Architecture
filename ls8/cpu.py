"""CPU functionality."""

import sys

LDI = 0b10000010
PRINT_COMMAND = 0b01000111
MULT = 0b10100010
HALT = 0b00000001
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMPP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256  # how many bits
        self.memory = [0] * 8  # 8-bit memory
        self.running = True
        self.pc = 0
        self.memory[7] = 0xF4
        self.stackpointer = self.memory[7]
        self.branchtable = {}  # set to empty dictionary
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRINT_COMMAND] = self.handle_PRINT_COMMAND
        self.branchtable[MULT] = self.handle_MULT
        self.branchtable[HALT] = self.handle_HALT
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[CMPP] = self.handle_CMPP
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        self.flag = 0b00000000

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = sys.argv[1]

        with open(program) as f:
            for line in f:
                line = line.split('#')[0]
                line = line.strip()
                if line is '':
                    continue
                value = int(line, 2)
                self.ram[address] = value
                address += 1

        for instruction in program:
            self.ram[address] = instruction
            address += 1

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
            print(" %02X" % self.memory[i], end='')

        print()

    def handle_HALT(self, pc):
        self.running = False
        self.pc += 1

    def handle_LDI(self, pc):
        operand_a = self.ram_read(pc + 1)
        operand_b = self.ram_read(pc + 2)
        self.memory[operand_a] = operand_b
        self.pc += 3

    def handle_PRINT_COMMAND(self, pc):
        operand_a = self.ram_read(pc + 1)
        operand_b = self.memory[operand_a]
        print(operand_b)
        self.pc += 2

    def handle_MULT(self, pc):
        operand_a = self.ram_read(pc + 1)
        num_a = self.memory[operand_a]

        operand_b = self.ram_read(pc + 2)
        num_b = self.memory[operand_b]

        result = num_a * num_b
        self.memory[operand_a] = result
        self.pc += 3

    def handle_ADD(self, pc):
        operand_a = self.ram_read(pc + 1)
        num_a = self.memory[operand_a]

        operand_b = self.ram_read(pc + 2)
        num_b = self.memory[operand_b]

        result = num_a + num_b
        self.memory[operand_a] = result
        self.pc += 3

    def handle_PUSH(self, pc):
        self.stackpointer -= 1
        copy = self.ram_read(pc + 1)
        self.ram[self.stackpointer] = self.memory[copy]
        self.pc += 2

    def handle_POP(self, pc):
        location = self.ram_read(pc + 1)
        self.memory[location] = self.ram[self.stackpointer]
        self.stackpointer += 1
        self.pc += 2

    def handle_CALL(self, pc):
        self.stackpointer -= 1
        self.ram[self.stackpointer] = self.pc + 2
        address = self.ram_read(pc + 1)
        self.pc = self.memory[address]

    def handle_CMPP(self, pc):
        self.flag = 0b00000000
        operand_a = self.ram_read(pc + 1)  # save reg A to a variable
        # access reg's value and save it to a variable
        num_a = self.memory[operand_a]

        operand_b = self.ram_read(pc + 2)  # save reg A to a variable
        # access reg's value and save it to a variable
        num_b = self.memory[operand_b]

        if num_a == num_b:
            self.flag = 0b00000001  # if the reg A is equal to reg B then flag = 1
        elif num_a < num_b:
            self.flag = 0b00000100  # if the reg A is less than reg B then flag = 4
        elif num_a > num_b:
            self.flag = 0b0000010  # if the reg A is greater than reg B then flag = 2
        self.pc += 3

    def handle_JMP(self, pc):
        # jump to the address at the given reg
        # set pc to that adress
        address = self.ram_read(pc + 1)
        self.pc = self.memory[address]

    def handle_JEQ(self, pc):
        # if the flag is true, jump to the address at that reg
        if self.flag == 0b00000001:
            address = self.ram_read(pc + 1)
            self.pc = self.memory[address]
        else:
            self.pc += 2

    def handle_JNE(self, pc):
        # if flag is false or 4 then jump to the address at the given reg
        if self.flag == 0b00000010 or self.flag == 0b00000100:
            address = self.ram_read(pc + 1)
            self.pc = self.memory[address]
        else:
            self.pc += 2

    def handle_RET(self, pc):
        self.pc = self.ram[self.stackpointer]
        self.stackpointer += 1

    def run(self):
        """Run the CPU."""
        while self.running is True:
            instruction = self.ram_read(self.pc)
            self.branchtable[instruction](self.pc)

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, value):
        self.ram[MDR] = value
