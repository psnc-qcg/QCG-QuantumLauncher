from dataclasses import dataclass


@dataclass
class Result:
    best_bitstring: str
    best_energy: float
    most_common_bitstring: str
    most_common_bitstring_energy: float
    distribution: dict
    energies: dict
    num_of_samples: int
    average_energy: float
    energy_std: float
    result: any

    def __str__(self):
        return f"Result(bitstring={self.best_bitstring}, energy={self.best_energy})"

    def __repr__(self):
        return str(self)

    def best(self):
        return self.best_bitstring, self.best_energy

    def most_common(self):
        return self.most_common_bitstring, self.most_common_bitstring_energy
