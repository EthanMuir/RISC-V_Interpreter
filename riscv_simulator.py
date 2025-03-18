class RISCVSimulator:
    def __init__(self):
        # Initialize registers (x0 to x31)
        self.registers = [0] * 32
        self.registers[0] = 0  # x0 is hardwired to 0
        
        # Memory (simple implementation using dictionary)
        self.memory = {}
        
        # Program counter
        self.pc = 0
        
        # Metrics
        self.instruction_count = 0
        self.cycle_count = 0
        self.memory_accesses = 0
        
        # Labels dictionary for jumps/branches
        self.labels = {}
        self.labels_upper = {}  # Case-insensitive lookup

    def load_program(self, program_text):
        """
        Load a program from text format into simulator memory.
        Program format should be a list of strings with RISC-V instructions.
        """
        # Parse program to identify labels first
        cleaned_program = []
        line_number = 0
        
        for line in program_text:
            # Remove comments and leading/trailing whitespace
            line = line.split('#')[0].strip()
            if not line:
                continue
                
            # Check if line contains a label
            if ':' in line:
                label, instruction = line.split(':', 1)
                label = label.strip()
                self.labels[label] = line_number
                self.labels_upper[label.upper()] = line_number  # Store uppercase version too
                instruction = instruction.strip()
                if instruction:  # If there's an instruction after the label
                    cleaned_program.append(instruction.strip('"'))
                    line_number += 1
            else:
                cleaned_program.append(line.strip('"'))
                line_number += 1
                
        self.program = cleaned_program
        return cleaned_program
    
    def lookup_label(self, label):
        """Look up a label with case insensitivity."""
        if label in self.labels:
            return self.labels[label]
        elif label.upper() in self.labels_upper:
            return self.labels_upper[label.upper()]
        else:
            raise KeyError(f"Label not found: {label}")
    
    def execute_program(self):
        """Execute the loaded program from start to finish."""
        self.pc = 0
        while 0 <= self.pc < len(self.program):
            self.execute_instruction(self.program[self.pc])
    
    def execute_instruction(self, instruction):
        """Parse and execute a single instruction."""
        instruction = instruction.strip().upper()
        parts = instruction.replace(',', ' ').split()
        
        if not parts:
            self.pc += 1
            return
            
        opcode = parts[0]
        self.instruction_count += 1
        self.cycle_count += 1  # Assuming single-cycle implementation
        
        # Execute based on opcode
        if opcode == "ADD":
            rd = int(parts[1])
            rs1 = int(parts[2])
            rs2 = int(parts[3])
            self.registers[rd] = self.registers[rs1] + self.registers[rs2]
            self.pc += 1
            
        elif opcode == "SUB":
            rd = int(parts[1])
            rs1 = int(parts[2])
            rs2 = int(parts[3])
            self.registers[rd] = self.registers[rs1] - self.registers[rs2]
            self.pc += 1
            
        elif opcode == "LI":
            rd = int(parts[1])
            imm = int(parts[2])
            self.registers[rd] = imm
            self.pc += 1
            
        elif opcode == "LW":
            rd = int(parts[1])
            offset_base = parts[2].split('(')
            offset = int(offset_base[0]) if offset_base[0] else 0
            base = int(offset_base[1].rstrip(')'))
            address = self.registers[base] + offset
            self.registers[rd] = self.memory.get(address, 0)
            self.memory_accesses += 1
            self.pc += 1
            
        elif opcode == "SW":
            rs2 = int(parts[1])
            offset_base = parts[2].split('(')
            offset = int(offset_base[0]) if offset_base[0] else 0
            base = int(offset_base[1].rstrip(')'))
            address = self.registers[base] + offset
            self.memory[address] = self.registers[rs2]
            self.memory_accesses += 1
            self.pc += 1
            
        elif opcode == "BEQ":
            rs1 = int(parts[1])
            rs2 = int(parts[2])
            label = parts[3]
            if self.registers[rs1] == self.registers[rs2]:
                self.pc = self.lookup_label(label)
            else:
                self.pc += 1
                
        elif opcode == "JAL":
            # Handle different JAL formats:
            # JAL label (implicit rd=1)
            # JAL rd, label (explicit rd)
            
            if len(parts) == 2:
                # Format: JAL label
                rd = 1  # Default to x1 for return address
                target_label = parts[1]
            else:
                # Format: JAL rd, label
                rd = int(parts[1])
                target_label = parts[2]
            
            # Store return address (next instruction) in rd
            self.registers[rd] = self.pc + 1
            
            # Jump to label
            self.pc = self.lookup_label(target_label)
            
        elif opcode == "J":
            # Check if it's a numeric jump or a label
            if parts[1].isdigit():
                # Jump to PC + offset (used for return jumps)
                offset = int(parts[1])
                self.pc += offset
            else:
                target_label = parts[1]
                self.pc = self.lookup_label(target_label)
        
        else:
            print(f"Unknown instruction: {instruction}")
            self.pc += 1
            
        # Always ensure x0 is 0
        self.registers[0] = 0
    
    def dump_registers(self):
        """Print the current state of all registers."""
        for i in range(32):
            if self.registers[i] != 0:  # Only show non-zero registers for clarity
                print(f"x{i} = {self.registers[i]}")
    
    def get_metrics(self):
        """Return execution metrics."""
        return {
            "instructions": self.instruction_count,
            "cycles": self.cycle_count,
            "memory_accesses": self.memory_accesses
        }
    
    def reset(self):
        """Reset the simulator state."""
        self.registers = [0] * 32
        self.memory = {}
        self.pc = 0
        self.instruction_count = 0
        self.cycle_count = 0
        self.memory_accesses = 0


def parse_program_file(filename):
    """Parse a program file into a list of instructions."""
    with open(filename, 'r') as file:
        content = file.read()
    
    # Extract program array if present
    if '=' in content and '[' in content and ']' in content:
        program_content = content.split('[', 1)[1].rsplit(']', 1)[0]
        program_lines = [line.strip().strip('"').strip("'") for line in program_content.split('\n')]
        return [line for line in program_lines if line]
    else:
        # Return raw lines otherwise
        return [line.strip() for line in content.split('\n') if line.strip()]


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python riscv_simulator.py <program_file>")
        return
    
    program_file = sys.argv[1]
    program = parse_program_file(program_file)
    
    simulator = RISCVSimulator()
    cleaned_program = simulator.load_program(program)
    
    print("Loaded program:")
    for i, instr in enumerate(cleaned_program):
        print(f"{i}: {instr}")
    
    print("\nExecuting program...")
    simulator.execute_program()
    
    print("\nFinal register values:")
    simulator.dump_registers()
    
    metrics = simulator.get_metrics()
    print("\nExecution metrics:")
    print(f"Instruction count: {metrics['instructions']}")
    print(f"Cycle count: {metrics['cycles']}")
    print(f"Memory accesses: {metrics['memory_accesses']}")


if __name__ == "__main__":
    main()