# coding: utf-8
import pygame
import circle

# Inicialização do Pygame
pygame.init()

# Configurações da tela
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mover Círculo")

# Cor de fundo (branco)
white = (255, 255, 255)

# Criação do círculo
my_circle = circle.Circle(screen, 50, (screen_width // 2, screen_height // 2))


# Loop principal
running = True
dragging = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if my_circle.is_inside(event.pos):
                    dragging = True
                    offset_x = my_circle.x - event.pos[0]
                    offset_y = my_circle.y - event.pos[1]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                my_circle.x = event.pos[0] + offset_x
                my_circle.y = event.pos[1] + offset_y


    # Preenche a tela com branco
    screen.fill(white)

    # Desenha o círculo
    my_circle.draw()

    # Atualiza a tela
    pygame.display.flip()

pygame.quit()
