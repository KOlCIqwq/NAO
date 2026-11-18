''' Composite Layered Move: 10-Diagonal_right locomotion + beat-locked Astley arm sway '''
import sys
from naoqi import ALProxy

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("Could not create proxy to ALMotion: %s" % e)
        return

    # Disable arms in locomotion solver
    motion.setMoveArmsEnabled(False, False)

    # 1. Non-blocking diagonal step right returning to center
    motion.post.moveTo(-0.03, -0.02, 0.0)

    # 2. Concurrently execute beat-locked Astley arm sway (4.24s, 8 beats at 113.3 BPM)
    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"
    ]
    t_grid = [0.35, 0.53, 1.06, 1.59, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        [-0.08, 0.10, -0.10, -0.10, 0.12, -0.10, -0.10, 0.10, -0.04],
        [-0.32, -0.35, -0.38, -0.38, 0.0, 0.38, 0.38, -0.15, 0.0],
        [1.38, 1.38, 1.43, 1.43, 1.25, 1.05, 1.05, 1.20, 1.18],
        [0.10, 0.10, 0.10, 0.10, 0.28, 0.66, 0.66, 0.32, 0.28],
        [-0.50, -0.50, -0.44, -0.44, -0.95, -1.22, -1.22, -1.05, -1.05],
        [-1.40, -1.40, -1.48, -1.48, -1.10, -1.48, -1.48, -0.95, -0.85],
        [-0.55, -0.55, -0.61, -0.61, 0.0, -0.61, -0.61, 0.0, 0.0],
        [1.05, 1.05, 1.08, 1.08, 1.25, 1.43, 1.43, 1.20, 1.18],
        [-0.62, -0.62, -0.66, -0.66, -0.28, -0.10, -0.10, -0.32, -0.28],
        [1.18, 1.18, 1.22, 1.22, 0.95, 0.44, 0.44, 1.05, 1.05],
        [1.40, 1.40, 1.48, 1.48, 1.10, 1.48, 1.48, 0.95, 0.85],
        [0.55, 0.55, 0.61, 0.61, 0.0, 0.61, 0.61, 0.0, 0.0],
    ]

    try:
        motion.angleInterpolation(names, keys, times, True)
    except Exception as e:
        print("Sway interpolation error: %s" % e)

    motion.waitUntilMoveIsFinished()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9559
    main(ip, port)
