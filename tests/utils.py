class MockReader:
    def __init__(self, data: bytes):
        self._data = data

    def read(self, size=0):
        user_data, self._data = self._data[:size], self._data[size:]
        return user_data


def as_reader(data: bytes):
    return MockReader(data).read
