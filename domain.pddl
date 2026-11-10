(define (domain nao_choreography)
  (:requirements :strips :typing)
  (:types
    posture move phase loc
  )

  (:predicates
    (at_posture ?p - posture)
    (at_loc ?l - loc)
    (current_phase ?ph - phase)
    (next_phase ?from - phase ?to - phase)
    (mandatory_done ?ph - phase)
    (move_done ?m - move)
    (valid_pre ?m - move ?p - posture)
    (valid_post ?m - move ?p - posture)
    (is_mandatory ?m - move ?ph - phase)
    (allowed_in_phase ?m - move ?ph - phase)
    (loc_transition ?m - move ?from_loc - loc ?to_loc - loc)
  )

  ;; Execute mandatory transition move advancing sequence P1 -> P2 -> P3 -> P4 -> P5 -> P6
  (:action execute_mandatory
    :parameters (?m - move ?from_pos - posture ?to_pos - posture ?curr - phase ?next - phase)
    :precondition (and
      (current_phase ?curr)
      (next_phase ?curr ?next)
      (is_mandatory ?m ?curr)
      (at_posture ?from_pos)
      (valid_pre ?m ?from_pos)
      (valid_post ?m ?to_pos)
    )
    :effect (and
      (not (at_posture ?from_pos))
      (at_posture ?to_pos)
      (not (current_phase ?curr))
      (current_phase ?next)
      (mandatory_done ?curr)
      (move_done ?m)
    )
  )

  ;; Execute stationary intermediate move in its designated musical phase
  (:action execute_intermediate
    :parameters (?m - move ?from_pos - posture ?to_pos - posture ?ph - phase)
    :precondition (and
      (current_phase ?ph)
      (allowed_in_phase ?m ?ph)
      (at_posture ?from_pos)
      (valid_pre ?m ?from_pos)
      (valid_post ?m ?to_pos)
    )
    :effect (and
      (not (at_posture ?from_pos))
      (at_posture ?to_pos)
      (move_done ?m)
    )
  )

  ;; Execute displacement intermediate move in its designated musical phase
  (:action execute_displacement
    :parameters (?m - move ?from_pos - posture ?to_pos - posture ?from_l - loc ?to_l - loc ?ph - phase)
    :precondition (and
      (current_phase ?ph)
      (allowed_in_phase ?m ?ph)
      (at_posture ?from_pos)
      (valid_pre ?m ?from_pos)
      (valid_post ?m ?to_pos)
      (at_loc ?from_l)
      (loc_transition ?m ?from_l ?to_l)
    )
    :effect (and
      (not (at_posture ?from_pos))
      (at_posture ?to_pos)
      (not (at_loc ?from_l))
      (at_loc ?to_l)
      (move_done ?m)
    )
  )
)
