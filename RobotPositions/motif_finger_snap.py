''' Motif: Rhythmic Finger Snap (beat-locked 113.3 BPM, 8 beats = 4.24s, snap-and-hold) '''
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

    # 8 beats with crisp snaps & beat bounces:
    # 0.30s -> 0.53s: Right arm snap up + hold
    # 0.85s -> 1.06s: Snare snap + head nod
    # 1.40s -> 1.59s: Left arm snap up + hold
    # 1.90s -> 2.12s: Snare snap + head nod
    # 2.45s -> 3.18s: Double snap Right + hold
    # 3.50s -> 4.24s: Both arms groove bounce ready
    t_grid = [0.30, 0.53, 0.85, 1.06, 1.40, 1.59, 1.90, 2.12, 2.45, 3.18, 3.50, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        # HeadPitch (nods on every beat)
        [-5.0 * DEG, 7.0 * DEG, -5.0 * DEG, 8.0 * DEG, -5.0 * DEG, 7.0 * DEG, -5.0 * DEG, 8.0 * DEG, -6.0 * DEG, -6.0 * DEG, 6.0 * DEG, 0.0 * DEG],
        # HeadYaw
        [-15.0 * DEG, -15.0 * DEG, -18.0 * DEG, -18.0 * DEG, 15.0 * DEG, 15.0 * DEG, 18.0 * DEG, 18.0 * DEG, -16.0 * DEG, -16.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # LShoulderPitch
        [75.0 * DEG, 75.0 * DEG, 75.0 * DEG, 75.0 * DEG, 38.0 * DEG, 38.0 * DEG, 32.0 * DEG, 32.0 * DEG, 75.0 * DEG, 75.0 * DEG, 68.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [16.0 * DEG, 16.0 * DEG, 16.0 * DEG, 16.0 * DEG, 28.0 * DEG, 28.0 * DEG, 32.0 * DEG, 32.0 * DEG, 16.0 * DEG, 16.0 * DEG, 18.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-60.0 * DEG, -60.0 * DEG, -60.0 * DEG, -60.0 * DEG, -45.0 * DEG, -45.0 * DEG, -40.0 * DEG, -40.0 * DEG, -60.0 * DEG, -60.0 * DEG, -60.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-45.0 * DEG, -45.0 * DEG, -45.0 * DEG, -45.0 * DEG, -82.0 * DEG, -82.0 * DEG, -75.0 * DEG, -75.0 * DEG, -45.0 * DEG, -45.0 * DEG, -55.0 * DEG, -50.0 * DEG],
        # LWristYaw
        [0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, -45.0 * DEG, -45.0 * DEG, -60.0 * DEG, -60.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # LHand (pop snap!)
        [0.1, 0.1, 0.1, 0.1, 0.9, 0.1, 0.9, 0.1, 0.2, 0.2, 0.4, 0.3],
        # RShoulderPitch
        [38.0 * DEG, 38.0 * DEG, 32.0 * DEG, 32.0 * DEG, 75.0 * DEG, 75.0 * DEG, 75.0 * DEG, 75.0 * DEG, 35.0 * DEG, 35.0 * DEG, 68.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-28.0 * DEG, -28.0 * DEG, -32.0 * DEG, -32.0 * DEG, -16.0 * DEG, -16.0 * DEG, -16.0 * DEG, -16.0 * DEG, -30.0 * DEG, -30.0 * DEG, -18.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [45.0 * DEG, 45.0 * DEG, 40.0 * DEG, 40.0 * DEG, 60.0 * DEG, 60.0 * DEG, 60.0 * DEG, 60.0 * DEG, 42.0 * DEG, 42.0 * DEG, 60.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [82.0 * DEG, 82.0 * DEG, 75.0 * DEG, 75.0 * DEG, 45.0 * DEG, 45.0 * DEG, 45.0 * DEG, 45.0 * DEG, 80.0 * DEG, 80.0 * DEG, 55.0 * DEG, 50.0 * DEG],
        # RWristYaw
        [45.0 * DEG, 45.0 * DEG, 60.0 * DEG, 60.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 55.0 * DEG, 55.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        # RHand (pop snap!)
        [0.9, 0.1, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1, 0.9, 0.1, 0.4, 0.3],
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
