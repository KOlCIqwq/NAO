''' Motif: Rick Astley Signature Sway (beat-locked 113.3 BPM, 8 beats = 4.24s, snap-and-hold) '''
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

    # 8 beats at 113.3 BPM (0.53s/beat) with snap-and-hold on musical stops:
    # 0.30s -> 0.53s: Hit LEFT sway + hold (Beat 1)
    # 1.06s -> 1.59s: Accent sway + dramatic STOP/HOLD ("Never gonna give you up [stop]") (Beats 2-3)
    # 2.12s -> 2.38s: Drop/transition beat (Beat 4)
    # 2.65s -> 3.18s: Hit RIGHT sway + dramatic STOP/HOLD ("never gonna let you down [stop]") (Beats 5-6)
    # 3.71s -> 4.24s: Bounce center-left groove ready (Beats 7-8)
    t_grid = [0.30, 0.53, 1.06, 1.59, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        # HeadPitch (nods on every beat)
        [-6.0 * DEG, 6.0 * DEG, -10.0 * DEG, -10.0 * DEG, 8.0 * DEG, -10.0 * DEG, -10.0 * DEG, 8.0 * DEG, -4.0 * DEG],
        # HeadYaw (follows sway, holds on stops)
        [18.0 * DEG, 20.0 * DEG, 22.0 * DEG, 22.0 * DEG, 0.0 * DEG, -22.0 * DEG, -22.0 * DEG, 12.0 * DEG, 0.0 * DEG],
        # LShoulderPitch
        [52.0 * DEG, 52.0 * DEG, 45.0 * DEG, 45.0 * DEG, 72.0 * DEG, 82.0 * DEG, 82.0 * DEG, 58.0 * DEG, 68.0 * DEG],
        # LShoulderRoll
        [38.0 * DEG, 38.0 * DEG, 42.0 * DEG, 42.0 * DEG, 16.0 * DEG, 6.0 * DEG, 6.0 * DEG, 28.0 * DEG, 16.0 * DEG],
        # LElbowYaw
        [-75.0 * DEG, -75.0 * DEG, -80.0 * DEG, -80.0 * DEG, -55.0 * DEG, -30.0 * DEG, -30.0 * DEG, -68.0 * DEG, -60.0 * DEG],
        # LElbowRoll
        [-88.0 * DEG, -88.0 * DEG, -85.0 * DEG, -85.0 * DEG, -65.0 * DEG, -80.0 * DEG, -80.0 * DEG, -75.0 * DEG, -55.0 * DEG],
        # LWristYaw
        [-35.0 * DEG, -35.0 * DEG, -40.0 * DEG, -40.0 * DEG, 0.0 * DEG, 25.0 * DEG, 25.0 * DEG, -20.0 * DEG, 0.0 * DEG],
        # LHand
        [0.6, 0.4, 0.7, 0.7, 0.3, 0.5, 0.5, 0.6, 0.4],
        # RShoulderPitch
        [82.0 * DEG, 82.0 * DEG, 85.0 * DEG, 85.0 * DEG, 72.0 * DEG, 45.0 * DEG, 45.0 * DEG, 70.0 * DEG, 68.0 * DEG],
        # RShoulderRoll
        [-6.0 * DEG, -6.0 * DEG, -5.0 * DEG, -5.0 * DEG, -16.0 * DEG, -42.0 * DEG, -42.0 * DEG, -18.0 * DEG, -16.0 * DEG],
        # RElbowYaw
        [30.0 * DEG, 30.0 * DEG, 25.0 * DEG, 25.0 * DEG, 55.0 * DEG, 80.0 * DEG, 80.0 * DEG, 55.0 * DEG, 60.0 * DEG],
        # RElbowRoll
        [80.0 * DEG, 80.0 * DEG, 82.0 * DEG, 82.0 * DEG, 65.0 * DEG, 85.0 * DEG, 85.0 * DEG, 65.0 * DEG, 55.0 * DEG],
        # RWristYaw
        [-25.0 * DEG, -25.0 * DEG, -25.0 * DEG, -25.0 * DEG, 0.0 * DEG, 40.0 * DEG, 40.0 * DEG, 15.0 * DEG, 0.0 * DEG],
        # RHand
        [0.5, 0.4, 0.5, 0.5, 0.3, 0.7, 0.7, 0.5, 0.4],
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
