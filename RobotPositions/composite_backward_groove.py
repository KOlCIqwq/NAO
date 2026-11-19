''' Composite Layered Move: Moonwalk backward return (-0.12, 0.0) + relaxed beat-locked shoulder groove '''
import sys
from naoqi import ALProxy

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("Could not create proxy to ALMotion: %s" % e)
        return

    motion.setMoveArmsEnabled(False, False)

    # 1. Exact inverse 12cm backward step returning to center
    motion.post.moveTo(-0.12, 0.0, 0.0)

    # 2. Beat-locked relaxed shoulder groove & head nod (4.24s, 8 beats)
    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"
    ]
    t_grid = [0.35, 0.53, 1.06, 1.59, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        [-0.08, 0.10, -0.08, -0.08, 0.10, -0.08, -0.08, 0.08, 0.0],
        [-0.14, -0.14, 0.14, 0.14, 0.0, -0.14, -0.14, 0.08, 0.0],
        [1.26, 1.26, 1.12, 1.12, 1.24, 1.14, 1.14, 1.20, 1.22],
        [0.18, 0.18, 0.28, 0.28, 0.22, 0.28, 0.28, 0.24, 0.24],
        [-0.90, -0.90, -1.18, -1.18, -1.05, -1.16, -1.16, -1.05, -1.05],
        [-0.82, -0.82, -1.08, -1.08, -0.88, -1.04, -1.04, -0.88, -0.85],
        [0.10, 0.10, -0.15, -0.15, 0.0, -0.12, -0.12, 0.0, 0.0],
        [1.12, 1.12, 1.26, 1.26, 1.24, 1.26, 1.26, 1.20, 1.22],
        [-0.28, -0.28, -0.18, -0.18, -0.22, -0.18, -0.18, -0.24, -0.24],
        [1.18, 1.18, 0.90, 0.90, 1.05, 0.92, 0.92, 1.05, 1.05],
        [1.08, 1.08, 0.82, 0.82, 0.88, 0.84, 0.84, 0.88, 0.85],
        [-0.10, -0.10, 0.15, 0.15, 0.0, 0.12, 0.12, 0.0, 0.0],
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
