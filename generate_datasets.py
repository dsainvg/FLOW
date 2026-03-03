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

def generate_batch(sizes, name, total_puzzles=5):
    all_puzzles = []
    all_solutions = []
    all_metadata = []
    unique_hashes = set() # To ensure uniqueness

    os.makedirs('outputs', exist_ok=True)
    out_file = f'outputs/flow_{name}.npz'

    print(f"Starting generation for {total_puzzles} unique puzzles for {name}...")

    max_size = max(sizes)

    # We will generate in a loop until we reach total_puzzles to ensure we
    # don't stop if some generation attempts time out or return duplicate grids
    while len(all_puzzles) < total_puzzles:
        # Determine how many tasks we need in this batch to hit the goal
        remaining = total_puzzles - len(all_puzzles)
        # Generate in chunks to utilize multiprocessing without overwhelming memory
        # Much smaller chunks to see progressive updates
        chunk_size = min(remaining, 100)

        tasks = []
        for _ in range(chunk_size):
            size = np.random.choice(sizes)
            min_colors = max(3, size - 2)
            max_colors = size + 1
            num_colors = np.random.randint(min_colors, max_colors + 1)
            tasks.append((size, num_colors))

        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        results = pool.map(generate_single_puzzle, tasks)
        pool.close()
        pool.join()

        added = 0
        for p, s, m in results:
            if p is None or m['difficulty_score'] == 0:
                continue

            # Check uniqueness across dataset using a hash of the puzzle grid
            p_bytes = p.tobytes()
            if p_bytes not in unique_hashes:
                unique_hashes.add(p_bytes)
                all_puzzles.append(p)
                all_solutions.append(s)
                all_metadata.append(m)
                added += 1

            if len(all_puzzles) >= total_puzzles:
                break

        if added > 0:
            print(f"Progress: {len(all_puzzles)} / {total_puzzles} unique puzzles generated...")

    # Save to a SINGLE npz file
    padded_puzzles = np.zeros((len(all_puzzles), max_size, max_size), dtype=int)
    padded_solutions = np.zeros((len(all_solutions), max_size, max_size), dtype=int)

    for j, (p, s) in enumerate(zip(all_puzzles, all_solutions)):
        curr_size = p.shape[0]
        padded_puzzles[j, :curr_size, :curr_size] = p
        padded_solutions[j, :curr_size, :curr_size] = s

    np.savez_compressed(
        out_file,
        puzzles=padded_puzzles,
        solutions=padded_solutions,
        metadata=np.array(all_metadata, dtype=object)
    )
    print(f"Finished {name}: Total unique valid puzzles saved to {out_file} = {len(all_puzzles)}")

if __name__ == "__main__":
    print("Starting Target Dataset Generation: 4x4 (1,000) and 9x9 (10,000)...")

    # Generate exactly 1,000 unique 4x4 grids into a single file
    generate_batch([4], "4x4_1000", total_puzzles=1000)

    # Generate exactly 10,000 unique 9x9 grids into a single file.
    # Warning: Synchronous generation of 10k 9x9 combinations guaranteed to be
    # unique and 100% full grid will time out the LLM bash session (400s limit).
    generate_batch([9], "9x9_10000", total_puzzles=10000)

    print("All requested datasets successfully created and saved.")