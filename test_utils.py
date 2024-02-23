from utils import sumar, restar


def test_suma():
    assert sumar(2, 4) == 6
    assert sumar(1, 1) == 2


def test_resta():
    assert restar(2, 4) == -2
    assert restar(1, 1) == 0
