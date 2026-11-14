''' Composite Layered Move: 9-Diagonal_left locomotion + finger_snap arm gestures '''
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
    # dx = 0.03m, dy = 0.02m (smooth subtle stage step)
    motion.post.moveTo(0.03, 0.02, 0.0)

    # 2. Concurrently execute finger snap arm and head gestures
    # Scaled to 4.24s (2 musical bars at 113.3 BPM)
    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"
    ]
    times = [
        [0.8, 2.1, 3.4, 4.2], # HeadPitch
        [0.8, 2.1, 3.4, 4.2], # HeadYaw
        [0.8, 2.1, 3.4, 4.2], # LShoulderPitch
        [0.8, 2.1, 3.4, 4.2], # LShoulderRoll
        [0.8, 2.1, 3.4, 4.2], # LElbowYaw
        [0.8, 2.1, 3.4, 4.2], # LElbowRoll
        [0.8, 2.1, 3.4, 4.2], # LWristYaw
        [0.8, 1.5, 2.1, 3.0, 3.6, 4.2], # LHand
        [0.8, 2.1, 3.4, 4.2], # RShoulderPitch
        [0.8, 2.1, 3.4, 4.2], # RShoulderRoll
        [0.8, 2.1, 3.4, 4.2], # RElbowYaw
        [0.8, 2.1, 3.4, 4.2], # RElbowRoll
        [0.8, 2.1, 3.4, 4.2], # RWristYaw
        [0.8, 1.5, 2.1, 3.0, 3.6, 4.2], # RHand
    ]
    keys = [
        [-0.05, 0.1, -0.05, 0.0],
        [-0.2, 0.2, -0.15, 0.0],
        [1.2, 0.8, 1.2, 1.4],
        [0.25, 0.35, 0.25, 0.18],
        [-1.2, -1.5, -1.2, -1.35],
        [-0.4, -1.4, -0.4, -0.5],
        [-0.5, 0.2, -0.5, 0.0],
        [0.8, 0.0, 0.9, 0.0, 0.8, 0.3],
        [1.2, 0.8, 1.2, 1.4],
        [-0.25, -0.35, -0.25, -0.18],
        [1.2, 1.5, 1.2, 1.35],
        [0.4, 1.4, 0.4, 0.5],
        [0.5, -0.2, 0.5, 0.0],
        [0.8, 0.0, 0.9, 0.0, 0.8, 0.3],
    ]

    try:
        motion.angleInterpolation(names, keys, times, True)
    except Exception as e:
        print("Arm interpolation error: %s" % e)

    # Wait for step to settle cleanly
    motion.waitUntilMoveIsFinished()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9559
    main(ip, port)
