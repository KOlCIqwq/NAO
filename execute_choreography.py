"""
NAO Choreography Executor
Reads the PDDL-generated choreography plan and executes it sequentially on the NAO robot.
Compatible with Python 2.7 (Choregraphe SDK) and Python 3.

Supports synchronized background audio playback (inspired by TheDebuggers / PartyNAO).
"""

import sys
import os
import json
import time
import subprocess

# Add RobotPositions directory to import path
script_dir = os.path.dirname(os.path.abspath(__file__))
positions_dir = os.path.join(script_dir, "RobotPositions")
sys.path.insert(0, positions_dir)

try:
    from naoqi import ALProxy
    _orig_ALProxy = ALProxy
    _proxy_cache = {}
    _SIT_NAMES = ['HeadYaw', 'HeadPitch', 'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw', 'LHand', 'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll', 'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch', 'RAnkleRoll', 'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw', 'RHand']
    _SIT_ANGLES = [-0.0307, -0.0399, 0.8399, 0.3002, -0.4654, -1.1948, -0.0016, 0.296, -0.6059, 0.267, -1.5294, 1.3959, 0.8437, -0.0122, -0.6059, -0.2561, -1.5325, 1.4021, 0.8238, 0.02, 0.8875, -0.3316, 0.5407, 1.255, -0.0077, 0.3348]
    _SITRELAX_ANGLES = [-0.0246, 0.0184, 2.0854, 0.0945, -2.0508, -0.182, -0.95, 0.1384, -0.5215, 0.132, -1.1152, -0.0415, 0.922, 0.0, -0.5215, -0.2209, -1.06, -0.092, 0.922, 0.0, 2.0857, -0.1591, 2.0609, 0.0428, 0.95, 0.1396]
    class _DummyTTS(object):
        def say(self, *args, **kwargs):
            pass
    class _FastPostureProxy(object):
        def __init__(self, real_proxy, motion_proxy=None):
            self._real = real_proxy
            self._motion = motion_proxy
        def goToPosture(self, postureName, speed):
            # In simulated NAO (Choregraphe), the default IK solver for Sit & SitRelax
            # collides with the ground plane, causing left tipping and 30s timeout freezes.
            # Using verified direct joint interpolation transitions in 2.5s smoothly with 100% balance.
            if self._motion is not None:
                if postureName == "Sit":
                    self._motion.angleInterpolation(_SIT_NAMES, _SIT_ANGLES, 2.5, True)
                    return True
                elif postureName == "SitRelax":
                    self._motion.angleInterpolation(_SIT_NAMES, _SITRELAX_ANGLES, 2.5, True)
                    return True
                elif postureName in ["Stand", "StandInit"]:
                    # In simulated NAO, standing directly from SitRelax causes feet to slip outward.
                    # Tucking knees and feet into Sit first gives stable ground support so NAO rises cleanly.
                    try:
                        curr = self._real.getPosture()
                        if curr in ["SitRelax", "Sitting", "Unknown"]:
                            self._motion.angleInterpolation(_SIT_NAMES, _SIT_ANGLES, 1.8, True)
                    except Exception:
                        pass
                    return self._real.goToPosture("StandInit", 0.9)
            return self._real.goToPosture(postureName, max(0.95, float(speed)))
        def __getattr__(self, name):
            return getattr(self._real, name)
    def _cached_ALProxy(name, ip, port):
        if name == "ALTextToSpeech":
            return _DummyTTS()
        key = (name, ip, port)
        if key not in _proxy_cache:
            p = _orig_ALProxy(name, ip, port)
            if name == "ALRobotPosture":
                m = _cached_ALProxy("ALMotion", ip, port)
                p = _FastPostureProxy(p, m)
            _proxy_cache[key] = p
        return _proxy_cache[key]
    # Patch naoqi.ALProxy so imported move modules reuse existing connections
    import naoqi
    naoqi.ALProxy = _cached_ALProxy
except ImportError:
    ALProxy = None
    _orig_ALProxy = None

# Monkey-patch time.sleep to eliminate 1-second dead-stop freezes between moves
_orig_sleep = time.sleep
def _fluid_sleep(secs):
    # Eliminate pauses (>= 0.1s) from move files to keep choreography continuous and fluid
    if secs >= 0.1:
        return
    _orig_sleep(min(secs, 0.02))
time.sleep = _fluid_sleep

def start_music(audio_path):
    """Launches non-blocking background music player."""
    if not audio_path or not os.path.exists(audio_path):
        return None
    print("Starting background music: {}".format(audio_path))
    try:
        if sys.platform.startswith("win"):
            cmd = 'powershell -NoProfile -Command "$p = New-Object -ComObject wmplayer.ocx; $p.openPlayer(\'{}\')"'.format(os.path.abspath(audio_path).replace("\\", "/"))
            return subprocess.Popen(cmd, shell=True)
        else:
            player = "mpg123" if os.system("which mpg123 > /dev/null 2>&1") == 0 else "afplay"
            return subprocess.Popen([player, audio_path])
    except Exception as e:
        print("Could not start audio playback: {}".format(e))
        return None

def stop_music(proc):
    """Terminates background music playback cleanly."""
    if proc is not None:
        try:
            proc.terminate()
        except Exception:
            pass

def load_plan(plan_file="choreography_plan.json"):
    plan_path = os.path.join(script_dir, plan_file)
    if not os.path.exists(plan_path):
        print("Plan file not found. Running nao_planner to generate one...")
        import nao_planner
        nao_planner.generate_full_choreography()

    with open(plan_path, "r") as f:
        data = json.load(f)
    return data

def execute_plan(ip="127.0.0.1", port=9559, plan_file="choreography_plan.json", music_file=None):
    dry_run = (port == 0 or port == "dry_run" or port == "dry-run")
    if ALProxy is None and not dry_run:
        print("ERROR: naoqi library not found. Please run within Choregraphe environment (e.g. run_sim.bat).")
        return False

    data = load_plan(plan_file)
    moves = data.get("moves", [])
    total_dur = data.get("total_duration", 0)

    print("=== NAO Choreography Execution ===")
    if dry_run:
        print("Running in DRY-RUN mode: verifying move sequencing, posture transitions, and modules...")
        motion = None
        posture = None
    else:
        print("Connecting to robot at {}:{}...".format(ip, port))
        try:
            motion = ALProxy("ALMotion", ip, port)
            posture = ALProxy("ALRobotPosture", ip, port)
        except Exception as e:
            print("Failed to connect to ALProxy: {}".format(e))
            return False
        print("Robot connected successfully.")
        print("Waking up robot and setting StandInit...")
        motion.wakeUp()
        posture.goToPosture("StandInit", 0.8)

    # Optional audio track start
    music_proc = None
    if not music_file:
        for candidate in ["rick_120s.mp3", "rick.mp3", "rick.wav", "classic_hit.wav", "music.mp3", "song.mp3"]:
            if os.path.exists(os.path.join(script_dir, candidate)):
                music_file = os.path.join(script_dir, candidate)
                break
    if music_file and os.path.exists(music_file):
        music_proc = start_music(music_file)

    print("Executing {} planned moves (Estimated duration: {:.1f}s)...".format(len(moves), total_dur))
    start_time = time.time()

    current_posture = "StandInit"
    for idx, move_file in enumerate(moves, 1):
        mod_name = os.path.splitext(move_file)[0]
        print("--> Step {:02d}/{:02d}: Executing {}".format(idx, len(moves), mod_name))

        # Fluid posture transition: if moving from floor/crouch to a standing movement, stand up smoothly
        is_floor_move = any(x in move_file for x in ["6-Crouch", "16-Sit", "17-SitRelax", "sitting_mood", "sitting_handkiss", "sitting_wavess"])
        if not is_floor_move and current_posture in ["Crouch", "Sitting"]:
            try:
                if not dry_run:
                    posture.goToPosture("StandInit", 0.85)
                current_posture = "Standing"
            except Exception:
                pass

        try:
            mod = __import__(mod_name)
            is_bezier = hasattr(mod, "keys") and mod.keys and isinstance(mod.keys[0], list) and mod.keys[0] and isinstance(mod.keys[0][0], list)
            if hasattr(mod, "main") and is_bezier:
                if not dry_run:
                    mod.main(ip, port)
            elif hasattr(mod, "names") and hasattr(mod, "keys") and hasattr(mod, "times"):
                # Keyframe trajectory export: interpolate joint angles directly via ALMotion
                if not dry_run and motion is not None:
                    # For standing upper-body dance moves (finger_snap), filter out corrupted leg keyframes
                    # that tilt the robot onto its heels and cause it to fall backwards.
                    exec_names = []
                    exec_keys = []
                    exec_times = []
                    is_standing_upper_dance = any(x in mod_name for x in ["finger_snap", "high_clap", "whip", "dab", "guitar", "proud", "Disco", "DanceMove", "ThrillerClap", "ThrillerSnapSnap", "new_hiphop"])
                    is_sitting_dance = ("sitting" in mod_name)
                    for n, k, t in zip(mod.names, mod.keys, mod.times):
                        if (is_standing_upper_dance or is_sitting_dance) and any(leg in n for leg in ["Hip", "Knee", "Ankle"]):
                            continue
                        exec_names.append(n)
                        exec_keys.append(k)
                        exec_times.append(t)
                    # Uniform lead-in time to prevent Max Velocity violations
                    min_t = min(t_list[0] for t_list in exec_times if t_list) if exec_times else 0.0
                    lead_in = max(0.65, 0.7 - min_t)
                    adjusted_times = [[round(t + lead_in, 3) for t in t_list] for t_list in exec_times]
                    motion.angleInterpolation(exec_names, exec_keys, adjusted_times, True)
            elif hasattr(mod, "main"):
                if not dry_run:
                    mod.main(ip, port)
            elif dry_run:
                print("Warning: Move {} has neither main() nor keyframe arrays".format(mod_name))
            else:
                print("Warning: Move {} has neither main() nor keyframe arrays".format(mod_name))
        except Exception as e:
            print("Error executing {}: {}".format(mod_name, e))

        # Update posture tracker
        if "6-Crouch" in move_file:
            current_posture = "Crouch"
        elif "16-Sit" in move_file or "17-SitRelax" in move_file or "sitting" in move_file:
            current_posture = "Sitting"
        elif "11-Stand" in move_file or "14-StandInit" in move_file:
            current_posture = "Standing"

        _orig_sleep(0.05)

    elapsed = time.time() - start_time
    print("\n=== Choreography Complete ===")
    print("Actual execution time: {:.1f} seconds".format(elapsed))

    stop_music(music_proc)
    if not dry_run:
        print("Choreography finished. Maintaining final standing pose.")
        # Returning via goToPosture("StandInit") triggers inverse-kinematics leg solver
        # which abruptly jerks leg joints and knocks the simulated robot over.
        # Returning smoothly via upper-body angle interpolation keeps the robot standing safely.
        stand_init_names = [
            "HeadYaw", "HeadPitch",
            "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand",
            "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"
        ]
        stand_init_angles = [
            0.0, 0.0,
            1.4, 0.18, -1.35, -0.5, 0.0, 0.3,
            1.4, -0.18, 1.35, 0.5, 0.0, 0.3
        ]
        motion.angleInterpolation(stand_init_names, stand_init_angles, 2.0, True)
       # In simulated NAO (Choregraphe), motion.rest() shuts down motor stiffness while standing,
        # causing gravity simulation to drop the robot onto the floor. Keep StandInit stable.
    print("Finished successfully.")
    return True

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 9559
    music_arg = None

    args = sys.argv[1:]
    if len(args) > 0 and args[0].isdigit():
        port = int(args[0])
        args = args[1:]
    elif len(args) > 0 and args[0] in ["dry_run", "dry-run", "0"]:
        port = 0
        args = args[1:]
    for idx, a in enumerate(args):
        if a in ["--music", "-m"] and idx + 1 < len(args):
            joined = " ".join(args[idx + 1:])
            if os.path.exists(joined):
                music_arg = joined
            else:
                music_arg = args[idx + 1]

    execute_plan(ip, port, music_file=music_arg)
