#
# Have you heard the tragedy of Frog Leaper the Wise? It's not a story 
# a programmer would tell you. Once upon a time, in the days of yore,
# when PATIENCE was still in development, many brave souls made their 
# efforts to simulate the dangerous and elusive magnetic field. Euler
# was the bold venturer, ever ready to fight in the name of science. 
# He drew first blood from the simulator, but alas, he could only 
# simulate electric fields with his inferior first-order method. 
# Runge-Kutta came next, taking the baton from 
# Euler as champions of accuracy, pioneering with their second-order
# scheme. It was not enough. Weep, O, you programmers, for under
# Runge-Kutta it was that the dark side started to gain victory.
# Blood was spilled by the megabytes in the form of energy leakage,
# for though our champions were accurate, their valiant scheme 
# failed to conserve the energy that was the lifeblood of the magnetic
# field. Particles spiraled out of control, struggling to maintain a 
# circular path but eventually fading away into the depths of magnitude
# where even the bravest dare not venture.
# And then there was Boris.
#
# enter Boris

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import ConfigParser

#--------------------- fetch simulation settings

# open the config file to read parameters
config = ConfigParser.ConfigParser()
config.read("config.ini")

#analytical mode
analysis_on = config.getint("analysis" , "analysis_on")

# field data
B = [ config.getfloat("fields" , "B_x") , config.getfloat("fields" , "B_y") , config.getfloat("fields" , "B_z") ]
E = [ config.getfloat("fields" , "E_x") , config.getfloat("fields" , "E_y") , config.getfloat("fields" , "E_z") ] 

# particle data
mass = config.getfloat("particle" , "mass")
charge = config.getfloat("particle" , "charge")

# boundary conditions
pos_0 = [ config.getfloat("boundary-conditions","x_0") , config.getfloat("boundary-conditions","y_0") , config.getfloat("boundary-conditions","z_0") ]
vel_0 = [ config.getfloat("boundary-conditions","v_x_0") , config.getfloat("boundary-conditions","v_y_0") , config.getfloat("boundary-conditions","v_z_0") ]

pos_init = pos_0
vel_init = vel_0
	
#time info
steps = config.getint("time-step","steps")
t_final = config.getfloat("time-step","t_final")
h = t_final/steps

#storage variables for plotting
plot_pos_x = list()
plot_pos_y = list()
plot_pos_z = list()

#boris variables
t_vector = np.multiply(charge * h / mass * 0.5 , B)
s_vector = np.divide( np.multiply(2. , t_vector) , 1 + (np.linalg.norm(t_vector)**2))


#--------------------- run the simulation
larmor_radius = (mass * np.linalg.norm(vel_0))**2 / (charge *np.linalg.norm(np.cross(vel_0 , B)))
#analysis mode
if analysis_on == 1 :
	plot_pos_x_aly = list()
	plot_pos_x_aly = list()
	larmor_radius = (mass * np.linalg.norm(vel_0))**2 / (charge *np.linalg.norm(np.cross(vel_0 , B)))
	
#calculate the magnetic field as a function of time
def b_field ( t ) :
	return np.cos(np.multiply(B, 2.0 * np.pi / 30.0))
	
#calculate the acceleration
def acceleration ( EField , BField , velocity ) :
	a_0 = np.add(np.multiply( charge/mass , np.cross( vel_0 , B ) ), np.multiply( charge/mass , E ) )
	return a_0
	
#calculate the position
def positionUpdate ( h , x_prev , v_prev , v_new ) :
	return np.add(x_prev , np.multiply(h/2.0 , np.add(v_new , v_prev)))
	
#algorithm
a_0 = acceleration ( E , B , vel_0 )
v_nminushalf = np.subtract(vel_0 , np.multiply(h/2. , a_0) )
vel_0 = v_nminushalf

for step in range(steps) :
	#a_0 = acceleration ( E , B , vel_0 )
	#B = b_field(time)
	
	v_minus = np.add( vel_0 , np.multiply( h/2. , np.multiply( charge/mass , E ) ) )
	v_nminushalf = np.subtract( v_minus , np.multiply( charge/mass , E ) )
	
	v_prime = np.add( v_minus , np.cross( v_minus , t_vector ) )
	
	v_plus = np.add( v_minus , np.cross( v_prime , s_vector ) )
	v_nplushalf = np.add( v_plus , np.multiply( charge/mass , E ) )
	
	pos_1 = positionUpdate( h , pos_0 , v_nminushalf , v_nplushalf )
	
	plot_pos_x.append(pos_0[0])
	plot_pos_y.append(pos_0[1])
	plot_pos_z.append(pos_0[2])

	pos_0 = pos_1
	vel_0 = v_nplushalf

#--------------------- generate the plot
fig = plt.figure()

fig.suptitle('Trajectory in EM field \n computed using Boris pusher \n in ' + str(steps) + " steps" , fontweight='bold' , fontsize=40)
#pltPos = fig.add_subplot(111)

#pltPos.grid(b=True, color='k', linestyle='--')
#pltPos.set_xlabel('x-position (m)' , fontweight='bold')
#pltPos.set_ylabel('y-position (m)' , fontweight='bold')

#pltPos.plot(plot_pos_x , plot_pos_y , 'b-', label='Boris path')
#pltPos.scatter(plot_pos_x[0] ,plot_pos_y[0], color='k' , s=100,marker='o' , label='initial position')
#pltPos.scatter(plot_pos_x[-1] , plot_pos_y[-1], color='k' , s=100,marker='x' , label='final position')
	
#analysis mode
#if analysis_on == 1 :
#	t_arr = np.linspace(0.0, t_final, steps)
#	Bmag = np.linalg.norm(B)
#	Omega_L = charge*Bmag/mass
#	
#	x_ana = pos_init[0] + (vel_init[0]*np.sin(Omega_L*t_arr) + vel_init[1]*(1 - np.cos(Omega_L*t_arr)))/Omega_L
#	y_ana = pos_init[1] + (vel_init[0]*(np.cos(Omega_L*t_arr) - 1) + vel_init[1]*np.sin(Omega_L*t_arr))/Omega_L
#	
#	pltPos.plot(x_ana , y_ana , 'g--' , label='Analytical path')
#	pltPos.set_title('Larmor radius = ' + str(larmor_radius) + ' metres')

ax = fig.gca(projection='3d')
ax.plot(plot_pos_x, plot_pos_y, plot_pos_z, label='Boris path')
ax.scatter(plot_pos_x[0] , plot_pos_y[0] , plot_pos_z[0] , color='r' , s=200,marker='o' , label='initial position')
ax.scatter(plot_pos_x[-1] , plot_pos_y[-1] , plot_pos_z[-1] , color='r' , s=200,marker='x' , label='final position')
#ax.quiver(larmor_radius , larmor_radius , 2 , B[0]*1000 , B[1]*1000, B[2]*1000 , length = 3.0, colors = (1,.5,1,1), label='B-field (not to scale)', normalize=True)
#ax.quiver(larmor_radius , larmor_radius , 0 , E[0]*1000 , E[1]*1000, E[2]*1000 , length = 3.0, colors = (.5,1,1,1), label='E-field (not to scale)', normalize=True)
#ax.set_xlim(-100)
#ax.set_ylim(-99)
#ax.set_zlim(98)

#ax.text(pos_init[0] + 1, pos_init[1] + 1, pos_init[2] + 1, 'starting position' + str(pos_init))

ax.set_xlabel('x-position (m) | E = ' + str(E[0]) +  ' | B = ' + str(B[0]) , fontweight='light' , fontsize=25)
ax.set_ylabel('y-position (m) | E = ' + str(E[1]) +  ' | B = ' + str(B[1]) , fontweight='light' , fontsize=25)
ax.set_zlabel('z-position (m) | E = ' + str(E[2]) +  ' | B = ' + str(B[2]) , fontweight='light' , fontsize=25)
ax.legend()

#ax.set_aspect(1)
plt.legend(loc='best' , fontsize=25)
plt.show()



	
	


	
	





