''' Quantum Launcher '''
from os import makedirs, path
import pickle
from templates import Problem, Backend, Algorithm

class QuantumLauncher():
    ''' Global Launcher problem'''

    def __init__(self, problem: Problem, algorithm: Algorithm, backend:Backend) -> None:
        self.problem: Problem = problem
        self.algorithm: Algorithm = algorithm
        self.backend: Backend = backend
        self.path = None
        self.res = {}
        self.dir = 'data/'
        self.res_path = None
        self.result_paths = []

    def run(self) -> dict:
        ''' runs problem on machine'''
        return self.algorithm.run(self.problem.get_hamiltonian(), self.backend)

    def get_path(self) -> str:
        ''' Outputs path of current output '''
        return self.path

    def set_dir(self, dir_path: str) -> None:
        ''' Setting output file directory path '''
        self.dir = dir_path

    def process(self, alg_options,
                save_to_file: bool = False) -> dict:
        ''' Runs and proccesses problem on algorithm '''
        results = self.run()
        energy = results['energy']
        variant = self.problem.variant
        results['variant'] = variant
        results['alg_options'] = alg_options
        results['backend_name'] = self.backend.name
        if save_to_file:
            self.res_path = self.dir + '/' + self.problem.path_name + '-' + \
                self.backend.path_name + '-' \
                + self.algorithm.path_name + '-' + str(energy) + '.pkl'
            self.result_paths.append(self.res_path)
            self.dir = path.dirname(self.res_path)
            if not path.exists(self.dir):
                makedirs(self.dir)
            with open(self.res_path, 'wb') as file:
                pickle.dump(results, file)
        self.res = {}
        self.res = results
        return results

def from_pickle(path_:str) -> dict:
    ''' reades pickle and returns as a dict '''
    with open(path_, 'rb') as file_:
        return pickle.load(file_)
