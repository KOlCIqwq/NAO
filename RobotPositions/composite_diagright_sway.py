''' Composite Layered Move: Diagonal-right return (-0.08, -0.08) + relaxed beat-locked shoulder counter-sway '''
import sys
from naoqi import ALProxy

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("Could not create proxy to ALMotion: %s" % e)
        return

    motion.setMoveArmsEnabled(False, False)

    # 1. Exact inverse diagonal return to center
    motion.post.moveTo(-0.08, -0.08, 0.0)

    # 2. Beat-locked relaxed shoulder counter-sway (4.24s, 8 beats)
    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"
    ]
    t_grid = [0.35, 0.53, 1.06, 1.59, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        [-0.08, 0.10, -0.08, -0.08, 0.10, -0.08, -0.08, 0.08, 0.0],
        [-0.22, -0.22, -0.25, -0.25, 0.0, 0.25, 0.25, -0.10, 0.0],
        [1.32, 1.32, 1.36, 1.36, 1.24, 1.10, 1.10, 1.22, 1.22],
        [0.14, 0.14, 0.12, 0.12, 0.24, 0.42, 0.42, 0.26, 0.24],
        [-0.75, -0.75, -0.68, -0.68, -1.00, -1.18, -1.18, -1.05, -1.05],
        [-1.15, -1.15, -1.20, -1.20, -0.95, -1.18, -1.18, -0.90, -0.85],
        [-0.25, -0.25, -0.28, -0.28, 0.0, -0.25, -0.25, 0.0, 0.0],
        [1.10, 1.10, 1.12, 1.12, 1.24, 1.36, 1.36, 1.22, 1.22],
        [-0.40, -0.40, -0.42, -0.42, -0.24, -0.12, -0.12, -0.26, -0.24],
        [1.15, 1.15, 1.18, 1.18, 1.00, 0.68, 0.68, 1.05, 1.05],
        [1.15, 1.15, 1.20, 1.20, 0.95, 1.20, 1.20, 0.90, 0.85],
        [0.25, 0.25, 0.28, 0.28, 0.0, 0.25, 0.25, 0.0, 0.0],
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
