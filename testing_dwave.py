import matplotlib.pyplot as plt
import networkx as nx
from problems import EC, JSSP, MaxCut, QATM
from templates import QuantumLauncher
from dwave_routines import DwaveBackend, DwaveSolver, QiskitToDwave


solver = DwaveSolver()
backend = DwaveBackend()
# pr = EC("exact", instance_name="toy")
# pr = MaxCut(instance_name="default")
pr = JSSP(3, "exact", instance_name="toy", optimization_problem=True)

ql = QuantumLauncher(pr, solver, backend, path="testing")
ql._prepare_problem()
if not isinstance(pr, QiskitToDwave):
    quit(1)
qubo, offset = pr.get_dwave_qubo()
res = solver.solve_dwave(qubo, offset)
print(res)
