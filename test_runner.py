from riscv_simulator import RISCVSimulator

def run_program(program_name, program_data, max_instructions=100):
    """Run a program and return the results and metrics."""
    simulator = RISCVSimulator()
    cleaned_program = simulator.load_program(program_data)
    
    print(f"\n=== Running {program_name} ===")
    print("Program instructions:")
    for i, instr in enumerate(cleaned_program):
        print(f"{i}: {instr}")
    
    print("\nExecuting...")
    
    # Modified execution with instruction limit
    simulator.pc = 0
    instruction_limit = max_instructions
    
    while 0 <= simulator.pc < len(simulator.program) and instruction_limit > 0:
        simulator.execute_instruction(simulator.program[simulator.pc])
        instruction_limit -= 1
        
    if instruction_limit <= 0:
        print(f"Execution stopped after {max_instructions} instructions (possible infinite loop)")
    
    print("\nFinal register values:")
    simulator.dump_registers()
    
    metrics = simulator.get_metrics()
    print("\nExecution metrics:")
    print(f"Instruction count: {metrics['instructions']}")
    print(f"Cycle count: {metrics['cycles']}")
    print(f"Memory accesses: {metrics['memory_accesses']}")
    
    return simulator.registers, metrics

# Sample programs from the lab assignment
program1 = [
    "li 2 1",
    "li 3 10",
    "add 2 3 2",
    "add 2 3 2",
    "add 2 3 2",
    "add 2 3 2",
    "add 2 3 2"
]

program2 = [
    "li 2 123353",
    "li 3 45551",
    "sub 2 3 2",
    "sub 2 3 2",
    "sub 2 3 2",
    "sub 2 3 2",
    "sub 2 3 2"
]

program3 = [
    "li 2 577",
    "li 3 555",
    "li 5 443",
    "SUB 2 3 2",
    "SUB 2 3 2",
    "ADD 2 5 3",
    "ADD 2 2 2",
    "SUB 2 3 2",
    "SUB 2 3 2",
    "SUB 2 3 2",
    "ADD 5 3 2",
    "ADD 3 2 3"
]

program4 = [
    "start: LI 3 1",
    "LI 5 10",
    "count_loop: BEQ 3 5 done",
    "JAL increment",  # JAL with implicit return address register (x1)
    "J count_loop",
    "increment: ADD 3 3 1",
    "J 1", # Jump back to caller (PC + 1 from JAL)
    "done: J done"
]

# Run all programs
results = {}

for name, program in [("Program 1", program1), ("Program 2", program2), 
                      ("Program 3", program3), ("Program 4", program4)]:
    results[name] = run_program(name, program)

# Print comparative summary
print("\n=== Comparative Summary ===")
print("Program | Instructions | Cycles | Memory Accesses")
print("--------|--------------|--------|---------------")
for name, (_, metrics) in results.items():
    print(f"{name} | {metrics['instructions']} | {metrics['cycles']} | {metrics['memory_accesses']}")