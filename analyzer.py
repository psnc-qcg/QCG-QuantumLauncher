''' TODO Analyzers for problems '''
import os
from abc import ABC, abstractmethod
import pickle
import pandas as pd
import numpy as np

from algorithms import ALG_LIST
from problems import QATM

class Analyzer(ABC):
    ''' Abstract class for Analyzers '''
    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def read_data(self, path) -> None:
        ''' Reads the data '''

    #@abstractmethod
    def read_result(self, exp, log_path):
        ''' Reads the result '''
        with open(log_path, 'rb') as file_:
            res = pickle.load(file_)
        return res

class JSSPAnalyzer(Analyzer):
    ''' Analyzer for Job Shop Shedduling problem'''
    def __init__(self) -> None:
        ...
    def read_data(self, path) -> None:
        dirs = os.listdir(path)
        columns = ['instance', 'max_time', 'variant', 'onehot', 'p', 'backend', 'energy']
        df = pd.DataFrame([x[:-4].split('-') for x in dirs], columns=columns)
        self.df = df.astype({'max_time': int, 'p': int, 'energy': float})
        return df

class ECAnalyzer(Analyzer):
    ''' Analyzer for exact cover problem '''
    def __init__(self):
        ...
    def read_data(self, path):
        algorithms = ['falqon', 'qaoa']
        dirs = np.asarray(os.listdir(path))
        columns = ['instance', 'backend', 'algorithm']
        df = pd.DataFrame([x[:-4].split('-')[:3] for x in dirs], columns=columns)

        for algo in algorithms:
            subdf = df[df["algorithm"] == algo]
            if len(subdf) > 0:
                params = np.asarray([x[:-4].split('-')[3:] for x in dirs[subdf.index]])
                if algo == 'falqon':
                    for i, col_name in enumerate(['n', 'delta_t', 'beta_0', 'energy']):
                        df.loc[subdf.index, col_name] = params[:, i]
                    df = df.astype({'n': int,
                                    'delta_t': float,
                                    'beta_0': float})
                if algo == 'qaoa':
                    for i, col_name in enumerate(['p', 'energy']):
                        df.loc[subdf.index, col_name] = params[:, i]
                    df = df.astype({'p': int,
                                    'energy': float})
        df = df.fillna(0)


        df['filename'] = dirs
        return df

class NewAnalyzer(Analyzer):
    ''' New Analyzer idea '''
    def __init__(self) -> None:
        #super().__init__()
        self.alg_dict = {j.name:j.parameters for j in ALG_LIST}
        self.backend_dict = {}
        self.problem = QATM()

    def read_data(self, path) -> None:
        #super().read_data(path)
        ...

    def set_problem(self, problem) -> None:
        ''' Set's problem for further use '''
        self.problem = problem

    def set_backend(self, backends:list) -> None:
        ''' Set's backend for further use '''
        self.backend_dict = {j.name:j.parameters for j in backends}

    def set_algorithms(self, algorithms:list) -> None:
        ''' Set's algorithms for further use '''
        self.alg_dict = {j.name:j.parameters for j in algorithms}

    def _create_name(self, data:dict, names:dict) -> list[str]:
        ''' changes dict to list of str '''
        res = []
        for cat in data:
            for i in range(data[cat]):
                if names[cat][i] not in res:
                    res.append(names[cat][i])
        return res

    def analyze_data(self, path) -> pd.DataFrame:
        ''' Analyzes data and transforms it into pandas.DataFrame'''
        #dirs = os.listdir(path)
        dirs = ['100-test@1-local_backend-qaoa@1.01.pkl','110-test@1-backend-falqon@1.2@1@1.01.pkl']
        columns = ['Problem', 'Backend','Algorithm']
        #data_frame = pd.DataFrame([[0, 1] for x in dirs], columns=columns)
        algorithms, backends, problems = {}, {}, []
        for file in dirs:
            if file.endswith('.pkl'):
                _, problem, backend, algorithm = file.split('-')
                problem = problem.split('@')
                algorithm = algorithm.split('@')
                backend = backend.split('@')

                if algorithm[0] not in algorithms:
                    algorithms[algorithm[0]] = len(algorithm) - 1
                if backend[0] not in backends:
                    backends[backend[0]] = len(backend) - 1
        columns = ['problem'] + [f'problem_param_{j}' for j in problems]
        columns += ['backend'] + self._create_name(backends, self.backend_dict)
        columns += ['algorithm'] + self._create_name(algorithms, self.alg_dict)
        columns += ['path']
        data_frame = pd.DataFrame(0, index=[i for i, _ in enumerate(dirs)], columns=columns)
        for i, file in enumerate(dirs):
            _, problem, backend, algorithm = file[:-4].split('-')
            backend = backend.split('@')
            algorithm = algorithm.split('@')

            data_frame.at[i, 'backend'] = backend[0]
            for param, value in enumerate(backend[1:]):
                data_frame.at[i, self.backend_dict[backend[0]][param]] = float(value)
            data_frame.at[i,'algorithm'] = algorithm[0]
            for param, value in enumerate(algorithm[1:]):
                data_frame.at[i, self.alg_dict[algorithm[0]][param]] = float(value)
            data_frame.at[i, 'path'] = file
        return data_frame

    def test(self) -> None:
        '''test'''
        dirs = ['100-test@1-local_backend-qaoa@1.00.pkl','110-test@1-backend-falqon@1.2@1@1.00.pkl']
        return pd.DataFrame(['@'.join(i[:-4].split('-')).split('@') for i in dirs])

def main():
    '''main'''
    test = NewAnalyzer()
    print(test.test())
    print(test.analyze_data('.'))
if __name__ == '__main__':
    main()
