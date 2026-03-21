import pygame
from ui_controls import *
import math
global mass, planet, G, dt, GRID_DENSITY, angle, magnitude
GRID_DENSITY = 50
MASS_DENSITY = 0.1
dt = 1
G = 100
mass = 10
angle = 0
magnitude = 0
planet = []
class Body:
    def __init__(self, position, velocity, density, mass):
        self.position = position
        self.velocity = velocity
        self.density = density
        self.mass = mass
        self.x = position[0]
        self.y = position[1]
    def setVelocity(self, x, y):
        self.velocity = [x, y]
    def checkCollision(self, p):
        if (self == p):
            return
        if distance(self.position, p.position) <= (1/(self.density/self.mass)/2):
            self.collide(p)
    def collide(self, p):
        pass
    def update(self):

        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.x = self.position[0]
        self.y = self.position[1]

class Planet(Body):
    def __init__(self, planet_density, location, mass, velocity, screen):
        super().__init__(location, velocity, planet_density, mass)
        self.planet_size = 1/(self.density/self.mass)
        self.screen = screen
    def collide(self, p):
        if isinstance(p, Planet):
            self.position = [(self.position[0]+p.position[0])/2, (self.position[1]+p.position[1])/2]
            self.velocity = [(self.velocity[0]+p.velocity[0])/2, (self.velocity[1]+p.velocity[1])/2]
            self.mass += p.mass
            self.mass = min(250, self.mass)
            self.planet_size = 1/(self.density/self.mass)
            planet.remove(p)
    def draw(self):
        print("there")
        pygame.draw.circle(self.screen, "yellow", (self.x, self.y), radius = self.planet_size//2)
    def update(self):
        super().update()
        self.planet_size = 1/(self.density/self.mass)

class Blackhole:
    def __init__(self, radius, position, rotation):
        self.radius = radius
        self.position = position
        self.rotation = rotation

    def draw():
        pass
    
class Photon:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

    def draw():
        pass

def gravity(position, planets, type = "planet", ind = -1):
    gx = 0
    gy = 0
    for i,p in enumerate(planets):
        dx = position[0] - p.x
        dy = position[1] - p.y
        if type != 'gridline':
            dist = max(distance(position, p.position), 65)
        else:
            dist = max(distance(position, p.position), 100)

        gx -= G * p.mass * (dx/(dist**3))
        gy -= G * p.mass * (dy/(dist**3))
    return [gx, gy]

def distance(positionA, positionB):
    return (((positionA[0] - positionB[0])**2) + ((positionA[1] - positionB[1])**2))**(1/2)


def create_planet(planet_density, location, mass, velocity, screen):
    new_planet = Planet(planet_density, location, mass, velocity, screen)
    planet.extend([new_planet])

def change_mass(value):
    global mass
    mass = value

def change_angle(value):
    global angle
    angle = value
def reset_sim():
    planet.clear()
def change_magnitude(value):
    global magnitude
    magnitude = value
def begin_sim():
    global is_title_screen
    is_title_screen = False
def main():
    global is_title_screen
    is_title_screen = True
    pygame.init()
    WIDTH = 1000
    HEIGHT = 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Universe Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Comic Sans MS", 15)
    m_slider = Slider(800, 200, 100, 20, 10, 100, color = "white", text = "Mass Slider", font = font, on_change = change_mass, continuous=True)
    angle_slider = Slider(800, 240, 100, 20, 0, 360, color = "white", text ="Angle", font = font, on_change = change_angle, continuous=True)
    magnitude_slider =  Slider(800, 280, 100, 20, 0, 20, color = "white", text ="Magnitude", font = font, on_change = change_magnitude, continuous=True)
    
    widgets = [m_slider, angle_slider, magnitude_slider]
    running = True
    dt = clock.tick(60)/1000
    while running:
        screen.fill("black")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_sim()
            for w in widgets:
                
                w.handle_event(event)
            

            if event.type == pygame.MOUSEBUTTONUP and event.pos[0] < 600:
                x, y = event.pos
                create_planet(1, [x, y], mass, [magnitude*math.cos(angle*0.0174533), magnitude*math.sin(angle*0.0174533)], screen)
        # Draw widgets after background
        if not is_title_screen:
            for w in widgets:
                w.draw(screen)
            pygame.draw.line(screen, "white", (800, 400), ((5*magnitude)*math.cos(angle*0.0174533) + 800, (5*magnitude)*math.sin(angle*0.0174533) +400))
            pygame.draw.circle(screen, "white", (800, 400), radius = 5*magnitude, width = 2)
            # draw spacetime grid
            points = []
            for i in range(-1, (WIDTH)//GRID_DENSITY + 1):
                temp = []
                for j in range(-1, (HEIGHT)//GRID_DENSITY + 1):
                    x = (i*GRID_DENSITY)+(GRID_DENSITY//2)
                    y = (j*GRID_DENSITY)+(GRID_DENSITY//2)
                    grav = gravity([x,y], planet, type = "gridline")
                    scale = 10
                    x += grav[0]*scale
                    y += grav[1]*scale
                    point = (x, y)
                    temp.append(point)
                    pygame.draw.circle(screen, (0, min(max(255-i*15, 0), 255), min(max(255-j*15, 0), 255)), (x, y), radius = 2)
                points.append(temp)
                print(points)
            

            for row in range(len(points)):
                for col in range(len(points[row])):
                    pygame.draw.line(screen, "lightblue", (points[row][col][0], points[row][col][1]), (points[min(row+1, len(points)-1)][col][0], points[min(row+1, len(points)-1)][col][1]))
                    pygame.draw.line(screen, "lightblue", (points[row][col][0], points[row][col][1]), (points[row][min(col+1, len(points[row])-1)][0], points[row][min(col+1, len(points[row])-1)][1]))
            previousPlanets = planet
            px = 0
            py = 0
            totalMass = 0
            for p in planet:
                for pp in planet:
                    p.checkCollision(pp)
            for i, p in enumerate(planet):
                grav = gravity(p.position, previousPlanets, ind=i)
                p.velocity[0] += grav[0] * dt
                p.velocity[1] += grav[1] * dt
                px += p.position[0] * p.mass
                py += p.position[1] * p.mass
                totalMass += p.mass
                p.update()
                p.draw()
                print(p.x, p.y, p.velocity, p.position)
            pygame.draw.circle(screen, "white", (px/max(totalMass, 1), py/max(totalMass, 1)), radius=5)
        else:
            drawText(screen, "Spacetime Simulation", size = 30)
            drawText(screen, "Created by: Kevin Wang and Ubayd Subahan", x_offset = -35, size = 35)
            drawText(screen, "Click to place a celestial body, use sliders to adjust values", x_offset=-75, size = 20)
            drawText(screen, "Click to begin", x_offset=-100, size = 20)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    
                    is_title_screen = False
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    
def drawText(screen, text, x_offset = 0, size = 55):
    font = pygame.font.SysFont("Helvetica", size, True, False)
    text_object = font.render(text, 0, pygame.Color("white"))
    text_location = pygame.Rect(0, 0, 1000, 600).move((1000//2- text_object.get_width()/2), (600//2 - text_object.get_height()/2)-x_offset)
    screen.blit(text_object, text_location)
    

if __name__ == "__main__":
    main()
