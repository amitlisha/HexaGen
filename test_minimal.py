"""Test the minimal hexagen library."""

from minimal_hexagen import Game, Tile, WIDTH, HEIGHT, COLORS

# Test basic functionality
with Game() as g:
    print(f"Board size: {g.width}x{g.height}")
    print(f"Board state length: {len(g.board_state)}")

    # Test single tile
    tile = Tile(row=5, column=7)
    print(f"\nCreated tile: {tile}")
    print(f"Initial color: {tile.color}")

    tile.draw('red')
    print(f"After drawing red: {tile.color}")

    # Check board state
    non_white = [i for i, c in enumerate(g.board_state) if c != 0]
    print(f"\nNon-white tiles: {len(non_white)}")

    print("\n✓ Minimal library works!")
