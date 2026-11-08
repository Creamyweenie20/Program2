from Dag import DAG                      
from Generator import write_generator    

def build(statements):
    dag = DAG()
    for s in statements:
        dag.add_statemnt(s)
    return dag

# Test 1: your original example
dag = build([
    'A = B + C',
    'D = A + E',
    'F = D + G',
    'H = F + I',
    'J = K + L'
])
dag.print_levels()
verilog = write_generator(dag, "synth_core_gen")
print(verilog)