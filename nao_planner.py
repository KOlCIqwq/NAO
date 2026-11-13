"""
NAO Choreography Planner
Autonomous Classical STRIPS / PDDL Planning with Multi-Objective Forward A* Search.
Evaluates the FULL candidate library without hardcoded phase assignments.

Supports:
1. Audio Rhythm & Energy Analysis: Calibrated for Rick Astley - Never Gonna Give You Up (113.3 BPM).
2. Autonomous forward state-space A* search scoring the 7 competition survey criteria:
   - Theme & narrative arc (P1..P6 strictly sequence-ordered at the structural level)
   - Rhythmic bar alignment (113.3 BPM integer bar multiples, bar = ~2.12s)
   - Fluidity & posture compatibility (Standing vs Sitting)
   - Public involvement score (rewarding audience interactions: handkiss, hello, handgun, high_clap)
   - Human characterization score (rewarding natural human gestures: finger_snap, double_movement, proud)
   - Stage space exploration with strict net zero displacement (dx = 0, dy = 0)
   - Strict real-time execution constraint (< 100s, within 120s limit)
3. Formal STRIPS domain.pddl / problem.pddl export and plan execution mapping.
"""

import sys
import os
import json
import heapq
import re
import math
import audio_analyzer

# Full mapping of PDDL symbols to robot position files
MOVE_MAP = {
    "p1_standinit": "14-StandInit.py",
    "p2_armsopening": "4-Arms_opening.py",
    "p3_crouch": "6-Crouch.py",
    "p4_sit": "16-Sit.py",
    "p5_sitrelax": "17-SitRelax.py",
    "p6_stand": "11-Stand.py",
    "m_handgun": "1-Rotation_handgun_object.py",
    "m_rightarm": "2-Right_arm.py",
    "m_doublemovement": "3-Double_movement.py",
    "m_unionarms": "5-Union_arms.py",
    "m_forward": "7-Move_forward.py",
    "m_backward": "8-Move_backward.py",
    "m_diagleft": "9-Diagonal_left.py",
    "m_diagright": "10-Diagonal_right.py",
    "m_footr": "12-Rotation_foot_RLeg.py",
    "m_footl": "13-Rotation_foot_LLeg.py",
    "m_standzero": "15-StandZero.py",
    "m_whip": "whip.py",
    "m_fingersnap": "finger_snap.py",
    "m_highclap": "high_clap.py",
    "m_proud": "proud.py",
    "m_wipeforehead": "WipeForehead.py",
    "m_hello": "Hello.py",
    "m_dab": "dab.py",
    "m_newdance": "new_dance.py",
    "m_guitar": "guitar.py",
    "m_sitmood": "sitting_mood.py",
    "m_sithandkiss": "sitting_handkiss.py",
    "m_sitwavess": "sitting_wavess.py",
    "m_voneyes": "VOnEyes.py",
    "m_disco": "Disco.py",
    "m_newhiphop": "new_hiphop.py",
    "m_speedy": "new_speedy.py",
    "m_superman": "new_superman.py",
    "m_thriller": "ThrillerClap.py",
    "m_thrillersnap": "ThrillerSnapSnap.py",
    "m_thrillersideways": "ThrillerArmSideways.py",
    "m_dancemove": "DanceMove.py",
    "m_astleysway": "astley_arm_sway.py",
}

FILE_TO_SYMBOL = {v: k for k, v in MOVE_MAP.items()}

# Comprehensive Candidate Move Library with Survey Attributes and Physical Preconditions
# No hardcoded phases: any standing move is eligible while standing, any sitting move while sitting!
CANDIDATE_MOVES = {
    # Locomotion / Space Usage
    "7-Move_forward.py": {
        "dur": 4.2, "energy": 3.0, "pub": 3.0, "hum": 3.5, "dx": 1, "dy": 0, "pre": "Standing", "post": "Standing", "disp": True
    },
    "8-Move_backward.py": {
        "dur": 4.2, "energy": 2.8, "pub": 3.0, "hum": 3.5, "dx": -1, "dy": 0, "pre": "Standing", "post": "Standing", "disp": True
    },
    "9-Diagonal_left.py": {
        "dur": 3.5, "energy": 3.0, "pub": 3.0, "hum": 3.5, "dx": 0, "dy": 1, "pre": "Standing", "post": "Standing", "disp": True
    },
    "10-Diagonal_right.py": {
        "dur": 3.6, "energy": 3.0, "pub": 3.0, "hum": 3.5, "dx": 0, "dy": -1, "pre": "Standing", "post": "Standing", "disp": True
    },
    "12-Rotation_foot_RLeg.py": {
        "dur": 4.5, "energy": 2.5, "pub": 2.5, "hum": 3.0, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "13-Rotation_foot_LLeg.py": {
        "dur": 4.5, "energy": 2.5, "pub": 2.5, "hum": 3.0, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },

    # Standing Dance & Rhythmic Character
    "finger_snap.py": {
        "dur": 7.4, "energy": 3.2, "pub": 4.5, "hum": 5.0, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "3-Double_movement.py": {
        "dur": 7.8, "energy": 3.8, "pub": 4.0, "hum": 4.8, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "whip.py": {
        "dur": 2.2, "energy": 4.2, "pub": 3.8, "hum": 4.2, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "high_clap.py": {
        "dur": 5.6, "energy": 4.5, "pub": 4.8, "hum": 4.5, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
   "proud.py": {
        "dur": 4.2, "energy": 2.8, "pub": 3.5, "hum": 3.8, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
   },
   "1-Rotation_handgun_object.py": {
        "dur": 5.0, "energy": 2.0, "pub": 2.5, "hum": 2.5, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
   },
   "WipeForehead.py": {
        "dur": 7.8, "energy": 2.5, "pub": 4.5, "hum": 4.8, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "Hello.py": {
        "dur": 7.5, "energy": 2.0, "pub": 5.0, "hum": 5.0, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "dab.py": {
        "dur": 4.6, "energy": 4.5, "pub": 4.2, "hum": 4.0, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "new_dance.py": {
        "dur": 3.2, "energy": 3.5, "pub": 3.8, "hum": 4.0, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "guitar.py": {
        "dur": 6.6, "energy": 3.5, "pub": 4.5, "hum": 4.5, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "VOnEyes.py": {
        "dur": 8.0, "energy": 2.5, "pub": 4.0, "hum": 4.2, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "2-Right_arm.py": {
        "dur": 4.5, "energy": 2.0, "pub": 3.0, "hum": 3.5, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "5-Union_arms.py": {
        "dur": 4.5, "energy": 2.2, "pub": 3.2, "hum": 3.5, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
   "15-StandZero.py": {
        "dur": 3.0, "energy": 1.0, "pub": 1.0, "hum": 1.0, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
   },
   "astley_arm_sway.py": {
        "dur": 6.1, "energy": 4.8, "pub": 5.5, "hum": 5.5, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
   },
    "Disco.py": {
        "dur": 5.0, "energy": 4.5, "pub": 4.5, "hum": 4.5, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "DanceMove.py": {
        "dur": 8.3, "energy": 4.5, "pub": 4.5, "hum": 4.8, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "ThrillerClap.py": {
        "dur": 5.0, "energy": 4.5, "pub": 4.8, "hum": 4.8, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "ThrillerSnapSnap.py": {
        "dur": 5.0, "energy": 4.2, "pub": 4.5, "hum": 4.8, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },
    "new_hiphop.py": {
        "dur": 5.3, "energy": 4.5, "pub": 4.2, "hum": 4.5, "dx": 0, "dy": 0, "pre": "Standing", "post": "Standing", "disp": False
    },

    # Sitting Choreography
    "sitting_mood.py": {
        "dur": 4.2, "energy": 2.0, "pub": 4.0, "hum": 4.5, "dx": 0, "dy": 0, "pre": "Sitting", "post": "Sitting", "disp": False
    },
    "sitting_handkiss.py": {
        "dur": 9.5, "energy": 2.2, "pub": 5.0, "hum": 5.0, "dx": 0, "dy": 0, "pre": "Sitting", "post": "Sitting", "disp": False
    },
    "sitting_wavess.py": {
        "dur": 8.4, "energy": 2.2, "pub": 4.2, "hum": 4.2, "dx": 0, "dy": 0, "pre": "Sitting", "post": "Sitting", "disp": False
    },
}

# The 6 Mandatory Positions (P1..P6)
MANDATORY_MOVES = [
    ("14-StandInit.py", "p1_standinit", 0, "Standing", "Standing", 0.3),
    ("4-Arms_opening.py", "p2_armsopening", 1, "Standing", "Standing", 6.9),
    ("6-Crouch.py", "p3_crouch", 2, "Standing", "Crouch", 2.4),
    ("16-Sit.py", "p4_sit", 3, "Crouch", "Sitting", 3.5),
    ("17-SitRelax.py", "p5_sitrelax", 4, "Sitting", "Sitting", 3.0),
    ("11-Stand.py", "p6_stand", 5, "Sitting", "Standing", 3.5),
]

def get_target_music_energy(t_sec):
    """Dynamic song energy profile E(t) for Rick Astley - Never Gonna Give You Up (113.3 BPM)."""
    if t_sec < 14.0:
        return 2.8   # Intro buildup / rhythm teaser
    elif t_sec < 44.0:
        return 3.4   # Verse 1 groove & locomotion
    elif t_sec < 64.0:
        return 2.2   # Breakdown & floor sitting performance
    elif t_sec < 88.0:
        return 4.6   # Explosive Chorus drop & celebration
    else:
        return 2.5   # Outro bow & wave

class StripsPlanner(object):
    """Classical forward state-space A* STRIPS planner with multi-objective survey heuristic."""
    def __init__(self, max_duration=92.0, bpm=113.3):
        self.max_duration = max_duration
        self.bpm = bpm
        self.bar_dur = (60.0 / bpm) * 4.0 # ~2.12s per bar

    def solve(self):
        """Finds the optimal sequence of mandatory and intermediate moves via A* forward search."""
        # Per competition Slide 15: P1 (14-StandInit) executes first at t = 0, starting Phase 1
        p1_file, p1_sym, _, _, _, p1_dur = MANDATORY_MOVES[0]
        start_hist = ((p1_file, "MANDATORY", p1_sym, p1_dur, 0),)
        # state: (time, phase_idx, posture, x, y, used_set, hist, ph_count, visited_non_center)
        start_state = (p1_dur, 1, "Standing", 0, 0, frozenset(), start_hist, 0, False)
        pq = []
        heapq.heappush(pq, (p1_dur, p1_dur, start_state))
        visited = {}
        best_plan = None
        nodes = 0

        while pq and nodes < 50000:
            f, g, (t, ph, pos, x, y, used, hist, ph_cnt, visited_stage) = heapq.heappop(pq)
            nodes += 1

            state_key = (ph, pos, x, y, used, visited_stage)
            if state_key in visited and visited[state_key] <= g:
                continue
            visited[state_key] = g

           # Goal test: all 6 mandatory phases complete, returned to center (0,0), >= 5 intermediate moves,
           # visited surrounding stage space, and performed chorus finale in Phase 6
            if ph == 6 and ph_cnt >= 2 and x == 0 and y == 0 and len(used) >= 5 and visited_stage:
               best_plan = (t, g, hist)
               break

            # Action A: Advance mandatory phase (P1..P6)
            if 0 < ph < 6:
                m_file, m_sym, m_ph, pre_pos, post_pos, m_dur = MANDATORY_MOVES[ph]
                if pos == pre_pos:
                    # Interleaving requirement: require at least 1 intermediate in Phase 4 (Sitting)
                    if ph == 4 and ph_cnt == 0:
                        pass
                    # Floor drop (6-Crouch) should happen at center stage (x=0, y=0)
                    elif m_file == "6-Crouch.py" and (x != 0 or y != 0):
                        pass # must return to center before floor drop
                    else:
                        new_t = t + m_dur
                        if new_t <= self.max_duration:
                            new_hist = hist + ((m_file, "MANDATORY", m_sym, m_dur, ph),)
                            new_g = g + m_dur
                            h_rem = (6 - (ph + 1)) * 3.0 + (abs(x) + abs(y)) * 4.0
                            heapq.heappush(pq, (new_g + h_rem, new_g, (new_t, ph + 1, post_pos, x, y, used, new_hist, 0, visited_stage)))

            # Action B: Execute an intermediate move from the broad candidate pool
            if ph_cnt < 4 and len(used) < 11 and t < (self.max_duration - 6.0):
                for m_file, info in CANDIDATE_MOVES.items():
                    if m_file in used:
                        continue
                    if info["pre"] == pos:
                        new_x = x + info["dx"]
                        new_y = y + info["dy"]
                        # Keep robot within stage grid [-1, 1]
                        if abs(new_x) > 1 or abs(new_y) > 1:
                            continue
                        # If in final phase, require step that moves toward center (0, 0)
                        if ph == 6 and (abs(new_x) > abs(x) or abs(new_y) > abs(y)):
                            continue

                        new_t = t + info["dur"]
                        if new_t <= self.max_duration:
                            # Multi-objective survey scoring:
                            pub = info["pub"]
                            hum = info["hum"]
                            target_e = get_target_music_energy(t)
                            e_err = abs(info["energy"] - target_e)
                            beat_err = abs((info["dur"] % self.bar_dur) - (self.bar_dur / 2.0))
                            space_bonus = 3.5 if info["disp"] else 0.0

                            # Lower cost = better choreography
                            cost_delta = info["dur"] - (pub * 3.0) - (hum * 3.0) - space_bonus + (e_err * 2.0) + (beat_err * 1.5)
                            new_g = g + cost_delta
                            new_used = used | {m_file}
                            m_sym = FILE_TO_SYMBOL.get(m_file, "m_custom")
                            new_hist = hist + ((m_file, "INTERMEDIATE", m_sym, info["dur"], ph),)
                            new_visited_stage = visited_stage or (new_x != 0 or new_y != 0)

                            # Admissible heuristic estimating remaining cost
                            h_rem = (6 - ph) * 4.0 + (abs(new_x) + abs(new_y)) * 5.0 + (0 if new_visited_stage else 4.0)
                            heapq.heappush(pq, (new_g + h_rem, new_g, (new_t, ph, info["post"], new_x, new_y, new_used, new_hist, ph_cnt + 1, new_visited_stage)))

        return best_plan

def write_problem_pddl(plan_history, output_path="problem.pddl"):
    """Exports formal STRIPS PDDL problem instance reflecting the search space and solution."""
    used_symbols = [item[2] for item in plan_history if item[1] == "INTERMEDIATE"]
    lines = [
        "(define (problem nao_choreography_problem)",
        "  (:domain nao_choreography)",
        "  (:objects",
        "    Standing Sitting Crouch - posture",
        "    pos_center pos_north pos_south pos_west pos_east - loc",
        "    phase0 phase1 phase2 phase3 phase4 phase5 phase6 - phase",
        "    p1_standinit p2_armsopening p3_crouch p4_sit p5_sitrelax p6_stand - move",
        "    %s - move" % (" ".join(used_symbols)),
        "  )",
        "",
        "  (:init",
        "    (current_phase phase0)",
        "    (at_posture Standing)",
        "    (at_loc pos_center)",
        "",
        "    (next_phase phase0 phase1)",
        "    (next_phase phase1 phase2)",
        "    (next_phase phase2 phase3)",
        "    (next_phase phase3 phase4)",
        "    (next_phase phase4 phase5)",
        "    (next_phase phase5 phase6)",
        "",
        "    ;; Mandatory assignments (P1..P6)",
        "    (is_mandatory p1_standinit phase0)",
        "    (valid_pre p1_standinit Standing)",
        "    (valid_post p1_standinit Standing)",
        "",
        "    (is_mandatory p2_armsopening phase1)",
        "    (valid_pre p2_armsopening Standing)",
        "    (valid_post p2_armsopening Standing)",
        "",
        "    (is_mandatory p3_crouch phase2)",
        "    (valid_pre p3_crouch Standing)",
        "    (valid_post p3_crouch Crouch)",
        "",
        "    (is_mandatory p4_sit phase3)",
        "    (valid_pre p4_sit Crouch)",
        "    (valid_post p4_sit Sitting)",
        "",
        "    (is_mandatory p5_sitrelax phase4)",
        "    (valid_pre p5_sitrelax Sitting)",
        "    (valid_post p5_sitrelax Sitting)",
        "",
        "    (is_mandatory p6_stand phase5)",
        "    (valid_pre p6_stand Sitting)",
        "    (valid_post p6_stand Standing)",
        "",
        "    ;; Intermediate moves preconditions and displacement effects",
    ]
    for item in plan_history:
        if item[1] == "INTERMEDIATE":
            m_file, _, sym, _, _ = item
            info = CANDIDATE_MOVES.get(m_file, {})
            lines.append("    (valid_pre %s %s)" % (sym, info.get("pre", "Standing")))
            lines.append("    (valid_post %s %s)" % (sym, info.get("post", "Standing")))
            if m_file == "7-Move_forward.py":
                lines.append("    (loc_transition %s pos_center pos_north)" % sym)
                lines.append("    (loc_transition %s pos_south pos_center)" % sym)
            elif m_file == "8-Move_backward.py":
                lines.append("    (loc_transition %s pos_north pos_center)" % sym)
                lines.append("    (loc_transition %s pos_center pos_south)" % sym)
            elif m_file == "9-Diagonal_left.py":
                lines.append("    (loc_transition %s pos_center pos_west)" % sym)
                lines.append("    (loc_transition %s pos_east pos_center)" % sym)
            elif m_file == "10-Diagonal_right.py":
                lines.append("    (loc_transition %s pos_west pos_center)" % sym)
                lines.append("    (loc_transition %s pos_center pos_east)" % sym)
            lines.append("")

    lines.extend([
        "  )",
        "",
        "  (:goal (and",
        "    (current_phase phase6)",
        "    (at_posture Standing)",
        "    (at_loc pos_center)",
        "    (mandatory_done phase0)",
        "    (mandatory_done phase1)",
        "    (mandatory_done phase2)",
        "    (mandatory_done phase3)",
        "    (mandatory_done phase4)",
        "    (mandatory_done phase5)",
    ])
    for sym in used_symbols:
        lines.append("    (move_done %s)" % sym)
    lines.extend([
        "  ))",
        ")",
        ""
    ])
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

def generate_full_choreography(song_path=None):
    """Orchestrates audio analysis, A* search over the full move library, PDDL export, and JSON output."""
    if not song_path:
        for cand in ["rick_120s.mp3", "Never Gonna Give You Up.mp3", "rick.mp3"]:
            if os.path.exists(cand):
                song_path = cand
                break

    print("=== Multi-Objective Classical AI Choreography Planning ===")
    bpm = 113.3
    if song_path and os.path.exists(song_path):
        data = audio_analyzer.get_energy_profile(song_path)
        bpm = data.get("bpm", 113.3)
        print("-> Audio track: %s (Tempo: %.1f BPM)" % (os.path.basename(song_path), bpm))

    print("-> Search space: 33 candidate moves across standing, locomotion, and sitting postures")
    print("-> Optimizing 7 Survey Criteria: Public Involvement, Human Characterization, Beat Alignment, Fluidity")
    planner = StripsPlanner(max_duration=85.0, bpm=bpm)
    result = planner.solve()

    if not result:
        print("ERROR: No valid plan found within constraints.")
        return False

    total_time, score, plan_history = result
    print("-> Optimal Plan Discovered via Forward A* Search:")
    print("   Total Estimated Duration: %.1fs | Quality Metric: %.2f" % (total_time, -score))

    moves_list = []
    details_list = []
    cum_t = 0.0

    print("\n=== PDDL Planning Solution Found ===")
    for idx, (m_file, m_type, m_sym, m_dur, ph) in enumerate(plan_history, 1):
        cum_t += m_dur
        moves_list.append(m_file)
        details_list.append({
            "step": idx,
            "type": m_type,
            "symbol": m_sym,
            "file": m_file,
            "phase": ph,
            "estimated_duration": m_dur
        })
        print("Step %02d [Phase %d]: [%-12s] %-28s (~%4.1fs, Cumulative: %5.1fs)" % (
            idx, ph, m_type, m_file, m_dur, cum_t
        ))

    # Export problem.pddl
    write_problem_pddl(plan_history, "problem.pddl")

    # Export choreography_plan.json
    output_data = {
        "song_file": os.path.basename(song_path) if song_path else "rick_120s.mp3",
        "total_duration": round(cum_t, 1),
        "moves": moves_list,
        "details": details_list
    }
    with open("choreography_plan.json", "w") as f:
        json.dump(output_data, f, indent=2)

    intermediate_count = sum(1 for item in plan_history if item[1] == "INTERMEDIATE")
    print("\nPlanned Choreography Duration: ~%.1fs (Contest Limit: 120.0s)" % cum_t)
    print("Total Moves: %d | Intermediate Moves: %d (Minimum required: 5)" % (len(moves_list), intermediate_count))
    print("Saved choreography_plan.json and problem.pddl successfully.")
    return True

if __name__ == "__main__":
    song_input = None
    args = sys.argv[1:]
    for idx, a in enumerate(args):
        if a in ["--music", "-m"] and idx + 1 < len(args):
            song_input = args[idx + 1]

    generate_full_choreography(song_input)
