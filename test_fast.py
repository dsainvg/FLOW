from generator import FlowGenerator
import time
start = time.time()
gen = FlowGenerator(4, 3)
res = gen.generate()
print(f"4x4 Time taken: {time.time() - start:.3f}s")
if res[0] is not None:
    print("Found 4x4!")
