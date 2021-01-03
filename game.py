
import arcade
import os
import random
import math
import time
import threading

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Space shooter game"
LEFT_LIMIT = 150
RIGHT_LIMIT = SCREEN_WIDTH - 40
BOTTOM_LIMIT = 350
TOP_LIMIT = SCREEN_HEIGHT - 40

EXPLOSION_TEXTURE_COUNT = 60


class Explosion(arcade.Sprite):
    """ This class creates an explosion animation """

    def __init__(self, texture_list):
        super().__init__()

        # Start at the first frame
        self.current_texture = 0
        self.textures = texture_list

    def update(self):

        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()

class BulletSprite(arcade.Sprite):
    def __init__(self, image_file_name, scale):
        super().__init__(image_file_name, scale=scale)

    def update(self):
        super().update()
        #Remove bullets if they fly offscreen
        if self.top < 0:
            self.remove_from_sprite_lists()

        if self.top > SCREEN_HEIGHT:
            self.remove_from_sprite_lists()

class PlayerSprite(arcade.Sprite):

    def __init__(self, image_file_name, scale):

        super().__init__(image_file_name, scale=scale)

        self.respawning = 0
        self.shield = 0
        self.respawn()

    def update(self):

        super().update()

        if self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH
        if self.left < 150:
            self.left = 150

        if self.respawning:
            self.respawning += 1
            self.alpha = self.respawning
            if self.respawning > 250:
                self.respawning = 0
                self.alpha = 255
        
        if self.shield:
            self.shield += 1
            if self.shield < 255:
                self.alpha = self.shield
            if self.shield > 360:
                self.shield = 0
    
    def respawn(self):
        self.respawning = 1
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = 20

    def makeShield(self):
        #deploy a shield
        self.shield = 1

class MyGame(arcade.Window):

    def __init__(self,width,height,title):
        super().__init__(width,height,title)

        self.frame_count = 0

        self.player_list = None
        self.enemy_list = None
        self.bullet_list = None
        self.player_bullet_list = None
        self.explosions_list = None
        self.ship_life_list = None
        self.player = None

        self.background = None
        self.gun_sound = None
        self.hit_sound = None

        self.set_mouse_visible(False)

        self.score = 0
        self.gameOver = False
        self.lives = 3
        self.level = 1
        #This represnts the probability of the enemy shooting in each frame (1/200)
        self.probability = 200
        self.shield = 3
        self.misses = 0

        self.explosion_texture_list = []
    
    def setup(self):
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.ship_life_list = arcade.SpriteList()

        #Load the backgrounds and sounds
        self.background = arcade.load_texture("stars.jpg")
        #When a bullet is fired
        self.gun_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        #When a bullet hits a player or enemy
        self.hit_sound = arcade.sound.load_sound(":resources:sounds/explosion2.wav")
        #When shield is deployed
        self.shield_sound = arcade.sound.load_sound(":resources:sounds/upgrade5.wav")
        #When game is over
        self.gameOver_sound = arcade.sound.load_sound(":resources:sounds/gameover1.wav")         

        # Add player ship
        self.player = PlayerSprite(":resources:images/space_shooter/playerShip3_orange.png", 0.5)
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.center_y = 20
        self.player_list.append(self.player)

        #Add enemies
        self.spawnEnemies()

        #Add the little icons at the bottom left corner represeting lives
        cur_pos = 0
        for i in range(self.lives):
            life = arcade.Sprite(":resources:images/space_shooter/playerLife1_orange.png", 0.7)
            life.center_x = cur_pos + life.width
            life.center_y = life.height
            cur_pos += life.width
            self.ship_life_list.append(life)

        # Load the explosions from a sprite sheet
        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        file_name = ":resources:images/spritesheets/explosion.png"
        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)

        #Play song
        self.play_song()

    def on_draw(self):
    
        arcade.start_render()

        #Draw the background
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        #Draw the score, Game over texts and the little icons representing the player lives
        arcade.draw_text(f"Score: {self.score}", 10,70, arcade.color.WHITE, 15)
        if self.gameOver:
            arcade.draw_text(f"Game Over!", 10, 250, arcade.color.RED, 20)
        arcade.draw_text(f"Level: {self.level}", 10,90, arcade.color.WHITE, 15)
        self.ship_life_list.draw()

        #Draw the the no. of shields the player has remaining (A shield gives player immunity from collisions for 6 secs)
        arcade.draw_text(f"Shields: {self.shield}", 10, 150, arcade.color.WHITE, 15)

        #Draw hit/miss ratio after game is over
        if self.gameOver:
            if self.score != 0 :
                arcade.draw_text(f"Ratio : {round((self.misses/self.score)*100,2)}%", 10, 200, arcade.color.WHITE, 15)
            else:
                arcade.draw_text(f"No hits", 10, 200, arcade.color.WHITE, 15)

        #Draw the player,enemy Ships, explosions and bullets
        self.player_bullet_list.draw()
        self.explosions_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()

    def spawnEnemies(self):
        #Level 1 of enemies
        EnemyCount = random.randrange(5, 15)
        for i in range(EnemyCount):
            enemy_sprite = arcade.Sprite(":resources:images/space_shooter/playerShip1_green.png", 0.5)
            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)
            enemy_sprite.change_y = -0.5
            enemy_sprite.angle = 180
            self.enemy_list.append(enemy_sprite)
    
    def spawnEnemiesLevel2(self):
        #Level 2 of enemies
        EnemyCount = random.randrange(15, 25)
        self.probability = 100
        self.level = 2
        for i in range(EnemyCount):
            enemy_sprite = arcade.Sprite("enemyShip.png", 0.5)
            enemy_sprite.center_y = random.randrange(BOTTOM_LIMIT, TOP_LIMIT)
            enemy_sprite.center_x = random.randrange(LEFT_LIMIT, RIGHT_LIMIT)
            enemy_sprite.change_y = -0.5
            enemy_sprite.angle = 180
            self.enemy_list.append(enemy_sprite)

    def createExplosion(self, hit_list):
        #Creates an explosion animation
        explosion = Explosion(self.explosion_texture_list)
        explosion.center_x = hit_list[0].center_x
        explosion.center_y = hit_list[0].center_y
        explosion.update()
        self.explosions_list.append(explosion)
        arcade.sound.play_sound(self.hit_sound)

    def play_song(self):
        self.music = arcade.Sound("music.mp3", streaming=True)
        self.music.play(0.5)

    def stopGame(self):
        self.player.remove_from_sprite_lists()
        self.music.stop()
        self.gameOver = True
        self.shield = 0
        self.level = 0
        arcade.play_sound(self.gameOver_sound)

    def on_update(self, delta_time):
        
        #This is a 60 fps game, so this function is called 60 times each second

        for enemy in self.enemy_list:
            #If enemy flies off screen, it reappers on the top. Also increments misses by 1
            if enemy.center_y < 0:
                enemy.center_y = TOP_LIMIT
                if not self.gameOver:
                    self.misses += 1

        if len(self.enemy_list) == 0:
            #Check which level we are in and spawn enemies accordingly
            if (self.score <= 50):
                self.spawnEnemies()
            else:
                self.spawnEnemiesLevel2()

        if not self.gameOver:

            #loop through each enemy we have and have them shoot 
            for enemy in self.enemy_list:
                if random.randrange(self.probability) == 0:
                    bullet = BulletSprite(":resources:images/space_shooter/laserBlue01.png",1)
                    bullet.center_x = enemy.center_x
                    bullet.angle = -90
                    bullet.top = enemy.bottom
                    bullet.change_y = -2
                    self.bullet_list.append(bullet)

            #Check for bullet collisions with enemies
            for bullet in self.player_bullet_list:
                hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                if len(hit_list) > 0:
                    self.createExplosion(hit_list)
                    bullet.remove_from_sprite_lists()
                for enemy in hit_list:
                    self.score += 1
                    enemy.remove_from_sprite_lists()
                    arcade.sound.play_sound(self.hit_sound)

            #Check for bullet collisions with player
            if (not self.player.respawning) and (not self.player.shield):
                for bullet in self.bullet_list:
                    hit_list = arcade.check_for_collision_with_list(bullet, self.player_list)
                    if len(hit_list) > 0:
                        self.createExplosion(hit_list)
                        bullet.remove_from_sprite_lists()
                        if self.lives > 0:
                            self.lives -= 1
                            self.player.respawn()
                            self.ship_life_list.pop().remove_from_sprite_lists()
                        else:
                            self.stopGame()

            #Check for collisions between player and enemy
            if (not self.player.respawning) and (not self.player.shield):
                for enemy in self.enemy_list:
                    hit_list = arcade.check_for_collision_with_list(enemy, self.player_list)
                    if len(hit_list) > 0:
                        self.createExplosion(hit_list)
                        enemy.remove_from_sprite_lists()
                        if self.lives > 0:
                            self.lives -= 1
                            self.player.respawn()
                            self.ship_life_list.pop().remove_from_sprite_lists()
                        else:
                            self.stopGame()           

        self.bullet_list.update()
        self.player_bullet_list.update()
        self.player_list.update()
        self.enemy_list.update()
        self.explosions_list.update()

    def on_key_press(self, key, modifiers):

        if not self.gameOver:
            if key == arcade.key.LEFT:
                #Move left
                self.player.change_x = -5
            elif key == arcade.key.RIGHT:
                #Move right
                self.player.change_x = 5
            elif key == arcade.key.SPACE:
                #Space key is used for shooting a bullet
                arcade.play_sound(self.gun_sound)
                bullet = BulletSprite(":resources:images/space_shooter/laserRed01.png",1)
                bullet.center_x = self.player.center_x
                bullet.bottom = self.player.top
                bullet.angle = 0
                bullet.change_y = 5
                self.player_bullet_list.append(bullet)
            elif key == arcade.key.Z:
                #Z key for deploying a shield
                if self.shield > 0:
                    self.shield -= 1
                    arcade.play_sound(self.shield_sound)
                    self.player.makeShield()
                

    def on_key_release(self, key, modifiers):
        if not self.gameOver:
            if key == arcade.key.LEFT or key == arcade.key.RIGHT:
                self.player.change_x = 0

def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

    
