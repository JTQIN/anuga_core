"""Simple water flow example using ANUGA

Water flowing down a channel with a topography that varies with time
"""

#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
from anuga import rectangular_cross
from anuga import Domain
from anuga import Reflective_boundary
from anuga import Dirichlet_boundary
from anuga import Time_boundary
from anuga import Region
from anuga import indent

#------------------------------------------------------------------------------
# Setup computational domain
#------------------------------------------------------------------------------
length = 24.
width = 5.
dx = dy = 0.2 #.1           # Resolution: Length of subdivisions on both axes

points, vertices, boundary = rectangular_cross(int(length/dx), int(width/dy),
                                               len1=length, len2=width)
domain = Domain(points, vertices, boundary)
domain.set_name() # Output name
print domain.statistics()


#------------------------------------------------------------------------------
# Setup initial conditions
#------------------------------------------------------------------------------
def topography(x,y):
    """Complex topography defined by a function of vectors x and y."""

    z = -x/100

    # Step
    id = ( 2 < x ) & (x < 4)
    z[id] +=  0.4 - 0.05*y[id]

    # Permanent pole
    id = (x - 8)**2 + (y - 2)**2 < 0.4**2
    z[id] += 1

    # Pole 2
    #id =  (x - 14)**2 + (y - 3.5)**2 < 0.4**2
    #z[id] += 1.0


    return z



domain.set_quantity('elevation', topography)           # elevation is a function
domain.set_quantity('friction', 0.01)                  # Constant friction
domain.set_quantity('stage', expression='elevation')   # Dry initial condition

#------------------------------------------------------------------------------
# Setup boundary conditions
#------------------------------------------------------------------------------
Bi = Dirichlet_boundary([0.4, 0, 0])          # Inflow
Br = Reflective_boundary(domain)              # Solid reflective wall
Bo = Dirichlet_boundary([-5, 0, 0])           # Outflow

domain.set_boundary({'left': Bi, 'right': Bo, 'top': Br, 'bottom': Br})

#------------------------------------------------------------------------------
# Setup operators which are applied each inner step
#------------------------------------------------------------------------------
from anuga.operators.set_friction_operators import Depth_friction_operator

op1 = Depth_friction_operator(domain)

p1 = [ [12.0, 2.5], [13.5, 2.5], [13.5, 4.0], [12.0, 4.0] ]
op2 = Depth_friction_operator(domain,
                                  friction_max = 10,
                                  friction_min = 0.0,
                                  polygon=p1)

# Setup region for integrating quantities
p2 = [ [8.0, 2.5], [9.5, 2.5], [9.5, 4.0], [8.0, 4.0] ]
reg = Region(domain, polygon=p2)

# Some useful aliases
stage = domain.quantities['stage']
elev = domain.quantities['elevation']

#------------------------------------------------------------------------------
# Evolve system through time
#------------------------------------------------------------------------------
for t in domain.evolve(yieldstep=0.1, finaltime=10.0):
    domain.print_timestepping_statistics()
    domain.print_operator_timestepping_statistics()

    # let calculate the integral of height over a region
    height = stage-elev
    print indent+'Int_p2(h) = '+str(height.get_integral(region=reg))






