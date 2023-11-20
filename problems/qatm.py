""" QATM Problem """
import os

import numpy as np
import pandas as pd

from templates import Problem


class QATM(Problem):
    """ class for QATM problem """

    def __init__(self, onehot: str, instance: any = None, instance_name: str | None = None,
                 instance_path: str | None = None) -> None:
        super().__init__(instance=instance, instance_name=instance_name,
                         instance_path=instance_path)
        self.onehot = onehot

        self.instance_name = instance_name.split('.')[0]

    @property
    def setup(self) -> dict:
        return {
            'onehot': self.onehot,
            'instance_name': self.instance_name
        }

    def _get_path(self) -> str:
        return f'{self.name}@{self.instance_name}'

    def read_instance(self, instance_path: str, instance_name: str) -> None:
        self.instance_name = instance_name.split('.', 1)[0]
        cm_path = os.path.join(instance_path, 'CM_' + instance_name)
        aircrafts_path = os.path.join(instance_path, 'aircrafts_' + instance_name)

        self.instance = {'cm': np.loadtxt(cm_path),
                         'aircrafts': pd.read_csv(aircrafts_path, delimiter=' ', names=['manouver', 'aircraft'])}

    def analyze_result(self, result: dict):
        """
        Analyzes the result in terms of collisions and violations of onehot constraint
        :param result: dict, where keys are bitstrings and values are probabolities
        :return: collisions and onehot violations as ndarray
        """
        keys = list(result.keys())
        vectorized_result = (np.fromstring("".join(keys), 'u1') - ord('0')).reshape(len(result), -1)

        cm = self.instance['cm'].copy().astype(int)
        np.fill_diagonal(cm, 0)
        collisions = np.einsum('ij,ij->i', vectorized_result @ cm, vectorized_result) / 2

        df = pd.DataFrame(vectorized_result.transpose())
        df['aircraft'] = self.instance['aircrafts']['aircraft']
        onehot_violations = (df.groupby(by='aircraft').sum() != 1).sum(axis=0).ravel()

        return collisions, onehot_violations
