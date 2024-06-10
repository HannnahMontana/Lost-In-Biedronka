import pygame, sys

from settings import HEIGHT, WIDTH


class Level:
    def __init__(self, player, images):
        self.player = player
        self.set_of_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.images = images

        def draw(self, surface):
            super().draw(surface)
            # przeszkody
            for obstacle in self.obstacles:
                surface.blit(self.imagesP2, obstacle.topleft)

        self.sciany = [
                # placeholder (left, top, width, height)
            #góra
            pygame.Rect(0, 0, 550, 75),
            pygame.Rect(816, 0, 550, 75),

            #dol
            pygame.Rect(0, 665, 550, 75),
            pygame.Rect(816, 665, 550, 75),

            #prawo
            pygame.Rect(1294, 0, 75, 250),
            pygame.Rect(1294, 490, 75, 250),

            #lewo
            pygame.Rect(0, 0, 75, 250),
            pygame.Rect(0, 490, 75, 250)







        ]

        self.imagesP = pygame.image.load('images-from-shooting-game/meteorBrown_big1.png')


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

        # Kolizja pocisków z wrogami
        for enemy in self.enemies:
            collisions = pygame.sprite.spritecollide(enemy, self.set_of_bullets, False)
            for bullet in collisions:
                if bullet.owner == self.player:
                    bullet.kill()
                    enemy.take_damage(1)
                    enemy.kill_if_dead()

        # Kolizja pocisków z przeszkodami
        for obstacle in self.obstacles:
            for bullet in self.set_of_bullets:
                if obstacle.colliderect(bullet.rect):
                    bullet.kill()

        for sciany in self.sciany:
            for bullet in self.set_of_bullets:
                if sciany.colliderect(bullet.rect):
                    bullet.kill()

        # Kolizja pocisków z graczem
        collisions = pygame.sprite.spritecollide(self.player, self.set_of_bullets, False)
        for bullet in collisions:
            if bullet.owner != self.player:
                bullet.kill()
                self.player.take_damage(1)

        # Kolizja player z enemy (do poprawy)
        collisions = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in collisions:
            self.player.take_damage(1)

    def draw(self, surface):
        """
        Rysuje na ekranie rzeczy dla levelu
        :param surface:
        :return:
        """
        self.set_of_bullets.draw(surface)
        self.enemies.draw(surface)



        for sciany in self.sciany:
            #surface.blit(self.imagesP, sciany.topleft)
            pygame.draw.rect(surface, (0, 0, 0), sciany)

            # rysowanie żyć
        for i in range(self.player.lives - 1):
            surface.blit(self.images['PLAYERLIFE'], (20 + i * 45, 20))

    def reset(self):
            self.__init__(self.player, self.images)