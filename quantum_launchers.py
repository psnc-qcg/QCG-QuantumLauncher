''' Quantum Launcher '''
from os import makedirs, path
import pickle
from templates import QuantumLauncher

class QiskitLauncher(QuantumLauncher):
    ''' Global Launcher problem'''

    def run(self) -> dict:
        return self.algorithm.run(self.problem.get_hamiltonian(), self.backend)

    def process(self, alg_options,
                save_to_file: bool = False) -> dict:
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
