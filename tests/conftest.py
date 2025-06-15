import pytest
from hexagen import Game


@pytest.fixture
def game():
    g = Game()
    g.__enter__()
    try:
        yield g
    finally:
        g.__exit__(None, None, None)
