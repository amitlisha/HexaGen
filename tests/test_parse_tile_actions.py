from gpt.runner_utils import parse_tile_actions


def test_parse_tile_actions_tuple_list():
    text = "[(1,2,'red'), (3,4,\"blue\")]"
    dims, tiles = parse_tile_actions(text)
    assert dims is None
    assert tiles == [(1,2,'red'), (3,4,'blue')]


def test_parse_tile_actions_regex():
    text = "(1,2,green) (5,6,orange)"
    dims, tiles = parse_tile_actions(text)
    assert dims is None
    assert tiles == [(1,2,'green'), (5,6,'orange')]

