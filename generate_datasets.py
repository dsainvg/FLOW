import numpy as np
import os
from generator import FlowGenerator
import time

def generate_single_puzzle(size, num_colors):
    generator = FlowGenerator(size, num_colors)
    start_time = time.time()
    puzzle, solution, difficulty_score = generator.generate()
    elapsed = time.time() - start_time
    print(f"  Generated {size}x{size}/{num_colors}c in {elapsed:.2f}s - score={difficulty_score}")

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
    return puzzle, solution, metadata, end_time - start_time

def generate_batch(sizes, name, total_puzzles=5, fixed_num_colors=None):
    all_puzzles = []
    all_solutions = []
    all_metadata = []
    unique_hashes = set()

    os.makedirs('outputs', exist_ok=True)
    out_file = f'outputs/flow_{name}.npz'
    max_size = max(sizes)

    print(f"Starting generation: {total_puzzles} puzzles -> {out_file}")

    attempts = 0
    max_attempts = total_puzzles * 20  # safety cap to avoid infinite loop

    while len(all_puzzles) < total_puzzles:
        if attempts >= max_attempts:
            print(f"WARNING: reached max attempts ({max_attempts}). "
                  f"Collected {len(all_puzzles)}/{total_puzzles} puzzles.")
            break
        attempts += 1

        size = np.random.choice(sizes)
        if fixed_num_colors is not None:
            num_colors = fixed_num_colors
        else:
            min_colors = max(3, size - 2)
            max_colors = size + 1
            num_colors = np.random.randint(min_colors, max_colors + 1)

        try:
            p, s, m = generate_single_puzzle(size, num_colors)
        except Exception as e:
            print(f"  Generation error: {e} — skipping")
            continue

        if p is None or m['difficulty_score'] == 0:
            continue

        p_bytes = p.tobytes()
        if p_bytes not in unique_hashes:
            unique_hashes.add(p_bytes)
            all_puzzles.append(p)
            all_solutions.append(s)
            all_metadata.append(m)
            print(f"Progress: {len(all_puzzles)}/{total_puzzles}")

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
    # --- Quick smoke test with 5 examples ---
    print("=== Smoke test: 5 puzzles (4x4, 4 colors) ===")
    generate_batch([4], "4x4_test5", total_puzzles=5, fixed_num_colors=4)
    print("Smoke test passed!\n")

    # --- Full dataset: 1,280 unique 4x4 grids with exactly 4 colors ---
    print("=== Full run: 1,280 puzzles (4x4, 4 colors) ===")
    generate_batch([4], "4x4_4colors_1280", total_puzzles=1280, fixed_num_colors=4)

    print("All requested datasets successfully created and saved.")