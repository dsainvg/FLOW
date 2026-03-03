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

    # Sequential generation is safer if generator is stuck on large grids
    # For large datasets, using multiprocessing Pool is much faster
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    results = pool.map(generate_single_puzzle, tasks)
    pool.close()
    pool.join()

    for p, s, m in results:
        # Ignore dummy fallback puzzles (difficulty 0)
        if m['difficulty_score'] > 0:
            all_puzzles.append(p)
            all_solutions.append(s)
            all_metadata.append(m)

    if not all_puzzles:
        print(f"No valid puzzles generated for batch {name}. Skipping save.")
        return

    max_size = max(sizes)
    padded_puzzles = np.zeros((len(all_puzzles), max_size, max_size), dtype=int)
    padded_solutions = np.zeros((len(all_solutions), max_size, max_size), dtype=int)

    for i, (p, s) in enumerate(zip(all_puzzles, all_solutions)):
        curr_size = p.shape[0]
        padded_puzzles[i, :curr_size, :curr_size] = p
        padded_solutions[i, :curr_size, :curr_size] = s

    os.makedirs('outputs', exist_ok=True)
    out_file = f'outputs/flow_{name}.npz'
    np.savez_compressed(
        out_file,
        puzzles=padded_puzzles,
        solutions=padded_solutions,
        metadata=np.array(all_metadata, dtype=object)
    )
    print(f"Saved batch {name} to {out_file} with {len(all_puzzles)} puzzles.")

if __name__ == "__main__":
    print("Starting Massive Dataset Generation...")
    # Generate 1000 puzzles for small sizes to test the massive generation framework
    # Note: 10,000 per size would take many hours. Doing 1,000 to demonstrate
    # it can reliably output large `.npz` files and use multiprocessing.
    generate_batch([5, 6, 7], "small_massive", num_puzzles_per_size=1000)

    # Medium sizes (8x8 to 10x10)
    generate_batch([8, 9, 10], "medium_massive", num_puzzles_per_size=500)

    print("All massive batches generated.")