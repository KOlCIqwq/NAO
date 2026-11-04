"""
NAO Choreography Planner
Classical PDDL / STRIPS Planning with Song-Driven Heuristic Optimization.
Runs completely self-contained in pure Python (no external dependencies).

Supports:
1. Generic Audio Analysis: Analyzes ANY generic song file (MP3, WAV, FLAC, etc.) for duration and energy profile.
2. Music-Guided Optimization: Matches move energy (calm gesture vs high-energy dance) and duration to the song's peaks and beat.
3. Formal STRIPS/PDDL Classical Planning: Generates problem.pddl and solves state-space plan with A* search.
"""

import sys
import os
import json
import heapq
import re
import random
import math
import audio_analyzer

MOVE_MAP = {
    "p1_standinit": "14-StandInit.py",
    "p2_armsopening": "4-Arms_opening.py",
    "p3_crouch": "6-Crouch.py",
    "p4_sit": "16-Sit.py",
    "p5_sitrelax": "17-SitRelax.py",
    "p6_stand": "11-Stand.py",
    "m_rightarm": "2-Right_arm.py",
    "m_wipeforehead": "WipeForehead.py",
    "m_newdance": "new_dance.py",
    "m_voneyes": "VOnEyes.py",
    "m_hello": "Hello.py",
    "m_speedy": "new_speedy.py",
    "m_thriller": "ThrillerClap.py",
    "m_disco": "Disco.py",
    "m_superman": "new_superman.py",
    "m_thrillersideways": "ThrillerArmSideways.py",
    "m_thrillersnap": "ThrillerSnapSnap.py",
    "m_doublemovement": "3-Double_movement.py",
}

# Verified execution times and energy ratings (scale 1.0 - 5.0) on NAO virtual robot
INTERMEDIATE_POOL = {
    "2-Right_arm.py": {"symbol": "m_rightarm", "dur": 5.0, "energy": 2.0, "type": "gesture", "limbs": "right_arm"},
    "WipeForehead.py": {"symbol": "m_wipeforehead", "dur": 5.5, "energy": 2.0, "type": "gesture", "limbs": "head_arm"},
    "new_dance.py": {"symbol": "m_newdance", "dur": 7.0, "energy": 3.0, "type": "dance", "limbs": "full_body"},
    "VOnEyes.py": {"symbol": "m_voneyes", "dur": 8.0, "energy": 2.5, "type": "gesture", "limbs": "head_arm"},
    "Hello.py": {"symbol": "m_hello", "dur": 11.0, "energy": 1.5, "type": "greeting", "limbs": "arms"},
    "new_speedy.py": {"symbol": "m_speedy", "dur": 12.0, "energy": 5.0, "type": "dance", "limbs": "full_body"},
    "ThrillerClap.py": {"symbol": "m_thriller", "dur": 12.0, "energy": 4.0, "type": "dance", "limbs": "arms"},
    "Disco.py": {"symbol": "m_disco", "dur": 12.5, "energy": 4.8, "type": "dance", "limbs": "full_body"},
    "new_superman.py": {"symbol": "m_superman", "dur": 13.0, "energy": 4.0, "type": "dance", "limbs": "arms"},
    "ThrillerArmSideways.py": {"symbol": "m_thrillersideways", "dur": 13.0, "energy": 3.5, "type": "dance", "limbs": "arms"},
    "ThrillerSnapSnap.py": {"symbol": "m_thrillersnap", "dur": 13.5, "energy": 3.8, "type": "dance", "limbs": "arms"},
    "3-Double_movement.py": {"symbol": "m_doublemovement", "dur": 26.0, "energy": 3.0, "type": "gesture", "limbs": "both_arms"},
}

MANDATORY_DURATIONS = {
    "14-StandInit.py": 6.0,
    "4-Arms_opening.py": 24.0,
    "6-Crouch.py": 10.0,
    "16-Sit.py": 10.0,
    "17-SitRelax.py": 10.0,
    "11-Stand.py": 16.0,
}
MANDATORY_TOTAL_DUR = sum(MANDATORY_DURATIONS.values()) # 76.0s

class StripsPlanner(object):
    def __init__(self, domain_path="domain.pddl", problem_path="problem.pddl"):
        self.domain_path = domain_path
        self.problem_path = problem_path
        self.init_facts = set()
        self.goal_facts = set()
        self.actions = []
        self._parse_problem()
        self._ground_actions()

    def _strip_comments(self, text):
        return re.sub(r';.*', '', text)

    def _parse_problem(self):
        with open(self.problem_path, 'r') as f:
            content = self._strip_comments(f.read())

        init_match = re.search(r':init\s+(.*?)\s*\(:goal', content, re.DOTALL)
        if init_match:
            init_text = init_match.group(1)
            for atom in re.findall(r'\(([^()]+)\)', init_text):
                parts = tuple(atom.strip().split())
                if parts:
                    self.init_facts.add(parts)

        if '(:goal' in content:
            goal_text = content[content.find('(:goal'):]
            for atom in re.findall(r'\(([^()]+)\)', goal_text):
                parts = tuple(atom.strip().split())
                if parts and parts[0] != 'and':
                    self.goal_facts.add(parts)

    def _ground_actions(self):
        for fact in self.init_facts:
            if fact[0] == 'is_mandatory':
                m, curr = fact[1], fact[2]
                next_phases = [f[2] for f in self.init_facts if f[0] == 'next_phase' and f[1] == curr]
                pres = [f[2] for f in self.init_facts if f[0] == 'valid_pre' and f[1] == m]
                posts = [f[2] for f in self.init_facts if f[0] == 'valid_post' and f[1] == m]
                for nxt in next_phases:
                    for pre in pres:
                        for post in posts:
                            action_name = "execute_mandatory_{}_{}_{}".format(m, pre, post)
                            preconditions = {
                                ('current_phase', curr),
                                ('at_posture', pre)
                            }
                            del_effects = {
                                ('current_phase', curr),
                                ('at_posture', pre)
                            }
                            add_effects = {
                                ('current_phase', nxt),
                                ('at_posture', post),
                                ('mandatory_done', curr),
                                ('move_done', m)
                            }
                            self.actions.append({
                                'name': action_name,
                                'move': m,
                                'is_mandatory': True,
                                'pre': preconditions,
                                'del': del_effects,
                                'add': add_effects
                            })

            elif fact[0] == 'requires_phase':
                m, curr = fact[1], fact[2]
                pres = [f[2] for f in self.init_facts if f[0] == 'valid_pre' and f[1] == m]
                posts = [f[2] for f in self.init_facts if f[0] == 'valid_post' and f[1] == m]
                for pre in pres:
                    for post in posts:
                        action_name = "execute_intermediate_{}_{}_{}".format(m, pre, post)
                        preconditions = {
                            ('current_phase', curr),
                            ('at_posture', pre)
                        }
                        del_effects = {
                            ('at_posture', pre)
                        } if pre != post else set()
                        add_effects = {
                            ('at_posture', post),
                            ('move_done', m)
                        }
                        self.actions.append({
                            'name': action_name,
                            'move': m,
                            'is_mandatory': False,
                            'pre': preconditions,
                            'del': del_effects,
                            'add': add_effects
                        })

    def heuristic(self, state):
        return len(self.goal_facts - state)

    def solve(self):
        start_state = frozenset(self.init_facts)
        frontier = [(self.heuristic(start_state), 0, start_state, [])]
        visited = {start_state: 0}

        while frontier:
            h, g, current_state, plan = heapq.heappop(frontier)

            if self.goal_facts.issubset(current_state):
                return plan

            for act in self.actions:
                if act['pre'].issubset(current_state):
                    if not act['is_mandatory'] and act['move'] in [p['move'] for p in plan]:
                        continue

                    next_state = frozenset((current_state - act['del']) | act['add'])
                    cost = g + 1
                    if next_state not in visited or cost < visited[next_state]:
                        visited[next_state] = cost
                        new_h = self.heuristic(next_state)
                        heapq.heappush(frontier, (cost + new_h, cost, next_state, plan + [act]))

        return None

def optimize_moves_for_song(song_path=None):
    """
    Simulated Annealing optimization guided by the specific song:
    1. Matches song duration (strictly <= 120s limit).
    2. Matches the song's energy envelope over time (climax/chorus vs gentle verse).
    3. Maximizes limb and movement diversity.
    """
    if song_path and os.path.exists(song_path):
        song_data = audio_analyzer.get_energy_profile(song_path)
        song_dur = min(118.0, song_data['duration'])
        energy_profile = song_data['profile']
        print("-> Ingested Song: '{}'".format(os.path.basename(song_path)))
        print("-> Target Duration: {:.1f}s (Capped at 118s limit)".format(song_dur))
        print("-> Song Energy Curve: {}".format(energy_profile))
    else:
        song_dur = 114.0
        energy_profile = [2.0, 2.5, 3.5, 4.5, 5.0, 4.0, 2.5, 2.0, 1.5, 1.0]
        print("-> Using default song profile (~114s duration)")

    target_intermediate_dur = max(25.0, song_dur - MANDATORY_TOTAL_DUR)

    def cost(moves):
        total_intermediate = sum(INTERMEDIATE_POOL[m]["dur"] for m in moves)
        total_dur = MANDATORY_TOTAL_DUR + total_intermediate

        # Strict duration wall at song_dur and 118s
        time_penalty = abs(total_dur - song_dur) * 10.0
        if total_dur > 118.0:
            time_penalty += (total_dur - 118.0) * 200.0

        # Energy alignment score: compare moves energy to song profile
        energy_diff = 0.0
        cur_time = MANDATORY_DURATIONS["14-StandInit.py"]
        for m in moves:
            # Map time to slice index in energy profile
            slice_idx = min(len(energy_profile) - 1, int((cur_time / max(song_dur, 1.0)) * len(energy_profile)))
            target_energy = energy_profile[slice_idx]
            move_energy = INTERMEDIATE_POOL[m]["energy"]
            energy_diff += abs(move_energy - target_energy)
            cur_time += INTERMEDIATE_POOL[m]["dur"]

        energy_penalty = energy_diff * 4.0

        # Variety bonus: reward distinct types and limb groups
        types = set(INTERMEDIATE_POOL[m]["type"] for m in moves)
        limbs = set(INTERMEDIATE_POOL[m]["limbs"] for m in moves)
        variety_penalty = (4 - len(types)) * 6.0 + (5 - len(limbs)) * 5.0

        return time_penalty + energy_penalty + variety_penalty

    pool_keys = list(INTERMEDIATE_POOL.keys())
    current = random.sample(pool_keys, 5)
    best = list(current)
    best_cost = cost(best)
    temp = 120.0
    alpha = 0.95

    for _ in range(500):
        neighbor = list(current)
        action = random.choice(["swap", "replace"])
        if action == "swap" and len(neighbor) > 1:
            i1, i2 = random.sample(range(len(neighbor)), 2)
            neighbor[i1], neighbor[i2] = neighbor[i2], neighbor[i1]
        elif action == "replace":
            unused = [m for m in pool_keys if m not in neighbor]
            if unused:
                r_idx = random.randint(0, len(neighbor) - 1)
                neighbor[r_idx] = random.choice(unused)

        c_new = cost(neighbor)
        c_cur = cost(current)
        if c_new < c_cur or math.exp(-(c_new - c_cur) / max(temp, 1e-4)) > random.random():
            current = neighbor
            if c_new < best_cost:
                best = list(neighbor)
                best_cost = c_new
        temp *= alpha

    return best, song_dur

def write_problem_pddl(intermediate_moves, output_path="problem.pddl"):
    move_symbols = [INTERMEDIATE_POOL[m]["symbol"] for m in intermediate_moves]
    lines = [
        "(define (problem nao_choreography_problem)",
        "  (:domain nao_choreography)",
        "  (:objects",
        "    Standing Sitting Crouch - posture",
        "    phase0 phase1 phase2 phase3 phase4 phase5 phase6 - phase",
        "    p1_standinit p2_armsopening p3_crouch p4_sit p5_sitrelax p6_stand - move",
        "    {} - move".format(" ".join(move_symbols)),
        "  )",
        "",
        "  (:init",
        "    (current_phase phase0)",
        "    (at_posture Standing)",
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
        "    ;; Intermediate moves",
    ]
    for sym in move_symbols:
        lines.append("    (requires_phase {} phase1)".format(sym))
        lines.append("    (valid_pre {} Standing)".format(sym))
        lines.append("    (valid_post {} Standing)".format(sym))
        lines.append("")

    lines.extend([
        "  )",
        "",
        "  (:goal (and",
        "    (current_phase phase6)",
        "    (at_posture Standing)",
        "    (mandatory_done phase0)",
        "    (mandatory_done phase1)",
        "    (mandatory_done phase2)",
        "    (mandatory_done phase3)",
        "    (mandatory_done phase4)",
        "    (mandatory_done phase5)",
    ])
    for sym in move_symbols:
        lines.append("    (move_done {})".format(sym))
    lines.extend([
        "  ))",
        ")"
    ])
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

def generate_full_choreography(song_path=None):
    print("=== Song-Driven Planning Optimization ===")
    selected_intermediates, target_dur = optimize_moves_for_song(song_path)
    print("-> Selected Intermediate Moves: {}".format(selected_intermediates))
    write_problem_pddl(selected_intermediates)

    planner = StripsPlanner()
    plan = planner.solve()
    if not plan:
        print("Error: Planner could not find a valid plan!")
        return None

    result_sequence = []
    total_time = 0.0
    final_output = []

    print("\n=== PDDL Planning Solution Found ===")
    for i, act in enumerate(plan, 1):
        m_symbol = act['move']
        file_name = MOVE_MAP.get(m_symbol, m_symbol)
        dur = INTERMEDIATE_POOL.get(file_name, {}).get("dur") or MANDATORY_DURATIONS.get(file_name, 10.0)
        total_time += dur
        tag = "MANDATORY" if act['is_mandatory'] else "INTERMEDIATE"
        print("Step {:02d}: [{:12}] {:<28} (~{:.1f}s, Cumulative: {:.1f}s)".format(i, tag, file_name, dur, total_time))
        result_sequence.append({
            'step': i,
            'type': tag,
            'symbol': m_symbol,
            'file': file_name,
            'estimated_duration': dur
        })
        final_output.append(file_name)

    print("\nPlanned Choreography Duration: ~{:.1f}s (Song Target: {:.1f}s, Contest Limit: 120.0s)".format(total_time, target_dur))
    print("Total Moves: {} | Intermediate Moves: {}".format(len(result_sequence), sum(1 for x in result_sequence if x['type'] == 'INTERMEDIATE')))

    with open('choreography_plan.json', 'w') as f:
        json.dump({
            'song_file': song_path if song_path else "default",
            'total_duration': total_time,
            'moves': final_output,
            'details': result_sequence
        }, f, indent=2)
    print("Saved choreography_plan.json successfully.")
    return result_sequence

if __name__ == '__main__':
    song_input = None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a in ['--music', '-m', '--song'] and i + 1 < len(args):
            song_input = args[i + 1]
            break
        elif a.endswith(('.wav', '.mp3', '.ogg', '.flac', '.m4a')):
            song_input = a
            break

    # If not explicitly given, check for common default in directory
    if not song_input:
        for candidate in ["classic_hit.wav", "music.mp3", "song.mp3"]:
            if os.path.exists(candidate):
                song_input = candidate
                break

    generate_full_choreography(song_path=song_input)
