import numpy as np
import os
from generator import FlowGenerator
import time
import multiprocessing

def generate_single_puzzle(args):
    size, num_colors = args
    print(f"Generating puzzle size {size}x{size} with {num_colors} colors...")
    generator = FlowGenerator(size, num_colors)
    start_time = time.time()
    puzzle, solution, difficulty_score = generator.generate()
    end_time = time.time()
    print(f"Generated {size}x{size} in {end_time - start_time:.2f}s - Difficulty: {difficulty_score}")

    base_score = size * num_colors
    if difficulty_score < base_score * 2:
        tier = "Easy"
    elif difficulty_score < base_score * 3:
        tier = "Medium"
    elif difficulty_score < base_score * 4:
        tier = "Hard"
    else:
        tier = "Extreme"

    metadata = {
        'size': size,
        'num_colors': num_colors,
        'difficulty': tier,
        'difficulty_score': difficulty_score,
        'steps_to_solve': 0
    }
    return puzzle, solution, metadata

def generate_batch(sizes, name, num_puzzles_per_size=5):
    all_puzzles = []
    all_solutions = []
    all_metadata = []

    tasks = []
    for size in sizes:
        min_colors = max(3, size - 2)
        max_colors = size + 1
        for _ in range(num_puzzles_per_size):
            num_colors = np.random.randint(min_colors, max_colors + 1)
            tasks.append((size, num_colors))

    print(f"Starting generation for {len(tasks)} puzzles...")

    # We will process in chunks of 500 to save memory and ensure partial results are saved
    chunk_size = 500
    total_valid = 0

    os.makedirs('outputs', exist_ok=True)

    for i in range(0, len(tasks), chunk_size):
        chunk_tasks = tasks[i:i + chunk_size]

        # Parallel generation for speed
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        results = pool.map(generate_single_puzzle, chunk_tasks)
        pool.close()
        pool.join()

        chunk_puzzles = []
        chunk_solutions = []
        chunk_metadata = []

        for p, s, m in results:
            if m['difficulty_score'] > 0:
                chunk_puzzles.append(p)
                chunk_solutions.append(s)
                chunk_metadata.append(m)

        if chunk_puzzles:
            max_size = max(sizes)
            padded_puzzles = np.zeros((len(chunk_puzzles), max_size, max_size), dtype=int)
            padded_solutions = np.zeros((len(chunk_solutions), max_size, max_size), dtype=int)

            for j, (p, s) in enumerate(zip(chunk_puzzles, chunk_solutions)):
                curr_size = p.shape[0]
                padded_puzzles[j, :curr_size, :curr_size] = p
                padded_solutions[j, :curr_size, :curr_size] = s

            out_file = f'outputs/flow_{name}_part{(i//chunk_size)+1}.npz'
            np.savez_compressed(
                out_file,
                puzzles=padded_puzzles,
                solutions=padded_solutions,
                metadata=np.array(chunk_metadata, dtype=object)
            )
            total_valid += len(chunk_puzzles)
            print(f"Saved chunk {(i//chunk_size)+1} to {out_file} with {len(chunk_puzzles)} valid puzzles.")

    print(f"Finished {name}: Total valid puzzles saved = {total_valid}")

if __name__ == "__main__":
    print("Starting Target Dataset Generation: 4x4 (1,000) and 9x9 (10,000)...")

    # Generate 1,000 4x4 grids
    generate_batch([4], "4x4", num_puzzles_per_size=1000)

    # Generate 10,000 9x9 grids
    # 9x9 grids are computationally heavy (NP-Complete solver checks)
    # The timeout mechanism (60s) ensures we skip impossible ones, but getting 10,000
    # will take quite a long time. The chunking mechanism ensures we save every 500.
    generate_batch([9], "9x9", num_puzzles_per_size=10000)

    print("Requested dataset generation queued and saving progressively.")