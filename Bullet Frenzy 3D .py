from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

# Global Constants (Game Setup) 
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
TILE_SIZE = 100
GRID_SIZE = 13 # 13x13 grid
TOTAL_GRID_SIZE = GRID_SIZE * TILE_SIZE
OFFSET = TOTAL_GRID_SIZE / 2 # Center the grid around (0, 0)
WALL_HEIGHT = 100

# Calculate grid bounds
GRID_MIN = -OFFSET
GRID_MAX = +OFFSET 

# grid boundary checks
def within_grid(x, y, pad=0.0):
    return (GRID_MIN + pad <= x <= GRID_MAX - pad) and (GRID_MIN + pad <= y <= GRID_MAX - pad)

# Entity Classes 

class Player:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.speed = 35.0
        self.acceleration = 5.0
        self.friction = 0.9
        self.life = 5
        self.size_pad = 20 # Padding for wall collision

    def apply_movement(self, key_pressed):
        if key_pressed == b'd':
            self.angle -= 15
        elif key_pressed == b'a':
            self.angle += 15
        
        rad = math.radians(self.angle)
        
        if key_pressed == b'w':
            self.vel_x += math.sin(-rad) * self.acceleration
            self.vel_y += math.cos(rad) * self.acceleration
        elif key_pressed == b's':
            self.vel_x -= math.sin(-rad) * self.acceleration
            self.vel_y -= math.cos(rad) * self.acceleration

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # player position within grid bounds
        self.x = max(GRID_MIN + self.size_pad, min(self.x, GRID_MAX - self.size_pad))
        self.y = max(GRID_MIN + self.size_pad, min(self.y, GRID_MAX - self.size_pad))

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)

        # Player rotation: 90 degrees on game over
        if game.game_over:
            glRotatef(90, 0, -1, 0)
        else:
            glRotatef(self.angle, 0, 0, 1)

        
        

        # Left leg
        glPushMatrix()
        glColor3f(0, 0, 1)
        glTranslatef(-10, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 8, 50, 20, 20)
        glPopMatrix()

        # Right leg
        glPushMatrix()
        glColor3f(0, 0, 1)
        glTranslatef(10, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 8, 50, 20, 20)
        glPopMatrix()
        
        #  Body 
        glPushMatrix()
        glColor3f(0.0, 1, 0.0)
        glTranslatef(0, 0, 75)
        glScalef(0.8, 0.4, 2.0)
        glutSolidCube(30)
        glPopMatrix()
        
        #  Main Gun
        glPushMatrix()
        glColor3f(0.7, 0.7, 0.7)
        glTranslatef(0, 0, 90)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 10, 3, 80, 20, 20)
        glPopMatrix()
        
        # Left hand
        glPushMatrix()
        glColor3f(1.0, 0.8, 0.6)
        glTranslatef(-20, 10, 100)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 8, 3, 40, 20, 20)
        glPopMatrix()
        
        # Right hand
        glPushMatrix()
        glColor3f(1.0, 0.8, 0.6)
        glTranslatef(20, 10, 100)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 8, 3, 40, 20, 20)
        glPopMatrix()
        
        # Head 
        glPushMatrix()
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, 0, 120)
        glutSolidSphere(22, 20, 20)
        glPopMatrix()

         # Clean up quadric object
        glPopMatrix()

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.life = 5


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.z = 95 # Consistent height
        self.speed = 3.0
        self.size = 10.0
        self.max_dist = 100000.0
        self.dist = 0.0

        rad = math.radians(angle)
        self.dx = math.sin(-rad) * self.speed
        self.dy = math.cos(rad) * self.speed

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dist += math.hypot(self.dx, self.dy)
        return within_grid(self.x, self.y) and self.dist <= self.max_dist

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(1.0, 0.0, 0.0)
        glutSolidCube(self.size)
        glPopMatrix()

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.1
        self.min_distance = 100
        self.radius = 40

    def draw(self, scale):
        # Draw Enemy 
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glScalef(scale, scale, 1.0)
        glColor3f(1.0, 0.0, 0.0)
        glutSolidSphere(self.radius, 20, 20)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(self.x, self.y, self.radius)
        glScalef(scale, scale, 1.0)
        glColor3f(0.0, 0.0, 0.0)
        glutSolidSphere(24, 20, 20)
        glPopMatrix()


class GameState:
    def __init__(self):
        self.player = Player()
        self.enemies = []
        self.bullets = []
        
        self.score = 0
        self.bullets_missed = 0
        self.max_missed_bullets = 10
        
        self.game_over = False
        self.game_over_reason = ""
        
        # Enemy spawning and animation
        self.initial_enemy_count = 5
        self.enemy_scale = 1.0
        self.scale_growing = True
        
        # Camera & View
        self.camera_pos = (0, 500, 500)
        self.fovY = 120
        self.first_person = False
        self.auto_cam_follow = False # For cheat mode
        
        # Cheat mode
        self.cheat_mode = False
        self.cheat_bullet_ready = True
        self.aim_tolerance_deg = 5.0

        self.spawn_initial_enemies()

    def random_spawn_point(self, min_dist_from_player=150):
        pad = 50
        for i in range(100):
            rx = random.randint(int(GRID_MIN) + pad, int(GRID_MAX) - pad)
            ry = random.randint(int(GRID_MIN) + pad, int(GRID_MAX) - pad)
            if math.hypot(rx - self.player.x, ry - self.player.y) >= min_dist_from_player:
                return [rx, ry]
        return [GRID_MIN + pad, GRID_MIN + pad] # Fallback

    def spawn_initial_enemies(self):
        self.enemies = []
        for i in range(self.initial_enemy_count):
            x, y = self.random_spawn_point(min_dist_from_player=500)
            self.enemies.append(Enemy(x, y))

    def set_game_over(self, reason):
        self.game_over = True
        self.game_over_reason = reason
        self.player.vel_x = 0
        self.player.vel_y = 0

    def move_enemies(self):
        if self.game_over:
            return

        for i, enemy in enumerate(self.enemies):
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist_to_player = math.hypot(dx, dy)

            # Move towards player
            if dist_to_player > enemy.min_distance:
                enemy.x += (dx / dist_to_player) * enemy.speed
                enemy.y += (dy / dist_to_player) * enemy.speed

            # space from other enemies
            for j, other_enemy in enumerate(self.enemies):
                if i == j: continue
                dx2 = enemy.x - other_enemy.x
                dy2 = enemy.y - other_enemy.y
                dist = math.hypot(dx2, dy2)
                if dist < enemy.min_distance and dist != 0:
                    push = (enemy.min_distance - dist) / 2.0
                    enemy.x += (dx2 / dist) * push
                    enemy.y += (dy2 / dist) * push

            # enemy position within grid bounds
            pad = 30
            enemy.x = max(GRID_MIN + pad, min(enemy.x, GRID_MAX - pad))
            enemy.y = max(GRID_MIN + pad, min(enemy.y, GRID_MAX - pad))
            
            # Check collision with player
            if not self.game_over and math.hypot(enemy.x - self.player.x, enemy.y - self.player.y) < 100:
                self.player.life = max(0, self.player.life - 1)
                new_x, new_y = self.random_spawn_point(min_dist_from_player=150)
                enemy.x = new_x
                enemy.y = new_y
                if self.player.life <= 0:
                    self.set_game_over("life")

    def update_enemy_scale(self):
        if self.game_over: return
        
        if self.scale_growing:
            self.enemy_scale += 0.01
            if self.enemy_scale >= 1.5:
                self.scale_growing = False
        else:
            self.enemy_scale -= 0.01
            if self.enemy_scale <= 1.0:
                self.scale_growing = True

    def fire_bullet(self):
        if self.game_over: return
        
        # Calculate position
        rad = math.radians(self.player.angle)
        dir_x = math.sin(-rad)
        dir_y = math.cos(rad)
        muzzle_offset = 60
        
        bx = self.player.x + dir_x * muzzle_offset
        by = self.player.y + dir_y * muzzle_offset
        
        if not within_grid(bx, by, pad=20):
            bx, by = self.player.x, self.player.y

        new_bullet = Bullet(bx, by, self.player.angle)
        self.bullets.append(new_bullet)

    def update_bullets_and_collisions(self):
        if self.game_over: return
        
        new_bullets = []
        for bullet in self.bullets:
            if not bullet.update():
                # Out of bounds or max distance reached
                self.bullets_missed += 1
                self.cheat_bullet_ready = True
                if self.bullets_missed >= self.max_missed_bullets:
                    self.set_game_over("miss")
                continue

            hit = False
            for i, enemy in enumerate(self.enemies):
                # Enemy hit check
                if math.hypot(bullet.x - enemy.x, bullet.y - enemy.y) <= enemy.radius + 5:
                    self.score += 1
                    new_x, new_y = self.random_spawn_point(min_dist_from_player=150)
                    enemy.x = new_x
                    enemy.y = new_y
                    self.cheat_bullet_ready = True
                    hit = True
                    break
            
            if not hit:
                new_bullets.append(bullet)

        self.bullets = new_bullets
    
    def cheat_mode_behavior(self):
        if not self.enemies: return

        # Constant rotation
        self.player.angle += 1
        self.player.angle %= 360

        if not self.cheat_bullet_ready: return

        # Auto-aim logic
        target_enemy = None
        min_dist = float('inf')
        
        for enemy in self.enemies:
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            dist = math.hypot(dx, dy)

            angle_to_enemy = math.degrees(math.atan2(-dx, dy)) % 360
            
            diff = abs(self.player.angle - angle_to_enemy)
            if diff > 180:
                diff = 360 - diff

            if diff < self.aim_tolerance_deg and dist < min_dist:
                min_dist = dist
                target_enemy = enemy

        if target_enemy:
            self.fire_bullet()
            self.cheat_bullet_ready = False
            
    def reset_game(self):
        self.player.reset()
        self.score = 0
        self.bullets_missed = 0
        self.bullets = []
        self.game_over = False
        self.game_over_reason = ""
        self.enemy_scale = 1.0
        self.scale_growing = True
        self.spawn_initial_enemies()
        self.first_person = False
        self.camera_pos = (0, 500, 500)
        self.cheat_mode = False
        self.auto_cam_follow = False
        self.cheat_bullet_ready = True


# Global game e gamestate call kora
game = GameState()

 

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid_and_walls():
    # Floor (Chessboard pattern)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if (i + j) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0) # White
            else:
                glColor3f(0.6, 0.4, 0.8) # Purple
            x = j * TILE_SIZE + GRID_MIN
            y = i * TILE_SIZE + GRID_MIN
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0.0)
            glVertex3f(x + TILE_SIZE, y, 0.0)
            glVertex3f(x + TILE_SIZE, y + TILE_SIZE, 0.0)
            glVertex3f(x, y + TILE_SIZE, 0.0)
            glEnd()
    
    # Walls (4 sides)
    left, right = GRID_MIN, GRID_MAX
    bottom, top = GRID_MIN, GRID_MAX

    # Bottom (Front)
    glColor3f(0.3, 1.0, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(left, bottom, 0.0)
    glVertex3f(right, bottom, 0.0)
    glVertex3f(right, bottom, WALL_HEIGHT)
    glVertex3f(left, bottom, WALL_HEIGHT)
    glEnd()

    #  Right
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(right, bottom, 0.0)
    glVertex3f(right, top, 0.0)
    glVertex3f(right, top, WALL_HEIGHT)
    glVertex3f(right, bottom, WALL_HEIGHT)
    glEnd()
    
    # Top (Back)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(right, top, 0.0)
    glVertex3f(left, top, 0.0)
    glVertex3f(left, top, WALL_HEIGHT)
    glVertex3f(right, top, WALL_HEIGHT)
    glEnd()
    
    #  Left
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(left, top, 0.0); glVertex3f(left, bottom, 0.0)
    glVertex3f(left, bottom, WALL_HEIGHT); glVertex3f(left, top, WALL_HEIGHT)
    glEnd()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(game.fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    x, y, z = game.camera_pos

    if game.first_person:
        # First-person view
        rad = math.radians(game.player.angle)
        cam_z = 175
        
        cam_x = game.player.x
        cam_y = game.player.y
        
        look_x = cam_x + math.sin(-rad) * 100
        look_y = cam_y + math.cos(rad) * 100
        
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, cam_z, 0, 0, 1)

    elif game.cheat_mode and game.auto_cam_follow:
        # Special cheat camera view
        cam_x, cam_y, cam_z = 40, 20, 160
        look_x, look_y, look_z = -20, -20, 150
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)

    else:
        # Default Top-Down view
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def showScreen():
   
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    
    setupCamera()
    
    
    draw_grid_and_walls()

    
    for enemy in game.enemies:
        enemy.draw(game.enemy_scale)
    game.player.draw()
    for bullet in game.bullets:
        bullet.draw()
    
    
    glLoadIdentity()
    
    
    if not game.game_over:
        draw_text(15, 770, f"Player Life Remaining: {game.player.life}")
        draw_text(15, 740, f"Game Score: {game.score}")
        draw_text(15, 710, f"Bullets Missed: {game.bullets_missed} / {game.max_missed_bullets}")
        draw_text(15, 680, f"Cheat Mode: {'ON' if game.cheat_mode else 'OFF'} (Press C)")
    else:
        draw_text(15, 770, "GAME OVER")
        reason = "You ran out of lives!" if game.game_over_reason == "life" else "You missed 10 bullets!"
        draw_text(15, 740, reason)
        draw_text(15, 710, f"Final Score: {game.score}")
        draw_text(15, 680, "Press 'R' to Restart")
        
    glutSwapBuffers()



def keyboardListener(key, x, y):
    if game.game_over:
        if key in (b'R', b'r'):
            game.reset_game()
        return

    if key in (b'w', b'a', b's', b'd'):
        game.player.apply_movement(key)
    elif key in (b'R', b'r'):
        game.reset_game()
    elif key in (b'C', b'c'):
        game.cheat_mode = not game.cheat_mode
    elif key in (b'V', b'v'):
        game.auto_cam_follow = not game.auto_cam_follow

def specialKeyListener(key, x, y):
    cx, cy, cz = game.camera_pos
    if key == GLUT_KEY_UP:
        cz += 10
    if key == GLUT_KEY_DOWN:
        cz -= 10
    if key == GLUT_KEY_LEFT:
        cx -= 10
    if key == GLUT_KEY_RIGHT:
        cx += 10
    game.camera_pos = (cx, cy, cz)

def mouseListener(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        game.fire_bullet()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        game.first_person = not game.first_person

def idle():
    if not game.game_over:
        game.player.update()
        game.move_enemies()
        game.update_enemy_scale()
        game.update_bullets_and_collisions()
        
        if game.cheat_mode:
            game.cheat_mode_behavior()

    glutPostRedisplay()



def main():
    glutInit()
   
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB) 
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy 3D ")
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()