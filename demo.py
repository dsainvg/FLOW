from flow_utils import load_flow_dataset, visualize_flow
from solver import FlowSolver
import numpy as np

def run_demo():
    print("Loading Flow Dataset (Small)...")
    puzzles, solutions, meta = load_flow_dataset('outputs/flow_small.npz')

    print(f"Loaded {len(puzzles)} puzzles.\n")

    for i in range(len(puzzles)):
        size = meta[i]['size']
        colors = meta[i]['num_colors']
        difficulty = meta[i]['difficulty_score']

        print(f"=== Puzzle {i+1} ===")
        print(f"Size: {size}x{size}")
        print(f"Colors: {colors}")
        print(f"Difficulty Score: {difficulty}")
        print("\nStarting Puzzle Grid:")

        # Slicing because it might be zero-padded to a larger size if batched
        actual_puzzle = puzzles[i][:size, :size]
        actual_solution = solutions[i][:size, :size]

        visualize_flow(actual_puzzle)

        print("\nOriginal Solution Grid (from Generator):")
        visualize_flow(actual_solution)

        print("\nSolving using FlowSolver...")
        solver = FlowSolver(actual_puzzle)
        found_solutions = solver.solve()

        if found_solutions:
            print(f"Solver found {len(found_solutions)} solution(s).")
            print("Solver's Solution Grid:")
            visualize_flow(found_solutions[0])

            # Check if it matches exactly (note: multiple solutions may be isomorphic,
            # but we designed puzzles to have exactly one)
            if np.array_equal(found_solutions[0], actual_solution):
                print("-> Solver solution EXACTLY MATCHES Generator solution! ✅")
            else:
                print("-> Solver solution differs from Generator solution. ❌")
        else:
            print("Solver failed to find a solution. ❌")

        print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    run_demo()
