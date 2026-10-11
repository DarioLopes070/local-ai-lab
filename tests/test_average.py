
import pytest


def average(numbers):
    if not numbers:
        raise ValueError("A lista não pode estar vazia")
    return sum(numbers) / len(numbers)


def test_average_positive_numbers():
    assert average([1, 2, 3]) == 2.0


def test_average_negative_numbers():
    assert average([-1, 0, 1]) == 0.0


def test_average_floats():
    assert average([1.5, 2.5]) == 2.0


def test_average_empty_list():
    with pytest.raises(ValueError):
        average([])