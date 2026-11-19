"""
NAO Choreography Planner
Autonomous forward state-space A* planner compliant with the NAO Planning Competition rules:
- Initial state: StandInit | Goal state: Crouch
- All 6 mandatory positions {Sit, SitRelax, WipeForehead, Stand, Hello, StandZero}
  scheduled dynamically by A* in any valid posture-consistent order
- At least 5 official Slide 16/17 intermediate moves + expanded movement library
- Net zero stage displacement (dx = 0, dy = 0) with stage exploration
- Auto-extracted kinematic features (duration, angular velocity, amplitude, pause holds)
  matched against real audio bar energy & beat dips (< 120s limit)
"""

import sys
import os
import re
import ast
import json
import heapq
import math
import audio_analyzer

INITIAL_SPEC = {
    "file": "14-StandInit.py", "pre": "Standing", "post": "Standing", "fallback_dur": 0.5
}
GOAL_SPEC = {
    "file": "6-Crouch.py", "pre": "Standing", "post": "Crouch", "fallback_dur": 1.8
}

# 6 Mandatory Positions from Competition Slide 13 (index -> bitmask 1 << i)
MANDATORY_SPECS = [
    {"file": "16-Sit.py", "pre": "Standing", "post": "Sitting", "center_only": True, "fallback_dur": 3.5},
    {"file": "17-SitRelax.py", "pre": "Sitting", "post": "Sitting", "center_only": False, "fallback_dur": 2.5},
    {"file": "11-Stand.py", "pre": "Sitting", "post": "Standing", "center_only": False, "fallback_dur": 3.3},
    {"file": "WipeForehead.py", "pre": "Standing", "post": "Standing", "center_only": False, "fallback_dur": 6.0},
    {"file": "Hello.py", "pre": "Standing", "post": "Standing", "center_only": False, "fallback_dur": 5.6},
    {"file": "15-StandZero.py", "pre": "Standing", "post": "Standing", "center_only": False, "fallback_dur": 1.4},
]

# Intermediate Candidate Pool: Official Slide 16/17 moves + expanded dance/motif library
INTERMEDIATE_SPECS = {
    # Official Slide 16/17 positions
    "3-Double_movement.py":         {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": True, "fallback_dur": 4.0},
    "4-Arms_opening.py":            {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": True, "fallback_dur": 4.0},
    "7-Move_forward.py":            {"pre": "Standing", "post": "Standing", "dx": 1, "dy": 0, "official": True, "fallback_dur": 3.5},
    "8-Move_backward.py":           {"pre": "Standing", "post": "Standing", "dx": -1, "dy": 0, "official": True, "fallback_dur": 3.5},
    "9-Diagonal_left.py":           {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 1, "official": True, "fallback_dur": 3.0},
    "10-Diagonal_right.py":         {"pre": "Standing", "post": "Standing", "dx": 0, "dy": -1, "official": True, "fallback_dur": 3.0},
    "sprinkler.py":                 {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": True, "fallback_dur": 10.4},

    # Expanded stage locomotion composites
    "composite_diagleft_snap.py":   {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 1, "official": False, "fallback_dur": 4.24},
    "composite_diagright_sway.py":  {"pre": "Standing", "post": "Standing", "dx": 0, "dy": -1, "official": False, "fallback_dur": 4.24},
    "composite_forward_groove.py":  {"pre": "Standing", "post": "Standing", "dx": 1, "dy": 0, "official": False, "fallback_dur": 4.24},
    "composite_backward_groove.py": {"pre": "Standing", "post": "Standing", "dx": -1, "dy": 0, "official": False, "fallback_dur": 4.24},

    # Expanded beat-quantized standing motifs & full-body dances
    "motif_hip_grooves.py":         {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.24},
    "motif_knee_bounce_step.py":    {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 2.12},
    "motif_astley_groove.py":       {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.24},
    "motif_disco_point.py":         {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.24},
    "motif_beat_drop.py":           {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 2.12},
    "motif_groove_pause.py":        {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 2.12},
    "motif_pop_clap.py":            {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 2.12},
    "motif_sprinkler.py":           {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.24},
    "motif_finger_snap.py":         {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.24},
    "motif_dance_wave.py":          {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.24},
    "Disco.py":                     {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 5.0},
    "new_hiphop.py":                {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 5.32},
    "new_speedy.py":                {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.60},
    "new_dance.py":                 {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 3.24},
    "dab.py":                       {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.64},
    "ThrillerClap.py":              {"pre": "Standing", "post": "Standing", "dx": 0, "dy": 0, "official": False, "fallback_dur": 5.0},

    # Sitting moves
    "motif_sitting_kiss.py":        {"pre": "Sitting", "post": "Sitting", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.24},
    "sitting_mood.py":              {"pre": "Sitting", "post": "Sitting", "dx": 0, "dy": 0, "official": False, "fallback_dur": 4.20},
}

_STRIPPED_LEG_FILES = set(["finger_snap.py", "DanceMove.py"])


def _parse_trajectories(txt):
    """Extracts (joint_names, times_lists, keys_lists) from Choregraphe exports and motif/composite scripts."""
    # Case A: names.append(...) + times.append([...]) and keys.append([...])
    n_app = re.findall(r'names\.append\(["\']([^"\']+)["\']\)', txt)
    t_app = re.findall(r"times\.append\((\[[^\n]+\])\)", txt)
    k_app = re.findall(r"keys\.append\((\[[^\n]+\])\)", txt)
    if t_app and k_app:
        times_out, keys_out = [], []
        for ts, ks in zip(t_app, k_app):
            tl = ast.literal_eval(ts)
            kl_raw = ast.literal_eval(ks)
            kl = [float(el[0]) if isinstance(el, list) else float(el) for el in kl_raw]
            times_out.append([float(x) for x in tl])
            keys_out.append(kl)
        jnames = n_app if len(n_app) == len(times_out) else ["j%d" % i for i in range(len(times_out))]
        return jnames, times_out, keys_out

    # Case B: top-level names = [...], times = [[...]], keys = [[...]]
    m_n = re.search(r"^names\s*=\s*(\[[^\n]+\])\s*$", txt, re.M)
    m_t = re.search(r"^times\s*=\s*(\[\[.*?\]\])\s*$", txt, re.M | re.S)
    m_k = re.search(r"^keys\s*=\s*(\[\[.*?\]\])\s*$", txt, re.M | re.S)
    if m_t and m_k:
        times_out = [[float(x) for x in tl] for tl in ast.literal_eval(m_t.group(1))]
        keys_out = [[float(x) for x in kl] for kl in ast.literal_eval(m_k.group(1))]
        jnames = ast.literal_eval(m_n.group(1)) if m_n else ["j%d" % i for i in range(len(times_out))]
        return jnames, times_out, keys_out

    # Case C: motif/composite names = [...] + t_grid = [...] or times = [[...]] inside main() + keys = [...]
    m_names = re.search(r"^[ \t]*names\s*=\s*\[", txt, re.M)
    m_start = re.search(r"^[ \t]*(?:t_grid|times)\s*=", txt, re.M)
    m_end = re.search(r"motion\.angleInterpolation", txt)
    start_pos = m_names.start() if (m_names and m_start and m_names.start() < m_start.start()) else (m_start.start() if m_start else -1)
    if start_pos >= 0 and m_end and m_end.start() > start_pos:
        block_lines = txt[start_pos:m_end.start()].splitlines()
        indent = len(block_lines[0]) - len(block_lines[0].lstrip())
        cleaned = "\n".join(line[indent:] if len(line) >= indent else line for line in block_lines)
        cleaned = re.sub(r"\ntry:\s*$", "", cleaned.rstrip())
        env = {"DEG": math.pi / 180.0, "list": list, "round": round, "range": range}
        ns = dict(env)
        ns["__builtins__"] = env
        ns["names"] = ["j%d" % i for i in range(24)]
        try:
            exec(compile(cleaned, "<traj>", "exec"), ns, ns)
        except Exception:
            return [], [], []
        if isinstance(ns.get("times"), list) and isinstance(ns.get("keys"), list):
            jnames = ns["names"] if len(ns.get("names", [])) == len(ns["keys"]) else ["j%d" % i for i in range(len(ns["keys"]))]
            return jnames, ns["times"], ns["keys"]
    return [], [], []


def extract_move_features(move_file, spec, positions_dir="RobotPositions"):
    """Computes physical kinematic attributes automatically from RobotPositions/<move_file>."""
    path = os.path.join(positions_dir, move_file)
    txt = ""
    if os.path.exists(path):
        with open(path, "r") as f:
            txt = f.read()

    has_walk = ("moveTo" in txt)
    leg_active = has_walk or (
        move_file not in _STRIPPED_LEG_FILES
        and any(k in txt for k in ["HipPitch", "KneePitch", "AnklePitch", "HipRoll", "RLeg", "LLeg"])
    )

    jnames, times_lists, keys_lists = _parse_trajectories(txt)
    start_pose, end_pose = {}, {}
    peak_vel = 0.0
    if times_lists and keys_lists:
        max_t = max(max(tl) for tl in times_lists if tl)
        dur = round(max_t + (1.0 if "goToPosture" in txt else 0.0), 2)

        joint_speeds, joint_amps = [], []
        step_spans = {}
        for jn, tl, kl in zip(jnames, times_lists, keys_lists):
            if kl:
                start_pose[jn] = float(kl[0])
                end_pose[jn] = float(kl[-1])
            if len(tl) < 2 or len(kl) < 2:
                continue
            amp = max(kl) - min(kl)
            joint_amps.append(amp)
            span_t = max(tl[-1] - tl[0], 0.1)
            path_len = sum(abs(kl[i] - kl[i - 1]) for i in range(1, min(len(tl), len(kl))))
            joint_speeds.append(path_len / span_t)
            for i in range(1, min(len(tl), len(kl))):
                dt = tl[i] - tl[i - 1]
                peak_vel = max(peak_vel, abs(kl[i] - kl[i - 1]) / max(dt, 0.04))
                if dt >= 0.40:
                    key = (round(tl[i - 1], 2), round(tl[i], 2))
                    step_spans[key] = max(step_spans.get(key, 0.0), abs(kl[i] - kl[i - 1]))

        top_n = max(1, len(joint_speeds) // 2)
        raw_vel = sum(sorted(joint_speeds)[-top_n:]) / float(top_n)
        raw_amp = sum(sorted(joint_amps)[-top_n:]) / float(top_n)
        has_pause = any(max_dk < 0.05 for max_dk in step_spans.values())
    else:
        tvar, block_sum = None, 0.0
        for line in txt.replace("\r", "\n").splitlines():
            ls = line.strip()
            if not ls or ls.startswith("#"):
                continue
            mt = re.match(r"timeLists?\s*=\s*([0-9.]+)", ls)
            if mt:
                tvar = float(mt.group(1))
            if "angleInterpolation(" in ls and ".post." not in ls:
                ma = re.search(r"angleInterpolation\([^,]+,[^,]+,\s*([0-9.]+)", ls)
                if ma:
                    block_sum += float(ma.group(1))
                elif tvar is not None:
                    block_sum += tvar
        set_cnt = txt.count("setAngles(")
        dur = round(block_sum + 0.25 * set_cnt, 2) if block_sum > 0.0 else float(spec["fallback_dur"])
        if has_walk:
            raw_vel, raw_amp = 0.28, 0.45
        elif "angleInterpolation" in txt or "setAngles" in txt:
            calls = txt.count("angleInterpolation") + txt.count("setAngles")
            raw_vel = min(0.45, 0.32 + 0.02 * calls)
            raw_amp = 0.70
        else:
            raw_vel, raw_amp = 0.25, 0.60
        has_pause = False

    feat = dict(spec)
    feat["file"] = move_file
    feat["dur"] = dur
    feat["raw_vel"] = round(raw_vel, 4)
    feat["raw_amp"] = round(raw_amp, 4)
    feat["peak_vel"] = round(peak_vel, 2)
    feat["start_pose"] = start_pose
    feat["end_pose"] = end_pose
    feat["has_pause"] = has_pause
    feat["leg_active"] = leg_active
    feat["has_walk"] = has_walk
    return feat


def _linear_norm(val, lo, hi, out_lo, out_hi):
    if hi <= lo:
        return (out_lo + out_hi) / 2.0
    ratio = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    return round(out_lo + ratio * (out_hi - out_lo), 2)


def build_move_library(positions_dir="RobotPositions"):
    """Extracts and normalizes physical features across all initial, mandatory, intermediate, and goal moves."""
    init_feat = extract_move_features(INITIAL_SPEC["file"], INITIAL_SPEC, positions_dir)
    goal_feat = extract_move_features(GOAL_SPEC["file"], GOAL_SPEC, positions_dir)
    mand_list = [extract_move_features(s["file"], s, positions_dir) for s in MANDATORY_SPECS]
    inter_dict = {f: extract_move_features(f, s, positions_dir) for f, s in INTERMEDIATE_SPECS.items()}

    all_feats = [init_feat, goal_feat] + mand_list + list(inter_dict.values())
    vels = sorted(f["raw_vel"] for f in all_feats)
    amps = sorted(f["raw_amp"] for f in all_feats)
    v_lo, v_hi = vels[0], vels[int(0.90 * (len(vels) - 1))]
    a_lo, a_hi = amps[0], amps[int(0.90 * (len(amps) - 1))]

    for f in all_feats:
        f["energy"] = _linear_norm(f["raw_vel"], v_lo, v_hi, 1.4, 5.0)
        f["expressiveness"] = _linear_norm(f["raw_amp"], a_lo, a_hi, 1.5, 5.0)

    return init_feat, goal_feat, mand_list, inter_dict


_REAL_BAR_FEATURES = None
_REAL_ENERGY_PROFILE = None
_REAL_PHASE = 0.21
_REAL_BAR_DUR = 2.11827
_REAL_SONG_DURATION = 120.0


def load_real_energy_profile(song_path=None):
    """Loads per-bar energy & pause features from WAV (or energy profile fallback)."""
    global _REAL_ENERGY_PROFILE, _REAL_BAR_FEATURES, _REAL_PHASE, _REAL_BAR_DUR, _REAL_SONG_DURATION
    candidates = []
    if song_path:
        base, _ = os.path.splitext(song_path)
        candidates.extend([base + ".wav", song_path])
    candidates.extend(["rick_120s.wav", "rick_120s.mp3"])
    for cand in candidates:
        if cand and os.path.exists(cand):
            bar_data = audio_analyzer.get_bar_features(cand)
            if bar_data and bar_data.get("bars"):
                _REAL_BAR_FEATURES = bar_data["bars"]
                _REAL_PHASE = bar_data.get("phase", 0.21)
                _REAL_BAR_DUR = bar_data.get("bar_interval", 2.11827)
                _REAL_SONG_DURATION = bar_data.get("duration", 120.0)
                return bar_data
            data = audio_analyzer.get_energy_profile(cand, num_slices=24)
            if data and data.get("profile"):
                _REAL_ENERGY_PROFILE = data["profile"]
                _REAL_SONG_DURATION = data.get("duration", 120.0)
                return data
    return None


def get_music_features(t_sec):
    """Returns (target_energy, has_pause, section_id) directly from extracted audio bars/profile."""
    if _REAL_BAR_FEATURES:
        idx = int(max(0.0, t_sec - _REAL_PHASE) / max(_REAL_BAR_DUR, 0.1))
        idx = max(0, min(len(_REAL_BAR_FEATURES) - 1, idx))
        b = _REAL_BAR_FEATURES[idx]
        return b["energy"], b["has_pause"], b.get("section", 0)
    if _REAL_ENERGY_PROFILE:
        idx = int((t_sec / max(_REAL_SONG_DURATION, 1.0)) * len(_REAL_ENERGY_PROFILE))
        idx = max(0, min(len(_REAL_ENERGY_PROFILE) - 1, idx))
        return _REAL_ENERGY_PROFILE[idx], False, 0
    return 3.0, False, 0


class ChoreographyPlanner(object):
    """Forward state-space A* planner optimizing extracted kinematics & audio alignment."""

    def __init__(self, init_feat, goal_feat, mandatory_lib, intermediate_lib,
                 max_duration=115.0, bpm=113.3, music_fn=None):
        self.init_feat = init_feat
        self.goal_feat = goal_feat
        self.mandatory = mandatory_lib
        self.intermediate = intermediate_lib
        self.max_duration = max_duration
        self.bpm = bpm
        self.bar_dur = (60.0 / bpm) * 4.0
        self.music_fn = music_fn or get_music_features
        self._feat_by_file = {self.init_feat["file"]: self.init_feat, self.goal_feat["file"]: self.goal_feat}
        for m in self.mandatory:
            self._feat_by_file[m["file"]] = m
        self._feat_by_file.update(self.intermediate)

    def _pose_gap(self, prev_file, next_file):
        p_end = self._feat_by_file.get(prev_file, {}).get("end_pose", {})
        n_start = self._feat_by_file.get(next_file, {}).get("start_pose", {})
        if not p_end or not n_start:
            return 0.25
        shared = [abs(p_end[j] - n_start[j]) for j in p_end if j in n_start]
        return (sum(shared) / float(len(shared))) if shared else 0.25

    def _query_music(self, t_sec):
        res = self.music_fn(t_sec)
        if len(res) >= 3:
            return res[0], res[1], res[2]
        return res[0], res[1], 0

    def solve(self):
        init_dur = self.init_feat["dur"]
        crouch_dur = self.goal_feat["dur"]
        _, _, init_sec = self._query_music(0.0)
        start_hist = ((self.init_feat["file"], "INITIAL", init_dur, False, init_sec),)
        # state: (t, mand_mask, pos, x, y, off_cnt, visited_stage, used_tuple, hist)
        start_state = (init_dur, 0, "Standing", 0, 0, 0, False, (), start_hist)
        pq = [(0.0, 0.0, start_state)]
        visited = {}
        nodes = 0

        while pq and nodes < 120000:
            f, g, (t, mand_mask, pos, x, y, off_cnt, visited_stage, used, hist) = heapq.heappop(pq)
            nodes += 1

            last_mand = bool(hist and hist[-1][1] == "MANDATORY")
            state_key = (mand_mask, pos, x, y, min(off_cnt, 5), visited_stage, last_mand, int(round(t / 2.0)))
            if state_key in visited and visited[state_key] <= f:
                continue
            visited[state_key] = f

            # Goal test: all 6 mandatory done, Standing at center, stage explored, >=5 official moves, >=109s
            if (mand_mask == 63 and pos == "Standing" and x == 0 and y == 0
                    and visited_stage and off_cnt >= 5 and t >= 109.0 and t + crouch_dur <= self.max_duration):
                _, _, goal_sec = self._query_music(t)
                goal_hist = hist + ((self.goal_feat["file"], "GOAL", crouch_dur, True, goal_sec),)
                return (t + crouch_dur, g, goal_hist, nodes)

            # Admissible time-budget pruning
            rem_mand_dur = sum(m["dur"] for i, m in enumerate(self.mandatory) if not (mand_mask & (1 << i)))
            if t + rem_mand_dur + crouch_dur > self.max_duration:
                continue

            target_e, is_pause, sec_id = self._query_music(t)

            # Action A: Execute any remaining Mandatory position (unordered bitmask)
            for i, m in enumerate(self.mandatory):
                if mand_mask & (1 << i):
                    continue
                if m["pre"] != pos:
                    continue
                if pos == "Standing" and last_mand:
                    continue
                if m.get("center_only") and (x != 0 or y != 0):
                    continue
                # 11-Stand (idx 2) cannot run before 17-SitRelax (idx 1) since 16-Sit is single-use
                if i == 2 and not (mand_mask & (1 << 1)):
                    continue

                new_t = t + m["dur"]
                new_mask = mand_mask | (1 << i)
                rem_after = sum(self.mandatory[j]["dur"] for j in range(len(self.mandatory)) if not (new_mask & (1 << j)))
                if new_t + rem_after + crouch_dur > self.max_duration:
                    continue

                e_err = abs(m["energy"] - target_e)
                cost_delta = max(0.3, (2.5 + e_err * 3.0) * (m["dur"] / 4.24))
                new_g = g + cost_delta
                new_pos = m["post"]
                new_hist = hist + ((m["file"], "MANDATORY", m["dur"], True, sec_id),)
                h = self._heuristic(new_t, new_mask, new_pos, x, y, off_cnt, visited_stage)
                heapq.heappush(pq, (new_g + h, new_g, (new_t, new_mask, new_pos, x, y, off_cnt, visited_stage, used, new_hist)))

            # Action B: Execute any Intermediate move
            same_sec_moves = set(h_item[0] for h_item in hist[:-1] if h_item[1] == "INTERMEDIATE" and h_item[4] == sec_id)
            for m_file, info in self.intermediate.items():
                if info["pre"] != pos:
                    continue
                if hist and hist[-1][0] == m_file:
                    continue
                if (pos == "Standing" and not info["leg_active"]
                        and hist and hist[-1][1] == "INTERMEDIATE"
                        and not self.intermediate.get(hist[-1][0], {}).get("leg_active", True)):
                    continue

                rem = info["dur"] % self.bar_dur
                beat_err = min(rem, self.bar_dur - rem)
                if info["dur"] > 6.0 or info["has_walk"]:
                    max_plays = 1
                elif info["leg_active"] and info["dur"] <= 4.3 and beat_err < 0.08:
                    max_plays = 3
                elif info["leg_active"]:
                    max_plays = 2
                else:
                    max_plays = 1
                if used.count(m_file) >= max_plays:
                    continue

                new_x = x + info["dx"]
                new_y = y + info["dy"]
                if abs(new_x) > 1 or abs(new_y) > 1:
                    continue
                if t >= (self.max_duration - 14.0) and (abs(new_x) > abs(x) or abs(new_y) > abs(y)):
                    continue

                new_t = t + info["dur"]
                if new_t + rem_mand_dur + crouch_dur > self.max_duration:
                    continue

                e_err = abs(info["energy"] - target_e)
                expr = info["expressiveness"]
                body_score = 2.0 if info["leg_active"] else 0.0
                pause_score = 2.0 if (is_pause and info["has_pause"]) else 0.0
                is_new_off = info["official"] and (m_file not in used)
                off_bonus = 2.5 if (is_new_off and off_cnt < 5) else 0.0
                repeat_bonus = 2.6 if (m_file in same_sec_moves and not info["has_walk"]) else 0.0
                jerk_pen = max(0.0, info.get("peak_vel", 0.0) - 4.5) * 0.8
                pose_gap = self._pose_gap(hist[-1][0], m_file) if hist else 0.0

                cost_delta = max(0.3, (
                    12.0 - expr - body_score - pause_score - off_bonus - repeat_bonus
                    + e_err * 2.0 + beat_err * 4.5 + jerk_pen + pose_gap * 2.5
                ) * (info["dur"] / 4.24))
                new_g = g + cost_delta
                new_off_cnt = off_cnt + (1 if is_new_off else 0)
                new_visited = visited_stage or (new_x != 0 or new_y != 0)
                new_used = used + (m_file,)
                new_hist = hist + ((m_file, "INTERMEDIATE", info["dur"], info["official"], sec_id),)

                h = self._heuristic(new_t, mand_mask, info["post"], new_x, new_y, new_off_cnt, new_visited)
                heapq.heappush(pq, (new_g + h, new_g, (new_t, mand_mask, info["post"], new_x, new_y, new_off_cnt, new_visited, new_used, new_hist)))

        return None

    def _heuristic(self, t, mand_mask, pos, x, y, off_cnt, visited_stage):
        rem_m = 6 - bin(mand_mask).count("1")
        rem_o = max(0, 5 - off_cnt)
        rem_t = max(0.0, 109.0 - t)
        return (
            rem_m * 4.0
            + rem_o * 3.5
            + (abs(x) + abs(y)) * 2.5
            + (0.0 if visited_stage else 2.5)
            + (2.0 if pos == "Sitting" else 0.0)
            + rem_t * 1.55
        )


def generate_full_choreography(song_path=None):
    """Orchestrates audio analysis, kinematic extraction, A* planning, and JSON export."""
    if not song_path:
        for cand in ["rick_120s.mp3", "Never Gonna Give You Up.mp3", "rick.mp3"]:
            if os.path.exists(cand):
                song_path = cand
                break

    print("=== Forward A* NAO Choreography Planner ===")
    bpm, phase = 113.3, 0.21
    data = load_real_energy_profile(song_path)
    if data:
        bpm = data.get("bpm", 113.3)
        phase = data.get("phase", 0.21)
        print("-> Audio: %s (%.1f BPM, %d bars)" % (
            os.path.basename(song_path) if song_path else "rick_120s.wav", bpm, len(data.get("bars", []))))

    init_feat, goal_feat, mand_lib, inter_lib = build_move_library()
    print("-> Auto-extracted kinematics for %d moves:" % (2 + len(mand_lib) + len(inter_lib)))
    for f in mand_lib + [init_feat, goal_feat]:
        print("   [MAND/IG] %-22s dur=%4.1fs vel=%.2f amp=%.2f E=%.1f" % (
            f["file"], f["dur"], f["raw_vel"], f["raw_amp"], f["energy"]))

    planner = ChoreographyPlanner(init_feat, goal_feat, mand_lib, inter_lib, max_duration=115.0, bpm=bpm)
    result = planner.solve()
    if not result:
        print("ERROR: No valid plan found within constraints.")
        return False

    total_time, total_cost, plan_history, expanded = result
    print("-> A* solved in %d expanded nodes | Cost: %.2f | Duration: %.1fs" % (expanded, total_cost, total_time))

    moves_list, details_list = [], []
    cum_t = 0.0
    print("\n=== Planned Choreography ===")
    for idx, (m_file, m_type, m_dur, is_official, sec_id) in enumerate(plan_history, 1):
        cum_t += m_dur
        moves_list.append(m_file)
        details_list.append({
            "step": idx,
            "type": m_type,
            "file": m_file,
            "official": bool(is_official),
            "section": int(sec_id),
            "estimated_duration": round(m_dur, 2),
        })
        tag = "[OFFICIAL]" if (m_type == "INTERMEDIATE" and is_official) else ""
        print("Step %02d [sec=%d]: [%-12s] %-28s (~%4.1fs, Cum: %5.1fs) %s" % (
            idx, sec_id, m_type, m_file, m_dur, cum_t, tag))

    output_data = {
        "song_file": os.path.basename(song_path) if song_path else "rick_120s.mp3",
        "bpm": bpm,
        "phase": phase,
        "total_duration": round(cum_t, 1),
        "moves": moves_list,
        "details": details_list,
    }
    with open("choreography_plan.json", "w") as f:
        json.dump(output_data, f, indent=2)

    off_used = sum(1 for item in plan_history if item[1] == "INTERMEDIATE" and item[3])
    inter_total = sum(1 for item in plan_history if item[1] == "INTERMEDIATE")
    print("\nDuration: %.1fs (<120s) | Intermediate: %d (Official Slide 16/17: %d >= 5)" % (
        cum_t, inter_total, off_used))
    print("Saved choreography_plan.json successfully.")
    return True


if __name__ == "__main__":
    song_input = None
    args = sys.argv[1:]
    for idx, a in enumerate(args):
        if a in ["--music", "-m"] and idx + 1 < len(args):
            song_input = args[idx + 1]
    generate_full_choreography(song_input)
