import time
import numpy as np
import os
from generator import FlowGenerator


def main():
    size = 4
    num_colors = 4
    total = 1280

    os.makedirs('outputs', exist_ok=True)

    unique_hashes = set()
    puzzles = []
    solutions = []
    metadata = []
    times = []

    start_all = time.time()
    attempt = 0
    while len(puzzles) < total:
        attempt += 1
        gen = FlowGenerator(size, num_colors)
        t0 = time.time()
        # Prefer fast sequential fill directly to avoid solver timeouts
        solution_grid = gen.generate_full_grid()
        if solution_grid is None:
            # fallback to direct fast fill
            solution_grid = gen._fast_sequential_fill()
        t1 = time.time()
        elapsed = t1 - t0

        if solution_grid is None:
            print(f"Attempt {attempt}: failed to create full solution (retrying)")
            continue

        puzzle = gen.extract_puzzle(solution_grid)

        p_bytes = puzzle.tobytes()
        if p_bytes in unique_hashes:
            print(f"Attempt {attempt}: duplicate (skipping)")
            continue

        unique_hashes.add(p_bytes)
        puzzles.append(puzzle)
        solutions.append(solution_grid)
        metadata.append({'size': size, 'num_colors': num_colors})
        times.append(elapsed)

        if len(puzzles) % 200 == 0 or len(puzzles) == total:
            avg = np.mean(times)
            print(f"Generated {len(puzzles)}/{total} — last={elapsed:.4f}s avg={avg:.4f}s")

    total_time = time.time() - start_all

    # Save padded arrays
    max_size = size
    padded_puzzles = np.zeros((len(puzzles), max_size, max_size), dtype=int)
    padded_solutions = np.zeros((len(solutions), max_size, max_size), dtype=int)
    for i, (p, s) in enumerate(zip(puzzles, solutions)):
        padded_puzzles[i, :p.shape[0], :p.shape[1]] = p
        padded_solutions[i, :s.shape[0], :s.shape[1]] = s

    out_file = 'outputs/flow_4x4_1280_4colors.npz'
    np.savez_compressed(out_file, puzzles=padded_puzzles, solutions=padded_solutions, metadata=np.array(metadata, dtype=object))
    np.save('outputs/flow_4x4_1280_4colors_times.npy', np.array(times))

    print('\nGeneration complete')
    print(f"Total generated: {len(puzzles)}")
    print(f"Total attempts: {attempt}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Avg per puzzle: {np.mean(times):.4f}s")
    print(f"Median per puzzle: {np.median(times):.4f}s")
    print(f"Min per puzzle: {np.min(times):.4f}s")
    print(f"Max per puzzle: {np.max(times):.4f}s")
    print(f"Saved: {out_file}")
    print("Times saved: outputs/flow_4x4_1280_4colors_times.npy")


if __name__ == '__main__':
    main()
