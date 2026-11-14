''' Composite Layered Move: 8-Move_backward locomotion + finger_snap arms '''
import sys
from naoqi import ALProxy

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("Could not create proxy to ALMotion: %s" % e)
        return

    # Free arms for concurrent dance
    motion.setMoveArmsEnabled(False, False)

    # 1. Non-blocking backward step (dx = -0.04m returning to center)
    motion.post.moveTo(-0.04, 0.0, 0.0)

    # 2. Concurrently execute finger snap arm and head gestures (4.24s)
    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"
    ]
    times = [
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 1.5, 2.1, 3.0, 3.6, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 2.1, 3.4, 4.2],
        [0.8, 1.5, 2.1, 3.0, 3.6, 4.2],
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

    motion.waitUntilMoveIsFinished()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9559
    main(ip, port)
