''' Motif: 80s Disco Point Dance (beat-locked 113.3 BPM, 8 beats = 4.24s, snap-and-hold) '''
import sys
import math
from naoqi import ALProxy

DEG = math.pi / 180.0

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("ALMotion error: %s" % e)
        return

    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"
    ]

    # 8 beats with crisp hits & freeze holds:
    # 0.32s -> 1.06s: Right point HIGH-RIGHT + HOLD!
    # 1.40s -> 2.12s: Right snap DOWN to hip + head nod + HOLD!
    # 2.45s -> 3.18s: Left point HIGH-LEFT + HOLD!
    # 3.55s -> 4.24s: Left snap DOWN to groove-ready pose
    t_grid = [0.42, 1.06, 1.56, 2.12, 2.60, 3.18, 3.68, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        # HeadPitch
        [-16.0 * DEG, -16.0 * DEG, 8.0 * DEG, 6.0 * DEG, -16.0 * DEG, -16.0 * DEG, 8.0 * DEG, 0.0 * DEG],
        # HeadYaw
        [-28.0 * DEG, -28.0 * DEG, 0.0 * DEG, 0.0 * DEG, 28.0 * DEG, 28.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # LShoulderPitch
        [72.0 * DEG, 72.0 * DEG, 70.0 * DEG, 70.0 * DEG, -38.0 * DEG, -38.0 * DEG, 68.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [18.0 * DEG, 18.0 * DEG, 22.0 * DEG, 22.0 * DEG, 42.0 * DEG, 42.0 * DEG, 18.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-60.0 * DEG, -60.0 * DEG, -60.0 * DEG, -60.0 * DEG, -30.0 * DEG, -30.0 * DEG, -65.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-70.0 * DEG, -70.0 * DEG, -82.0 * DEG, -82.0 * DEG, -8.0 * DEG, -8.0 * DEG, -60.0 * DEG, -50.0 * DEG],
        # LWristYaw
        [0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, -45.0 * DEG, -45.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # LHand
        [0.2, 0.2, 0.2, 0.2, 0.95, 0.95, 0.3, 0.4],
        # RShoulderPitch
        [-38.0 * DEG, -38.0 * DEG, 70.0 * DEG, 70.0 * DEG, 72.0 * DEG, 72.0 * DEG, 70.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-42.0 * DEG, -42.0 * DEG, -22.0 * DEG, -22.0 * DEG, -18.0 * DEG, -18.0 * DEG, -18.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [30.0 * DEG, 30.0 * DEG, 60.0 * DEG, 60.0 * DEG, 60.0 * DEG, 60.0 * DEG, 65.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [8.0 * DEG, 8.0 * DEG, 82.0 * DEG, 82.0 * DEG, 70.0 * DEG, 70.0 * DEG, 60.0 * DEG, 50.0 * DEG],
        # RWristYaw
        [45.0 * DEG, 45.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # RHand
        [0.95, 0.95, 0.2, 0.2, 0.2, 0.2, 0.3, 0.4],
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
