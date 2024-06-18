import pygame, sys, random

from ladybug import Ladybug
from pallet_truck import PalletTruck
from settings import HEIGHT, WIDTH, GRID_SIZE


class Level:
    level_count = 0

    def __init__(self, player, images, entry_door_direction=None):
        self.player = player
        self.set_of_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.obstacles = None
        self.images = images
        self.entry_door_direction = entry_door_direction
        self.closed_doors = []

        self.walls = [
            # szerokość ściany - 550 albo 250, przejście - 266 na poziomie i 240 na pionie
            # placeholder (left, top, width, height)
            # góra
            pygame.Rect(0, 0, 675, 80),
            pygame.Rect(880, 0, 550, 80),
            # dol
            pygame.Rect(0, 658, 675, 80),
            pygame.Rect(870, 658, 550, 80),
            # prawo
            pygame.Rect(1270, 0, 100, 250),
            pygame.Rect(1270, 420, 100, 350),
            # lewo
            pygame.Rect(0, 0, 90, 250),
            pygame.Rect(0, 420, 90, 350)
        ]

        self.doors = [
            pygame.Rect(720, 0, 170, 80),  # Top door
            pygame.Rect(720, 658, 170, 80),  # Bottom door
            pygame.Rect(1270, 280, 100, 130),  # Right door
            pygame.Rect(0, 277, 90, 120)  # Left door
        ]

        # drzwi przeciwne do tych z ktorych przychodzimy
        _opposite_door_index = {'up': 1, 'down': 0, 'right': 3, 'left': 2}
        self.door_player_enter = self.doors[_opposite_door_index.get(entry_door_direction, -1)]
        self.doors_to_open = self._get_random_doors()

        self.width = WIDTH // GRID_SIZE
        self.height = HEIGHT // GRID_SIZE

        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        self.player_invulnerable = False
        self.invulnerable_start_time = 0

    def update_grid(self):
        for obstacle in self.obstacles + self.walls:
            # oblicza zakresy iteracji dodając komórki wokół przeszkód
            top = max((obstacle.top // GRID_SIZE) - 1, 0)
            bottom = min((obstacle.bottom // GRID_SIZE) + 1, len(self.grid))
            left = max((obstacle.left // GRID_SIZE) - 1, 0)
            right = min((obstacle.right // GRID_SIZE) + 1, len(self.grid[0]))

            # zaznacza obszar zajmowany przez przeszkodę (+ komórki dookoła)
            for i in range(top, bottom):
                for j in range(left, right):
                    self.grid[i][j] = 1

    def _get_random_doors(self):
        """
        Zwraca listę 1 lub 2 losowych drzwi, poza tymi z których wyszedł gracz.
        :return:
        """
        num_doors_to_open = random.randint(1, 2)
        available_doors = [door for door in self.doors if door != self.door_player_enter]
        return random.sample(available_doors, num_doors_to_open)

    def update(self):
        """
        Aktualizuje rzeczy widoczne na ekranie w grze
        :return:
        """
        self.set_of_bullets.update()
        self.enemies.update(self.player.rect.center)

        # Usuwanie pocisków znajdujących się poza ekranem
        for b in self.set_of_bullets:
            if b.rect.bottom < 0 or b.rect.top > HEIGHT or b.rect.left > WIDTH or b.rect.right < 0:
                b.kill()

        # todo: trzeba to na pewno skrócić i uprościć - kolizje
        # Kolizja pocisków z wrogami
        for enemy in self.enemies:
            collisions = pygame.sprite.spritecollide(enemy, self.set_of_bullets, False)
            for bullet in collisions:
                if bullet.owner == self.player:
                    bullet.kill()
                    enemy.take_damage(1)
                    enemy.kill_if_dead()

        # kolizje pocisków i ścian, przeszkód, drzwi
        all_collidables = self.obstacles + self.walls + self.doors
        for bullet in self.set_of_bullets:
            for collidable in all_collidables:
                if collidable.colliderect(bullet.rect):
                    bullet.kill()
                    break

        # Kolizja pocisków z graczem
        if not self.player.invulnerable:
            collisions = pygame.sprite.spritecollide(self.player, self.set_of_bullets, False)
            for bullet in collisions:
                if bullet.owner != self.player:
                    bullet.kill()
                    self.player.take_damage(1)

        # Obsługa kolizji gracza z wrogiem i odpychanie

        collisions = pygame.sprite.spritecollide(self.player, self.enemies, False)

        for enemy in collisions:
            self.player.take_damage(1)

            self.player.push(self.player, enemy, all_collidables)
            self.player.push(enemy, self.player)

        # todo: bug - można dodać popychanie wrogów przez nas, żeby sie uwolnić od utknięcia w rogu
        #  (nie wiem czy to możliwe)
        # todo: KOLIZJE WROGÓW ZE SOBĄ
        # todo: przerobić te metode na kilka mniejszych bo jest syf

        # todo: trigger wrogów, niech nie atakują od razu - opoznienie ich na moment

        # for enemy in self.enemies:
        #     for other_enemy in self.enemies:
        #         if enemy != other_enemy and enemy.rect.colliderect(other_enemy.rect):
        #             self.player.push(enemy, other_enemy, self.obstacles, self.enemies)

        # otwiera drzwi gdy zabijemy wszystkich enemies
        if self.closed_doors and not self.enemies:
            self.closed_doors = [door for door in self.doors if door not in self.doors_to_open]

        if self.enemies:
            if self.player.rect.top < 5:
                self.player.rect.top = 5
            if self.player.rect.bottom > HEIGHT - 5:
                self.player.rect.bottom = HEIGHT - 5
            if self.player.rect.left < 5:
                self.player.rect.left = 5
            if self.player.rect.right > WIDTH - 5:
                self.player.rect.right = WIDTH - 5

    def draw(self, surface):
        """
        Rysuje elementy poziomu
        :param surface:
        :return:
        """
        self.set_of_bullets.draw(surface)
        self.enemies.draw(surface)

        # rysuje zamknięte drzwi
        if self.closed_doors:
            scaled_img = pygame.transform.scale(self.images['OBSTACLE4'], (self.images['OBSTACLE4'].get_width() // 2,
                                                                           self.images['OBSTACLE4'].get_height() // 2))
            for door in self.closed_doors:
                surface.blit(scaled_img, door)

        # rysowanie żyć
        scaled_heart = pygame.transform.scale(self.images['HEART'], (self.images['HEART'].get_width() // 3,
                                                                     self.images['HEART'].get_height() // 3))
        for i in range(self.player.lives - 1):
            surface.blit(scaled_heart, (20 + i * 45, 20))

    def reset(self, direction=None):
        """
        Resetuje poziom (np. po przejściu przez krawędź ekranu)
        :param direction:
        :return:
        """
        # Resetowanie poziomu (np. po przejściu przez krawędź ekranu)
        self.__init__(self.player, self.images, entry_door_direction=direction)

    def trigger_doors(self):
        """
        Zamyka wszystkie drzwi
        :return:
        """
        # Zamknięcie drzwi wszystkich
        self.closed_doors = self.doors
        # self.update_grid()  # Zaktualizuj siatkę po zamknięciu drzwi
