''' Composite Layered Move: Diagonal-left step (0.08, 0.08) + relaxed beat-locked shoulder groove '''
import sys
from naoqi import ALProxy

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("Could not create proxy to ALMotion: %s" % e)
        return

    # Disable arms in locomotion solver so upper-body groove runs concurrently with walking
    motion.setMoveArmsEnabled(False, False)

    # 1. Start non-blocking visible diagonal step left
    motion.post.moveTo(0.08, 0.08, 0.0)

    # 2. Concurrently execute beat-locked relaxed shoulder bounce & head nod (4.24s, 8 beats)
    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"
    ]
    t_grid = [0.35, 0.53, 1.06, 1.59, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        [-0.08, 0.10, -0.08, -0.08, 0.10, -0.08, -0.08, 0.08, 0.0],
        [0.18, 0.18, -0.15, -0.15, 0.0, 0.18, 0.18, -0.08, 0.0],
        [1.24, 1.24, 1.08, 1.08, 1.24, 1.12, 1.12, 1.22, 1.22],
        [0.24, 0.24, 0.30, 0.30, 0.24, 0.28, 0.28, 0.24, 0.24],
        [-1.08, -1.08, -1.25, -1.25, -1.08, -1.20, -1.20, -1.05, -1.05],
        [-0.80, -0.80, -1.05, -1.05, -0.80, -1.00, -1.00, -0.85, -0.85],
        [-0.18, -0.18, 0.12, 0.12, -0.12, 0.10, 0.10, 0.0, 0.0],
        [1.24, 1.24, 1.08, 1.08, 1.24, 1.12, 1.12, 1.22, 1.22],
        [-0.24, -0.24, -0.30, -0.30, -0.24, -0.28, -0.28, -0.24, -0.24],
        [1.08, 1.08, 1.25, 1.25, 1.08, 1.20, 1.20, 1.05, 1.05],
        [0.80, 0.80, 1.05, 1.05, 0.80, 1.00, 1.00, 0.85, 0.85],
        [0.18, 0.18, -0.12, -0.12, 0.12, -0.10, -0.10, 0.0, 0.0],
    ]

    try:
        motion.angleInterpolation(names, keys, times, True)
    except Exception as e:
        print("Arm interpolation error: %s" % e)

    motion.waitUntilMoveIsFinished()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9559
    main(ip, port)
