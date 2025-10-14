import time
import requests
import numpy as np


START_P = 1.0
START_I = 0.1
TEST_TIME = 90

ITERATIONS = 3
GRID_SIZE = 3
GRID_RANGE = 2.0

def get_data():

    return d['temp'], d['target'], d['duty_cycle']

def set_pi(p, i):


def test_pi(p, i, duration=TEST_TIME):
    set_pi(p, i)
    time.sleep(5)

    errors = []
    times = []
    temps = []
    prev_temp = None
    
    disturbance_pause_until = 0
    
    print(f"Test time {duration}s...", end='', flush=True)
    start = time.time()
    
    while time.time() - start < duration:
        temp, target, duty = get_data()
        t = time.time() - start
        error = target - temp

        if prev_temp and prev_temp - temp > 5:
            print("!", end='', flush=True)
            disturbance_pause_until = time.time() + 3

        if time.time() > disturbance_pause_until:
            errors.append(error)
            times.append(t)
            temps.append(temp)
            print(".", end='', flush=True)
        else:
            print("-", end='', flush=True)
        
        prev_temp = temp
        time.sleep(3)
    
    print()
    
    if len(errors) < 5:
        return 999999

    itae = np.trapz(np.array(times) * np.abs(errors), times)
    overshoot = max(0, -min(errors))
    score = itae + overshoot * 100
    
    print(f"  Score={score:.1f} (ITAE={itae:.1f}, Overshoot={overshoot:.2f}°C, Meseaure={len(errors)})")
    return score

def tune():

    best_p = START_P
    best_i = START_I
    best_score = 999999
    
    total_tests = ITERATIONS * GRID_SIZE * GRID_SIZE
    current_test = 0
    
    print("=== START TUN PI BetaPowders&Sinterit ===")
    print(f"Itteration: {ITERATIONS}, Grid: {GRID_SIZE}x{GRID_SIZE}")
    print(f"No of test: {total_tests}")

    
    for iteration in range(ITERATIONS):
        print(f"\n Itter {iteration+1}/{ITERATIONS}")
        
        if iteration == 0:
            p_vals = np.linspace(best_p/GRID_RANGE, best_p*GRID_RANGE, GRID_SIZE)
            i_vals = np.linspace(best_i/GRID_RANGE, best_i*GRID_RANGE, GRID_SIZE)
        else:
            range_factor = 1.15
            p_vals = np.linspace(best_p/range_factor, best_p*range_factor, GRID_SIZE)
            i_vals = np.linspace(best_i/range_factor, best_i*range_factor, GRID_SIZE)

        for p in p_vals:
            for i in i_vals:
                current_test += 1
                print(f"\n[{current_test}/{total_tests}] P={p:.3f}, I={i:.3f}")
                score = test_pi(p, i)
                
                if score < best_score:
                    best_score = score
                    best_p = p
                    best_i = i
    
    print(f"\n\n=== Top ===")
    print(f"Kp = {best_p:.4f}")
    print(f"Ki = {best_i:.4f}")
    print(f"Score = {best_score:.1f}")
    
    set_pi(best_p, best_i)
    print("\n✓ Near")

if __name__ == "__main__":
    tune()