print('STARTING NEW TEST OF ROCKET CALC======================================================================')
import rocket_calc as rc

#kick logging
rc.setup_my_logger()
rc.log_to_console()

#kick engine class
bru_solid=rc.engine('F15','0')
print(bru_solid.initial_mass)
print(bru_solid.prop_mass)
print(bru_solid.specific_impulse)
print(bru_solid.thrust)
print(bru_solid.mass)
print(bru_solid.final_mass)
print(bru_solid.engine_data)

#kick stage class
bru_booster=[bru_solid, bru_solid]
bru_orbiter=[bru_solid]
stage_1=rc.stage(0.1,bru_booster,.02,.75)
print(stage_1.stage_data)
stage_2=rc.stage(0.2,bru_orbiter,.03,.76)

#kick vehicle class
rocket_assembly=[stage_1, stage_2]
thanks_giver=rc.vehicle(rocket_assembly)

#kick launch class
launch_sim=rc.launch(thanks_giver,30,1)

#print(launch_sim.launch_data)



