''' TODO Analyzers for problems '''
import os
from abc import ABC, abstractmethod
import pickle
import pandas as pd
import numpy as np

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