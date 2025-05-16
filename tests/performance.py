# 100 searches with cache vs without cache

import os
import sys
import time
import random
from contextlib import redirect_stdout


# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from directory import DirectoryTree, Role

NUM_LAYERS = 200
NUM_CATS = 5000
NUM_SEARCHES = 10000
REPEATS = 10
CACHE_SIZES = [0, 100, 500, 1000, 2000, 3000]
CATS_PER_LAYER = NUM_CATS // NUM_LAYERS

# Generate a fixed list of cat names
CAT_NAMES = [f"cat_{i}" for i in range(NUM_CATS)]

# Generate a fixed search pattern: some cats are searched more often
POPULAR_CATS = CAT_NAMES[:40]  # First 10 cats are 'popular'
SEARCH_SEQUENCE = []
for i in range(NUM_SEARCHES):
    if i % 4 == 0:
        SEARCH_SEQUENCE.append(random.choice(POPULAR_CATS))
    else:
        SEARCH_SEQUENCE.append(random.choice(CAT_NAMES))

# Ensure reproducibility
random.seed(42)

def build_tree(cache_size):
    # Use a unique cafe name for each run to avoid pickle conflicts
    cafe_name = f"perf_cafe_{random.randint(0, int(1e9))}"
    tree = DirectoryTree(name=cafe_name, role=Role.ADMIN, cache_size=cache_size)
    # Build NUM_LAYERS deep, each with one cubby, and distribute cats
    current_path = []
    cat_idx = 0
    with open(os.devnull, 'w') as devnull, redirect_stdout(devnull):
        for layer in range(NUM_LAYERS):
            cubby_name = f"cubby_{layer}"
            tree.mkcby(cubby_name)
            tree.walk(cubby_name)
            # Add CATS_PER_LAYER cats in this cubby, suppressing rescue output
            for _ in range(CATS_PER_LAYER):
                if cat_idx < NUM_CATS:
                    tree.rescue(CAT_NAMES[cat_idx], Role.ADMIN)
                    cat_idx += 1
    tree.walk("/")  # Return to root
    return tree, cafe_name

def run_searches(tree):
    hits = 0
    accesses = 0
    cache = getattr(tree, 'cache', None)
    with open(os.devnull, 'w') as devnull, redirect_stdout(devnull):
        if cache:
            orig_get = cache.get
            def counting_get(key):
                nonlocal hits, accesses
                accesses += 1
                result = orig_get(key)
                if result is not None:
                    hits += 1
                return result
            cache.get = counting_get
            # Suppress all output from tree.find by redirecting sys.stdout
            for cat in SEARCH_SEQUENCE:
                tree.find(cat)
            cache.get = orig_get  # Restore
        else:
            for cat in SEARCH_SEQUENCE:
                tree.find(cat)
                accesses += 1  # For no-cache, every access is a miss
    return hits, accesses

def cleanup_cafe(cafe_name):
    pkl_path = os.path.join("cafes", f"{cafe_name}.pkl")
    if os.path.exists(pkl_path):
        os.remove(pkl_path)

def main():
    print("Performance Test: CatFS DirectoryTree Search with/without Cache")
    print(f"Tree: {NUM_LAYERS} layers, {NUM_CATS} cats, {NUM_SEARCHES} searches per run, {REPEATS} repeats per config.")
    print("Cache sizes tested:", CACHE_SIZES)
    print()
    summary = []
    for cache_size in CACHE_SIZES:
        total_time = 0.0
        total_hits = 0
        total_accesses = 0
        print(f"Testing cache_size={cache_size}...")
        for repeat in range(REPEATS):
            tree, cafe_name = build_tree(cache_size)
            start = time.time()
            hits, accesses = run_searches(tree)
            elapsed = time.time() - start
            total_time += elapsed
            total_hits += hits
            total_accesses += accesses
            cleanup_cafe(cafe_name)
            print(f"  Run {repeat+1}: time={elapsed:.3f}s, hits={hits}, accesses={accesses}, hit rate={hits/(accesses or 1):.3f}")
        avg_time = total_time / REPEATS
        avg_hits = total_hits / REPEATS
        avg_accesses = total_accesses / REPEATS
        hit_rate = avg_hits / (avg_accesses or 1)
        print(f"[cache_size={cache_size}] AVG: time={avg_time:.3f}s, hits={avg_hits:.1f}, accesses={avg_accesses:.1f}, hit rate={hit_rate:.3f}")
        print()
        summary.append((cache_size, avg_time, avg_hits, avg_accesses, hit_rate))
    # Print summary table
    print("\nSummary Table (Averages over all runs):")
    print(f"{'Cache Size':>10} | {'Avg Time (s)':>12} | {'Avg Hits':>8} | {'Avg Accesses':>13} | {'Hit Rate':>8}")
    print("-"*63)
    for cache_size, avg_time, avg_hits, avg_accesses, hit_rate in summary:
        print(f"{cache_size:>10} | {avg_time:12.3f} | {avg_hits:8.1f} | {avg_accesses:13.1f} | {hit_rate:8.3f}")
    print()

if __name__ == "__main__":
    main()

