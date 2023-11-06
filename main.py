import pygame
from LoadImage import LoadImage
import random
import sys
from props import Props
from gui import Gui
from afterdeath import AfterDeath
from menu import Menu


pygame.init()

width, height = 1080, 720

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("The Running Zombie")

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)

class Player(pygame.sprite.Sprite):

    def __init__(self):
      super().__init__()
  
      self.walk_images = [
        pygame.image.load(filename).convert_alpha()
        for filename in LoadImage.playerwalk
      ]
      self.walk_images = [
        pygame.transform.scale(image, (100, 100)) for image in self.walk_images
      ]
      self.death_images = [
        pygame.image.load(filename).convert_alpha()
        for filename in LoadImage.playerdie
      ]
      self.death_images = [
        pygame.transform.scale(image, (100, 100)) for image in self.death_images
      ]
      self.playerstand_images = [
        pygame.image.load(filename).convert_alpha()
        for filename in LoadImage.playerstand
      ]
      self.playerstand_images = [
        pygame.transform.scale(image, (100, 100))
        for image in self.playerstand_images
      ]
  
      self.image_index = 0
      self.image = self.walk_images[self.image_index]
      self.rect = self.image.get_rect()
      self.rect.bottomleft = (width // -10, height - 2)
      self.speed = 1.5
      self.jump_power = 15
      self.jump_velocity = 0
      self.is_jumping = False
      self.animation_delay = 5
      self.animation_counter = 0
      self.facing_left = False
      self.health = 100
      self.heart = 3
      self.is_dying = False
      self.idle_timer = 0
      self.idle_animation_delay = 50
      self.damage = 10
      self.health_bar_full = LoadImage.healthbar.copy()
      self.health_bar_width = self.health_bar_full.get_width()
      self.invincible = False
      self.frozen = False
      self.burn = False
      self.frozen_duration = 0
      self.slow_duration = 0

    
    def update(self, camera_x):
      keys = pygame.key.get_pressed()
      any_key_pressed = any(keys)
  
      if not self.is_dying:
        if keys[pygame.K_LEFT]:
          self.rect.x -= self.speed
          self.facing_left = True
          self.animate()
        elif keys[pygame.K_RIGHT]:
          self.rect.x += self.speed
          self.facing_left = False
          self.animate()
  
        if keys[pygame.K_SPACE]:
          if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = self.jump_power
  
        if self.is_jumping:
          self.jump_velocity -= 1
          self.rect.y -= self.jump_velocity
  
          if self.rect.y >= height - self.rect.height:
            self.is_jumping = False
        else:
          if self.rect.y < height - self.rect.height:
            self.jump_velocity -= 1
            self.rect.y -= self.jump_velocity
  
        if not any_key_pressed and not self.is_jumping:
          self.animate_idle()
  
      self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
      self.rect.y = max(0, min(self.rect.y, height - self.rect.height))
  
      if self.health < 0:
        self.health = 0
  
      if self.invincible is True:
        self.health = 20000
  
      if self.rect.bottom > height:
        self.rect.bottom = height
  
      if self.frozen:
        self.frozen_duration += 1
        if self.frozen_duration >= 180:
            self.frozen_duration = 0
            self.frozen = False

      if self.slow_duration > 0:
        self.speed = 0.5
        self.slow_duration -= 1
      else:
        self.speed = 1.5
  
      if self.health <= 0:
        self.is_dying = True
  
    def animate(self):
      if not self.is_dying:
        self.animation_counter += 1
        if self.animation_counter >= self.animation_delay:
          self.animation_counter = 0
          self.image_index = (self.image_index + 1) % len(self.walk_images)
          self.image = self.walk_images[self.image_index]
  
          if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)
  
    def animate_idle(self):
      if not self.is_dying:
        self.animation_counter += 1
        if self.animation_counter >= self.animation_delay:
          self.animation_counter = 0
          self.image_index = (self.image_index + 1) % len(
            self.playerstand_images)
          self.image = self.playerstand_images[self.image_index]
  
          if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)
  
    def animate_death(self):
      if self.is_dying:
        self.animation_counter += 1
        if self.animation_counter >= self.animation_delay:
          self.animation_counter = 0
          self.image_index = (self.image_index + 1) % len(self.death_images)
          self.image = self.death_images[self.image_index]
  
          if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        

menu = Menu(screen, LoadImage.menu_image, LoadImage.start_button, LoadImage.exit_button, LoadImage.restart_button)

while True:
    selected_action = menu.handle_events()
    if selected_action == "start":
        break
    menu.draw()
    pygame.display.flip()

player = Player()
gui = Gui(player)

pygame.display.set_icon(LoadImage.icon)
background1 = pygame.transform.scale(LoadImage.background1, (1080, 720))
death_screen = pygame.transform.scale(LoadImage.death_screen, (1080, 720))

bombs_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

health_packs_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


class Bombs(pygame.sprite.Sprite):

    def __init__(self, player, bomb_type, x, y):
        super().__init__()

        if bomb_type == "nuke":
            self.image = pygame.image.load("image/bomb_nuke.png").convert_alpha()
            self.image = pygame.transform.rotate(self.image, -90)
        elif bomb_type == "regular":
            self.image = pygame.image.load("image/bomb_reg.png").convert_alpha()
        elif bomb_type == "frozen":
            self.image = pygame.image.load("image/frozen_bomb.png").convert_alpha()

        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 4
        self.exploded = False
        self.player = player
        self.bomb_type = bomb_type

    def update(self, camera_x):
        if not self.exploded:
            self.rect.y += self.speed

            if self.rect.bottom >= height:
                self.exploded = True
                self.explode()

            if self.rect.bottom > height:
                self.rect.bottom = height

    def random_bomb(self):
        bomb_x = random.randint(0, width - self.rect.width)
        bomb_y = 0
        bomb_type = "regular" if random.random() < 0.8 else "nuke" or "frozen"
        bomb = Bombs(self.player, bomb_type, bomb_x, bomb_y)
        all_sprites.add(bomb)
        bombs_group.add(bomb)

    def explode(self):
        explosion_type = "nuke" if self.bomb_type == "nuke" else "normal"
        explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player,
                              explosion_type)
        all_sprites.add(explosion)

        if self.bomb_type == "regular":
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player,
                                  "normal")
            all_sprites.add(explosion)

        if self.bomb_type == "frozen":
            explosion = Explosion(self.rect.centerx, self.rect.bottom, self.player,
                                  "frozen")
            all_sprites.add(explosion)

        self.kill()
        bombs_group.add(explosion)


class HealthPack(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('image/health_pack.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.take = False
        self.speed = 4

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def random_health_pack(self):
        health_pack_x = random.randint(0, width - self.rect.width)
        health_pack_y = 0
        health_pack = HealthPack(health_pack_x, health_pack_y)
        self.all_sprites.add(health_pack)

    def collect(self, player):
        player.health += 0.5
        if player.health > 1.0:
            player.health = 1.0
        self.kill()

    def update(self, camera_x):
        if not self.take:
            self.rect.y += self.speed

            if self.rect.bottom > height:
                self.rect.bottom = height


class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y, player, explosion_type):
        super().__init__()
        self.player = player
        self.explosion_type = explosion_type
        self.animation_delay = 100
        self.animation_counter = 0
        self.animation_start_time = pygame.time.get_ticks()
        self.finished = False
        self.distance_threshold = 0
        self.damage_amount = 0

        if explosion_type == "normal":
            self.images = [
                pygame.image.load(image_path).convert_alpha()
                for image_path in LoadImage.explosion_files
            ]
            self.images = [
                pygame.transform.scale(image, (150, 150)) for image in self.images
            ]
            self.distance_threshold = 90
            self.damage_amount = 5

        elif explosion_type == "nuke":
            self.images = [
                pygame.image.load(image_path).convert_alpha()
                for image_path in LoadImage.nuke
            ]
            self.images = [
                pygame.transform.scale(image, (300, 300)) for image in self.images
            ]
            self.distance_threshold = 250
            self.damage_amount = 50

        elif explosion_type == "frozen":
            self.images = [
                pygame.image.load(image_path).convert_alpha()
                for image_path in LoadImage.frozen_bomb
            ]
            self.images = [
                pygame.transform.scale(image, (150, 150)) for image in self.images
            ]
            self.distance_threshold = 90
            self.damage_amount = 0

        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, camera_x):
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.animation_start_time

        if elapsed_time >= self.animation_delay:
            self.animation_counter += 1
            self.animation_start_time = current_time

        if self.animation_counter < len(self.images):
            self.image = self.images[self.animation_counter]

        if self.rect.bottom > height:
            self.rect.bottom = height

        if self.animation_counter >= len(self.images) - 1:
            if not self.finished:
                self.finished = True
                self.handle_collisions()
                self.kill()

    def handle_collisions(self):
        if self.player:
            player_rect = self.player.rect
            player_center_x = player_rect.centerx
            player_bottom = player_rect.bottom

            if (player_center_x - self.rect.centerx) ** 2 + (
                    player_bottom - self.rect.bottom) ** 2 <= self.distance_threshold ** 2:
                if self.explosion_type == "frozen":
                    self.player.frozen = True
                    self.player.frozen_duration = 0
                else:
                    self.player.health -= self.damage_amount
                    self.player.slow_duration = 420
                    self.player.slow_start_time = pygame.time.get_ticks()
                    self.player.slow_counter = 0
                    self.player.slow_start_x = self.player.rect.centerx
                    self.player.slow_start_y = self.player.rect.centery


class GameLoop:
    def __init__(self):
        pygame.init()

        self.player = Player()
        width, height = 1080, 720
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("The Running Zombie")
        self.time_of_death = 0
        self.game_state = "playing"
        self.running = True
        self.clock = pygame.time.Clock()
        self.death_animation_started = False
        self.death_animation_duration = 800
        self.death_animation_start_time = 0
        self.death_screen_duration = 1000
        self.death_screen_start_time = 1000
        self.bombs_group = pygame.sprite.Group()
        self.gui = Gui(self.player)
        self.camera_x = 0

        bombs_group = pygame.sprite.Group()
        self.bombs_group = bombs_group

        self.props_group = pygame.sprite.Group()
        self.prop_images = ["half_car.png", "moon_cross.png"]

        prop = Props(70, 650, "half_car", "right", self.camera_x)
        prop2 = Props(500, 410, "moon_cross", "left", self.camera_x)
        self.props_group.add(prop, prop2)

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.all_sprites.add(prop, prop2)

        self.last_bomb_spawn_time = pygame.time.get_ticks()
        self.bomb_spawn_delay = random.randint(2500, 4000)
        self.last_nuke_spawn_time = pygame.time.get_ticks()
        self.nuke_spawn_delay = random.randint(4000, 7000)
        self.last_frozen_spawn_time = pygame.time.get_ticks()
        self.frozen_spawn_delay = random.randint(4000, 7000)

        # Create a group to store health packs
        health_packs_group = pygame.sprite.Group()
        self.health_packs_group = health_packs_group

        pygame.sprite.Group()
        prop = Props(70, 650, "half_car", "right", self.camera_x)
        prop2 = Props(500, 410, "moon_cross", "left", self.camera_x)
        self.props_group.add(prop, prop2)
        self.all_sprites.add(prop, prop2)

        self.player = Player()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def restart_game(self):
        self.game_state = "playing"
        self.player = Player()
        self.gui = Gui(self.player)
        self.camera_x = 0
        self.all_sprites.empty()
        self.all_sprites.add(self.player)
        self.bombs_group.empty()
        self.last_bomb_spawn_time = pygame.time.get_ticks()
        self.bomb_spawn_delay = random.randint(2500, 4000)
        self.last_nuke_spawn_time = pygame.time.get_ticks()
        self.nuke_spawn_delay = random.randint(4000, 7000)
        self.last_frozen_spawn_time = pygame.time.get_ticks()
        self.frozen_spawn_delay = random.randint(4000, 7000)

    def run(self):
        after_death = AfterDeath(self.screen, death_screen, LoadImage.restart_button, LoadImage.exit_button)

        while self.running:
            self.handle_events()
            current_time = pygame.time.get_ticks()

            if not self.death_animation_started:
                if current_time - self.last_bomb_spawn_time >= self.bomb_spawn_delay:
                    bomb_regular = Bombs(self.player, "regular", random.randint(0, width), 0)
                    self.all_sprites.add(bomb_regular)
                    self.bombs_group.add(bomb_regular)  # Add the bomb to the bombs_group
                    self.last_bomb_spawn_time = current_time
                    self.bomb_spawn_delay = random.randint(2500, 4000)

            if self.game_state == "playing":
                if self.player.health <= 0:
                    self.game_state = "death_animation"
                    self.death_animation_start_time = current_time
                    self.player.animate()

            elif self.game_state == "death_animation":
                if current_time - self.death_animation_start_time >= self.death_animation_duration:
                    self.game_state = "death_screen"
                    self.player.animate()

            elif self.game_state == "death_screen":
                selected_action = after_death.run()
                if selected_action == "restart":
                    self.restart_game()
                elif selected_action == "exit":
                    self.running = False
                    sys.exit()

            if random.random() < 0.02:
                health_pack = HealthPack(random.randint(0, width - 30), 0)
                self.all_sprites.add(health_pack)
                health_packs_group.add(health_pack)

            for health_pack in health_packs_group:
                health_pack.update(self.camera_x)
                if health_pack.rect.top > height:
                    health_pack.kill()

            collected_health_packs = pygame.sprite.spritecollide(player, health_packs_group, True)
            for health_pack in collected_health_packs:
                health_pack.collect(player)

            if not self.death_animation_started:
                if current_time - self.last_bomb_spawn_time >= self.bomb_spawn_delay:
                    bomb_regular = Bombs(self.player, "regular", random.randint(0, width), 0)
                    self.all_sprites.add(bomb_regular)
                    bombs_group.add(bomb_regular)  # Add the bomb to the bombs_group
                    self.last_bomb_spawn_time = current_time
                    self.bomb_spawn_delay = random.randint(2500, 4000)

            if current_time - self.last_nuke_spawn_time >= self.nuke_spawn_delay:
                bomb_nuke = Bombs(self.player, "nuke", random.randint(0, width), 0)
                self.all_sprites.add(bomb_nuke)
                bombs_group.add(bomb_nuke)  # Add the bomb to the bombs_group
                self.last_nuke_spawn_time = current_time
                self.nuke_spawn_delay = random.randint(4000, 7000)

            if current_time - self.last_frozen_spawn_time >= self.frozen_spawn_delay:
                bomb_frozen = Bombs(self.player, "frozen", random.randint(0, width), 0)
                self.all_sprites.add(bomb_frozen)
                bombs_group.add(bomb_frozen)  # Add the bomb to the bombs_group
                self.last_frozen_spawn_time = current_time
                self.frozen_spawn_delay = random.randint(5000, 8000)

            self.camera_x = max(
                0,
                min(int(self.player.rect.x - (width // 2)),
                    int(background1.get_width() - width)))
            self.screen.blit(background1, (-self.camera_x, 0))

            if self.death_animation_started:
                if current_time - self.death_animation_start_time >= self.death_animation_duration:
                    self.running = False

            self.props_group.update(self.camera_x)
            self.props_group.draw(self.screen)
            health_packs_group.update(self.camera_x)

            for explosion in explosion_group:
                explosion.update(self.camera_x)
                explosion.draw(screen)

            for bomb in bombs_group:
                bomb.update(self.camera_x)
                if bomb.rect.colliderect(player.rect):
                    explosion = Explosion(bomb.rect.centerx, bomb.rect.bottom, player)
                    explosion_group.add(explosion)

                self.screen.blit(bomb.image, (bomb.rect.x - self.camera_x, bomb.rect.y))

            for health_pack in health_packs_group:
                health_pack.draw(self.screen)

            self.all_sprites.update(self.camera_x)
            self.player.update(self.camera_x)
            self.gui.draw_health_bar()
            self.gui.draw_point_score(screen)
            self.all_sprites.draw(self.screen)
            self.player.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        if not self.running:
            self.screen.blit(death_screen, (0, 0))
            pygame.display.flip()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    game_loop = GameLoop()
    game_loop.run()
    