import pygame, os, sys

from level import Level
from level_start import Level_start
from settings import SIZESCREEN, FPS, HEIGHT, WIDTH
from player import Player
from utils import load_images
from level_1 import Level_1
from boss_level import Boss_level
from boost_level import Boost_level


class Text:
    def __init__(self, text, text_color, pc_x, pc_y, font_size=36, font_type=None):
        self.rect = None
        self.image = None
        self.text = str(text)
        self.text_color = text_color
        self.font_size = font_size
        self.font_type = font_type
        self.font = pygame.font.SysFont(self.font_type, self.font_size)
        self.pc_x = pc_x
        self.pc_y = pc_y
        self.update()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self):
        self.image = self.font.render(self.text, True, self.text_color)
        self.rect = self.image.get_rect()
        self.rect.center = self.pc_x, self.pc_y


class Button:
    def __init__(self, text, text_color, background_color, width, height,
                 pc_x, pc_y, font_size=36, font_type=None):
        self.background_color = background_color
        self.width = width
        self.height = height
        self.text = Text(text, text_color, pc_x, pc_y, font_size, font_type)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.text.rect.center

    def draw(self, surface):
        surface.fill(self.background_color, self.rect)
        self.text.update()
        self.text.draw(surface)


def load_level(player, images, direction=None):
    Level.level_count += 1
    if Level.level_count == 1:
        return Level_start(player, images, direction)

    elif Level.level_count == 4:
        return Boost_level(player, images, direction)
    elif Level.level_count == 7:
        return Boss_level(player, images, direction)
    else:
        return Level_1(player, images, direction)


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load('music/background2.mp3')
    pygame.mixer.music.play(loops=-1)
    end_sound = pygame.mixer.Sound('music/end.mp3')
    win_sound = pygame.mixer.Sound('music/win.mp3')

    screen = pygame.display.set_mode(SIZESCREEN)
    clock = pygame.time.Clock()

    # ścieżka do obrazów
    path = os.path.join(os.getcwd(), 'images')
    # ładowanie obrazów

    images = load_images(path)
    background = images.pop('BACKGROUND')
    background_start = images.pop('BACKGROUND2')
    end = images.pop('END')
    win = images.pop('WIN')
    controls = images.pop('CONTROLS')
    plot2 = images.pop('PLOT2')
    plot3 = images.pop('PLOT3')
    plot4 = images.pop('PLOT4')
    DARKBLUE = pygame.color.THECOLORS['darkblue']
    YELLOW = pygame.color.THECOLORS['yellow']
    RED = pygame.color.THECOLORS['red']
    WHITE = pygame.color.THECOLORS['white']

    # tworzenie obiektu gracz
    player = Player(683, 360, player_images={
        'front': [images[f'FRONT{i}'] for i in range(1, 5)],
        'back': [images[f'BACK{i}'] for i in range(1, 5)],
        'left': [images[f'LEFT{i}'] for i in range(1, 5)],
        'right': [images[f'RIGHT{i}'] for i in range(1, 5)]
    }, bullet_img=images['PLAYER_BULLET'])

    # aktualizacja i tworzenie levelu
    current_level = load_level(player, images)

    # elementy startowe
    start_image = images['TITLE']
    start_image_rect = start_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))

    finish_text = Text("KONIEC GRY", WHITE, *screen.get_rect().center, font_size=120, font_type="Times New Roman")
    start = Button("START", YELLOW, RED, 200, 100, WIDTH // 4, 600, 70, "Arial")
    quit = Button("QUIT", YELLOW, RED, 200, 100, 3 * WIDTH // 4, 600, 70, "Arial")
    hard = Button("HARD", YELLOW, RED, 200, 100, WIDTH // 2, 600, 70, "Arial")

    # rysowanie rzeczy
    current_level.draw(screen)
    player.draw(screen)

    window_open = True
    active_game = False

    # pętla gry
    while window_open:

        # tło
        screen.blit(background, (-0, -0))

        # pętla zdarzeń
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_level.reset()
                    active_game = False

            if event.type == pygame.QUIT:
                window_open = False

            # klikanie w guziki
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start.rect.collidepoint(pygame.mouse.get_pos()):

                    # plansza startowa z fabułą gry
                    '''
                    pygame.time.delay(500)
                    screen.blit(plot2, (0, 0))
                    pygame.display.update()
                    pygame.time.delay(3000)
                    screen.blit(plot3, (3, 3))
                    pygame.display.update()
                    pygame.time.delay(3000)
                    screen.blit(plot4, (0, 0))
                    pygame.display.update()
                    pygame.time.delay(3000)
                    
'''
                    Level.level_count = 0
                    current_level = load_level(player, images)
                    player.reset_player()
                    active_game = True
                    pygame.time.delay(200)



                if quit.rect.collidepoint(pygame.mouse.get_pos()):
                    window_open = False
                    pygame.time.delay(200)

                if hard.rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.time.delay(500)
                    screen.blit(plot2, (0, 0))
                    pygame.display.update()
                    pygame.time.delay(3000)
                    screen.blit(plot3, (3, 3))
                    pygame.display.update()
                    pygame.time.delay(3000)
                    screen.blit(plot4, (0, 0))
                    pygame.display.update()
                    pygame.time.delay(3000)

                    Level.level_count = 0
                    current_level = load_level(player, images)
                    player.reset_player()
                    active_game = True
                    pygame.time.delay(200)

                    player.lives = 2

        if active_game:

            # rysowanie i aktualizacja obiektów
            player.update(pygame.key.get_pressed())
            current_level.update()
            current_level.draw(screen)
            player.draw(screen)
            if player.lives == 1:
                end_sound.play(0)
                active_game = False

                pygame.time.delay(1000)
                screen.blit(end, (0, 0))
                finish_text.draw(screen)
                pygame.display.update()
                pygame.time.delay(1000)

            if Level.level_count == 8:
                win_sound.play(0)
                active_game = False
                pygame.time.delay(500)
                screen.blit(win, (0, 0))
                pygame.display.update()
                pygame.time.delay(1000)

        else:  # rysowanie guzików
            if start.rect.collidepoint(pygame.mouse.get_pos()):
                start.background_color = YELLOW
                start.text.text_color = RED
            else:
                start.background_color = RED
                start.text.text_color = YELLOW
            if quit.rect.collidepoint(pygame.mouse.get_pos()):
                quit.background_color = YELLOW
                quit.text.text_color = RED
            else:
                quit.background_color = RED
                quit.text.text_color = YELLOW
            if hard.rect.collidepoint(pygame.mouse.get_pos()):
                hard.background_color = YELLOW
                hard.text.text_color = RED
            else:
                hard.background_color = RED
                hard.text.text_color = YELLOW




            screen.blit(background_start, (-100, -300))
            screen.blit(start_image, start_image_rect)

            start.draw(screen)
            quit.draw(screen)
            hard.draw(screen)


        # sprawdzanie przejścia przez krawędzie ekranu i resetowanie poziomu

        if player.rect.bottom >= HEIGHT:
            player.rect.top = 0
            current_level.reset()
            current_level = load_level(player, images, 'down')
            print(f"{current_level}")

        elif player.rect.top <= 0:
            player.rect.bottom = HEIGHT
            current_level.reset()
            current_level = load_level(player, images, 'up')

        elif player.rect.right > WIDTH:
            player.rect.left = 0
            current_level.reset()
            current_level = load_level(player, images, 'right')

        elif player.rect.left < 0:
            player.rect.right = WIDTH
            current_level.reset()
            current_level = load_level(player, images, 'left')

        # aktualizacja okna co ileś FPS
        pygame.display.flip()
        clock.tick(FPS)

    pygame.time.delay(500)
    pygame.display.update()
    pygame.quit()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
