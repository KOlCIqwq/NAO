(define (problem nao_choreography_problem)
  (:domain nao_choreography)
  (:objects
    Standing Sitting Crouch - posture
    pos_center pos_north pos_south pos_west pos_east - loc
    phase0 phase1 phase2 phase3 phase4 phase5 phase6 - phase
    p1_standinit p2_armsopening p3_crouch p4_sit p5_sitrelax p6_stand - move
    m_astleysway m_hello m_fingersnap m_thriller m_thrillersnap m_newdance m_diagleft m_diagright m_sithandkiss m_highclap m_disco - move
  )

  (:init
    (current_phase phase0)
    (at_posture Standing)
    (at_loc pos_center)

    (next_phase phase0 phase1)
    (next_phase phase1 phase2)
    (next_phase phase2 phase3)
    (next_phase phase3 phase4)
    (next_phase phase4 phase5)
    (next_phase phase5 phase6)

    ;; Mandatory assignments (P1..P6)
    (is_mandatory p1_standinit phase0)
    (valid_pre p1_standinit Standing)
    (valid_post p1_standinit Standing)

    (is_mandatory p2_armsopening phase1)
    (valid_pre p2_armsopening Standing)
    (valid_post p2_armsopening Standing)

    (is_mandatory p3_crouch phase2)
    (valid_pre p3_crouch Standing)
    (valid_post p3_crouch Crouch)

    (is_mandatory p4_sit phase3)
    (valid_pre p4_sit Crouch)
    (valid_post p4_sit Sitting)

    (is_mandatory p5_sitrelax phase4)
    (valid_pre p5_sitrelax Sitting)
    (valid_post p5_sitrelax Sitting)

    (is_mandatory p6_stand phase5)
    (valid_pre p6_stand Sitting)
    (valid_post p6_stand Standing)

    ;; Intermediate moves preconditions and displacement effects
    (valid_pre m_astleysway Standing)
    (valid_post m_astleysway Standing)

    (valid_pre m_hello Standing)
    (valid_post m_hello Standing)

    (valid_pre m_fingersnap Standing)
    (valid_post m_fingersnap Standing)

    (valid_pre m_thriller Standing)
    (valid_post m_thriller Standing)

    (valid_pre m_thrillersnap Standing)
    (valid_post m_thrillersnap Standing)

    (valid_pre m_newdance Standing)
    (valid_post m_newdance Standing)

    (valid_pre m_diagleft Standing)
    (valid_post m_diagleft Standing)
    (loc_transition m_diagleft pos_center pos_west)
    (loc_transition m_diagleft pos_east pos_center)

    (valid_pre m_diagright Standing)
    (valid_post m_diagright Standing)
    (loc_transition m_diagright pos_west pos_center)
    (loc_transition m_diagright pos_center pos_east)

    (valid_pre m_sithandkiss Sitting)
    (valid_post m_sithandkiss Sitting)

    (valid_pre m_highclap Standing)
    (valid_post m_highclap Standing)

    (valid_pre m_disco Standing)
    (valid_post m_disco Standing)

  )

  (:goal (and
    (current_phase phase6)
    (at_posture Standing)
    (at_loc pos_center)
    (mandatory_done phase0)
    (mandatory_done phase1)
    (mandatory_done phase2)
    (mandatory_done phase3)
    (mandatory_done phase4)
    (mandatory_done phase5)
    (move_done m_astleysway)
    (move_done m_hello)
    (move_done m_fingersnap)
    (move_done m_thriller)
    (move_done m_thrillersnap)
    (move_done m_newdance)
    (move_done m_diagleft)
    (move_done m_diagright)
    (move_done m_sithandkiss)
    (move_done m_highclap)
    (move_done m_disco)
  ))
)
