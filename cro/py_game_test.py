import pygame
import math
from ui_controls import *

# ----------------------------
# Simulation parameters
# ----------------------------
G = 0.1          # gravitational constant (tune for visuals)
ONE_PN = 0.01    # small post-Newtonian-like correction factor (tunable)
EPS = 2.0        # softening to avoid singularities
c = 1.0            # artificial "speed of light" units for GR-like cues (not used heavily here)

# Global state
mass = 10
bodies = []        # list of all physical bodies (planets, etc.)

# ----------------------------
# Physics models
# ----------------------------
class Body:
    """Base class for any gravitating body."""
    def __init__(self, density, location, mass, screen):
        self.density = density
        self.mass = mass
        self.x = float(location<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[0]</a>)
        self.y = float(location<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[1]</a>)
        self.vx = 0.0
        self.vy = 0.0
        self.screen = screen
        # Visual size inspired by density/mass mix (kept from your original)
        self.planet_size = max(2, int(1 / (self.density / self.mass)))
    def draw(self, color="yellow"):
        pygame.draw.circle(self.screen, color, (int(self.x), int(self.y)), radius=self.planet_size // 2)

class Planet(Body):
    def __init__(self, planet_density, location, mass, screen):
        super().__init__(planet_density, location, mass, screen)

class Blackhole(Body):
    def __init__(self, radius, position, rotation, screen):
        super().__init__(radius, position, mass=radius*5, screen=screen)  # simple proxy mass
        self.radius = radius
        self.rotation = rotation

class Photon:
    def __init__(self, position, velocity):
        self.position = list(position)
        self.velocity = list(velocity)
    def update(self):
        # Simple forward motion; optional light bending can be added here
        self.position<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[0]</a> += self.velocity<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[0]</a>
        self.position<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[1]</a> += self.velocity<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[1]</a>
    def draw(self, screen):
        pygame.draw.circle(screen, "white", (int(self.position<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[0]</a>), int(self.position<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[1]</a>)), 2)

# ----------------------------
# Helpers
# ----------------------------
def add_relativistic_correction(i, bodies):
    """Very lightweight, heuristic 1PN-like correction on body i due to others."""
    a_rx, a_ry = 0.0, 0.0
    xi, yi = bodies[i].x, bodies[i].y
    for j, b in enumerate(bodies):
        if i == j:
            continue
        dx = b.x - xi
        dy = b.y - yi
        r2 = dx*dx + dy*dy + EPS*EPS
        r = math.sqrt(r2)
        mj = b.mass
        # Simple directional correction toward/away from other body
        ux = dx / r
        uy = dy / r
        # Heuristic 1PN-like term (very small)
        a_rel = ONE_PN * G * mj / r2
        a_rx += a_rel * ux
        a_ry += a_rel * uy
    return a_rx, a_ry

def update_bodies(bodies, dt):
    n = len(bodies)
    ax = [0.0]*n
    ay = [0.0]*n

    # Newtonian pairwise gravity (action/reaction)
    for i in range(n):
        for j in range(i+1, n):
            bi = bodies[i]
            bj = bodies[j]
            dx = bj.x - bi.x
            dy = bj.y - bi.y
            r2 = dx*dx + dy*dy + EPS*EPS
            r = math.sqrt(r2)
            f = G * bi.mass * bj.mass / r2
            ux = dx / r
            uy = dy / r
            ax[i] += f * ux / bi.mass
            ay[i] += f * uy / bi.mass
            ax[j] -= f * ux / bj.mass
            ay[j] -= f * uy / bj.mass

    # Relativistic corrections (tiny)
    for i in range(n):
        rx, ry = add_relativistic_correction(i, bodies)
        ax[i] += rx
        ay[i] += ry

    # Integrate (semi-implicit Euler)
    for i, b in enumerate(bodies):
        b.vx += ax[i] * dt
        b.vy += ay[i] * dt
        b.x += b.vx * dt
        b.y += b.vy * dt

# ----------------------------
# UI helpers (using your existing pattern)
# ----------------------------
def create_planet(planet_size, location, mass, screen):
    new_planet = Planet(planet_size, location, mass, screen)
    # Optionally give an initial velocity for orbit-like motion
    new_planet.vx = 0.0
    new_planet.vy = 0.0
    bodies.append(new_planet)

def change_mass(value):
    global mass
    mass = value

# ----------------------------
# Main
# ----------------------------
def main():
    pygame.init()
    WIDTH = 1000
    HEIGHT = 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Universe Simulation (GR-ish)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Comic Sans MS", 15)

    # UI widgets (you can adapt positions as needed)
    b = Button(800, 100, 75, 75, "white", text="add body", font=font, on_click=lambda: create_planet(1, (WIDTH//2, HEIGHT//2), mass, screen), text_color="black")
    m_slider = Slider(800, 200, 100, 20, 10, 100, color="white", text="Mass Slider", font=font, on_change=change_mass)

    widgets = [b, m_slider]

    # Seed with a central mass to visualize gravity
    center = Body(density=50, location=(WIDTH//2, HEIGHT//2), mass=500, screen=screen)
    center.vx = 0.0
    center.vy = 0.0
    bodies.append(center)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # seconds per frame
        screen.fill("black")

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for w in widgets:
                w.handle_event(event)

            if event.type == pygame.MOUSEBUTTONUP:
                x, y = event.pos
                # Create a new body at click location
                create_planet(1, (x, y), mass, screen)

        # Update physics
        if len(bodies) > 0:
            update_bodies(bodies, dt)

        # Draw
        for obj in bodies:
            # For the central "center" you might want a distinct color
            if isinstance(obj, Body):
                obj.draw("yellow" if obj is not bodies<a href="" class="citation-link" target="_blank" style="vertical-align: super; font-size: 0.8em; margin-left: 3px;">[0]</a> else "orange")

        for p in []:  # placeholder for photons if added
            p.update()
            p.draw(screen)

        # Draw UI on top
        for w in widgets:
            w.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
