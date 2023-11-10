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
        return f'{self.name}/{self.instance_name}'

    def read_instance(self, instance_path: str, instance_name: str) -> None:
        self.instance_name = instance_name.split('.', 1)[0]
        program_directory = os.path.dirname(__file__)
        cm_path = os.path.join(program_directory, instance_path, 'CM_' + instance_name)
        aircrafts_path = os.path.join(program_directory, instance_path, 'aircrafts_' + instance_name)

        self.instance = np.loadtxt(cm_path), pd.read_csv(aircrafts_path, delimiter=' ', header=None)
