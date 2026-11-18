''' Motif: Pop Syncopated Claps (beat-locked 113.3 BPM, 4 beats = 2.12s, snap-and-hold) '''
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

    # 4 beats with crisp snare-hit claps (snap on beat, brief hold):
    # 0.35s -> 0.53s: Open wide (Beat 1)
    # 0.85s -> 1.06s: Sharp CLAP + hold (Beat 2 snare!)
    # 1.38s -> 1.59s: Open bounce (Beat 3)
    # 1.88s -> 2.12s: Sharp CLAP + hold (Beat 4 snare!)
    t_grid = [0.35, 0.53, 0.85, 1.06, 1.38, 1.59, 1.88, 2.12]
    times = [list(t_grid) for _ in names]

    keys = [
        [-6.0 * DEG, -6.0 * DEG, 10.0 * DEG, 10.0 * DEG, -6.0 * DEG, -6.0 * DEG, 12.0 * DEG, 8.0 * DEG],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        # Left arm:
        [52.0 * DEG, 52.0 * DEG, 35.0 * DEG, 35.0 * DEG, 52.0 * DEG, 52.0 * DEG, 35.0 * DEG, 45.0 * DEG],
        [26.0 * DEG, 26.0 * DEG, 5.0 * DEG, 5.0 * DEG, 26.0 * DEG, 26.0 * DEG, 5.0 * DEG, 12.0 * DEG],
        [-60.0 * DEG, -60.0 * DEG, -30.0 * DEG, -30.0 * DEG, -60.0 * DEG, -60.0 * DEG, -30.0 * DEG, -45.0 * DEG],
        [-38.0 * DEG, -38.0 * DEG, -85.0 * DEG, -85.0 * DEG, -38.0 * DEG, -38.0 * DEG, -85.0 * DEG, -65.0 * DEG],
        [0.0, 0.0, -55.0 * DEG, -55.0 * DEG, 0.0, 0.0, -55.0 * DEG, -30.0 * DEG],
        [0.8, 0.8, 1.0, 1.0, 0.8, 0.8, 1.0, 0.6],
        # Right arm:
        [52.0 * DEG, 52.0 * DEG, 35.0 * DEG, 35.0 * DEG, 52.0 * DEG, 52.0 * DEG, 35.0 * DEG, 45.0 * DEG],
        [-26.0 * DEG, -26.0 * DEG, -5.0 * DEG, -5.0 * DEG, -26.0 * DEG, -26.0 * DEG, -5.0 * DEG, -12.0 * DEG],
        [60.0 * DEG, 60.0 * DEG, 30.0 * DEG, 30.0 * DEG, 60.0 * DEG, 60.0 * DEG, 30.0 * DEG, 45.0 * DEG],
        [38.0 * DEG, 38.0 * DEG, 85.0 * DEG, 85.0 * DEG, 38.0 * DEG, 38.0 * DEG, 85.0 * DEG, 65.0 * DEG],
        [0.0, 0.0, 55.0 * DEG, 55.0 * DEG, 0.0, 0.0, 55.0 * DEG, 30.0 * DEG],
        [0.8, 0.8, 1.0, 1.0, 0.8, 0.8, 1.0, 0.6],
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
