
# type: ignore
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Initialize figure and axis
fig, ax = plt.subplots(figsize=(8, 4))
ax.set_xlim(0, 10)  # Adjust based on total time units
ax.set_ylim(0, 3)   # Two rows: Sequential (1) and Parallel (2)
ax.set_yticks([1, 2])
ax.set_yticklabels(["Sequential", "Parallel"])
ax.set_xlabel("Time (Units)")
ax.set_title("Sequential vs Parallel Test Execution")

# Create elements
sequential_blocks = []
parallel_blocks = []
time_bar, = ax.plot([], [], color='red', lw=2, label='Time Bar')

# Test case configurations
test_cases = 5  # Number of test cases
test_duration = 2  # Time per test case

# Initialize animation elements
def init():
    global sequential_blocks, parallel_blocks
    sequential_blocks = [ax.add_patch(plt.Rectangle((0, 1.5), 0, 0.4, color="blue")) for _ in range(test_cases)]
    parallel_blocks = [ax.add_patch(plt.Rectangle((0, 2.5), 0, 0.4, color="green")) for _ in range(test_cases)]
    time_bar.set_data([], [])
    return sequential_blocks + parallel_blocks + [time_bar]

# Update function for animation
def update(frame):
    # Sequential execution
    for i in range(test_cases):
        if frame >= i * test_duration and frame < (i + 1) * test_duration:
            sequential_blocks[i].set_width(test_duration)
            sequential_blocks[i].set_xy((i * test_duration, 1.5))
    
    # Parallel execution
    if frame < test_duration:
        for i in range(test_cases):
            parallel_blocks[i].set_width(test_duration)
            parallel_blocks[i].set_xy((frame, 2.5))
    
    # Update time bar
    time_bar.set_data([0, frame], [0.5, 0.5])
    return sequential_blocks + parallel_blocks + [time_bar]

# Create animation
ani = FuncAnimation(fig, update, frames=range(0, test_cases * test_duration + 1),
                    init_func=init, blit=True, interval=500)

plt.legend(loc="upper left")
plt.tight_layout()
plt.show()