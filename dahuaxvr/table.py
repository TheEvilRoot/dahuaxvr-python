from typing import List
import re


class DictList:
    def __init__(self):
        self.values = {}

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        yield from self.values.values()

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, key, value):
        self.values[key] = value



"""
Builder and parser for Dahua response table format e.g.
    table.key=1
    table.array[0].a=1
    table.array[0].b=2
    table.array[1].a=2
    table.array[1].b=2
"""


class TableBuilder:

    @staticmethod
    def parse(content: str):
        t = TableBuilder()
        for line in content.splitlines():
            line = line.strip()
            if len(line) == 0:
                continue
            try:
                key, value = line.split('=')
                keys = key.split('.')
                t.push(keys, value)
            except Exception as e:
                print(e, content)
        return t.build()

    def __init__(self):
        self.values = {}

    """
    Transform builder type to dict recursively
    :param value - value to be transformed.
    
    List will be transformed per item recursively
    TableBuilder will be transformed using self.build()
    Any other value - as is
    """

    def build_entry(self, value):
        if isinstance(value, TableBuilder):
            return value.build()
        elif isinstance(value, DictList):
            return [self.build_entry(v) for v in value]
        else:
            return value

    """
    Transform all values of table recursively and return dict
    """

    def build(self) -> dict:
        return {key: self.build_entry(value) for key, value in self.values.items()}

    """
    Push multidimensional key-value entry into current table.
    :param keys - keys hierarchy
    :param value - value to be associated with keys
    
    Will return value if it was associated successfully. None when keys are empty.
    Could throw errors when integrity is not valid due construction of table
    """

    def push(self, keys: List[str], value: str):
        assert len(keys) > 0, f'Could not push "{value}" because keys {keys}'
        key = keys[0]
        m = re.match(r'(\w+)(\[\d+])?', key)
        assert m is not None, f'Could not parse key "{key}"'
        key, array_spec = m.group(1), m.group(2)
        is_array, array_index = (True, int(array_spec[1:-1])) if array_spec is not None else (False, None)
        existing = self.values.get(key, None)
        if is_array:
            assert existing is None or isinstance(existing, DictList), f'Integrity check failed {existing} - "{key}"'
            if existing is None:
                existing = DictList()
                self.values[key] = existing
            if len(keys) > 1:
                if array_index >= len(existing):
                    b = TableBuilder()
                    existing[array_index] = b
                    return b.push(keys[1:], value)
                else:
                    assert isinstance(existing[array_index],
                                      TableBuilder), f'Integrity check failed {existing[array_index]} - "{key}"'
                    return existing[array_index].push(keys[1:], value)
            else:
                if array_index >= len(existing):
                    existing[array_index] = value
                    return value
                else:
                    existing[array_index] = value
                    return value
        if len(keys) > 1:
            if existing is None:
                b = TableBuilder()
                self.values[key] = b
                return b.push(keys[1:], value)
            else:
                assert isinstance(existing, TableBuilder), f'Integrity check failed {existing} - "{key}"'
                return existing.push(keys[1:], value)
        self.values[key] = value
        return value
