(define (problem nao_choreography_problem)
  (:domain nao_choreography)
  (:objects
    Standing Sitting Crouch - posture
    pos_center pos_north pos_south pos_west pos_east - loc
    phase0 phase1 phase2 phase3 phase4 phase5 phase6 - phase
    p1_standinit p2_armsopening p3_crouch p4_sit p5_sitrelax p6_stand - move
    m_motif_pause m_comp_diagleft_snap m_motif_clap m_comp_diagright_sway m_motif_astley m_motif_sitkiss m_motif_snap m_motif_sprinkler m_motif_wave m_motif_drop m_motif_disco m_newhiphop m_thriller - move
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
    (valid_pre m_motif_pause Standing)
    (valid_post m_motif_pause Standing)

    (valid_pre m_comp_diagleft_snap Standing)
    (valid_post m_comp_diagleft_snap Standing)
    (loc_transition m_comp_diagleft_snap pos_center pos_west)
    (loc_transition m_comp_diagleft_snap pos_east pos_center)

    (valid_pre m_motif_clap Standing)
    (valid_post m_motif_clap Standing)

    (valid_pre m_comp_diagright_sway Standing)
    (valid_post m_comp_diagright_sway Standing)
    (loc_transition m_comp_diagright_sway pos_west pos_center)
    (loc_transition m_comp_diagright_sway pos_center pos_east)

    (valid_pre m_motif_astley Standing)
    (valid_post m_motif_astley Standing)

    (valid_pre m_motif_clap Standing)
    (valid_post m_motif_clap Standing)

    (valid_pre m_motif_astley Standing)
    (valid_post m_motif_astley Standing)

    (valid_pre m_motif_pause Standing)
    (valid_post m_motif_pause Standing)

    (valid_pre m_motif_sitkiss Sitting)
    (valid_post m_motif_sitkiss Sitting)

    (valid_pre m_motif_snap Standing)
    (valid_post m_motif_snap Standing)

    (valid_pre m_motif_clap Standing)
    (valid_post m_motif_clap Standing)

    (valid_pre m_motif_sprinkler Standing)
    (valid_post m_motif_sprinkler Standing)

    (valid_pre m_motif_wave Standing)
    (valid_post m_motif_wave Standing)

    (valid_pre m_motif_sprinkler Standing)
    (valid_post m_motif_sprinkler Standing)

    (valid_pre m_motif_drop Standing)
    (valid_post m_motif_drop Standing)

    (valid_pre m_motif_wave Standing)
    (valid_post m_motif_wave Standing)

    (valid_pre m_motif_drop Standing)
    (valid_post m_motif_drop Standing)

    (valid_pre m_motif_disco Standing)
    (valid_post m_motif_disco Standing)

    (valid_pre m_motif_drop Standing)
    (valid_post m_motif_drop Standing)

    (valid_pre m_motif_disco Standing)
    (valid_post m_motif_disco Standing)

    (valid_pre m_newhiphop Standing)
    (valid_post m_newhiphop Standing)

    (valid_pre m_thriller Standing)
    (valid_post m_thriller Standing)

    (valid_pre m_motif_snap Standing)
    (valid_post m_motif_snap Standing)

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
  ))
)