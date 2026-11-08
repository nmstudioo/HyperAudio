# limiter reference + runtime checks
- ref.py: numpy float64 reference of the shared limiter. v7 settings: limit(x, nt=16, align=True, guard=1.015) with ref.KB=4.0.
- rt.py: runs an .eel in the NSEEL VM harness (local build at /home/claude/w/vm/harness, not in repo; replace path) and measures 8x true peak (edges trimmed).
- tune.py: detector grid used to choose 16-tap Kaiser(4), 4x phases, guard 1.015.
