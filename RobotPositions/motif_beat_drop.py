''' Motif: 1-Bar High-Energy Drop & Freeze (beat-locked 113.3 BPM, 4 beats = 2.12s) '''
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

    # 4 beats:
    # 0.30s -> 0.53s -> 1.06s: Sharp punch out/up on Beat 1, FREEZE/HOLD through Beat 2
    # 1.38s -> 1.59s: Sharp chest snap + head nod on Beat 3
    # 2.12s: Groove-ready settle on Beat 4
    t_grid = [0.30, 0.53, 1.06, 1.38, 1.59, 2.12]
    times = [list(t_grid) for _ in names]

    keys = [
        # HeadPitch
        [-10.0 * DEG, -10.0 * DEG, -10.0 * DEG, 10.0 * DEG, 10.0 * DEG, 0.0 * DEG],
        # HeadYaw
        [0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 12.0 * DEG, 12.0 * DEG, 0.0 * DEG],
        # LShoulderPitch (from ~68 deg -> 12 deg punch -> 45 deg chest snap -> 68 deg)
        [12.0 * DEG, 12.0 * DEG, 12.0 * DEG, 45.0 * DEG, 45.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [45.0 * DEG, 45.0 * DEG, 45.0 * DEG, 12.0 * DEG, 12.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-45.0 * DEG, -45.0 * DEG, -45.0 * DEG, -35.0 * DEG, -35.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-20.0 * DEG, -20.0 * DEG, -20.0 * DEG, -78.0 * DEG, -78.0 * DEG, -50.0 * DEG],
        # LWristYaw
        [-35.0 * DEG, -35.0 * DEG, -35.0 * DEG, 15.0 * DEG, 15.0 * DEG, 0.0 * DEG],
        # LHand
        [0.9, 0.9, 0.9, 0.2, 0.2, 0.4],
        # RShoulderPitch
        [12.0 * DEG, 12.0 * DEG, 12.0 * DEG, 45.0 * DEG, 45.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-45.0 * DEG, -45.0 * DEG, -45.0 * DEG, -12.0 * DEG, -12.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [45.0 * DEG, 45.0 * DEG, 45.0 * DEG, 35.0 * DEG, 35.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [20.0 * DEG, 20.0 * DEG, 20.0 * DEG, 78.0 * DEG, 78.0 * DEG, 50.0 * DEG],
        # RWristYaw
        [35.0 * DEG, 35.0 * DEG, 35.0 * DEG, -15.0 * DEG, -15.0 * DEG, 0.0 * DEG],
        # RHand
        [0.9, 0.9, 0.9, 0.2, 0.2, 0.4],
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
