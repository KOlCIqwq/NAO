''' Motif: Sprinkler Dance (quantized to 113.3 BPM, 8 beats = 4.24s) '''
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

    # 8 beats at 113.3 BPM:
    # Beat 1 (0.53s): Tick 1 (Left arm 45 deg left)
    # Beat 2 (1.06s): Tick 2 (Left arm 20 deg left)
    # Beat 3 (1.59s): Tick 3 (Left arm straight center)
    # Beat 4 (2.12s): Tick 4 (Left arm 20 deg right)
    # Beat 6 (3.18s): Smooth sweep back halfway
    # Beat 8 (4.24s): Smooth sweep back to start / StandInit
    times = [
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # HeadPitch
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # HeadYaw
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # LShoulderPitch
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # LShoulderRoll
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # LElbowYaw
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # LElbowRoll
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # LWristYaw
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # LHand
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # RShoulderPitch
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # RShoulderRoll
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # RElbowYaw
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # RElbowRoll
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # RWristYaw
        [0.53, 1.06, 1.59, 2.12, 3.18, 4.24], # RHand
    ]

    keys = [
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], # HeadPitch
        [15.0 * DEG, 10.0 * DEG, 0.0, -10.0 * DEG, 5.0 * DEG, 0.0], # HeadYaw (tracks left hand)
        # Left arm (ticking forward horizontally):
        [0.0, 0.0, 0.0, 0.0, 40.0 * DEG, 80.0 * DEG], # LShoulderPitch
        [40.0 * DEG, 25.0 * DEG, 10.0 * DEG, -5.0 * DEG, 25.0 * DEG, 15.0 * DEG], # LShoulderRoll
        [-80.0 * DEG, -80.0 * DEG, -80.0 * DEG, -80.0 * DEG, -70.0 * DEG, -60.0 * DEG], # LElbowYaw
        [-10.0 * DEG, -10.0 * DEG, -10.0 * DEG, -10.0 * DEG, -30.0 * DEG, -50.0 * DEG], # LElbowRoll
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], # LWristYaw
        [0.8, 0.8, 0.8, 0.8, 0.4, 0.3], # LHand
        # Right arm (behind head):
        [-65.0 * DEG, -65.0 * DEG, -65.0 * DEG, -65.0 * DEG, 0.0 * DEG, 80.0 * DEG], # RShoulderPitch
        [-15.0 * DEG, -15.0 * DEG, -15.0 * DEG, -15.0 * DEG, -20.0 * DEG, -15.0 * DEG], # RShoulderRoll
        [75.0 * DEG, 75.0 * DEG, 75.0 * DEG, 75.0 * DEG, 60.0 * DEG, 60.0 * DEG],   # RElbowYaw
        [88.0 * DEG, 88.0 * DEG, 88.0 * DEG, 88.0 * DEG, 50.0 * DEG, 30.0 * DEG],   # RElbowRoll
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], # RWristYaw
        [0.3, 0.3, 0.3, 0.3, 0.3, 0.3], # RHand
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()

