print('STARTING NEW TEST OF ROCKET CALC======================================================================')
import rocket_calc as rc

#kick logging
rc.setup_my_logger()
rc.log_to_console()

#kick engine class
bru_solid=rc.engine('C6','0')
print(bru_solid.initial_mass)
print(bru_solid.prop_mass)
print(bru_solid.specific_impulse)
print(bru_solid.thrust)
print(bru_solid.mass)
print(bru_solid.final_mass)
print(bru_solid.engine_data)

#kick stage class
bru_booster=[bru_solid]
#bru_orbiter=[bru_solid]
stage_1=rc.stage(dry_mass=0.068,engines=bru_booster,cross_section=0.0014,drag_coeff=0.75)
print(stage_1.stage_data)
#stage_2=rc.stage(dry_mass=0.05,engines=bru_booster,cross_section=.0011,drag_coeff=0.75)


#kick vehicle class
rocket_assembly=[stage_1]
thanks_giver=rc.vehicle(rocket_assembly)
print(thanks_giver.vehicle_data)

thanks_giver.vehicle_data.to_csv('vehicle_data.csv')

#kick launch class
launch_sim=rc.launch(thanks_giver,9,1.27)
print(launch_sim.launch_data)

launch_sim.launch_data.to_csv('launch_data.csv')

#print(launch_sim.launch_data)



