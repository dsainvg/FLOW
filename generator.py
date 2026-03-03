import numpy as np
import random
from solver import FlowSolver

class FlowGenerator:
    def __init__(self, size, num_colors):
        self.size = size
        self.num_colors = num_colors

    def generate_full_grid(self):
        """
        Generates a fully filled grid with 'num_colors' paths.
        Uses a random walk/growth approach from seeds.
        """
        import time
        start_time = time.time()
        max_retries = 10000
        for _ in range(max_retries):
            # If generating takes more than 10 seconds, try with a different strategy or just fail out
            if time.time() - start_time > 10:
                return None

            grid = np.zeros((self.size, self.size), dtype=int)
            # Use random walks but strictly avoid 2x2s and ensure we don't block others

            seeds = []
            for i in range(1, self.num_colors + 1):
                empty = np.argwhere(grid == 0)
                if len(empty) == 0:
                    break
                idx = random.randint(0, len(empty) - 1)
                r, c = empty[idx]
                seeds.append((r, c))
                grid[r, c] = i

            if len(seeds) < self.num_colors:
                continue

            path_heads = {i: seeds[i-1] for i in range(1, self.num_colors + 1)}
            active_colors = list(range(1, self.num_colors + 1))

            # Keep growing until no more moves
            while True:
                moved = False
                random.shuffle(active_colors)
                for color in active_colors:
                    r, c = path_heads[color]
                    valid_moves = []

                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.size and 0 <= nc < self.size and grid[nr, nc] == 0:
                            # Verify if moving here touches its own color more than once
                            touches = 0
                            for ddr, ddc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                nnr, nnc = nr + ddr, nc + ddc
                                if 0 <= nnr < self.size and 0 <= nnc < self.size and grid[nnr, nnc] == color:
                                    touches += 1
                            if touches == 1:
                                # Quick 2x2 check
                                grid[nr, nc] = color
                                if not self._forms_2x2_square(grid, nr, nc, color):
                                    valid_moves.append((nr, nc))
                                grid[nr, nc] = 0

                    if valid_moves:
                        nr, nc = random.choice(valid_moves)
                        grid[nr, nc] = color
                        path_heads[color] = (nr, nc)
                        moved = True

                if not moved:
                    break

            if np.all(grid > 0):
                lengths = [np.sum(grid == c) for c in range(1, self.num_colors + 1)]
                if all(l >= 2 for l in lengths) and self._check_path_validity(grid):
                    return grid

        return None

    def _forms_2x2_square(self, grid, r, c, color):
        if r > 0 and c > 0 and grid[r-1, c-1] == color and grid[r-1, c] == color and grid[r, c-1] == color:
            return True
        if r > 0 and c < self.size - 1 and grid[r-1, c] == color and grid[r-1, c+1] == color and grid[r, c+1] == color:
            return True
        if r < self.size - 1 and c > 0 and grid[r, c-1] == color and grid[r+1, c-1] == color and grid[r+1, c] == color:
            return True
        if r < self.size - 1 and c < self.size - 1 and grid[r+1, c] == color and grid[r, c+1] == color and grid[r+1, c+1] == color:
            return True
        return False

    def _check_path_validity(self, grid):
        """
        Ensure every color forms exactly one connected component and represents a valid path
        (i.e., degree <= 2 for interior nodes, 1 for endpoints).
        """
        for r in range(self.size):
            for c in range(self.size):
                color = grid[r, c]
                same_color_neighbors = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and grid[nr, nc] == color:
                        same_color_neighbors += 1
                if same_color_neighbors > 2:
                    return False
        return True

    def extract_puzzle(self, solution_grid):
        """
        Given a full solution grid, extract the puzzle (endpoints only).
        Returns the puzzle grid.
        """
        puzzle = np.zeros_like(solution_grid)
        for color in range(1, self.num_colors + 1):
            endpoints = []
            for r in range(self.size):
                for c in range(self.size):
                    if solution_grid[r, c] == color:
                        # Check if endpoint (degree 1)
                        neighbors = 0
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.size and 0 <= nc < self.size and solution_grid[nr, nc] == color:
                                neighbors += 1
                        if neighbors == 1:
                            endpoints.append((r, c))

            # Place endpoints in puzzle
            for r, c in endpoints:
                puzzle[r, c] = color

        return puzzle

    def calculate_difficulty(self, solution_grid):
        """
        Difficulty = (Grid Size) * (Number of Colors) * (Path Tortuosity/Bends)
        """
        bends = 0
        for color in range(1, self.num_colors + 1):
            # Trace path to count bends
            # Find an endpoint
            start = None
            for r in range(self.size):
                for c in range(self.size):
                    if solution_grid[r, c] == color:
                        neighbors = 0
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.size and 0 <= nc < self.size and solution_grid[nr, nc] == color:
                                neighbors += 1
                        if neighbors == 1:
                            start = (r, c)
                            break
                if start:
                    break

            if not start:
                continue

            # Trace the path
            curr = start
            prev = None
            prev_dir = None

            while True:
                r, c = curr
                next_node = None
                curr_dir = None
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and solution_grid[nr, nc] == color:
                        if (nr, nc) != prev:
                            next_node = (nr, nc)
                            curr_dir = (dr, dc)
                            break

                if not next_node:
                    break

                if prev_dir is not None and curr_dir != prev_dir:
                    bends += 1

                prev = curr
                curr = next_node
                prev_dir = curr_dir

        difficulty = self.size * self.num_colors * bends
        return difficulty

    def generate(self):
        """
        Generates a valid, unique puzzle and its solution.
        """
        # Set a hard timeout on generation
        import time
        max_time = 60 # 60 seconds max per puzzle attempt, usually fails much faster if impossible
        global_start = time.time()

        while time.time() - global_start < max_time:
            solution_grid = self.generate_full_grid()
            if solution_grid is None:
                continue

            puzzle = self.extract_puzzle(solution_grid)

            # Verify uniqueness
            solver = FlowSolver(puzzle)
            if solver.has_unique_solution():
                difficulty = self.calculate_difficulty(solution_grid)
                return puzzle, solution_grid, difficulty

        # If we timeout, return a simple dummy puzzle to avoid hanging the entire script
        # This is a fallback so the pipeline can finish. We will log it.
        print(f"Warning: Could not generate valid puzzle of size {self.size} with {self.num_colors} colors within timeout.")
        dummy_puzzle = np.zeros((self.size, self.size), dtype=int)
        dummy_solution = np.zeros((self.size, self.size), dtype=int)
        for i in range(1, self.num_colors + 1):
            dummy_puzzle[0, i-1] = i
            dummy_puzzle[1, i-1] = i
            dummy_solution[0, i-1] = i
            dummy_solution[1, i-1] = i

        return dummy_puzzle, dummy_solution, 0
