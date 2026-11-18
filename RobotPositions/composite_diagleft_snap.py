''' Composite Layered Move: 9-Diagonal_left locomotion + beat-locked finger_snap arm gestures '''
import sys
from naoqi import ALProxy

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("Could not create proxy to ALMotion: %s" % e)
        return

    # Disable arms in locomotion solver so arms can execute dance keyframes freely
    motion.setMoveArmsEnabled(False, False)

    # 1. Start non-blocking diagonal step left in background
    motion.post.moveTo(0.03, 0.02, 0.0)

    # 2. Concurrently execute beat-locked snap & head nod (4.24s, 8 beats at 113.3 BPM)
    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"
    ]
    t_grid = [0.35, 0.53, 1.06, 1.59, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        [-0.08, 0.10, -0.08, -0.08, 0.12, -0.08, -0.08, 0.10, 0.0],
        [-0.22, -0.22, 0.22, 0.22, 0.0, -0.18, -0.18, 0.10, 0.0],
        [1.15, 1.15, 0.80, 0.80, 1.15, 0.85, 0.85, 1.18, 1.18],
        [0.28, 0.28, 0.36, 0.36, 0.26, 0.34, 0.34, 0.28, 0.28],
        [-1.15, -1.15, -1.45, -1.45, -1.15, -1.35, -1.35, -1.05, -1.05],
        [-0.45, -0.45, -1.35, -1.35, -0.45, -1.20, -1.20, -0.85, -0.85],
        [-0.50, -0.50, 0.25, 0.25, -0.40, 0.20, 0.20, 0.0, 0.0],
        [0.85, 0.10, 0.90, 0.90, 0.10, 0.85, 0.10, 0.40, 0.40],
        [1.15, 1.15, 0.80, 0.80, 1.15, 0.85, 0.85, 1.18, 1.18],
        [-0.28, -0.28, -0.36, -0.36, -0.26, -0.34, -0.34, -0.28, -0.28],
        [1.15, 1.15, 1.45, 1.45, 1.15, 1.35, 1.35, 1.05, 1.05],
        [0.45, 0.45, 1.35, 1.35, 0.45, 1.20, 1.20, 0.85, 0.85],
        [0.50, 0.50, -0.25, -0.25, 0.40, -0.20, -0.20, 0.0, 0.0],
        [0.85, 0.10, 0.90, 0.90, 0.10, 0.85, 0.10, 0.40, 0.40],
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
