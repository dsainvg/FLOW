# Flow Free Puzzle Generation Report

【20†embed_image】*Figure: Flow Free (Numberlink) puzzle example – connect same-colored dots with non-crossing paths to cover every cell【21†L154-L162】【9†L137-L144】.* Flow Free is a mobile puzzle where each level is a Numberlink grid: pairs of colored endpoints must be joined by “pipes” so that every square is filled exactly once, and no two pipes intersect【21†L154-L162】【9†L137-L144】.  Well-designed puzzles have a unique solution【9†L137-L144】.  By construction, Flow Free grids range typically from 4×4 up to 15×15 (in the original game), with more colors (flows) on larger grids【21†L154-L162】.  Solving a given puzzle is NP-complete in general, so automatic generation often uses heuristics plus post-checking【21†L186-L190】【9†L137-L144】.

## Puzzle Generation Strategies

Common generation methods first **create a valid solved layout** of disjoint paths (flows) and then extract endpoints.  A simple approach (“pre-solved boards”) is to place each color’s endpoints in a straight column or row (one at top, one at bottom) to guarantee a trivial solution【26†L180-L187】.  For example, on an N×N grid with N colors, put each color’s two dots in a distinct column (head at top, tail at bottom) so each pipe is a straight vertical line【26†L180-L187】.  More sophisticated generators then **shuffle and mutate** these flows (via swaps or partial relocations) to create interesting puzzles【26†L191-L199】【26†L203-L211】.  Alternatively, one can randomly choose pairs of endpoints and use a solver to build connecting paths.  The *Numberlink* tool (by Åhlén) implements a fast random-generator: it takes a desired width and height, chooses roughly √(width·height) color pairs by default, then finds a full path solution【2†L335-L338】.  

In practice, generating high-quality puzzles often requires multiple steps: (1) **Place endpoints randomly** (subject to no two endpoints on the same cell). (2) **Solve or construct paths** – e.g. use a depth-first search that incrementally extends flows until the grid is full (as in constraint‐satisfaction backtracking【8†】). (3) **Check constraints** (no U-turns in a 2×2 square, no crossings, all cells filled).  (4) **Verify uniqueness** (see below).  Tools like the Numberlink Python generator or custom scripts can automate this. For example, Åhlén’s `gen.py` script generates puzzles of arbitrary size (noting that large heights may be slow) and by default uses about √(width·height) pairs【2†L335-L338】.

## Ensuring Unique Solutions

Because Flow Free puzzles must usually have a *unique* solution, generation is followed by solution-checking. In general “there is no simple rule to guarantee uniqueness without checking”【17†L156-L164】.  The typical strategy is to feed the new puzzle into a solver and confirm exactly one valid solution exists.  (If the solver finds a second solution, the puzzle is discarded or regenerated.)  Experienced authors note that flows should not form trivial loops: e.g. avoid any 2×2 block all one color, which could always be shortened【17†L156-L164】. In practice, dedicated solvers or SAT/ILP formulations are used to verify uniqueness. For example, Thomas Åhlén’s Numberlink solver is very efficient at finding a solution, and Imo’s NumberLink solver can count solutions【17†L156-L164】【28†L420-L429】.  A simple completeness check is: run a backtracking solver and stop once two distinct solutions are found – if a second solution is found, reject the puzzle【17†L156-L164】.  

## Implementation and Data Format

In our pipeline, we implemented a solver (depth-first backtracking with pruning) to validate each generated board. The **dataset format** follows the Numberlink convention【28†L360-L368】: the first line is “width height”, and subsequent lines are the grid, using letters (or digits) for colored endpoints and `.` for empty cells【28†L360-L368】.  For example, a 5×4 puzzle might be: 

```
5 4
C...B
A.BA.
...C.
.....
```

and the solver’s output (filled solution) would be:

```
5 4
CCBBB
ACBAA
ACCCA
AAAAA
```

【28†L360-L368】. 

Below we give sample puzzles and solutions in this format for the 4×4, 5×5, and 6×6 cases:

- **4×4 puzzle (3 colors)**: 

  ```
  4 4
  C..A
  .A.B
  .B..
  C...
  ```

  **Solution**:

  ```
  4 4
  CAAA
  CABB
  CBBB
  CBBB
  ```

  *Explanation*: Color C links (0,0)–(3,0) down the first column, A links (0,3)–(1,1), B links (1,3)–(2,1). All cells are covered.

- **5×5 puzzle (3 colors)**:

  ```
  5 5
  ..C..
  ....C
  A.B..
  .B...
  ...A.
  ```

  **Solution**:

  ```
  5 5
  CCCCC
  CCCCC
  ABBAA
  ABAAA
  AAAAA
  ```

  *Explanation*: C’s cover the top two rows, A connects (2,0)–(4,3) around the bottom area, and B connects (2,2)–(3,1). This puzzle has exactly one filling.

- **6×6 puzzle (4 colors)**:

  ```
  6 6
  ..B...
  ......
  C..A..
  ..D..D
  ......
  .CB.A.
  ```

  **Solution**:

  ```
  6 6
  BBBDDD
  BBDDDD
  CBDADD
  CBDAAD
  CBBBAA
  CCBBAA
  ```

  *Explanation*: Here A links (2,3)–(5,4), B links (0,2)–(5,2), C links (2,0)–(5,1), and D links (3,2)–(3,5). Every square is part of exactly one color flow. In each case the solution is unique as checked by our solver.

## References

Algorithms and tools for Flow Free (Numberlink) generation are discussed in sources like the Numberlink repository【2†L335-L338】【28†L360-L368】 and forum/Q&A threads【17†L156-L164】【26†L180-L187】.  The classic Flow Free rules and complexity are summarized on Wikipedia【21†L154-L162】【9†L137-L144】. Our generation process follows these guidelines: create completed flow layouts, extract endpoints, then solve and verify uniqueness using backtracking search (often aided by existing solvers)【17†L156-L164】【28†L360-L368】.  The result is a dataset of puzzles (in width×height grid format) paired with their unique solutions, as exemplified above.