import numpy as np
import pytest
from solver import FlowSolver
from flow_utils import load_flow_dataset

# We test with the small dataset we just generated
def test_uniqueness():
    puzzles, solutions, meta = load_flow_dataset('outputs/flow_small.npz')
    for i, puzzle in enumerate(puzzles):
        size = meta[i]['size']
        actual_puzzle = puzzle[:size, :size]
        solver = FlowSolver(actual_puzzle)
        assert solver.has_unique_solution(), f"Puzzle {i} does not have a unique solution!"

def test_grid_saturation():
    puzzles, solutions, meta = load_flow_dataset('outputs/flow_small.npz')
    for i, solution in enumerate(solutions):
        # The size might be smaller than max_size due to padding
        # Let's get the actual size from metadata
        size = meta[i]['size']
        actual_solution = solution[:size, :size]
        assert np.all(actual_solution > 0), f"Solution {i} contains empty cells!"

def test_connectivity():
    from collections import deque
    puzzles, solutions, meta = load_flow_dataset('outputs/flow_small.npz')

    for idx, solution in enumerate(solutions):
        size = meta[idx]['size']
        num_colors = meta[idx]['num_colors']
        actual_solution = solution[:size, :size]

        for color in range(1, num_colors + 1):
            # Find all cells of this color
            color_cells = []
            for r in range(size):
                for c in range(size):
                    if actual_solution[r, c] == color:
                        color_cells.append((r, c))

            if not color_cells:
                continue

            # Perform BFS to ensure all these cells form a single connected component
            start = color_cells[0]
            visited = set()
            queue = deque([start])

            while queue:
                r, c = queue.popleft()
                if (r, c) in visited:
                    continue
                visited.add((r, c))

                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < size and 0 <= nc < size:
                        if actual_solution[nr, nc] == color and (nr, nc) not in visited:
                            queue.append((nr, nc))

            # Check if we visited all cells of this color
            assert len(visited) == len(color_cells), f"Puzzle {idx}, Color {color} is not fully connected!"

def test_no_2x2_loops():
    """
    Ensure no 2x2 blocks of the same color exist in the generated solutions,
    as this would indicate a trivial loop.
    """
    puzzles, solutions, meta = load_flow_dataset('outputs/flow_small.npz')
    for idx, solution in enumerate(solutions):
        size = meta[idx]['size']
        actual_solution = solution[:size, :size]

        for r in range(size - 1):
            for c in range(size - 1):
                color = actual_solution[r, c]
                if color == 0:
                    continue
                # Check 2x2 square
                is_2x2 = (
                    actual_solution[r, c+1] == color and
                    actual_solution[r+1, c] == color and
                    actual_solution[r+1, c+1] == color
                )
                assert not is_2x2, f"Solution {idx} contains a 2x2 loop of color {color} at ({r},{c})!"

def test_invalid_board():
    """
    Test that the solver correctly identifies and rejects an invalid board.
    """
    # Create an invalid 3x3 board where endpoints are trapped
    # Color 2 is surrounded by color 1 endpoints or edges, making connection impossible
    invalid_puzzle = np.array([
        [1, 1, 1],
        [1, 2, 1],
        [0, 2, 0]
    ])
    solver = FlowSolver(invalid_puzzle)
    sols = solver.solve()
    assert len(sols) == 0, "Solver should not find a solution for an invalid board."
    assert not solver.has_unique_solution()

def test_tortuosity_correctness():
    """
    Test the difficulty calculation function directly to ensure bends are counted correctly.
    """
    from generator import FlowGenerator
    # Mock a generator to use its calculate_difficulty method
    gen = FlowGenerator(4, 2)
    # Create a test grid with known bends
    # Color 1: (0,0) -> (0,3) -> (3,3) -> (3,0) = 2 bends
    # Color 2: (1,1) -> (1,2) = 0 bends
    solution_grid = np.array([
        [1, 1, 1, 1],
        [0, 2, 2, 1],
        [0, 0, 0, 1],
        [1, 1, 1, 1]
    ])

    # We must patch num_colors to 2
    difficulty = gen.calculate_difficulty(solution_grid)

    # Grid Size = 4, Colors = 2, Bends = 2
    expected_difficulty = 4 * 2 * 2
    assert difficulty == expected_difficulty, f"Expected difficulty {expected_difficulty}, got {difficulty}"
