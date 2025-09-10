import pygame

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Circle Drag")

black = (0, 0, 0)
white = (255, 255, 255)

circle_radius = 50
circle_x = width // 2
circle_y = height // 2
dragging = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if (circle_x - circle_radius) < event.pos[0] < (circle_x + circle_radius) and (circle_y - circle_radius) < event.pos[1] < (circle_y + circle_radius):
                    dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                circle_x = event.pos[0]
                circle_y = event.pos[1]


    screen.fill(white)
    pygame.draw.circle(screen, black, (circle_x, circle_y), circle_radius)
    pygame.display.flip()

pygame.quit()
