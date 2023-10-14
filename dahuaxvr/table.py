from typing import List
import re


class TableBuilder:

    def __init__(self):
        self.values = {}

    def build_entry(self, value):
        if isinstance(value, TableBuilder):
            return value.build()
        elif isinstance(value, list):
            return [self.build_entry(v) for v in value]
        else:
            return value

    def build(self) -> dict:
        return {key: self.build_entry(value) for key, value in self.values.items()}

    def push(self, keys: List[str], value: str):
        assert len(keys) > 0, f'Could not push "{value}" because keys {keys}'
        key = keys[0]
        m = re.match(r'(\w+)(\[\d+])?', key)
        assert m is not None, f'Could not parse key "{key}"'
        key, array_spec = m.group(1), m.group(2)
        is_array, array_index = (True, int(array_spec[1:-1])) if array_spec is not None else (False, None)
        existing = self.values.get(key, None)
        if is_array:
            assert existing is None or isinstance(existing, list), f'Integrity check failed {existing} - "{key}"'
            if existing is None:
                existing = []
                self.values[key] = existing
            if len(keys) > 1:
                if array_index >= len(existing):
                    b = TableBuilder()
                    existing.append(b)
                    return b.push(keys[1:], value)
                else:
                    assert isinstance(existing[array_index],
                                      TableBuilder), f'Integrity check failed {existing[array_index]} - "{key}"'
                    return existing[array_index].push(keys[1:], value)
            else:
                if array_index >= len(existing):
                    existing.append(value)
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
