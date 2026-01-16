from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random



def draw_sphere_manual(radius, slices, stacks):
    glBegin(GL_TRIANGLES)
    for i in range(slices):
        for j in range(stacks):
            phi1 = math.pi * i / slices
            phi2 = math.pi * (i + 1) / slices
            theta1 = 2 * math.pi * j / stacks
            theta2 = 2 * math.pi * (j + 1) / stacks

            
            v1 = [radius*math.sin(phi1)*math.cos(theta1),
                  radius*math.sin(phi1)*math.sin(theta1),
                  radius*math.cos(phi1)]
            v2 = [radius*math.sin(phi2)*math.cos(theta1),
                  radius*math.sin(phi2)*math.sin(theta1),
                  radius*math.cos(phi2)]
            v3 = [radius*math.sin(phi2)*math.cos(theta2),
                  radius*math.sin(phi2)*math.sin(theta2),
                  radius*math.cos(phi2)]
            v4 = [radius*math.sin(phi1)*math.cos(theta2),
                  radius*math.sin(phi1)*math.sin(theta2),
                  radius*math.cos(phi1)]

            
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
            glVertex3f(v3[0], v3[1], v3[2])

           
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v3[0], v3[1], v3[2])
            glVertex3f(v4[0], v4[1], v4[2])
    glEnd()

def draw_cone_manual(radius, height, slices):
    glBegin(GL_TRIANGLES)
    for i in range(slices):
        angle1 = 2 * math.pi * i / slices
        angle2 = 2 * math.pi * (i + 1) / slices

        # Base
        glVertex3f(0, 0, 0)
        glVertex3f(radius * math.cos(angle1), radius * math.sin(angle1), 0)
        glVertex3f(radius * math.cos(angle2), radius * math.sin(angle2), 0)

        # Sides
        glVertex3f(radius * math.cos(angle1), radius * math.sin(angle1), 0)
        glVertex3f(radius * math.cos(angle2), radius * math.sin(angle2), 0)
        glVertex3f(0, 0, height)
    glEnd()

def draw_cube_manual(size):
    s = size / 2.0
    vertices = [
        [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
        [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]
    ]
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
        (2, 3, 7, 6), (0, 4, 7, 3), (1, 2, 6, 5)
    ]

    glBegin(GL_TRIANGLES)
    for f in faces:
        a = vertices[f[0]]
        b = vertices[f[1]]
        c = vertices[f[2]]
        d = vertices[f[3]]

        
        glVertex3f(a[0], a[1], a[2])
        glVertex3f(b[0], b[1], b[2])
        glVertex3f(c[0], c[1], c[2])

        
        glVertex3f(a[0], a[1], a[2])
        glVertex3f(c[0], c[1], c[2])
        glVertex3f(d[0], d[1], d[2])
    glEnd()



class Bullet:
    def __init__(self, x, y, z, target_x, target_y, damage, from_enemy):
        self.x, self.y, self.z = x, y, z
        self.damage = damage
        self.speed = 12.0
        self.from_enemy = from_enemy
        self.trail_positions = []
        self.max_trail_length = 8

        dx = target_x - x
        dy = target_y - y
        dist_horizontal = math.sqrt(dx**2 + dy**2)

        self.vx = (dx / dist_horizontal) if dist_horizontal > 0 else 0
        self.vy = (dy / dist_horizontal) if dist_horizontal > 0 else 0
        self.vz = -self.z / (dist_horizontal / self.speed) if dist_horizontal > 0 else -self.speed
        self.glow_phase = random.random() * math.pi * 2

    def move(self, dt):
        self.trail_positions.append((self.x, self.y, self.z))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt
        self.z += self.vz * dt
        self.glow_phase += 0.3

def draw_bullets(blt):
    for b in blt:
        
        if len(b.trail_positions) > 1:
            glBegin(GL_LINES)
            for i in range(len(b.trail_positions) - 1):
                if b.from_enemy:
                    glColor3f(1.0, 0.2, 0.2)
                else:
                    glColor3f(0.2, 0.8, 1.0)
                glVertex3f(b.trail_positions[i][0], b.trail_positions[i][1], b.trail_positions[i][2])
                glVertex3f(b.trail_positions[i + 1][0], b.trail_positions[i + 1][1], b.trail_positions[i + 1][2])
            glEnd()

        glPushMatrix()
        glTranslatef(b.x, b.y, b.z)
        if b.from_enemy:
            glColor3f(1.0, 0.1, 0.1)
        else:
            glColor3f(0.2, 0.9, 1.0)
        draw_sphere_manual(5, 8, 8)
        glPopMatrix()

class MortarRocket:
    def __init__(self, x, y, z, target_x, target_y, damage):
        self.x, self.y, self.z = x, y, z
        self.damage = damage
        self.gravity = -0.5
        self.vz = 15.0

        inner_val = max(0, (self.vz ** 2) - (2 * self.gravity * self.z))
        flight_time = (-self.vz - math.sqrt(inner_val)) / self.gravity
        self.vx = (target_x - x) / flight_time
        self.vy = (target_y - y) / flight_time

        self.spin = random.random() * 360
        self.smoke_trail = []
        self.impact_predicted = (target_x, target_y)

    def move(self, dt):
        step = dt * 60
        if random.random() < 0.3:
            self.smoke_trail.append({
                'x': self.x, 'y': self.y, 'z': self.z,
                'life': 60, 'size': random.uniform(8, 15)
            })

        for smoke in self.smoke_trail:
            smoke['life'] -= 1
        self.smoke_trail = [s for s in self.smoke_trail if s['life'] > 0]

        self.x += self.vx * step
        self.y += self.vy * step
        self.z += self.vz * step
        self.vz += self.gravity * step
        self.spin += 5

def draw_mortar_rockets(rockets):
    for r in rockets:
        for smoke in r.smoke_trail:
            glPushMatrix()
            glTranslatef(smoke['x'], smoke['y'], smoke['z'])
            glColor3f(0.3, 0.3, 0.3)
            draw_sphere_manual(smoke['size'], 5, 5)
            glPopMatrix()

        glPushMatrix()
        glTranslatef(r.x, r.y, r.z)
        angle = math.degrees(math.atan2(r.vx, r.vy))
        pitch = math.degrees(math.atan2(r.vz, math.hypot(r.vx, r.vy)))
        glRotatef(angle, 0, 0, 1)
        glRotatef(-pitch, 1, 0, 0)
        glRotatef(r.spin, 0, 0, 1)

        # Rocket Body
        glColor3f(0.8, 0.3, 0.1)
        # Cylinder simplified
        draw_sphere_manual(3.5, 6, 6)

        # Nose cone
        glTranslatef(0, 0, 6)
        glColor3f(0.9, 0.9, 0.1)
        draw_cone_manual(4, 8, 8)
        glPopMatrix()

        
        if r.z < 100:
            glPushMatrix()
            tx, ty = r.impact_predicted
            glTranslatef(tx, ty, 1)
            glColor3f(1, 0, 0)
            glBegin(GL_TRIANGLES)
            for i in range(20):
                a1 = 2 * math.pi * i / 20
                a2 = 2 * math.pi * (i + 1) / 20
                glVertex3f(0, 0, 0)
                glVertex3f(math.cos(a1) * 80, math.sin(a1) * 80, 0)
                glVertex3f(math.cos(a2) * 80, math.sin(a2) * 80, 0)
            glEnd()
            glPopMatrix()

class Explosion:
    def __init__(self, x, y, z, size=80):
        self.x, self.y, self.z = x, y, z
        self.size, self.life = size, 30
        self.max_life = 30
        self.particles = []
        for _ in range(10):
            self.particles.append({
                'x': x, 'y': y, 'z': z,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'vz': random.uniform(5, 15),
                'size': random.uniform(3, 8)
            })

    def update(self):
        self.life -= 1
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['z'] += p['vz']
            p['vz'] -= 0.8

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(1.0, 0.5, 0.0)
        draw_sphere_manual((1 - self.life / self.max_life) * self.size, 8, 8)
        glPopMatrix()

        for p in self.particles:
            if p['z'] > 0:
                glPushMatrix()
                glTranslatef(p['x'], p['y'], p['z'])
                glColor3f(0.3, 0.3, 0.3)
                draw_cube_manual(p['size'])
                glPopMatrix()

def check_collision(bx, by, br, ex, ey, er):
    dx, dy = bx - ex, by - ey
    return (dx * dx + dy * dy) <= (br + er) ** 2




###enemy

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time



def draw_sphere_manual(radius, slices, stacks):
    
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + float(i) / stacks)
        z0 = radius * math.sin(lat0)
        zr0 = radius * math.cos(lat0)

        lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
        z1 = radius * math.sin(lat1)
        zr1 = radius * math.cos(lat1)

        glBegin(GL_TRIANGLES)
        for j in range(slices):
            lng0 = 2 * math.pi * float(j) / slices
            x0 = math.cos(lng0)
            y0 = math.sin(lng0)

            lng1 = 2 * math.pi * float(j + 1) / slices
            x1 = math.cos(lng1)
            y1 = math.sin(lng1)

           
            glVertex3f(x0 * zr0, y0 * zr0, z0)
            glVertex3f(x1 * zr0, y1 * zr0, z0)
            glVertex3f(x0 * zr1, y0 * zr1, z1)

            glVertex3f(x1 * zr0, y1 * zr0, z0)
            glVertex3f(x1 * zr1, y1 * zr1, z1)
            glVertex3f(x0 * zr1, y0 * zr1, z1)
        glEnd()


def draw_circle_triangles(radius, segments):
    
    glBegin(GL_TRIANGLES)
    for i in range(segments):
        angle1 = 2.0 * math.pi * i / segments
        angle2 = 2.0 * math.pi * (i + 1) / segments

        # Center of the circle
        glVertex3f(0, 0, 0)
        # Point 1 on circumference
        glVertex3f(radius * math.cos(angle1), radius * math.sin(angle1), 0)
        # Point 2 on circumference
        glVertex3f(radius * math.cos(angle2), radius * math.sin(angle2), 0)
    glEnd()




class Enemy:
    def __init__(self, x, y, angle, id_val):
        self.x, self.y, self.z = x, y, 0
        self.angle = angle
        self.id = id_val
        self.damage = 20
        self.enemy_type = "grunt"

        self.health = 100
        self.max_health = 100
        self.is_alive = True
        self.attack_range = 600
        self.gun_pitch = 0.0
        self.speed = 0.8
        self.stop_dist = 400
        self.cooldown = 0

        self.bob_phase = random.random() * math.pi * 2
        self.lateral_offset = random.uniform(-5, 5)
        self.aggression = random.uniform(0.8, 1.2)

        self.hit_flash_timer = 0
        self.death_timer = 0
        self.last_pos = (x, y)

    def update(self, active_tower_objs):
        if not self.is_alive:
            if self.death_timer < 60:
                self.death_timer += 1
            return

        if self.cooldown > 0:
            self.cooldown -= 1

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        self.behave(active_tower_objs)
        self.bob_phase += 0.1

    def behave(self, active_tower_objs):
        targets = [t for t in active_tower_objs if t.health > 0]
        if not targets:
            self.z = 0
            return

        closest_tower = min(
            targets,
            key=lambda t: (self.x - t.x) ** 2 + (self.y - t.y) ** 2
        )

        row, col = self.id // 10, self.id % 10
        tx = closest_tower.x + (col - 5) * 28 + self.lateral_offset
        ty = closest_tower.y + (row - 2) * 28

        dx, dy = tx - self.x, ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 1.0:
            move_speed = self.speed * self.aggression
            self.x += (dx / dist) * move_speed
            self.y += (dy / dist) * move_speed
            self.angle = math.degrees(math.atan2(dx, dy))
            self.z = abs(2.0 * math.sin(self.bob_phase))
            self.gun_pitch = 0.0
        else:
            self.z = 0
            dx_t = closest_tower.x - self.x
            dy_t = closest_tower.y - self.y
            self.angle = math.degrees(math.atan2(dx_t, dy_t))

            if self.gun_pitch < 45:
                self.gun_pitch += 2.0

        self.last_pos = (self.x, self.y)

    def take_damage(self, dmg):
        if not self.is_alive:
            return
        self.health -= dmg
        self.hit_flash_timer = 5
        if self.health <= 0:
            self.is_alive = False
            self.death_timer = 0

    def draw_health_bar(self):
        if not self.is_alive:
            return

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z + 40)

        glColor3f(0.3, 0.3, 0.3)
        self.draw_line(-15, 15)

        hp_ratio = self.health / self.max_health
        hp = hp_ratio * 30

        if self.hit_flash_timer > 0:
            glColor3f(1.0, 1.0, 1.0)
        elif hp_ratio > 0.6:
            glColor3f(0.0, 1.0, 0.0)
        elif hp_ratio > 0.3:
            glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(1.0, 0.0, 0.0)

        self.draw_line(-15, -15 + hp)
        glPopMatrix()

    def draw_line(self, x1, x2):
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex3f(x1, 0, 0)
        glVertex3f(x2, 0, 0)
        glEnd()
        glLineWidth(1.0)



class EnemyKing(Enemy):
    def __init__(self, x, y, angle, id_val):
        super().__init__(x, y, angle, id_val)
        self.enemy_type = "king"
        self.speed = 5
        self.health = 500
        self.max_health = 500
        self.attack_range = 800
        self.fire_cooldown_max = 5
        self.fire_cooldown = 0
        self.damage = 80

        self.phase = 1
        self.enrage_threshold = 0.3
        self.is_enraged = False
        self.charge_timer = 0

    def get_target_pos(self):
        rad = math.radians(self.angle)
        tx = self.x - math.sin(rad) * self.attack_range
        ty = self.y + math.cos(rad) * self.attack_range
        return tx, ty

    def update(self, dt):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt
            if self.fire_cooldown < 0:
                self.fire_cooldown = 0
        else:
            self.fire_cooldown = 0

        health_ratio = self.health / self.max_health
        if health_ratio < self.enrage_threshold and not self.is_enraged:
            self.is_enraged = True
            self.speed *= 1.5
            self.fire_cooldown_max *= 0.6

        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

    def auto_move(self, dt):
        rad = math.radians(self.angle)
        speed_mult = 2.0 if self.is_enraged else 1.0
        self.x -= math.sin(rad) * self.speed * dt * 60 * speed_mult
        self.y += math.cos(rad) * self.speed * dt * 60 * speed_mult

    def fire_mortar(self, mortar_list, target_dist):
        if self.fire_cooldown > 0:
            return

        rad = math.radians(self.angle)
        target_x = self.x - math.sin(rad) * target_dist
        target_y = self.y + math.cos(rad) * target_dist

        mortar_list.append(
            MortarRocket(self.x, self.y, 50, target_x, target_y, self.damage)
        )

        if self.is_enraged:
            for offset_angle in (-15, 15):
                spread_rad = math.radians(self.angle + offset_angle)
                sx = self.x - math.sin(spread_rad) * target_dist
                sy = self.y + math.cos(spread_rad) * target_dist
                mortar_list.append(
                    MortarRocket(self.x, self.y, 50, sx, sy, self.damage // 2)
                )

        self.fire_cooldown = self.fire_cooldown_max

    def find_nearest_tower(self, towers):
        target = None
        min_dist = float('inf')
        for t in towers:
            if t.unlock == 1 and t.health > 0:
                d = math.hypot(t.x - self.x, t.y - self.y)
                priority = d * (t.health / t.max_health)
                if priority < min_dist:
                    min_dist = d
                    target = t
        return target, min_dist


def create_marching_group(LIMIT, gl):
    margin = 50
    cols = 5 + (gl // 2)
    rows = 5 + (gl // 3)

    spawn_options = [
        (-LIMIT + margin, LIMIT - margin, 135),
        (LIMIT - margin, LIMIT - margin, 225),
        (-LIMIT + margin, -LIMIT + margin, 45),
        (LIMIT - margin, -LIMIT + margin, 315)
    ]

    num_spawns = min(len(spawn_options), 1 + (gl // 5))
    chosen_points = random.sample(spawn_options, num_spawns)

    group = []
    boss = None

    for start_x, start_y, angle in chosen_points:
        spacing = 35
        for i in range((rows * cols) // num_spawns):
            row = i // cols
            col = i % cols

            ox = col * spacing - (row * 10)
            oy = row * spacing

            x_pos = max(-LIMIT + margin, min(LIMIT - margin, start_x + ox))
            y_pos = max(-LIMIT + margin, min(LIMIT - margin, start_y - oy))

            enemy = Enemy(x_pos, y_pos, angle, i)
            enemy.max_health += (gl * 20)
            enemy.health = enemy.max_health
            enemy.speed += (gl * 0.05)
            group.append(enemy)

    if gl >= 1:
        bx, by, ba = chosen_points[0]
        boss = EnemyKing(bx, by, ba, 999)
        boss.max_health += (gl * 100)
        boss.health = boss.max_health
        boss.damage += (gl * 5)
        group.append(boss)

    return group, boss



def draw_scene(enemies):
    for e in enemies:
        if not e.is_alive and e.death_timer > 30:
            continue

        glPushMatrix()

        if not e.is_alive:
            glColor3f(0.2, 0.2, 0.2)

        if e.enemy_type == "king":
            
            if e.is_enraged:
                glPushMatrix()
                glTranslatef(e.x, e.y, e.z)
                glColor3f(0.6, 0.0, 0.0)
                draw_sphere_manual(60, 12, 12)
                glPopMatrix()

            draw_enemy_king(e.x, e.y, e.z, e.angle, e.gun_pitch)
        else:
            draw_sticky_enemy(e.x, e.y, e.z, e.angle, e.is_alive, e.gun_pitch)

        glPopMatrix()
        e.draw_health_bar()


def draw_king_range(king, bmanual):
    if not king or king.health <= 0 or not bmanual:
        return

    tx, ty = king.get_target_pos()

    glPushMatrix()
    glTranslatef(tx, ty, 1)

    pulse = 0.5 + 0.3 * math.sin(time.time() * 5)

    # Outer danger zone
    glColor3f(0.4 * pulse, 0.0, 0.0)
    draw_circle_triangles(80, 32)

    # Reticle lines
    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for i in range(0, 360, 45):
        angle = math.radians(i)
        x1, y1 = math.cos(angle) * 50, math.sin(angle) * 50
        x2, y2 = math.cos(angle) * 80, math.sin(angle) * 80
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
    glEnd()

    # Center point
    glPointSize(8.0)
    glColor3f(1.0, 1.0, 0.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0, 0)
    glEnd()

    glPopMatrix()



#Graphics




btn_new_game = (400, 450, 600, 520)
btn_level    = (400, 350, 600, 420)
btn_exit     = (400, 250, 600, 320)


QUAD = gluNewQuadric()

def draw_circle(radius):
    glBegin(GL_TRIANGLES)
    for i in range(360):
        angle1 = math.radians(i)
        angle2 = math.radians(i + 1)
        x1 = radius * math.cos(angle1)
        y1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        y2 = radius * math.sin(angle2)
        glVertex3f(0, 0, 0)
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
    glEnd()

def drawlines(x0, y0, x1, y1, color=(1, 1, 1)):
    glColor3f(*color)
    glBegin(GL_LINES)
    glVertex2f(x0, y0)
    glVertex2f(x1, y1)
    glEnd()

def draw_button_border(x1, y1, x2, y2, color=(1, 1, 1)):
    drawlines(x1, y1, x2, y1, color)
    drawlines(x2, y1, x2, y2, color)
    drawlines(x2, y2, x1, y2, color)
    drawlines(x1, y2, x1, y1, color)

def draw_gem_icon(x, y):
    w, h = 20, 25
    c = (0.0, 1.0, 1.0)
    drawlines(x + w // 2, y,       x,         y - h // 2, c)
    drawlines(x,         y - h // 2, x + w // 2, y - h,     c)
    drawlines(x + w // 2, y - h,   x + w,     y - h // 2, c)
    drawlines(x + w,     y - h // 2, x + w // 2, y,       c)

def draw_heart(x, y, size=4, color=(1, 0, 0)):
    drawlines(x, y, x - size, y + size, color)
    drawlines(x - size, y + size, x - 2 * size, y, color)
    drawlines(x - 2 * size, y, x, y - 2 * size, color)
    drawlines(x, y - 2 * size, x + 2 * size, y, color)
    drawlines(x + 2 * size, y, x + size, y + size, color)
    drawlines(x + size, y + size, x, y, color)

#ENEMIES 

def draw_sticky_enemy(x, y, z, rotation, is_alive, gun_pitch):
    glPushMatrix()
    glTranslatef(x, y, z)

    
    if is_alive:
        glRotatef(rotation, 0, 0, 1)
    else:
        glRotatef(-90, 1, 0, 0)
        glTranslatef(0, 0, -5)

    #  LEGS 
    glColor3f(0.0, 0.0, 0.0)
    for offset in (-7, 7):
        glPushMatrix()
        glTranslatef(offset, 0, 0)
        gluCylinder(QUAD, 3, 3, 15, 10, 10)
        glPopMatrix()

    #  BODY 
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glutSolidCube(20)
    glPopMatrix()

    #  GUNS / ARMS 
    glColor3f(0.3, 0.3, 0.3)
    for side in (-12, 12):
        glPushMatrix()
        glTranslatef(side, 0, 25)
        glRotatef(-gun_pitch, 1, 0, 0)
        gluCylinder(QUAD, 3, 2, 25, 10, 10)
        glPopMatrix()

    #  HEAD / HELMET 
    glColor3f(0.0, 0.6, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 35)
    gluSphere(QUAD, 12, 16, 16)
    glPopMatrix()

    glPopMatrix()

def draw_enemy_king(x, y, z, angle, gun_pitch):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 0, 1)

    
    # BODY
    
    glColor3f(0.35, 0.0, 0.55)   
    glutSolidCube(40)

    
    # ARMOR RING
    
    glPushMatrix()
    glColor3f(0.6, 0.1, 0.8)
    glScalef(1.4, 1.4, 0.4)
    glutWireCube(40)
    glPopMatrix()

    
    # HEAD
    
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glColor3f(0.7, 0.2, 0.9)
    glutSolidSphere(14, 16, 16)
    glPopMatrix()

    
    # CROWN SPIKES
    
    glColor3f(1.0, 0.8, 0.2)
    for i in range(6):
        glPushMatrix()
        glRotatef(i * 60, 0, 0, 1)
        glTranslatef(0, 18, 45)
        glutSolidCone(4, 10, 8, 8)
        glPopMatrix()

   
    # GUN BARREL (rotates up/down)
    
    glPushMatrix()
    glTranslatef(0, 28, 10)
    glRotatef(-gun_pitch, 1, 0, 0)
    glColor3f(0.9, 0.1, 0.1)
    glScalef(1.5, 5.0, 1.0)
    glutSolidCube(6)
    glPopMatrix()

    glPopMatrix()




#player_KINGGGG





class PlayerKing:
    def __init__(self):
        self.x, self.y, self.z = 0, 70, 25
        self.angle = 0
        self.speed = 12
        self.is_attacking = False
        self.attack_timer = 0
        self.slash_anim = 0
        self.maxhealth = 500
        self.health = 500

    def draw_part(self, x, y, z, sx, sy, sz, color, shape="cube"):
        glPushMatrix()
        glColor3fv(color)
        glTranslatef(x, y, z)
        glScalef(sx, sy, sz)
        if shape == "cube":
            glutSolidCube(1)
        else:
            glutSolidSphere(1, 20, 20)
        glPopMatrix()

    def draw_solid_slash(self, cstate=0):
        if not self.is_attacking:
            return
        glPushMatrix()
        
        if cstate == 1:
            # Position slash effect relative to camera in FPS
            glTranslatef(0, 80, 0) 
        else:
            # Position slash relative to world hero
            glTranslatef(self.x, self.y + 60, self.z + 10)
            glRotatef(self.angle, 0, 0, 1)

        glRotatef(-self.slash_anim, 0, 0, 1)
        glColor3f(1.0, 0.9, 0.0)
        glLineWidth(8.0)
        glBegin(GL_LINES)
        for i in range(0, 180, 5):
            r1, r2 = math.radians(i), math.radians(i + 5)
            glVertex3f(250 * math.cos(r1), 250 * math.sin(r1), 0)
            glVertex3f(250 * math.cos(r2), 250 * math.sin(r2), 0)
        glEnd()
        glPopMatrix()

    def draw(self, cstate=0):
        # --- FIRST PERSON VIEW (cstate 1) ---
        if cstate == 1:
            # We skip drawing the body/head so the camera doesn't see inside them.
            # We only draw the arm and sword relative to the "Eyes" (0,0,0)
            glPushMatrix()
            # Push the sword to the bottom-right of the screen
            glTranslatef(25, 40, -25) 
            if self.is_attacking:
                # Vertical chop animation for FPS
                glRotatef(self.slash_anim - 60, 1, 0, 0) 
            
            # Draw just the sword and arm parts
            self.draw_part(0, 0, 0, 8, 8, 8, [1.0, 0.8, 0.6], "sphere")   # Hand
            self.draw_part(0, 15, 0, 4, 25, 4, [0.4, 0.2, 0.1], "cube")   # Handle
            self.draw_part(0, 50, 0, 8, 70, 3, [0.8, 0.8, 0.9], "cube")   # Blade
            glPopMatrix()
            
            # Draw the slash effect
            self.draw_solid_slash(cstate=1)

        # --- NORMAL VIEWS (State 0 and 2) ---
        else:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            glRotatef(self.angle, 0, 0, 1)

            # Body & Head
            self.draw_part(0, 0, 0, 40, 30, 50, [0.3, 0.0, 0.4], "sphere")
            self.draw_part(0, 0, 35, 20, 20, 20, [1.0, 0.8, 0.6], "sphere")

            # Crown
            self.draw_part(0, 0, 50, 22, 22, 10, [1.0, 0.8, 0.0], "cube")
            self.draw_part(0, 0, 58, 5, 5, 5, [1.0, 0.0, 0.0], "sphere")

            # Right Arm (Sword)
            glPushMatrix()
            glTranslatef(30, 10, 10)
            if self.is_attacking:
                glRotatef(self.slash_anim, 0, 0, 1)
            self.draw_part(0, 0, 0, 10, 10, 10, [1.0, 0.8, 0.6], "sphere")
            self.draw_part(0, 20, 0, 5, 30, 5, [0.4, 0.2, 0.1], "cube")
            self.draw_part(0, 60, 0, 10, 80, 4, [0.8, 0.8, 0.9], "cube")
            glPopMatrix()

            # Left Arm (Shield)
            glPushMatrix()
            glTranslatef(-30, 10, 10)
            self.draw_part(0, 0, 0, 10, 10, 10, [1.0, 0.8, 0.6], "sphere")
            self.draw_part(-5, 10, 0, 30, 5, 40, [0.0, 0.2, 0.5], "cube")
            self.draw_part(-6, 11, 0, 35, 2, 45, [1.0, 0.8, 0.0], "cube")
            glPopMatrix()

            glPopMatrix()
            # Draw the slash effect in world space
            self.draw_solid_slash(cstate=0)

    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = 15
            self.slash_anim = 120

    def update(self):
        if self.is_attacking:
            self.attack_timer -= 1
            self.slash_anim -= 8 # Slowed down slightly for smoother visual
            if self.attack_timer <= 0:
                self.is_attacking = False


#Tower ssss



class Tower:
    def __init__(self, index, x, y, z, box_cor):
        self.index = index
        self.x = x
        self.y = y
        self.z = z

        self.unlock = 0
        self.level = 1

        self.range = 300
        self.damage = 120
        self.fire_rate = 1.0

        self.max_health = 500
        self.health = 5000

        self.buttonbox = box_cor
        self.cooldown = 0

    #  BASIC FUNCTIONS 

    def upgrade(self):
        self.level += 1
        self.max_health += 50
        self.health = self.max_health

    def take_damage(self, dmg):
        if self.health <= 0:
            return
        self.health -= dmg
        if self.health < 0:
            self.health = 0

    # SHAPE DRAWING 

    def draw_circle(self, radius):
        
        glBegin(GL_TRIANGLES)
        for i in range(360):
            a1 = math.radians(i)
            a2 = math.radians(i + 1)

            glVertex3f(0, 0, 0)
            glVertex3f(radius * math.cos(a1), radius * math.sin(a1), 0)
            glVertex3f(radius * math.cos(a2), radius * math.sin(a2), 0)
        glEnd()

    def draw_sphere(self, radius, parts):
        
        glBegin(GL_QUADS)
        for i in range(parts):
            lat0 = math.pi * (-0.5 + float(i) / parts)
            lat1 = math.pi * (-0.5 + float(i + 1) / parts)

            z0 = radius * math.sin(lat0)
            z1 = radius * math.sin(lat1)
            zr0 = radius * math.cos(lat0)
            zr1 = radius * math.cos(lat1)

            for j in range(parts):
                lng0 = 2 * math.pi * float(j) / parts
                lng1 = 2 * math.pi * float(j + 1) / parts

                x0, y0 = math.cos(lng0), math.sin(lng0)
                x1, y1 = math.cos(lng1), math.sin(lng1)

                glVertex3f(x0 * zr0, y0 * zr0, z0)
                glVertex3f(x1 * zr0, y1 * zr0, z0)
                glVertex3f(x1 * zr1, y1 * zr1, z1)
                glVertex3f(x0 * zr1, y0 * zr1, z1)
        glEnd()

    def draw_cube(self, size):
        
        s = size / 2.0
        glBegin(GL_QUADS)

        # Front
        glVertex3f(-s, -s,  s)
        glVertex3f( s, -s,  s)
        glVertex3f( s,  s,  s)
        glVertex3f(-s,  s,  s)

        # Back
        glVertex3f(-s, -s, -s)
        glVertex3f(-s,  s, -s)
        glVertex3f( s,  s, -s)
        glVertex3f( s, -s, -s)

        # Top
        glVertex3f(-s,  s, -s)
        glVertex3f(-s,  s,  s)
        glVertex3f( s,  s,  s)
        glVertex3f( s,  s, -s)

        # Bottom
        glVertex3f(-s, -s, -s)
        glVertex3f( s, -s, -s)
        glVertex3f( s, -s,  s)
        glVertex3f(-s, -s,  s)

        # Right
        glVertex3f( s, -s, -s)
        glVertex3f( s,  s, -s)
        glVertex3f( s,  s,  s)
        glVertex3f( s, -s,  s)

        # Left
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s,  s)
        glVertex3f(-s,  s,  s)
        glVertex3f(-s,  s, -s)

        glEnd()

    #GUN 

    def draw_gun(self, unlocked, alive, bullet_dist):
        glPushMatrix()

        # Gun color 
        if not alive:
            glColor3f(0.07, 0.07, 0.07)   # dead
        elif unlocked:
            glColor3f(0.18, 0.18, 0.20)   # steel
        else:
            glColor3f(0.12, 0.12, 0.12)   # locked

        quad = gluNewQuadric()

        glRotatef(-90, 0, 1, 0)
        gluCylinder(quad, 8, 5, 60, 20, 20)

        # Bullet 
        if unlocked and alive:
            glPushMatrix()
            glColor3f(1.0, 0.2, 0.1)
            glTranslatef(0, 0, 60 + bullet_dist)
            self.draw_sphere(4, 8)
            glPopMatrix()

        # Gun base ball 
        glPushMatrix()
        glTranslatef(0, 0, -5)
        self.draw_sphere(10, 12)
        glPopMatrix()

        glPopMatrix()

    # MAIN RENDER 

    def render(self, rotation, bullet_dist):
        alive = self.health > 0
        unlocked = self.unlock

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)

        # If dead
        if not alive:
            glRotatef(15, 1, 0, 0)
            glTranslatef(0, -20, 0)

        quad = gluNewQuadric()

        #  Tower body 
        if not alive:
            glColor3f(0.12, 0.12, 0.12)   # burnt ash
        elif unlocked:
            glColor3f(0.55, 0.52, 0.48)   # stone
        else:
            glColor3f(0.20, 0.20, 0.20)   # locked dark

        gluCylinder(quad, 40, 40, 180, 32, 32)

        #  Windows 
        if unlocked and alive:
            glColor3f(1.0, 0.85, 0.3)     # warm yellow
        else:
            glColor3f(0.0, 0.0, 0.0)

        for h in [60, 110]:
            for a in [0, 90, 180, 270]:
                glPushMatrix()
                glRotatef(a, 0, 0, 1)
                glTranslatef(39, 0, h)
                glScalef(0.3, 0.8, 1.8)
                self.draw_cube(10)
                glPopMatrix()

        #  Rotating top
        glPushMatrix()
        glTranslatef(0, 0, 180)

        if unlocked and alive:
            glRotatef(rotation, 0, 0, 1)
            glColor3f(0.75, 0.60, 0.35)  # bronze
        else:
            glColor3f(0.15, 0.15, 0.15)

        if not alive:
            glRotatef(10, 0, 1, 0)

        gluCylinder(quad, 50, 50, 30, 32, 32)
        self.draw_circle(50)

        # 4) Gun
        glPushMatrix()
        glTranslatef(0, 0, 30)
        glRotatef(-90, 0, 0, 1)
        self.draw_gun(unlocked, alive, bullet_dist)
        glPopMatrix()

        glPopMatrix()  
        glPopMatrix()  



#utils 

from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18



# BUTTON DEFINITIONS

btn_new_game = (400, 450, 600, 520)
btn_level    = (400, 350, 600, 420)
btn_exit     = (400, 250, 600, 320)

def draw_text(x, y, text, color=(1, 1, 1), font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))


def draw_rect(x1, y1, x2, y2, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()


def draw_border(x1, y1, x2, y2, color, thickness=2.0):
    glColor3f(*color)
    glLineWidth(thickness)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()
    glLineWidth(1.0)


def clamp01(v):
    return max(0.0, min(1.0, v))


def draw_progress_bar(x1, y1, x2, y2, value01, back_color, fill_color):
    
    draw_rect(x1, y1, x2, y2, back_color)
    v = clamp01(value01)
    draw_rect(x1, y1, x1 + (x2 - x1) * v, y2, fill_color)


def draw_panel_with_border(x1, y1, x2, y2, fill_color, border_color, border_thickness=3.0):
    draw_rect(x1, y1, x2, y2, fill_color)
    draw_border(x1, y1, x2, y2, border_color, border_thickness)



# UI BEGIN / END

def begin_ui():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


def end_ui():
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



# MAIN UI

def draw_ui(towers, gems, gameon, level, state, enemyking, hero):
    begin_ui()

    # GAME OVER 
    if state == "game_over":
        draw_rect(0, 0, 1000, 800, (0.1, 0, 0))
        draw_text(420, 500, "GAME OVER", (1, 0, 0))
        draw_text(360, 420, "THE HERO HAS FALLEN")
        draw_text(380, 340, "PRESS R TO RESTART", (1, 1, 0))
        end_ui()
        return

    #  START MENU 
    if state == "start":
        draw_rect(0, 0, 1000, 800, (0, 0, 0))
        draw_text(420, 650, "KING'S GUARD", (1, 1, 0))

        draw_rect(*btn_new_game, (0.1, 0.3, 0.1))
        draw_text(470, 480, "START")

        draw_rect(*btn_level, (0.1, 0.2, 0.3))
        draw_text(450, 380, f"WAVE: {level}")

        draw_rect(*btn_exit, (0.3, 0.1, 0.1))
        draw_text(485, 280, "EXIT")

        end_ui()
        return

    # TOP BAR 
    draw_rect(0, 750, 1000, 800, (0.02, 0.02, 0.05))
    draw_text(30, 770, f"GEMS: {int(gems)}", (0, 1, 1))
    draw_text(200, 770, f"WAVE: {level}")
    draw_text(400, 770, "WASD MOVE | SPACE ATTACK", (0.7, 0.7, 0.7))

    #  ENEMY KING HP 
    if enemyking and enemyking.is_alive:
        bar_x1, bar_y1, bar_x2, bar_y2 = 310, 710, 690, 730
        hp01 = enemyking.health / enemyking.max_health if enemyking.max_health else 0
        draw_progress_bar(bar_x1, bar_y1, bar_x2, bar_y2, hp01, (0.2, 0, 0), (1, 0, 0))
        draw_text(440, 735, "ENEMY KING", (1, 0, 0))

    #  HERO HP 
    if hero:
        bar_x1, bar_y1, bar_x2, bar_y2 = 20, 20, 220, 45
        hp01 = hero.health / hero.maxhealth if hero.maxhealth else 0
        draw_progress_bar(bar_x1, bar_y1, bar_x2, bar_y2, hp01, (0.05, 0.1, 0.2), (0, 0.8, 1))
        draw_text(20, 55, f"HERO HP: {int(hero.health)}/{int(hero.maxhealth)}", (0, 1, 1))

    # TOWERS 
    for t in towers:
        x1, y1, x2, y2 = t.buttonbox

        if t.unlock == 0:
            draw_border(x1, y1, x2, y2, (0, 1, 0))
            draw_text(x1 + 5, y2 - 20, "LOCKED")
            draw_text(x1 + 5, y1 + 5, "COST: 50", (1, 1, 0))
            continue

        # unlocked tower
        draw_border(x1, y1, x2, y2, (0, 0.8, 1))
        draw_text(x1 + 5, y2 - 20, f"LVL {t.level}")

        # tower hp bar
        hpbar_x1, hpbar_y1 = x1 + 5, y2 - 40
        hpbar_x2, hpbar_y2 = x2 - 5, y2 - 35
        hp01 = t.health / t.max_health if t.max_health else 0
        draw_progress_bar(hpbar_x1, hpbar_y1, hpbar_x2, hpbar_y2, hp01, (0.3, 0, 0), (0, 1, 0))

        # upgrade text
        if t.health > 0:
            draw_text(x1 + 5, y1 + 5, f"UP: {25 * t.level}", (1, 1, 0))
        else:
            draw_text(x1 + 5, y1 + 5, "FIX: 150", (1, 0, 0))

    end_ui()



# WAVE INCOMING

def draw_wave_incoming_message(level, king, enemies):
    begin_ui()

    flash = abs(math.sin(time.time() * 8))
    draw_panel_with_border(
        200, 350, 800, 500,
        (0.3 * flash, 0, 0),
        (1, 0, 0),
        border_thickness=4
    )

    draw_text(300, 460, f"WAVE {level} INCOMING!", (1, 0, 0))
    draw_text(350, 420, f"ENEMY COUNT: {len(enemies)}", (1, 1, 0))

    if king and king.is_alive:
        draw_text(360, 380, "BOSS DETECTED", (1, 0.5, 0))

    end_ui()



# WAVE CLEARED
def draw_wave_clear_message(level):
    begin_ui()

    draw_panel_with_border(
        250, 300, 750, 450,
        (0, 0.2, 0),
        (0, 1, 0),
        border_thickness=3
    )

    bounce = 10 * abs(math.sin(time.time() * 3))
    draw_text(350, 400 + bounce, f"WAVE {level} CLEARED!", (1, 1, 0))
    draw_text(330, 350, "NEXT WAVE IN 3 SECONDS...", (0.8, 0.8, 0.8))
    draw_text(360, 320, f"GEM BONUS: +{150 * level}", (0, 1, 1))

    end_ui()



# CHEAT INDICATOR

def draw_cheat_indicators(CHEAT_MODE):
    active = [k for k, v in CHEAT_MODE.items() if v]
    if not active:
        return

    begin_ui()
    draw_rect(700, 720, 990, 745, (0.1, 0.1, 0.2))
    draw_text(710, 728, "CHEATS: " + ", ".join(active[:3]), (1, 0, 1))
    end_ui()


#cameraaaa

fovY = 140
camera_shake = {'x': 0, 'y': 0, 'z': 0, 'intensity': 0}


def setupCamera(camera_pos, hero_obj=None, cstate=0):
    # Projection 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    fov = 95 if cstate == 0 else 60  
    gluPerspective(fov, 1.25, 0.1, 1500)

    # ModelView 
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #  State 0 
    if cstate == 0:
        x, y, z, t = camera_pos
        gluLookAt(x, y, z,
                  0, 0, 0,
                  0, 0, 1)
        return

    # Hero data (State 1 & 2 uses hero)
    px, py = hero_obj.x, hero_obj.y
    hero_angle = hero_obj.angle
    ang = math.radians(hero_angle + 90)

    dx = math.cos(ang)
    dy = math.sin(ang)

    #  State 1 
    if cstate == 1:
        pz = hero_obj.z

        eye_x = px + dx * 45
        eye_y = py + dy * 45
        eye_z = pz + 45

        lx = px + dx * 150
        ly = py + dy * 150
        lz = eye_z -5

        gluLookAt(eye_x, eye_y, eye_z,
                  lx, ly, lz,
                  0, 0, 1)
        return

    #  State 2 
    cam_dist = 350
    cx = px - dx * cam_dist
    cy = py - dy * cam_dist

    lx = px + dx * 100
    ly = py + dy * 100

    gluLookAt(cx, cy, 220,
              lx, ly, 70,
              0, 0, 1)


def camera_shake_effect(intensity):
    global camera_shake
    camera_shake['intensity'] = max(camera_shake['intensity'], intensity)


def update_camera_shake():
    global camera_shake

    s = camera_shake['intensity']
    if s > 0:
        camera_shake['x'] = random.uniform(-1, 1) * s
        camera_shake['y'] = random.uniform(-1, 1) * s
        camera_shake['z'] = random.uniform(-1, 1) * s
        camera_shake['intensity'] *= 0.85
    else:
        camera_shake['x'] = 0
        camera_shake['y'] = 0
        camera_shake['z'] = 0


####mappp
from OpenGL.GL import *

class Map:
    GRID_LENGTH = 800

    def draw(self):
        L = self.GRID_LENGTH

        #  GRASS  (bright green )
        glBegin(GL_QUADS)
        glColor3f(0.10, 0.60, 0.22)
        glVertex3f(-L, -L, -2)
        glVertex3f( L, -L, -2)
        glVertex3f( L,  L, -2)
        glVertex3f(-L,  L, -2)
        glEnd()

        # grass tone variation
        glBegin(GL_QUADS)
        glColor3f(0.12, 0.66, 0.25)
        glVertex3f(-700, -500, -1.95)
        glVertex3f(-520, -500, -1.95)
        glVertex3f(-520, -320, -1.95)
        glVertex3f(-700, -320, -1.95)

        glColor3f(0.08, 0.55, 0.20)
        glVertex3f(520, 320, -1.95)
        glVertex3f(700, 320, -1.95)
        glVertex3f(700, 500, -1.95)
        glVertex3f(520, 500, -1.95)
        glEnd()

        # COURTYARD (light grey )
        glBegin(GL_QUADS)
        glColor3f(0.78, 0.78, 0.80)
        glVertex3f(-400, -600, -1.5)
        glVertex3f( 400, -600, -1.5)
        glVertex3f( 400,  600, -1.5)
        glVertex3f(-400,  600, -1.5)
        glEnd()

        # courtyard border
        glBegin(GL_QUADS)
        glColor3f(0.66, 0.66, 0.66)
        glVertex3f(-420, -620, -1.45)
        glVertex3f( 420, -620, -1.45)
        glVertex3f( 420, -600, -1.45)
        glVertex3f(-420, -600, -1.45)

        glVertex3f(-420, 600, -1.45)
        glVertex3f( 420, 600, -1.45)
        glVertex3f( 420, 620, -1.45)
        glVertex3f(-420, 620, -1.45)
        glEnd()

        #  PATH (brown )
        glBegin(GL_QUADS)
        glColor3f(0.52, 0.33, 0.16)
        glVertex3f(-100, -L, -1)
        glVertex3f( 100, -L, -1)
        glVertex3f( 100,  L, -1)
        glVertex3f(-100,  L, -1)
        glEnd()

        # path center
        glBegin(GL_QUADS)
        glColor3f(0.60, 0.40, 0.20)
        glVertex3f(-35, -L, -0.98)
        glVertex3f( 35, -L, -0.98)
        glVertex3f( 35,  L, -0.98)
        glVertex3f(-35,  L, -0.98)
        glEnd()

        #  TOWERS & WALLS
        self.draw_pedestal(0, 0)
        self.draw_pedestal(-250, 0)
        self.draw_pedestal(250, 0)
        self.draw_castle_walls()

    def draw_pedestal(self, x, y):
        glColor3f(0.35, 0.35, 0.36)
        self.draw_block(x, y, 65, 0.2)

        glColor3f(0.55, 0.55, 0.56)
        self.draw_block(x, y, 50, 0.5)

        glColor3f(0.62, 0.62, 0.63)
        self.draw_block(x, y, 52, 0.55)

    def draw_block(self, x, y, size, z):
        glBegin(GL_QUADS)
        glVertex3f(x-size, y-size, z)
        glVertex3f(x+size, y-size, z)
        glVertex3f(x+size, y+size, z)
        glVertex3f(x-size, y+size, z)
        glEnd()

    def draw_castle_walls(self):
        glColor3f(0.80, 0.76, 0.68)  # beige walls
        L = self.GRID_LENGTH
        W = 20
        H = 100

        self.draw_3d_box(-L, -L, -L + W, L, H)
        self.draw_3d_box(L - W, -L, L, L, H)
        self.draw_3d_box(-L, -L, L, -L + W, H)
        self.draw_3d_box(-L, L - W, L, L, H)

    def draw_3d_box(self, x1, y1, x2, y2, height):
        glBegin(GL_QUADS)

        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y1, 0)
        glVertex3f(x2, y1, height)
        glVertex3f(x1, y1, height)

        glVertex3f(x1, y2, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(x2, y2, height)
        glVertex3f(x1, y2, height)

        glVertex3f(x1, y1, 0)
        glVertex3f(x1, y2, 0)
        glVertex3f(x1, y2, height)
        glVertex3f(x1, y1, height)

        glVertex3f(x2, y1, 0)
        glVertex3f(x2, y2, 0)
        glVertex3f(x2, y2, height)
        glVertex3f(x2, y1, height)

        glColor3f(0.86, 0.83, 0.76)
        glVertex3f(x1, y1, height)
        glVertex3f(x2, y1, height)
        glVertex3f(x2, y2, height)
        glVertex3f(x1, y2, height)

        glEnd()


def draw_boundary_walls():
    LIMIT = 750
    Z = 2

    glLineWidth(3.0)
    glColor3f(1.0, 0.0, 0.0)  # pure red 

    glBegin(GL_LINE_LOOP)
    glVertex3f(-LIMIT, -LIMIT, Z)
    glVertex3f( LIMIT, -LIMIT, Z)
    glVertex3f( LIMIT,  LIMIT, Z)
    glVertex3f(-LIMIT,  LIMIT, Z)
    glEnd()

    glPointSize(8.0)
    glBegin(GL_POINTS)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-LIMIT, -LIMIT, Z)
    glVertex3f( LIMIT, -LIMIT, Z)
    glVertex3f( LIMIT,  LIMIT, Z)
    glVertex3f(-LIMIT,  LIMIT, Z)
    glEnd()

    glLineWidth(1.0)



#main.pyyyyy


from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random
from collections import deque


#  GAME STATE 
GRID_LENGTH = 800
gameon = False
gamestate = "start"
Game_level = 1  
gems = 150 
cstate=0
prev_time = time.time()
camera_pos = (0, 580, 500, 0)
boss_manual_mode = False

# CHEAT MODE 
CHEAT_MODE = {
    'god_mode': False,   
    'infinite_gems': False,   
    'one_shot_kill': False,    
    'tower_invincible': False,  
    'slow_motion': False,     
    'fast_reload': False,       
    'show_info': False         
}

#  WORLD OBJECTS
game_map = Map()
all_enemies, king = create_marching_group(GRID_LENGTH, Game_level)
hero = PlayerKing() 
bullets = deque()
mortar = deque()
explosions = []

# TOWERS 
towers = [
    Tower(0, 0, 0, 0, (820, 600, 980, 670)),
    Tower(1, -200, 0, 0, (820, 510, 980, 580)),
    Tower(2, 200, 0, 0, (820, 420, 980, 490))
]
# Start with first tower unlocked and stronger
towers[0].unlock = 1
towers[0].health = 1000
towers[0].max_health = 1000
towers[0].damage = 150
active_towers = [towers[0]]
tower_rotations = [0.0, 0.0, 0.0]

#  DIFFICULTY BALANCING 
BALANCE_CONFIG = {
    'hero_start_health': 800,     
    'tower_start_health': 1000,     
    'enemy_spawn_delay': 2.0,   
    'boss_damage_multiplier': 0.7, 
    'tower_fire_rate': 1.5,       
    'gem_drop_rate': 2.0          
}

waves_completed_in_level=0

def reset_game(full_restart=True):
    global all_enemies, king, bullets, mortar, towers, active_towers, explosions
    global gems, gameon, Game_level, gamestate, hero,waves_completed_in_level
    
    bullets.clear()
    mortar.clear()
    explosions.clear()
    
    if full_restart:
        Game_level = 1 
        gamestate = "start"
        gameon = False
        waves_completed_in_level = 0
        gems = 150  
        
        all_enemies, king = create_marching_group(GRID_LENGTH, Game_level)
        hero = PlayerKing()
        hero.maxhealth = BALANCE_CONFIG['hero_start_health']
        hero.health = hero.maxhealth
        
        towers = [
            Tower(0, 0, 0, 0, (820, 600, 980, 670)),
            Tower(1, -200, 0, 0, (820, 510, 980, 580)),
            Tower(2, 200, 0, 0, (820, 420, 980, 490))
        ]
        towers[0].unlock = 1
        towers[0].health = BALANCE_CONFIG['tower_start_health']
        towers[0].max_health = BALANCE_CONFIG['tower_start_health']
        towers[0].damage = 150
        active_towers = [towers[0]]
        
        glutPostRedisplay()
    else:
        waves_completed_in_level += 1
        if waves_completed_in_level>=3:
            level_up()
        else:
            
            all_enemies, king = create_marching_group(GRID_LENGTH, Game_level)
def level_up():
    global Game_level, gems, all_enemies, king, active_towers, bullets, mortar, hero, explosions,waves_completed_in_level
    
    Game_level += 1
    waves_completed_in_level=0
    hero.maxhealth += Game_level * 50
    hero.health = hero.maxhealth
    
    level_clear_bonus = 150 * Game_level
    gems += level_clear_bonus

    bullets.clear()
    mortar.clear()
    explosions.clear()
    
    all_enemies, king = create_marching_group(GRID_LENGTH, Game_level)
    
    for t in active_towers:
        t.health = min(t.max_health, t.health + 200)
    
    camera_shake_effect(15)
    
    level_up.wave_incoming_time = time.time()
    
    print("=" * 50)
    print(f" WAVE {Game_level} INCOMING! ")
    print(f" Gem Bonus: +{level_clear_bonus}")
    print(f"  Hero HP Restored!")
    print(f"  Enemies: {len(all_enemies)} units")
    if king:
        print(f" BOSS: Enemy King (HP: {king.health})")
    print("=" * 50)

def convert_coordinate(x, y):
    return x, 800 - y



#  RENDER 

def showScreen():
    global gameon, gamestate, king, hero, game_map, explosions, camera_pos, cstate
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if gameon:
        glDepthFunc(GL_LESS) 
        
        shake_cam = (
            camera_pos[0] + camera_shake['x'],
            camera_pos[1] + camera_shake['y'],
            camera_pos[2] + camera_shake['z'],
            camera_pos[3]
        )
        
        setupCamera(shake_cam, hero, cstate)
        
        game_map.draw()
        draw_boundary_walls()
        
        for exp in explosions: exp.draw()
        draw_scene(all_enemies)
        if hero: hero.draw(cstate)
        draw_bullets(bullets)
        draw_mortar_rockets(mortar)
        
        for tower in towers:
            tower.render(tower_rotations[tower.index], 0)
        glDepthFunc(GL_ALWAYS) 
        
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, 1000, 0, 800, -1, 1) 
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        alive_count = len([e for e in all_enemies if e.is_alive])
        if king and king.is_alive: alive_count += 1
        draw_ui.enemy_count = alive_count
      
        draw_ui(towers, gems, gameon, Game_level, gamestate, king, hero)

        if any(CHEAT_MODE.values()):
            draw_cheat_indicators(CHEAT_MODE)
        
        if hasattr(idle, 'wave_clear_time') and idle.wave_clear_time:
            draw_wave_clear_message(Game_level)
            
        if hasattr(level_up, 'wave_incoming_time'):
            elapsed = time.time() - level_up.wave_incoming_time
            if elapsed < 3:
                draw_wave_incoming_message(Game_level, king, all_enemies)

        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glDepthFunc(GL_LESS) 
            
    else:
        
        glDepthFunc(GL_ALWAYS) 
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, 1000, 0, 800, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        draw_ui(towers, gems, gameon, Game_level, gamestate, king, hero)
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glDepthFunc(GL_LESS) 
    
    glutSwapBuffers()


def handle_king_manual_control(key):
    global king, mortar
    if not (boss_manual_mode and king and king.health > 0):
        return

    step = king.speed
    rtd_speed = 5
    KING_LIMIT = 750
    rad_k = math.radians(king.angle % 360)
    
    # Calculate directional vectors
    dx = -step * math.sin(rad_k) 
    dy = step * math.cos(rad_k)
    
    next_kx, next_ky = king.x, king.y

    if key == b'i':
        next_kx += dx
        next_ky += dy
    elif key == b'k':
        next_kx -= dx
        next_ky -= dy
    elif key == b'j':    
        king.angle += rtd_speed
    elif key == b'l':   
        king.angle -= rtd_speed
    elif key == b'o':
        king.fire_mortar(mortar, king.attack_range)
        camera_shake_effect(8)
    
    king.x = max(-KING_LIMIT, min(KING_LIMIT, next_kx))
    king.y = max(-KING_LIMIT, min(KING_LIMIT, next_ky))


def keyboardListener(key, x, y):
    global hero, camera_pos, mortar, boss_manual_mode, gems
    global king, GRID_LENGTH, gamestate, gameon, CHEAT_MODE

    #  SYSTEM KEYS 
    if key == b'r' and gamestate == 'game_over': 
        reset_game(True)
        gamestate = 'start'
        glutPostRedisplay()
        return

    if key == b'm':
        boss_manual_mode = not boss_manual_mode
        print(f"Boss Control: {'MANUAL' if boss_manual_mode else 'AUTO'}")

    #  CHEAT CODES
    if key == b'c': CHEAT_MODE['god_mode'] = not CHEAT_MODE['god_mode']
    if key == b'v': 
        CHEAT_MODE['infinite_gems'] = not CHEAT_MODE['infinite_gems']
        if CHEAT_MODE['infinite_gems']: gems = 99999
    if key == b'b': CHEAT_MODE['one_shot_kill'] = not CHEAT_MODE['one_shot_kill']
    if key == b'n': CHEAT_MODE['tower_invincible'] = not CHEAT_MODE['tower_invincible']
    if key == b'x': CHEAT_MODE['slow_motion'] = not CHEAT_MODE['slow_motion']
    if key == b'z': CHEAT_MODE['fast_reload'] = not CHEAT_MODE['fast_reload']
    if key == b'g': gems += 500
    if key == b'h':
        if hero: hero.health = hero.maxhealth
        for t in active_towers: t.health = t.max_health
    if key == b'k':
        for e in all_enemies: e.is_alive = False
        if king: king.is_alive = False

    if not gameon or not hero:
        return

    # Hero movement logic 
    step, rtd_speed = hero.speed, 7
    rad = math.radians(hero.angle + 90)
    next_x, next_y = hero.x, hero.y

    if key == b'w':
        next_x += math.cos(rad) * step
        next_y += math.sin(rad) * step
    elif key == b's':
        next_x -= math.cos(rad) * step
        next_y -= math.sin(rad) * step
    elif key == b'a':
        hero.angle += rtd_speed
    elif key == b'd':
        hero.angle -= rtd_speed
    elif key == b' ':
        hero.attack()
        camera_shake_effect(5)
    
    #  Hero Position
    HERO_LIMIT = 750
    hero.x = max(-HERO_LIMIT, min(HERO_LIMIT, next_x))
    hero.y = max(-HERO_LIMIT, min(HERO_LIMIT, next_y))

    # King/Boss Manual Controls
    handle_king_manual_control(key)

    # Camera Zoom Controls
    cam_list = list(camera_pos)
    if key == b'+': cam_list[2] -= 20
    elif key == b'-': cam_list[2] += 20
    camera_pos = tuple(cam_list)
    
    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global camera_pos, DEFAULT_CAM
    x0, y0, z, t = camera_pos

    if key == GLUT_KEY_UP:
        z -= 20
    elif key == GLUT_KEY_DOWN:
        z += 20
    elif key == GLUT_KEY_LEFT:
        t -= 5
    elif key == GLUT_KEY_RIGHT:
        t += 5
    
    dist_horizontal = 600 
    new_x = dist_horizontal * math.sin(math.radians(t))
    new_y = dist_horizontal * math.cos(math.radians(t))
    
    camera_pos = (new_x, new_y, z, t)
    glutPostRedisplay()

def idle():
    global prev_time, all_enemies, hero, gems, explosions, king, gameon, wave_timer
    
    now = time.time()
    dt = now - prev_time
    prev_time = now

    if dt > 0.1: dt = 0.1
    
    if not gameon:
        return

    if CHEAT_MODE.get('slow_motion', False):
        dt *= 0.3

    update_camera_shake()
    if CHEAT_MODE.get('infinite_gems', False):
        gems = 9999
        
    if hero:
        hero.update()
        if CHEAT_MODE.get('god_mode', False):
            hero.health = hero.maxhealth
        
        # Hero Attack 
        if hero.is_attacking and 5 < hero.attack_timer < 14:
            damage = 99999 if CHEAT_MODE.get('one_shot_kill', False) else 50
            for e in all_enemies:
                if e.is_alive and math.hypot(hero.x - e.x, hero.y - e.y) < 220:
                    e.take_damage(damage)
                    camera_shake_effect(3)
                    if not e.is_alive:
                        gems += int(2 * BALANCE_CONFIG.get('gem_drop_rate', 1))

    # ENEMIES & BOSS 
    alive_enemies = [e for e in all_enemies if e.is_alive or e.death_timer < 60]
    for e in alive_enemies:
        if e.enemy_type == "grunt":
            e.update(active_towers)
    
    all_enemies = [e for e in alive_enemies if e.is_alive]

    if king and king.is_alive:
        enemy_king_logic(dt)

    # WAVE COMPLETION 
    alive_count = len([e for e in all_enemies if e.is_alive])
    boss_alive = king and king.is_alive
    
    if alive_count == 0 and not boss_alive:
        
        if wave_timer == 0:
            wave_timer = 3.0
            print(f" WAVE {Game_level} CLEARED! ")
        
        
        if wave_timer > 0:
            wave_timer -= dt
            
            if wave_timer <= 0:
                wave_timer = 0
                reset_game(False)
    else:
        
        wave_timer = 0
    
    # UPDATES 
    check_game_over()
    update_bullets(dt * 30)
    handle_tower_targeting(dt * 60)
    enemy_shooting(dt * 4)  
    update_mortar(dt * 0.01)
    
    for exp in explosions:
        exp.update()
    explosions = [e for e in explosions if e.life > 0]
    
    glutPostRedisplay()


def update_bullets(dt):
    global gems, bullets, towers, hero, GRID_LENGTH

    for i in range(len(bullets)):
        b = bullets.popleft()
        b.move(dt)

        hit = False
        
        if b.from_enemy:
            # Check hero collision
            if hero and hero.health > 0:
                dkx, dky, dkz = b.x - hero.x, b.y - hero.y, b.z - hero.z
                if dkx*dkx + dky*dky + dkz*dkz < (25 * 25):
                    if not CHEAT_MODE['god_mode']:
                        hero.health -= b.damage
                        camera_shake_effect(4)
                        if hero.health < 0:
                            hero.health = 0
                    hit = True
            
            # Check tower collision
            if not hit:
                for t in towers:
                    if t.health <= 0 or t.unlock == 0:
                        continue
                    dx, dy, dz = b.x - t.x, b.y - t.y, b.z - t.z
                    if dx*dx + dy*dy + dz*dz < (45 * 45):
                        if not CHEAT_MODE['tower_invincible']:
                            t.take_damage(b.damage)
                            camera_shake_effect(3)
                        hit = True
                        break
        else:
            # Tower bullets hit enemies
            damage = 99999 if CHEAT_MODE['one_shot_kill'] else b.damage
            for e in all_enemies:
                if not e.is_alive:
                    continue
                dx, dy, dz = b.x - e.x, b.y - e.y, b.z - e.z
                if dx*dx + dy*dy + dz*dz < (17 * 17):
                    e.take_damage(damage)
                    hit = True
                    if not e.is_alive:
                        gem_reward = int(10 * BALANCE_CONFIG['gem_drop_rate'])
                        gems += gem_reward
                    break

        if not hit and b.z > -10 and abs(b.x) < GRID_LENGTH and abs(b.y) < GRID_LENGTH:
            bullets.append(b)

def enemy_shooting(dt):
    global all_enemies, bullets, hero, active_towers
    
    for e in all_enemies:
        if not e.is_alive or e.cooldown > 0:
            if e.cooldown > 0:
                e.cooldown -= dt
            continue

        target_x, target_y = None, None
        min_d = 500  

        if hero and hero.health > 0:
            dx, dy = hero.x - e.x, hero.y - e.y
            dist_to_hero = math.hypot(dx, dy)
            if dist_to_hero < min_d:
                min_d = dist_to_hero
                target_x, target_y = hero.x, hero.y

        # Check towers
        for t in active_towers:
            if t.health > 0:
                dx, dy = t.x - e.x, t.y - e.y
                d = math.hypot(dx, dy)
                if d < min_d:
                    min_d = d
                    target_x, target_y = t.x, t.y

        # Fire at target
        if target_x is not None and e.enemy_type != "king":
            bullets.append(
                Bullet(e.x, e.y, 40, target_x, target_y, damage=3, from_enemy=True) 
            )
            e.cooldown = random.randint(120, 200)  

def update_mortar(dt):
    global mortar, towers, hero, GRID_LENGTH, explosions
    dt_scaled = dt * 60

    for i in range(len(mortar)):
        m = mortar.popleft()
        m.move(dt_scaled)
        
        if m.z <= 0:
            EXPLOSION_RADIUS = 80
            explosions.append(Explosion(m.x, m.y, 5))
            camera_shake_effect(12)
            
            damage = int(m.damage * BALANCE_CONFIG['boss_damage_multiplier'])
            
            # Damage towers
            for t in towers:
                if t.health <= 0 or t.unlock == 0:
                    continue
                dx, dy = m.x - t.x, m.y - t.y
                if dx*dx + dy*dy <= EXPLOSION_RADIUS**2:
                    if not CHEAT_MODE['tower_invincible']:
                        t.take_damage(damage)
            
            # Damage hero
            if hero and not CHEAT_MODE['god_mode']:
                dkx, dky = m.x - hero.x, m.y - hero.y
                if dkx*dkx + dky*dky <= EXPLOSION_RADIUS**2:
                    hero.health -= damage
                    if hero.health <= 0:
                        hero.health = 0
            continue

        if abs(m.x) > GRID_LENGTH * 1.5 or abs(m.y) > GRID_LENGTH * 1.5:
            continue

        mortar.append(m)

def check_game_over():
    global gamestate, gameon, active_towers, hero
    
    # Don't end game if invincibility cheats are on
    if CHEAT_MODE['tower_invincible'] or CHEAT_MODE['god_mode']:
        return
    
    if len(active_towers) > 0:
        all_destroyed = all(t.health <= 0 for t in active_towers)
        if all_destroyed:
            gamestate = "game_over"
            gameon = False
            print(" ALL TOWERS DESTROYED!")
    
    if hero and hero.health <= 0:
        gamestate = "game_over"
        gameon = False
        print(" THE HERO HAS FALLEN!")

def handle_tower_targeting(dt):
    for t in towers:
        if t.unlock == 0 or t.health <= 0:
            continue
            
        if t.cooldown > 0:
            if CHEAT_MODE['fast_reload']:
                t.cooldown = 0
            else:
                t.cooldown -= dt * BALANCE_CONFIG['tower_fire_rate']

        closest = None
        min_d = t.range  
        for e in all_enemies:
            if e.is_alive:
                dx, dy = e.x - t.x, e.y - t.y
                d = math.hypot(dx, dy)
                if d < min_d:
                    min_d = d
                    closest = e

        if not closest:
            continue

        dx, dy = closest.x - t.x, closest.y - t.y
        target_angle = math.degrees(math.atan2(dy, dx)) - 90
        diff = (target_angle - tower_rotations[t.index] + 180) % 360 - 180
        tower_rotations[t.index] += diff * 0.15

        if abs(diff) < 4 and t.cooldown <= 0:
            bullets.append(
                Bullet(t.x, t.y, 180, closest.x, closest.y, t.damage, from_enemy=False)
            )
            t.cooldown = 25

def enemy_king_logic(dt):
    global king, mortar, active_towers, boss_manual_mode

    if not king or king.health <= 0:
        return
        
    king.update(dt)

    if boss_manual_mode:
        return

    target, dist = king.find_nearest_tower(active_towers)

    if target:
        dx, dy = target.x - king.x, target.y - king.y
        king.angle = math.degrees(math.atan2(-dx, dy))

        
        WALL_LIMIT = 750
        can_approach = True
        
        rad = math.radians(king.angle)
        test_x = king.x - math.sin(rad) * king.speed * dt * 48
        test_y = king.y + math.cos(rad) * king.speed * dt * 48
        
        if abs(test_x) > WALL_LIMIT or abs(test_y) > WALL_LIMIT:
            can_approach = False
        
        if dist > king.attack_range * 0.7 and can_approach:
            king.auto_move(dt * 0.8)  
        
        if dist <= king.attack_range:
            if king.fire_cooldown <= 0:
                king.fire_mortar(mortar, dist)
                camera_shake_effect(10)
    else:
        
        king.angle = (king.angle + 3.0) % 360


def mouse_listener(button, state, x, y):
    global gamestate, gameon, Game_level, gems, active_towers,cstate
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        px, py = convert_coordinate(x, y)
        
        if gamestate == "start":
            if btn_new_game[0] <= px <= btn_new_game[2] and btn_new_game[1] <= py <= btn_new_game[3]:
                gamestate = "play"
                gameon = True
            elif btn_level[0] <= px <= btn_level[2] and btn_level[1] <= py <= btn_level[3]:
                Game_level = (Game_level % 20) + 1
                global all_enemies, king
                all_enemies, king = create_marching_group(GRID_LENGTH, Game_level)
            elif btn_exit[0] <= px <= btn_exit[2] and btn_exit[1] <= py <= btn_exit[3]:
                glutLeaveMainLoop()

        elif gamestate == "play":
            for t in towers:
                x1, y1, x2, y2 = t.buttonbox
                if x1 <= px <= x2 and y1 <= py <= y2:
                    if t.unlock == 1 and t.health <= 0:
                        rebuild_cost = 150  
                        if gems >= rebuild_cost:
                            gems -= rebuild_cost
                            t.health = t.max_health
                            print(f"REBUILT: Tower {t.index + 1}")
                    elif t.unlock == 0:
                        unlock_cost = 50
                        if gems >= unlock_cost:
                            gems -= unlock_cost
                            t.unlock = 1
                            t.health = BALANCE_CONFIG['tower_start_health']
                            t.max_health = BALANCE_CONFIG['tower_start_health']
                            active_towers.append(t)
                            print(f"DEPLOYED: Tower {t.index + 1}")
                    elif t.unlock == 1 and t.health > 0:
                        upgrade_cost = 25 * t.level  
                        if gems >= upgrade_cost:
                            gems -= upgrade_cost
                            t.upgrade()
                            print(f"UPGRADED: Tower {t.index + 1} -> Level {t.level}")
                    break
           
        glutPostRedisplay()
    
    

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if gamestate == "play":
            cstate = (cstate + 1) % 3
            print(f"Camera Mode: {cstate}")
            glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"King's Guard - Balanced Edition with Cheats")
    
    glutDisplayFunc(showScreen)
    glutMouseFunc(mouse_listener)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(idle)
    
    glEnable(GL_DEPTH_TEST)
   
   
    glutMainLoop()



if __name__ == "__main__":
    main()