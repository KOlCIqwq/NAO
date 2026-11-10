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
    class _DummyTTS(object):
        def say(self, *args, **kwargs):
            pass
    class _FastPostureProxy(object):
        def __init__(self, real_proxy):
            self._real = real_proxy
        def goToPosture(self, postureName, speed):
            # Course files hard-code speed=0.5, which causes simulated inverse-kinematics solver
            # to take 40+ seconds per sit/stand. Boosting to 1.0 completes in ~2s smoothly.
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
                p = _FastPostureProxy(p)
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
    # Drop hard stops (>= 0.8s) that freeze the robot between steps
    if secs >= 0.8:
        return
    _orig_sleep(secs * 0.4)
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
        for candidate in ["rick.mp3", "rick.wav", "classic_hit.wav", "music.mp3", "song.mp3"]:
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
        is_floor_move = any(x in move_file for x in ["6-Crouch", "16-Sit", "17-SitRelax"])
        if not is_floor_move and current_posture in ["Crouch", "Sitting"]:
            try:
                if not dry_run:
                    posture.goToPosture("StandInit", 0.85)
                current_posture = "Standing"
            except Exception:
                pass

        try:
            # Smooth bridge: before executing move, smoothly blend if arm joints deviate
            if not dry_run and motion is not None and current_posture == "Standing":
                arm_joints = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                              "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
                curr_arm = motion.getAngles(arm_joints, True)
                neutral_arm = [1.4, -0.18, 0.82, 1.05, 1.4, 0.18, -0.82, -1.05]
                max_dev = max(abs(c - n) for c, n in zip(curr_arm, neutral_arm))
                if max_dev > 0.45 and not is_floor_move:
                    motion.angleInterpolation(arm_joints, neutral_arm, 0.4, True)

            mod = __import__(mod_name)
            if hasattr(mod, "main"):
                if not dry_run:
                    mod.main(ip, port)
            elif hasattr(mod, "names") and hasattr(mod, "keys") and hasattr(mod, "times"):
                # Keyframe trajectory export: interpolate joint angles directly via ALMotion
                if not dry_run and motion is not None:
                    # Ensure lead-in time >= 0.4s to prevent Max Velocity violations
                    adjusted_times = []
                    for t_list in mod.times:
                        if t_list and t_list[0] < 0.4:
                            shift = 0.4 - t_list[0]
                            adjusted_times.append([round(t + shift, 3) for t in t_list])
                        else:
                            adjusted_times.append(t_list)
                    motion.angleInterpolation(mod.names, mod.keys, adjusted_times, True)
            elif dry_run:
                print("Warning: Move {} has neither main() nor keyframe arrays".format(mod_name))
            else:
                print("Warning: Move {} has neither main() nor keyframe arrays".format(mod_name))
        except Exception as e:
            print("Error executing {}: {}".format(mod_name, e))

        # Update posture tracker
        if "6-Crouch" in move_file:
            current_posture = "Crouch"
        elif "16-Sit" in move_file or "17-SitRelax" in move_file:
            current_posture = "Sitting"
        elif "11-Stand" in move_file or "14-StandInit" in move_file:
            current_posture = "Standing"

        _orig_sleep(0.05)

    elapsed = time.time() - start_time
    print("\n=== Choreography Complete ===")
    print("Actual execution time: {:.1f} seconds".format(elapsed))

    stop_music(music_proc)
    if not dry_run:
        print("Returning to StandInit and resting...")
        posture.goToPosture("StandInit", 0.6)
        motion.rest()
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
