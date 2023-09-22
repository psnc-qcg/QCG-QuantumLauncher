""" Analyzer for problems """
import os
import pickle
import pandas as pd
#import numpy as np

from algorithms import ALG_LIST
from backends import BACKEND_LIST

class Analyzer():
    """ Abstract class for Analyzers """
    def __init__(self) -> None:
        self.alg_dict = {j.name:j.parameters for j in ALG_LIST}
        self.backend_dict = {}
        self.problem = []

    def read_result(self, log_path:str):
        """ Reads the result """
        with open(log_path, 'rb') as file_:
            res = pickle.load(file_)
        return res

    def set_problem(self, problem) -> None:
        """ Set's problem for further use """
        self.problem = problem

    def set_backend(self, backends:list) -> None:
        """ Set's backend for further use """
        self.backend_dict = {j.name:j.parameters for j in backends}

    def set_algorithms(self, algorithms:list) -> None:
        """ Set's algorithms for further use """
        self.alg_dict = {j.name:j.parameters for j in algorithms}

    def _create_name(self, data:dict, names:dict) -> list[str]:
        """ changes dict to list of str """
        res = []
        for cat in data:
            for i in range(data[cat]):
                if names[cat][i] not in res:
                    res.append(names[cat][i])
        return res

    def read_data(self, path:str) -> pd.DataFrame:
        """ Analyzes data and transforms it into pandas.DataFrame"""
        if path == '__test__':
            dirs = ['100-test@1@2@onehot-local_backend-qaoa@1.01.pkl','110-test@1@3.11@exact-backend-falqon@1.2@1@1.01.pkl']
        else:
            dirs = os.listdir(path)
        #dirs = ['100-test@1@2@onehot-local_backend-qaoa@1.01.pkl','110-test@1@3.11@exact-backend-falqon@1.2@1@1.01.pkl']
        columns = ['Problem', 'Backend','Algorithm']
        #data_frame = pd.DataFrame([[0, 1] for x in dirs], columns=columns)
        algorithms, backends = {}, {}
        for file in dirs:
            if file.endswith('.pkl'):
                backend, algorithm = file.split('-')[1:-1]
                algorithm = algorithm.split('@')
                backend = backend.split('@')

                if algorithm[0] not in algorithms:
                    algorithms[algorithm[0]] = len(algorithm) - 1
                if backend[0] not in backends:
                    backends[backend[0]] = len(backend) - 1
        columns1 = [j for j in self.problem]
        columns = ['backend'] + self._create_name(backends, self.backend_dict)
        columns += ['algorithm'] + self._create_name(algorithms, self.alg_dict)
        columns += ['path']
        starter_data_frame = pd.DataFrame(data=[i.split('-', 1)[0].split('@', len(self.problem)) for i in dirs],
                                           index=range(len(dirs)), columns=columns1)
        data_frame = pd.DataFrame(0, index=range(len(dirs)), columns=columns)
        energies_data_frame = pd.DataFrame(data=[[i[:-4].rsplit('-', 1)[1], i] for i in dirs],
                                           index=range(len(dirs)), columns=['energy', 'path'])
        data_frame = pd.concat([starter_data_frame, data_frame, energies_data_frame], axis=1, join='inner')
        for i, file in enumerate(dirs):
            backend, algorithm = file[:-4].split('-')[1:-1]
            backend = backend.split('@')
            algorithm = algorithm.split('@')

            data_frame.at[i, 'backend'] = backend[0]
            for param, value in enumerate(backend[1:]):
                data_frame.at[i, self.backend_dict[backend[0]][param]] = float(value)
            data_frame.at[i,'algorithm'] = algorithm[0]
            for param, value in enumerate(algorithm[1:]):
                data_frame.at[i, self.alg_dict[algorithm[0]][param]] = float(value)
        return data_frame

def main():
    """main"""
    my_analyzer = Analyzer()
    my_analyzer.problem = ['instance', 'max-time', 'goal', 'exact']
    print(my_analyzer.read_data('test_data/jssp'))

if __name__ == '__main__':
    main()
