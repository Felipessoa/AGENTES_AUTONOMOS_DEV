import pygame

class Circle:
    def __init__(self, surface, radius, position):
        self.surface = surface
        self.radius = radius
        self.x, self.y = position
        self.color = (0, 0, 255) # Azul

    def draw(self):
        pygame.draw.circle(self.surface, self.color, (int(self.x), int(self.y)), self.radius)

    def is_inside(self, pos):
        distance = ((pos[0] - self.x)**2 + (pos[1] - self.y)**2)**0.5
        return distance <= self.radius
