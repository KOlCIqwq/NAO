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

_SYNC_STATE = {"music_start": None, "bpm": 113.3, "phase": 0.21, "sim_scale": 0.85}

def _max_time(t_obj):
    if isinstance(t_obj, (int, float)):
        return float(t_obj)
    if isinstance(t_obj, (list, tuple)) and t_obj:
        if isinstance(t_obj[0], (list, tuple)):
            vals = [max(float(x) for x in tl) for tl in t_obj if tl]
            return max(vals) if vals else 0.0
        return max(float(x) for x in t_obj)
    return 0.0

def _scale_times(times, names, scale):
    if isinstance(times, (int, float)):
        return round(max(0.25, float(times) * scale), 3)
    if not isinstance(times, (list, tuple)) or not times:
        return times
    if isinstance(times[0], (list, tuple)):
        out = []
        for tl in times:
            prev = 0.0
            new_tl = []
            for raw_t in tl:
                st = round(max(0.18, float(raw_t) * scale), 3)
                if st - prev < 0.16:
                    st = round(prev + 0.16, 3)
                new_tl.append(st)
                prev = st
            out.append(new_tl)
        return out
    is_single_joint = (not isinstance(names, (list, tuple))) or len(names) == 1
    if is_single_joint:
        prev = 0.0
        out = []
        for raw_t in times:
            st = round(max(0.18, float(raw_t) * scale), 3)
            if st - prev < 0.16:
                st = round(prev + 0.16, 3)
            out.append(st)
            prev = st
        return out
    return [round(max(0.18, float(raw_t) * scale), 3) for raw_t in times]

class _SyncedMotionProxy(object):
    def __init__(self, real_proxy):
        self._real = real_proxy

    def angleInterpolation(self, names, keys, times, isAbsolute=True):
        nominal_max = _max_time(times)
        if _SYNC_STATE["music_start"] is None or nominal_max <= 0.3:
            return self._real.angleInterpolation(names, keys, times, isAbsolute)

        sim_scale = _SYNC_STATE["sim_scale"]
        beat_dt = 60.0 / float(_SYNC_STATE["bpm"])
        phase = float(_SYNC_STATE["phase"])
        rem = nominal_max % beat_dt
        is_beat_move = isinstance(times, (list, tuple)) and nominal_max >= 1.8 and (rem < 0.08 or (beat_dt - rem) < 0.08)

        if is_beat_move:
            t_now = time.time() - _SYNC_STATE["music_start"]
            target_end = phase + round((t_now + nominal_max - phase) / beat_dt) * beat_dt
            desired_wall = max(nominal_max * 0.82, min(nominal_max * 1.12, target_end - t_now))
            scale = (desired_wall / nominal_max) * sim_scale
        else:
            scale = sim_scale

        scale = max(0.62, min(1.05, scale))
        scaled_times = _scale_times(times, names, scale)
        sent_max = _max_time(scaled_times)

        t0 = time.time()
        res = self._real.angleInterpolation(names, keys, scaled_times, isAbsolute)
        wall_dt = time.time() - t0

        if wall_dt > 0.5 and sent_max > 0.5:
            measured = max(0.62, min(1.05, sent_max / wall_dt))
            _SYNC_STATE["sim_scale"] = 0.55 * _SYNC_STATE["sim_scale"] + 0.45 * measured
        return res

    def __getattr__(self, name):
        return getattr(self._real, name)

try:
    from naoqi import ALProxy
    _orig_ALProxy = ALProxy
    _proxy_cache = {}
    _SIT_NAMES = ['HeadYaw', 'HeadPitch', 'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw', 'LHand', 'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll', 'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch', 'RAnkleRoll', 'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw', 'RHand']
    _SIT_ANGLES = [-0.0307, -0.0399, 0.8399, 0.3002, -0.4654, -1.1948, -0.0016, 0.296, -0.6059, 0.267, -1.5294, 1.3959, 0.8437, -0.0122, -0.6059, -0.2561, -1.5325, 1.4021, 0.8238, 0.02, 0.8875, -0.3316, 0.5407, 1.255, -0.0077, 0.3348]
    _SITRELAX_ANGLES = [-0.02, 0.0, 1.2, 0.15, -0.6, -0.5, 0.0, 0.3, -0.6059, 0.267, -1.50, 1.38, 0.84, -0.01, -0.6059, -0.2561, -1.50, 1.38, 0.84, 0.02, 1.2, -0.15, 0.6, 0.5, 0.0, 0.3]
    _CROUCH_ANGLES = [0.0, 0.0, 1.4, 0.18, -1.35, -0.5, 0.0, 0.3, 0.0, 0.0, -0.85, 2.05, -1.15, 0.0, 0.0, 0.0, -0.85, 2.05, -1.15, 0.0, 1.4, -0.18, 1.35, 0.5, 0.0, 0.3]
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
                    # In simulated NAO, standing directly from SitRelax causes feet to slip outward and fall.
                    # Tucking smoothly into Crouch first gives full center-of-gravity support so NAO rises cleanly in 2.5s.
                    try:
                        curr = self._real.getPosture()
                        if curr in ["SitRelax", "Sitting", "Sit", "Unknown"]:
                            self._motion.angleInterpolation(_SIT_NAMES, _CROUCH_ANGLES, 1.6, True)
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
            if name == "ALMotion":
                p = _SyncedMotionProxy(p)
            elif name == "ALRobotPosture":
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
    player = AudioPlayer(audio_path)
    if player.play():
        return player
    return None

class AudioPlayer(object):
    """Platform-independent background audio player supporting MP3 and WAV."""
    def __init__(self, audio_path):
        self.audio_path = os.path.abspath(audio_path) if audio_path else None
        self.mci = None
        self.proc = None
        self.alias = "bg_choreography_music"

    def play(self):
        if not self.audio_path or not os.path.exists(self.audio_path):
            print("Audio file not found: {}".format(self.audio_path))
            return False
        print("Starting background music: {}".format(os.path.basename(self.audio_path)))
        if sys.platform.startswith("win"):
            # Method 1: Windows Multimedia MCI (supports MP3 and WAV headlessly)
            try:
                import ctypes
                self.mci = ctypes.windll.winmm
                self.mci.mciSendStringA(str("close " + self.alias), None, 0, 0)
                cmd_open = str('open "' + self.audio_path + '" alias ' + self.alias)
                ret = self.mci.mciSendStringA(cmd_open, None, 0, 0)
                if ret == 0:
                    self.mci.mciSendStringA(str("play " + self.alias), None, 0, 0)
                    return True
            except Exception as e:
                print("MCI audio failed: {}".format(e))
            # Method 2: PowerShell MediaPlayer fallback
            try:
                ps_cmd = "(New-Object -ComObject wmplayer.ocx).openPlayer('" + self.audio_path.replace("'", "''") + "')"
                self.proc = subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_cmd])
                return True
            except Exception as e:
                print("Windows media fallback failed: {}".format(e))
                return False
        else:
            player = "mpg123" if os.system("which mpg123 > /dev/null 2>&1") == 0 else "afplay"
            try:
                self.proc = subprocess.Popen([player, self.audio_path])
                return True
            except Exception as e:
                print("POSIX audio playback failed: {}".format(e))
                return False

    def stop(self):
        if self.mci is not None:
            try:
                self.mci.mciSendStringA(str("stop " + self.alias), None, 0, 0)
                self.mci.mciSendStringA(str("close " + self.alias), None, 0, 0)
            except Exception:
                pass
        if self.proc is not None:
            try:
                self.proc.terminate()
            except Exception:
                pass

def stop_music(player):
    """Terminates background music playback cleanly."""
    if player is not None:
        try:
            player.stop()
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
    details = data.get("details", [])
    total_dur = data.get("total_duration", 0)
    _SYNC_STATE["bpm"] = float(data.get("bpm", 113.3))
    _SYNC_STATE["phase"] = float(data.get("phase", 0.21))
    MAX_WALL_TIME = 114.0  # Reserve ~2.5s for final StandInit settle so total < 120.0s

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
    if not dry_run:
        _SYNC_STATE["music_start"] = start_time

    current_posture = "StandInit"
    for idx, move_file in enumerate(moves, 1):
        mod_name = os.path.splitext(move_file)[0]
        detail = details[idx - 1] if idx - 1 < len(details) else {}
        move_type = detail.get("type", "INTERMEDIATE")
        est_dur = float(detail.get("estimated_duration", 4.24))
        is_disp = ("composite_" in move_file) or any(x in move_file for x in ["7-Move", "8-Move", "9-Diag", "10-Diag"])

        if not dry_run and move_type == "INTERMEDIATE" and not is_disp:
            elapsed_now = time.time() - start_time
            if elapsed_now + est_dur > MAX_WALL_TIME:
                print("--> Step {:02d}/{:02d}: Skipping {} (elapsed {:.1f}s, keeping total < 120s)".format(
                    idx, len(moves), mod_name, elapsed_now))
                continue

        print("--> Step {:02d}/{:02d}: Executing {}".format(idx, len(moves), mod_name))
        step_start = time.time()

        # Fluid posture transition: if moving from floor/crouch to a standing movement, stand up smoothly
        is_floor_move = ("sitting" in move_file.lower()) or any(x in move_file for x in ["6-Crouch", "16-Sit", "17-SitRelax", "11-Stand"])
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
                    is_standing_upper_dance = any(x in mod_name for x in ["finger_snap", "DanceMove"])
                    is_sitting_dance = ("sitting" in mod_name)
                    for n, k, t in zip(mod.names, mod.keys, mod.times):
                        if (is_standing_upper_dance or is_sitting_dance) and any(leg in n for leg in ["Hip", "Knee", "Ankle"]):
                            continue
                        exec_names.append(n)
                        exec_keys.append(k)
                        exec_times.append(t)
                    # Minimal lead-in time to prevent Max Velocity violations without adding dead air
                    min_t = min(t_list[0] for t_list in exec_times if t_list) if exec_times else 0.0
                    lead_in = max(0.25, 0.35 - min_t)
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

        if not dry_run:
            now_t = time.time()
            print("    [t={:.1f}s, step={:.2f}s, scale={:.2f}]".format(
                now_t - start_time, now_t - step_start, _SYNC_STATE["sim_scale"]))

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
