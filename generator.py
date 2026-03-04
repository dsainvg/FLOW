import numpy as np
import random
import time


class FlowGenerator:
    def __init__(self, size, num_colors):
        self.size = size
        self.num_colors = num_colors

    # ------------------------------------------------------------------
    # Hamiltonian path via recursive DFS with a per-attempt deadline
    # ------------------------------------------------------------------
    def _find_hamiltonian_path(self, deadline):
        """Return a list of all cells in Hamiltonian-path order, or None."""
        n = self.size
        total = n * n
        path = []
        visited = [[False] * n for _ in range(n)]

        def dfs(r, c):
            if time.time() > deadline:
                return False
            path.append((r, c))
            visited[r][c] = True
            if len(path) == total:
                return True
            nbrs = [(r+dr, c+dc) for dr, dc in ((-1,0),(1,0),(0,-1),(0,1))
                    if 0 <= r+dr < n and 0 <= c+dc < n]
            random.shuffle(nbrs)
            for nr, nc in nbrs:
                if not visited[nr][nc]:
                    if dfs(nr, nc):
                        return True
            # backtrack
            path.pop()
            visited[r][c] = False
            return False

        sr, sc = random.randint(0, n-1), random.randint(0, n-1)
        if dfs(sr, sc):
            return path
        return None

    def _segment_path(self, path):
        """Split path into num_colors contiguous segments, each length >= 2."""
        remaining = len(path)
        segment_lengths = []
        for i in range(self.num_colors - 1):
            max_len = remaining - (self.num_colors - 1 - i) * 2
            if max_len < 2:
                return None
            slen = random.randint(2, max_len)
            segment_lengths.append(slen)
            remaining -= slen
        if remaining < 2:
            return None
        segment_lengths.append(remaining)

        grid = np.zeros((self.size, self.size), dtype=int)
        color, idx = 1, 0
        for slen in segment_lengths:
            for _ in range(slen):
                r, c = path[idx]
                grid[r, c] = color
                idx += 1
            color += 1
        return grid

    def generate_full_grid(self):
        """Try up to 200 short DFS attempts (0.5 s each) to get a valid grid."""
        for _ in range(200):
            deadline = time.time() + 0.5
            path = self._find_hamiltonian_path(deadline)
            if path is None:
                continue
            grid = self._segment_path(path)
            if grid is not None:
                return grid
        return None

    # ------------------------------------------------------------------
    # Puzzle extraction and difficulty
    # ------------------------------------------------------------------
    def extract_puzzle(self, solution_grid):
        puzzle = np.zeros_like(solution_grid)
        for color in range(1, self.num_colors + 1):
            for r in range(self.size):
                for c in range(self.size):
                    if solution_grid[r, c] == color:
                        nbrs = sum(
                            1 for dr, dc in ((-1,0),(1,0),(0,-1),(0,1))
                            if 0 <= r+dr < self.size and 0 <= c+dc < self.size
                            and solution_grid[r+dr, c+dc] == color
                        )
                        if nbrs == 1:
                            puzzle[r, c] = color
        return puzzle

    def calculate_difficulty(self, solution_grid):
        bends = 0
        for color in range(1, self.num_colors + 1):
            start = None
            for r in range(self.size):
                for c in range(self.size):
                    if solution_grid[r, c] == color:
                        nbrs = sum(
                            1 for dr, dc in ((-1,0),(1,0),(0,-1),(0,1))
                            if 0 <= r+dr < self.size and 0 <= c+dc < self.size
                            and solution_grid[r+dr, c+dc] == color
                        )
                        if nbrs == 1:
                            start = (r, c)
                            break
                if start:
                    break
            if not start:
                continue
            curr, prev, prev_dir = start, None, None
            visited_trace = {start}
            while True:
                r, c = curr
                nxt, cdir = None, None
                for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                    nr, nc = r+dr, c+dc
                    if (0 <= nr < self.size and 0 <= nc < self.size
                            and solution_grid[nr, nc] == color
                            and (nr, nc) != prev
                            and (nr, nc) not in visited_trace):
                        nxt, cdir = (nr, nc), (dr, dc)
                        break
                if not nxt:
                    break
                if prev_dir is not None and cdir != prev_dir:
                    bends += 1
                visited_trace.add(nxt)
                prev, curr, prev_dir = curr, nxt, cdir
        return self.size * self.num_colors * max(bends, 1)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def generate(self):
        for _ in range(30):
            solution_grid = self.generate_full_grid()
            if solution_grid is None:
                continue
            puzzle = self.extract_puzzle(solution_grid)
            if all(np.sum(puzzle == c) == 2 for c in range(1, self.num_colors + 1)):
                return puzzle, solution_grid, self.calculate_difficulty(solution_grid)
        return None, None, 0
