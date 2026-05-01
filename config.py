import os
# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
# Default settings
DEFAULT_DURATION = 10  # Seconds
DEFAULT_RUNS = 1
DEFAULT_MONITOR_INTERVAL = 0.5  # Seconds
THREAD_COUNT = os.cpu_count() or 1
# Scoring Weights
SCORING_WEIGHTS = {
    "cpu": 0.35,
    "memory": 0.25,
    "disk": 0.20,
    "gpu": 0.20
}
# Ensure results directory exists
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)
