''' Motif: Pop Arm Roll & Wave Groove (beat-locked 113.3 BPM, 8 beats = 4.24s) '''
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

    # Every-beat groove (0.53s) with wave ripple & beat holds:
    t_grid = [0.53, 1.06, 1.59, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        # HeadPitch (nods on every beat)
        [-6.0 * DEG, 6.0 * DEG, -6.0 * DEG, 8.0 * DEG, -6.0 * DEG, 6.0 * DEG, -6.0 * DEG, 4.0 * DEG],
        # HeadYaw
        [15.0 * DEG, 18.0 * DEG, 0.0 * DEG, 0.0 * DEG, -15.0 * DEG, -18.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # LShoulderPitch
        [42.0 * DEG, 38.0 * DEG, 62.0 * DEG, 62.0 * DEG, 48.0 * DEG, 42.0 * DEG, 65.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [24.0 * DEG, 28.0 * DEG, 16.0 * DEG, 16.0 * DEG, 22.0 * DEG, 26.0 * DEG, 18.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-35.0 * DEG, -40.0 * DEG, -70.0 * DEG, -70.0 * DEG, -45.0 * DEG, -35.0 * DEG, -65.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-82.0 * DEG, -75.0 * DEG, -45.0 * DEG, -45.0 * DEG, -80.0 * DEG, -75.0 * DEG, -55.0 * DEG, -50.0 * DEG],
        # LWristYaw
        [-35.0 * DEG, -40.0 * DEG, 20.0 * DEG, 20.0 * DEG, -30.0 * DEG, -35.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # LHand
        [0.7, 0.7, 0.3, 0.3, 0.7, 0.7, 0.4, 0.4],
        # RShoulderPitch
        [48.0 * DEG, 42.0 * DEG, 62.0 * DEG, 62.0 * DEG, 42.0 * DEG, 38.0 * DEG, 65.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-22.0 * DEG, -26.0 * DEG, -16.0 * DEG, -16.0 * DEG, -24.0 * DEG, -28.0 * DEG, -18.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [45.0 * DEG, 35.0 * DEG, 70.0 * DEG, 70.0 * DEG, 35.0 * DEG, 40.0 * DEG, 65.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [80.0 * DEG, 75.0 * DEG, 45.0 * DEG, 45.0 * DEG, 82.0 * DEG, 75.0 * DEG, 55.0 * DEG, 50.0 * DEG],
        # RWristYaw
        [30.0 * DEG, 35.0 * DEG, -20.0 * DEG, -20.0 * DEG, 35.0 * DEG, 40.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # RHand
        [0.7, 0.7, 0.3, 0.3, 0.7, 0.7, 0.4, 0.4],
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
