Quantum Launcher
---
Quantum Launcher is a high-level python library that aims to simplify usage of different quantum algorithms. The goal is to make learning, using and benchmarking different quantum algorithms, hardware and problem formulations simpler.

Quantum Launcher splits solving problems on Quantum Machine into 3 main components:
- Problem: Formulation of the problem that we want to solve, for example: Maxcut or Exact Cover
- Algorithm: Algorithm implementation that we want to use for solving problem, for example: QAOA, FALQON, BBS
- Backend: The Hardware or local simulator that we want to use to execute our algorithm

So far Quantum Launcher provides user with:
- High-level architecture for executing problems
- Set of predefined problems, algorithms, and backends
- Automated processing of the problem
- Asynchronous architecture to execute problems either standalone or in a grid

Features planned to be implemented in feature:
