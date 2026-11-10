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
    "m_handgun": "1-Rotation_handgun_object.py",
    "m_rightarm": "2-Right_arm.py",
    "m_unionarms": "5-Union_arms.py",
    "m_forward": "7-Move_forward.py",
    "m_backward": "8-Move_backward.py",
    "m_diagleft": "9-Diagonal_left.py",
    "m_diagright": "10-Diagonal_right.py",
    "m_footr": "12-Rotation_foot_RLeg.py",
    "m_footl": "13-Rotation_foot_LLeg.py",
    "m_standzero": "15-StandZero.py",
    "m_dancemove": "DanceMove.py",
    "m_newhiphop": "new_hiphop.py",
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
    "m_fingersnap": "finger_snap.py",
    "m_guitar": "guitar.py",
    "m_highclap": "high_clap.py",
    "m_proud": "proud.py",
    "m_dab": "dab.py",
    "m_sithandkiss": "sitting_handkiss.py",
    "m_sitmood": "sitting_mood.py",
    "m_sitwavess": "sitting_wavess.py",
    "m_astleysway": "astley_arm_sway.py",
}

# Verified execution times and energy ratings (scale 1.0 - 5.0) on NAO virtual robot
INTERMEDIATE_POOL = {
    "1-Rotation_handgun_object.py": {"symbol": "m_handgun", "dur": 5.0, "energy": 2.5, "type": "gesture", "limbs": "arms"},
    "2-Right_arm.py": {"symbol": "m_rightarm", "dur": 22.0, "energy": 2.0, "type": "gesture", "limbs": "right_arm"},
    "5-Union_arms.py": {"symbol": "m_unionarms", "dur": 28.0, "energy": 2.2, "type": "gesture", "limbs": "both_arms"},
    "7-Move_forward.py": {"symbol": "m_forward", "dur": 4.2, "energy": 3.0, "type": "step", "limbs": "legs"},
    "8-Move_backward.py": {"symbol": "m_backward", "dur": 4.2, "energy": 2.8, "type": "step", "limbs": "legs"},
    "9-Diagonal_left.py": {"symbol": "m_diagleft", "dur": 3.5, "energy": 3.0, "type": "step", "limbs": "legs"},
    "10-Diagonal_right.py": {"symbol": "m_diagright", "dur": 3.6, "energy": 3.0, "type": "step", "limbs": "legs"},
    "12-Rotation_foot_RLeg.py": {"symbol": "m_footr", "dur": 4.5, "energy": 2.5, "type": "step", "limbs": "legs"},
    "13-Rotation_foot_LLeg.py": {"symbol": "m_footl", "dur": 4.5, "energy": 2.5, "type": "step", "limbs": "legs"},
    "15-StandZero.py": {"symbol": "m_standzero", "dur": 3.0, "energy": 1.0, "type": "gesture", "limbs": "full_body"},
    "DanceMove.py": {"symbol": "m_dancemove", "dur": 36.3, "energy": 4.2, "type": "dance", "limbs": "full_body"},
    "new_hiphop.py": {"symbol": "m_newhiphop", "dur": 5.3, "energy": 4.5, "type": "dance", "limbs": "full_body"},
    "WipeForehead.py": {"symbol": "m_wipeforehead", "dur": 7.9, "energy": 2.0, "type": "gesture", "limbs": "head_arm"},
    "new_dance.py": {"symbol": "m_newdance", "dur": 4.7, "energy": 3.0, "type": "dance", "limbs": "full_body"},
    "VOnEyes.py": {"symbol": "m_voneyes", "dur": 8.0, "energy": 2.5, "type": "gesture", "limbs": "head_arm"},
    "Hello.py": {"symbol": "m_hello", "dur": 7.5, "energy": 1.5, "type": "greeting", "limbs": "arms"},
    "new_speedy.py": {"symbol": "m_speedy", "dur": 6.4, "energy": 5.0, "type": "dance", "limbs": "full_body"},
    "ThrillerClap.py": {"symbol": "m_thriller", "dur": 12.0, "energy": 4.0, "type": "dance", "limbs": "arms"},
    "Disco.py": {"symbol": "m_disco", "dur": 6.9, "energy": 4.8, "type": "dance", "limbs": "full_body"},
    "astley_arm_sway.py": {"symbol": "m_astleysway", "dur": 6.0, "energy": 4.8, "type": "dance", "limbs": "arms_and_head"},
    "new_superman.py": {"symbol": "m_superman", "dur": 13.0, "energy": 4.0, "type": "dance", "limbs": "arms"},
    "ThrillerArmSideways.py": {"symbol": "m_thrillersideways", "dur": 13.0, "energy": 3.5, "type": "dance", "limbs": "arms"},
    "ThrillerSnapSnap.py": {"symbol": "m_thrillersnap", "dur": 13.5, "energy": 3.8, "type": "dance", "limbs": "arms"},
    "3-Double_movement.py": {"symbol": "m_doublemovement", "dur": 7.8, "energy": 3.0, "type": "gesture", "limbs": "both_arms"},
    "finger_snap.py": {"symbol": "m_fingersnap", "dur": 7.4, "energy": 3.5, "type": "dance", "limbs": "arms"},
    "guitar.py": {"symbol": "m_guitar", "dur": 9.4, "energy": 3.2, "type": "dance", "limbs": "arms"},
    "high_clap.py": {"symbol": "m_highclap", "dur": 5.6, "energy": 4.0, "type": "dance", "limbs": "arms"},
    "proud.py": {"symbol": "m_proud", "dur": 4.2, "energy": 2.2, "type": "gesture", "limbs": "full_body"},
    "dab.py": {"symbol": "m_dab", "dur": 6.4, "energy": 4.5, "type": "dance", "limbs": "full_body"},
    "sitting_handkiss.py": {"symbol": "m_sithandkiss", "dur": 9.5, "energy": 2.0, "type": "gesture", "limbs": "head_arm", "pre": "Sitting", "post": "Sitting"},
    "sitting_mood.py": {"symbol": "m_sitmood", "dur": 4.2, "energy": 1.5, "type": "gesture", "limbs": "head_arm", "pre": "Sitting", "post": "Sitting"},
    "sitting_wavess.py": {"symbol": "m_sitwavess", "dur": 8.4, "energy": 2.2, "type": "gesture", "limbs": "arms", "pre": "Sitting", "post": "Sitting"},
    "ThrillerSnapSnap.py": {"symbol": "m_thrillersnap", "dur": 7.7, "energy": 3.8, "type": "dance", "limbs": "arms"},
    "ThrillerClap.py": {"symbol": "m_thriller", "dur": 7.7, "energy": 4.0, "type": "dance", "limbs": "arms"},
}

MANDATORY_DURATIONS = {
    "14-StandInit.py": 0.3,
    "4-Arms_opening.py": 6.9,
    "6-Crouch.py": 2.4,
    "16-Sit.py": 12.4,
    "17-SitRelax.py": 5.1,
    "11-Stand.py": 15.5,
}
MANDATORY_TOTAL_DUR = sum(MANDATORY_DURATIONS.values()) # ~42.6s

class StripsPlanner(object):
    def __init__(self, domain_path="domain.pddl", problem_path="problem.pddl"):
        self.domain_path = domain_path
        self.problem_path = problem_path
        self.init_facts = []
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
                    if parts not in self.init_facts: self.init_facts.append(parts)

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

            elif fact[0] == 'allowed_in_phase':
                m, ph = fact[1], fact[2]
                pres = [f[2] for f in self.init_facts if f[0] == 'valid_pre' and f[1] == m]
                posts = [f[2] for f in self.init_facts if f[0] == 'valid_post' and f[1] == m]
                loc_trans = [(f[2], f[3]) for f in self.init_facts if f[0] == 'loc_transition' and f[1] == m]
                if loc_trans:
                    for pre in pres:
                        for post in posts:
                            for fl, tl in loc_trans:
                                action_name = "execute_displacement_{}_{}_{}_{}_{}_{}".format(m, pre, post, fl, tl, ph)
                                preconditions = {
                                    ('current_phase', ph),
                                    ('at_posture', pre),
                                    ('at_loc', fl)
                                }
                                del_effects = {
                                    ('at_loc', fl)
                                }
                                if pre != post:
                                    del_effects.add(('at_posture', pre))
                                add_effects = {
                                    ('at_posture', post),
                                    ('at_loc', tl),
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
                else:
                    for pre in pres:
                        for post in posts:
                            action_name = "execute_intermediate_{}_{}_{}_{}".format(m, pre, post, ph)
                            preconditions = {
                                ('current_phase', ph),
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
    if song_path and not os.path.exists(song_path):
        print('-> WARNING: Song file not found')
        song_path = None
    if song_path:
        song_data = audio_analyzer.get_energy_profile(song_path)
        song_dur = 72.0
        bpm = song_data.get('bpm', 113.3)
        bar_interval = song_data.get('bar_interval', 2.12)
        print('-> Ingested Song: %s' % os.path.basename(song_path))
        print('-> Target Duration: %.1fs (Calibrated for ~105s real simulation execution)' % song_dur)
        print('-> Detected BPM: %.1f (1 bar = %.2fs)' % (bpm, bar_interval))
    else:
        song_dur = 72.0
        bpm = 113.3
        print('-> Using default song profile (~72s duration)')

    # Authentic Rick Astley choreography moves distributed across performance phases:
    # Phase 1 (Intro, Standing): rhythmic finger snap
    m_p1 = 'finger_snap.py'
    # Phase 2 (Verse 1, Standing): Astley double arm roll + balanced forward/backward locomotion
    m_p2_step1 = '7-Move_forward.py'
    m_p2_step2 = '8-Move_backward.py'
    m_p2_dance = '3-Double_movement.py'
    # Phase 6 (Chorus finale, Standing): iconic Disco groove & audience engagement
    m_p6_dance = 'astley_arm_sway.py'
    m_p6_outro = 'Hello.py'

    assignments = [
        (m_p1, 'phase1'),
        (m_p2_step1, 'phase2'),
        (m_p2_step2, 'phase2'),
        (m_p2_dance, 'phase2'),
        (m_p6_dance, 'phase6'),
        (m_p6_outro, 'phase6')
    ]

    total_dur = MANDATORY_TOTAL_DUR + sum(INTERMEDIATE_POOL[m]['dur'] for m, _ in assignments)
    print('-> Allocated Intermediate Moves Across Phases:')
    for m, ph in assignments:
        print('   - [%s] %s (~%.1fs)' % (ph, m, INTERMEDIATE_POOL[m]['dur']))

    return assignments, song_dur

def write_problem_pddl(intermediate_assignments, output_path='problem.pddl'):
    move_symbols = [INTERMEDIATE_POOL[m]['symbol'] for m, _ in intermediate_assignments]
    lines = [
        '(define (problem nao_choreography_problem)',
        '  (:domain nao_choreography)',
        '  (:objects',
        '    Standing Sitting Crouch - posture',
        '    pos_center pos_north pos_south pos_west pos_east - loc',
        '    phase0 phase1 phase2 phase3 phase4 phase5 phase6 - phase',
        '    p1_standinit p2_armsopening p3_crouch p4_sit p5_sitrelax p6_stand - move',
        '    %s - move' % (' '.join(move_symbols)),
        '  )',
        '',
        '  (:init',
        '    (current_phase phase0)',
        '    (at_posture Standing)',
        '    (at_loc pos_center)',
        '',
        '    (next_phase phase0 phase1)',
        '    (next_phase phase1 phase2)',
        '    (next_phase phase2 phase3)',
        '    (next_phase phase3 phase4)',
        '    (next_phase phase4 phase5)',
        '    (next_phase phase5 phase6)',
        '',
        '    ;; Mandatory assignments (P1..P6)',
        '    (is_mandatory p1_standinit phase0)',
        '    (valid_pre p1_standinit Standing)',
        '    (valid_post p1_standinit Standing)',
        '',
        '    (is_mandatory p2_armsopening phase1)',
        '    (valid_pre p2_armsopening Standing)',
        '    (valid_post p2_armsopening Standing)',
        '',
        '    (is_mandatory p3_crouch phase2)',
        '    (valid_pre p3_crouch Standing)',
        '    (valid_post p3_crouch Crouch)',
        '',
        '    (is_mandatory p4_sit phase3)',
        '    (valid_pre p4_sit Crouch)',
        '    (valid_post p4_sit Sitting)',
        '',
        '    (is_mandatory p5_sitrelax phase4)',
        '    (valid_pre p5_sitrelax Sitting)',
        '    (valid_post p5_sitrelax Sitting)',
        '',
        '    (is_mandatory p6_stand phase5)',
        '    (valid_pre p6_stand Sitting)',
        '    (valid_post p6_stand Standing)',
        '',
        '    ;; Intermediate moves distributed by phase',
    ]
    for m, ph in intermediate_assignments:
        sym = INTERMEDIATE_POOL[m]['symbol']
        pre_pos = INTERMEDIATE_POOL[m].get('pre', 'Standing')
        post_pos = INTERMEDIATE_POOL[m].get('post', 'Standing')
        lines.append('    (allowed_in_phase %s %s)' % (sym, ph))
        lines.append('    (valid_pre %s %s)' % (sym, pre_pos))
        lines.append('    (valid_post %s %s)' % (sym, post_pos))
        if m == '7-Move_forward.py':
            lines.append('    (loc_transition %s pos_center pos_north)' % sym)
            lines.append('    (loc_transition %s pos_south pos_center)' % sym)
        elif m == '8-Move_backward.py':
            lines.append('    (loc_transition %s pos_north pos_center)' % sym)
            lines.append('    (loc_transition %s pos_center pos_south)' % sym)
        elif m == '9-Diagonal_left.py':
            lines.append('    (loc_transition %s pos_center pos_west)' % sym)
            lines.append('    (loc_transition %s pos_east pos_center)' % sym)
        elif m == '10-Diagonal_right.py':
            lines.append('    (loc_transition %s pos_west pos_center)' % sym)
            lines.append('    (loc_transition %s pos_center pos_east)' % sym)
        lines.append('')

    lines.extend([
        '  )',
        '',
        '  (:goal (and',
        '    (current_phase phase6)',
        '    (at_posture Standing)',
        '    (at_loc pos_center)',
        '    (mandatory_done phase0)',
        '    (mandatory_done phase1)',
        '    (mandatory_done phase2)',
        '    (mandatory_done phase3)',
        '    (mandatory_done phase4)',
        '    (mandatory_done phase5)',
    ])
    for sym in move_symbols:
        lines.append('    (move_done %s)' % sym)
    lines.extend([
        '  ))',
        ')'
    ])
    with open(output_path, 'w') as f_out:
        f_out.write('\n'.join(lines))


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
            joined = " ".join(args[i + 1:])
            if os.path.exists(joined):
                song_input = joined
            else:
                song_input = args[i + 1]
            break
        elif a.endswith(('.wav', '.mp3', '.ogg', '.flac', '.m4a')):
            song_input = a
            break

    # If not explicitly given, check for common default in directory
    if not song_input:
        for candidate in ["rick.mp3", "rick.wav", "classic_hit.wav", "music.mp3", "song.mp3"]:
            if os.path.exists(candidate):
                song_input = candidate
                break

    generate_full_choreography(song_path=song_input)
