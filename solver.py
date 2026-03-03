import numpy as np
from collections import deque

class FlowSolver:
    def __init__(self, puzzle):
        self.puzzle = np.array(puzzle)
        self.size = len(puzzle)
        self.grid = np.array(puzzle)
        self.colors = []
        self.endpoints = {}

        # Identify endpoints
        for r in range(self.size):
            for c in range(self.size):
                val = self.grid[r, c]
                if val > 0:
                    if val not in self.endpoints:
                        self.endpoints[val] = []
                    self.endpoints[val].append((r, c))
                    if val not in self.colors:
                        self.colors.append(val)

        self.colors.sort()
        self.solutions = []
        self.max_solutions = 2 # Usually only need to know if 0, 1, or >1

    def has_unique_solution(self):
        """
        Returns True if the puzzle has exactly one valid solution that fills the entire grid.
        """
        solutions = self.solve()
        return len(solutions) == 1

    def solve(self):
        """
        Main solve function. Returns all found solutions up to max_solutions.
        """
        self.solutions = []

        # Fast path if invalid board
        if not self.colors:
            return []

        for c in self.colors:
            if c not in self.endpoints or len(self.endpoints[c]) != 2:
                return []

        # Determine the order of colors to solve. Sorting by manhattan distance between endpoints can help heuristics.
        color_order = sorted(self.colors, key=lambda c: abs(self.endpoints[c][0][0] - self.endpoints[c][1][0]) + abs(self.endpoints[c][0][1] - self.endpoints[c][1][1]))

        self._backtrack(self.grid.copy(), color_order, 0, self.endpoints[color_order[0]][0])
        return self.solutions

    def _backtrack(self, current_grid, color_order, color_idx, current_pos):
        if len(self.solutions) >= self.max_solutions:
            return

        color = color_order[color_idx]
        target_pos = self.endpoints[color][1]

        # Early pruning: check if there are isolated empty cells
        if not self._check_reachability(current_grid, color_order, color_idx, current_pos):
            return

        r, c = current_pos

        # Explore neighbors
        # Pre-check empty cells to prune early
        empty_mask = current_grid == 0

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc

            if 0 <= nr < self.size and 0 <= nc < self.size:
                if (nr, nc) == target_pos:
                    # Reached the target for this color
                    if color_idx == len(color_order) - 1:
                        # All colors connected. Check grid saturation.
                        if np.all(current_grid > 0):
                            self.solutions.append(current_grid.copy())
                    else:
                        # Before starting next color, verify if the remaining empty cells are still valid
                        # A quick check is whether the remaining empty cells have paths to next colors
                        next_color = color_order[color_idx + 1]
                        next_start = self.endpoints[next_color][0]
                        self._backtrack(current_grid, color_order, color_idx + 1, next_start)
                elif current_grid[nr, nc] == 0:
                    # Check for 2x2 squares of same color (trivial loop prevention)
                    # We only need to check if placing `color` at (nr, nc) forms a 2x2.
                    current_grid[nr, nc] = color
                    if not self._forms_2x2_square(current_grid, nr, nc, color):
                        self._backtrack(current_grid, color_order, color_idx, (nr, nc))
                    current_grid[nr, nc] = 0 # Backtrack

    def _forms_2x2_square(self, grid, r, c, color):
        """
        Check if placing `color` at (r,c) forms a 2x2 square of the same color.
        """
        # Check top-left
        if r > 0 and c > 0 and grid[r-1, c-1] == color and grid[r-1, c] == color and grid[r, c-1] == color:
            return True
        # Check top-right
        if r > 0 and c < self.size - 1 and grid[r-1, c] == color and grid[r-1, c+1] == color and grid[r, c+1] == color:
            return True
        # Check bottom-left
        if r < self.size - 1 and c > 0 and grid[r, c-1] == color and grid[r+1, c-1] == color and grid[r+1, c] == color:
            return True
        # Check bottom-right
        if r < self.size - 1 and c < self.size - 1 and grid[r+1, c] == color and grid[r, c+1] == color and grid[r+1, c+1] == color:
            return True
        return False

    def _check_reachability(self, grid, color_order, current_color_idx, current_pos):
        """
        Checks if it's possible to connect all remaining endpoints.
        Also checks for isolated empty cells (grid saturation constraint).
        Returns True if the current state is valid, False otherwise.
        """
        # 1. Simple empty cell count vs required paths might be too complex for now,
        # but we MUST check if any empty cell is completely surrounded.
        # Actually, let's do a fast BFS for connected components of empty cells.
        # Each connected component of empty cells must have at least 2 adjacent path endpoints
        # (or 1 if it's currently being extended).

        # A simpler check: any empty cell with 0 empty neighbors and not adjacent to an active head
        # is a dead end and will cause grid saturation to fail.

        # Let's collect active heads
        active_heads = [current_pos]
        for i in range(current_color_idx + 1, len(color_order)):
            c = color_order[i]
            active_heads.append(self.endpoints[c][0])
            active_heads.append(self.endpoints[c][1])
        # Add the target for current color
        active_heads.append(self.endpoints[color_order[current_color_idx]][1])

        # Convert to set for faster lookup
        active_heads_set = set(active_heads)

        for r in range(self.size):
            for c in range(self.size):
                if grid[r, c] == 0:
                    empty_neighbors = 0
                    active_neighbor = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.size and 0 <= nc < self.size:
                            if grid[nr, nc] == 0:
                                empty_neighbors += 1
                            elif (nr, nc) in active_heads_set:
                                active_neighbor = True

                    if empty_neighbors == 0 and not active_neighbor:
                        return False # Dead end empty cell

        return True
