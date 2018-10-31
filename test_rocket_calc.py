import rocket_calc as rc

#kick logging
rc.setup_my_logger()
rc.log_to_console()

#kick engine class
bru_solid=rc.engine('F15','0')

#kick stage class
bru_booster=[bru_solid]
stage_1=rc.stage(0.1,bru_booster,.02,.75)

#kick vehicle class
rocket_assembly=[stage_1]
thanks_giver=rc.vehicle(rocket_assembly)

#kick launch class
launch_sim=rc.launch(thanks_giver,30,1)

print(launch_sim.launch_data)



