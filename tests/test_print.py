from typing import Any

import hydration as h


class Eric(h.Struct):
    board = h.Array(8)


def test_array_print():
    assert_str_eq(Eric(),
                  """
Eric:
board: Array[]
"""
                  )


def assert_str_eq(expected: Any, result: str):
    expected_str = str(expected).lstrip()
    print(expected_str.split('\n'))
    print(result.split('\n'))
    assert str(expected).split() == result.split()
