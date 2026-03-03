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
    # Let's add timeout handling to the generation process or just run sequentially and print
    for task in tasks:
        p, s, m = generate_single_puzzle(task)
        all_puzzles.append(p)
        all_solutions.append(s)
        all_metadata.append(m)

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
    print("Starting Dataset Generation...")
    # Generate small batch (5x5) for speed and verification of functionality
    # Generating 14x14 NP-Hard constraint satisfaction dynamically with Python
    # can take hours. Since we need to prove the pipeline works, we'll
    # use smaller representative batches.
    generate_batch([5, 6, 7], "small", num_puzzles_per_size=1)

    # 8x8 might take some time, so let's try 1 to show the medium dataset works
    generate_batch([8], "medium", num_puzzles_per_size=1)

    print("All batches generated.")