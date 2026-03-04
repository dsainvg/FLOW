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
        p, s, difficulty_score = gen.generate()
        t1 = time.time()
        elapsed = t1 - t0

        if p is None or difficulty_score == 0:
            print(f"Attempt {attempt}: skipped (no valid puzzle)")
            continue

        p_bytes = p.tobytes()
        if p_bytes in unique_hashes:
            print(f"Attempt {attempt}: duplicate (skipping)")
            continue

        unique_hashes.add(p_bytes)
        puzzles.append(p)
        solutions.append(s)
        metadata.append({'size': size, 'num_colors': num_colors, 'difficulty_score': difficulty_score})
        times.append(elapsed)

        if len(puzzles) % 100 == 0 or len(puzzles) == total:
            avg = np.mean(times)
            print(f"Generated {len(puzzles)}/{total} — last={elapsed:.3f}s avg={avg:.3f}s")

    total_time = time.time() - start_all

    # Save padded arrays
    max_size = size
    padded_puzzles = np.zeros((len(puzzles), max_size, max_size), dtype=int)
    padded_solutions = np.zeros((len(solutions), max_size, max_size), dtype=int)
    for i, (p, s) in enumerate(zip(puzzles, solutions)):
        padded_puzzles[i, :p.shape[0], :p.shape[1]] = p
        padded_solutions[i, :s.shape[0], :s.shape[1]] = s

    out_file = 'outputs/flow_4x4_1280.npz'
    np.savez_compressed(out_file, puzzles=padded_puzzles, solutions=padded_solutions, metadata=np.array(metadata, dtype=object))
    np.save('outputs/flow_4x4_1280_times.npy', np.array(times))

    print('\nGeneration complete')
    print(f"Total generated: {len(puzzles)}")
    print(f"Total attempts: {attempt}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Avg per puzzle: {np.mean(times):.4f}s")
    print(f"Median per puzzle: {np.median(times):.4f}s")
    print(f"Min per puzzle: {np.min(times):.4f}s")
    print(f"Max per puzzle: {np.max(times):.4f}s")
    print(f"Saved: {out_file}")
    print("Times saved: outputs/flow_4x4_1280_times.npy")

if __name__ == '__main__':
    main()
