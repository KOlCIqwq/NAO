(define (domain nao_choreography)
  (:requirements :strips :typing)
  (:types
    posture move phase
  )

  (:predicates
    (at_posture ?p - posture)
    (current_phase ?ph - phase)
    (next_phase ?from - phase ?to - phase)
    (mandatory_done ?ph - phase)
    (move_done ?m - move)
    (valid_pre ?m - move ?p - posture)
    (valid_post ?m - move ?p - posture)
    (is_mandatory ?m - move ?ph - phase)
    (requires_phase ?m - move ?ph - phase)
  )

  (:action execute_mandatory_move
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

  (:action execute_intermediate_move
    :parameters (?m - move ?from_pos - posture ?to_pos - posture ?curr - phase)
    :precondition (and
      (current_phase ?curr)
      (requires_phase ?m ?curr)
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
)
