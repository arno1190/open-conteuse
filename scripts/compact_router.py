"""Explicit Specctra router settings; leave In1 continuous for GND return."""
SETTINGS='''(autoroute_settings
 (fanout on) (autoroute on) (postroute on) (vias on)
 (via_costs 20) (plane_via_costs 5) (start_ripup_costs 100) (start_pass_no 1)
 (layer_rule F.Cu (active on) (preferred_direction horizontal) (preferred_direction_trace_costs 1) (against_preferred_direction_trace_costs 1.2))
 (layer_rule In1.Cu (active off) (preferred_direction horizontal) (preferred_direction_trace_costs 1) (against_preferred_direction_trace_costs 1.2))
 (layer_rule In2.Cu (active on) (preferred_direction vertical) (preferred_direction_trace_costs 1) (against_preferred_direction_trace_costs 1.2))
 (layer_rule B.Cu (active on) (preferred_direction horizontal) (preferred_direction_trace_costs 1) (against_preferred_direction_trace_costs 1.2)))'''
