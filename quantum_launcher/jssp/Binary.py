class Binary:
    ''' It's not the same as Binary, it just replicate "spin" calculation "Binary" from pyqubo '''
    def __init__(self, value:str):
        if isinstance(value, str):
            self.data = {value: 0.5}
            self.data['__free__'] = 0.5
        elif isinstance(value, int):
            self.data = {'__free__': value}
        elif isinstance(value, dict):
            self.data = value
        elif isinstance(value, Binary):
            self.data = value.data.copy()
        else:
            raise TypeError(f'Unsupported type: {type(value)}')
        self.variables:list = []
        
    def __str__(self):
        return str(self.data)

    def __add__(self, other):
        data = self.data.copy()
        if isinstance(other, str):
            if other in data:
                data[other] += 1
            else:
                data[other] = 1
        elif isinstance(other, int):
            if '__free__' in data:
                data['__free__'] += other
            else:
                data['__free__'] = other
        elif isinstance(other, float):
            if '__free__' in data:
                data['__free__'] += other
            else:
                data['__free__'] = other
        elif isinstance(other, dict):
            for key, value in other.items():
                if key in data:
                    data[key] += value
                else:
                    data[key] = value
        elif isinstance(other, Binary):
            for key, value in other.data.items():
                if key in data:
                    data[key] += value
                else:
                    data[key] = value
        else:
            raise TypeError(f'Unsupported type: {type(other)}')
        return Binary(data)
    
    def __radd__(self, other):
        data = self.data.copy()
        if isinstance(other, str):
            if other in data:
                data[other] += 1
            else:
                data[other] = 1
        elif isinstance(other, int):
            if '__free__' in data:
                data['__free__'] += other
            else:
                data['__free__'] = other
        elif isinstance(other, float):
            if '__free__' in data:
                data['__free__'] += other
            else:
                data['__free__'] = other
        elif isinstance(other, dict):
            for key, value in other.items():
                if key in data:
                    data[key] += value
                else:
                    data[key] = value
        elif isinstance(other, Binary):
            for key, value in other.data.items():
                if key in data:
                    data[key] += value
                else:
                    data[key] = value
        else:
            raise TypeError(f'Unsupported type: {type(other)}')
        return Binary(data)

    def __sub__(self, other):
        data = self.data.copy()
        if isinstance(other, str):
            if other in data:
                data[other] -= 1
                if data[other] == 0:
                    del data[other]
            else:
                data[other] = -1
        elif isinstance(other, int):
            if '__free__' in data:
                data['__free__'] -= other
                if data['__free__'] == 0:
                    del data['__free__']
            else:
                data['__free__'] = -other
        elif isinstance(other, float):
            if '__free__' in data:
                data['__free__'] -= other
                if data['__free__'] == 0:
                    del data['__free__']
            else:
                data['__free__'] = -other
        elif isinstance(other, dict):
            for key, value in other.items():
                if key in data:
                    data[key] -= value
                    if data[key] == 0:
                        del data[key]
                else:
                    data[key] = -value
        elif isinstance(other, Binary):
            for key, value in other.data.items():
                if key in data:
                    data[key] -= value
                    if data[key] == 0:
                        del data[key]
                else:
                    data[key] = -value
        else:
            raise TypeError(f'Unsupported type: {type(other)}')
        return Binary(data)
    
    def __rsub__(self, other):
        return Binary(other) - self

    def __neg__(self):
        data = {}
        for key, value in self.data.items():
            data[key] = -value
        return Binary(data)

    def __mul__(self, other):
        data = {}
        if isinstance(other, str):
            for key, value in self.data.items():
                if key == other:
                    if '__free__' in data:
                        data['__free__'] += value
                    else:
                        data['__free__'] = value
                else:
                    data[key, other] = value
        elif isinstance(other, int):
            for key, value in self.data.items():
                data[key] = value * other
        elif isinstance(other, float):
            for key, value in self.data.items():
                data[key] = value * other
        elif isinstance(other, dict):
            for key, value in self.data.items():
                for key2, value2 in other.items():
                    data[key, key2] = value * value2
        elif isinstance(other, Binary):
            for key, value in self.data.items():
                for key2, value2 in other.data.items():
                    if key == key2:
                        if '__free__' in data:
                            data['__free__'] += value * value2
                        else:
                            data['__free__'] = value * value2
                    else:
                        data[key, key2] = value * value2
        else:
            raise TypeError(f'Unsupported type: {type(other)}')
        return Binary(data)

    def __rmul__(self, other):
        data = {}
        if isinstance(other, str):
            for key, value in self.data.items():
                if key == other:
                    if '__free__' in data:
                        data['__free__'] += value
                    else:
                        data['__free__'] = value
                else:
                    data[key, other] = value
        elif isinstance(other, int):
            for key, value in self.data.items():
                data[key] = value * other
        elif isinstance(other, float):
            for key, value in self.data.items():
                data[key] = value * other
        elif isinstance(other, dict):
            for key, value in self.data.items():
                for key2, value2 in other.items():
                    data[key, key2] = value * value2
        elif isinstance(other, Binary):
            for key, value in self.data.items():
                for key2, value2 in other.data.items():
                    if key == key2:
                        if '__free__' in data:
                            data['__free__'] += value * value2
                        else:
                            data['__free__'] = value * value2
                    else:
                        data[key, key2] = value * value2
        else:
            raise TypeError(f'Unsupported type: {type(other)}')
        return Binary(data)

    def __pow__(self, other):
        data = self.data.copy()
        new_data = {}
        if isinstance(other, int) and other >= 0:
            if other == 0:
                return Binary({'__free__': 1})
            elif other == 1:
                return Binary(data)
            elif other == 2:
                return Binary(data) * Binary(data)

        else:
            raise TypeError(f'Unsupported type: {type(other)}')
        return Binary(data)

    def __truediv__(self, other):
        return self * (1 / other)

    def calculate(self):

        for key, value in self.data.copy().items():
            if isinstance(key, tuple):
                if key[0] == '__free__':
                    if key[1] in self.data:
                        self.data[key[1]] += value
                    else:
                        self.data[key[1]] = value
                    del self.data[key]
                elif key[1] == '__free__':
                    if key[0] in self.data:
                        self.data[key[0]] += value
                    else:
                        self.data[key[0]] = value
                    del self.data[key]
        energy = 0
        if '__free__' in self.data:
            energy = self.data['__free__']
            del self.data['__free__']

        linear_dict = {}
        quadratic_dict = {}
        for key, value in self.data.items():
            if isinstance(key, str):
                linear_dict[key] = value
            elif isinstance(key, tuple):
                if (key[1], key[0]) in quadratic_dict:
                    quadratic_dict[(key[1], key[0])] += value
                else:
                    quadratic_dict[key] = value
            else:
                raise TypeError(f'Unsupported type: {type(key)}')
        
        # order quadratic
        for key, value in quadratic_dict.copy().items():
            if key[0] > key[1]:
                quadratic_dict[(key[1], key[0])] = value
                del quadratic_dict[key]
        self.variables = list(linear_dict.keys())
        class spin:
            linear = linear_dict
            quadratic = quadratic_dict
            offset = energy
        self.spin = spin
        return linear_dict, quadratic_dict, energy

    def compile(self):
        self.calculate()
        return self

    def to_bqm(self):
        return self
