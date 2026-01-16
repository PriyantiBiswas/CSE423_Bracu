from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time


# Game variables
score = 0
game_sta = 'active'
cheat_mode = False


# Diamond variables
dia_size = 15
dia_x, dia_y = random.randint(50, 550), 800
dia_speed = 100.0
dia_color = [random.uniform(0.6, 1.0),random.uniform(0.6, 1.0),random.uniform(0.6, 1.0)]

# Catcher variables
cat_x, cat_y = 300, 25
cat_w, cat_h = 100, 15
cat_speed = 8  
cat_color = [1.0, 1.0, 1.0]

# Cross button variables
cros_x, cros_y, cros_size = 550, 550, 15

# Arrow button variables
arr_x, arr_y, arr_size = 50, 550, 15

# Pause button variables
pau_btn_x, pau_btn_y, pau_btn_size = 300, 550, 15

# Keyboard state
key_l = False
key_r = False   

last_time = None


def Find_Zo(x, y, x1, y1):
    dx = x1 - x
    dy = y1 - y

    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx < 0 and dy >= 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
        elif dx >= 0 and dy < 0:
            return 7
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx < 0 and dy >= 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        elif dx >= 0 and dy < 0:
            return 6


def conve_To_Zo0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y


def conve_From_Zo0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y


def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2f(int(x), int(y))
    glEnd()


def draw_line(x, y, x1, y1):
    zone = Find_Zo(x, y, x1, y1)
    x_conv, y_conv = conve_To_Zo0(x, y, zone)
    x1_conv, y1_conv = conve_To_Zo0(x1, y1, zone)
    if x_conv > x1_conv:
        x_conv, y_conv, x1_conv, y1_conv = x1_conv, y1_conv, x_conv, y_conv

    dx = x1_conv - x_conv
    dy = y1_conv - y_conv

    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x_cur, y_cur = x_conv, y_conv

    while x_cur <= x1_conv:
        rx, ry = conve_From_Zo0(x_cur, y_cur, zone)
        draw_pixel(rx, ry)
        if d > 0:
            d = d + incNE
            y_cur += 1
        else:
            d = d + incE
        x_cur += 1


def draw_dia(x, y, size):
    glColor3f(dia_color[0], dia_color[1], dia_color[2])
    
    # Top point
    top_x, top_y = x, y + size
    # Right point
    right_x, right_y = x + int(size * 0.6), y
    # Bottom point
    bottom_x, bottom_y = x, y - size
    # Left point
    left_x, left_y = x - int(size * 0.6), y
    
    #diamond shape 
    draw_line(top_x, top_y, right_x, right_y)
    draw_line(right_x, right_y, bottom_x, bottom_y)
    draw_line(bottom_x, bottom_y, left_x, left_y)
    draw_line(left_x, left_y, top_x, top_y)



def draw_cat(cat_x, cat_y, width):
    glColor3f(cat_color[0], cat_color[1], cat_color[2])
    # Bottom line
    draw_line(cat_x - width // 2, cat_y, cat_x + width // 2, cat_y)
    # Left edge
    draw_line(cat_x - width // 2, cat_y, cat_x - width // 3, cat_y - 15)
    # Right edge
    draw_line(cat_x + width // 2, cat_y, cat_x + width // 3, cat_y - 15)
    # Bottom edge connecting
    draw_line(cat_x - width // 3, cat_y - 15, cat_x + width // 3, cat_y - 15)


def draw_cross(x, y):
    glColor3f(1.0, 0.0, 0.0)
    draw_line(x - 10, y - 10, x + 10, y + 10)
    draw_line(x - 10, y + 10, x + 10, y - 10)


def draw_arrow(x, y):
    glColor3f(0.0, 1.0, 1.0)
    # Arrow shaft
    draw_line(x - 15, y, x + 5, y)
    # Arrow head top
    draw_line(x - 15, y, x - 8, y + 8)
    # Arrow head bottom
    draw_line(x - 15, y, x - 8, y - 8)


def draw_pause(x, y):
    glColor3f(1.0, 1.0, 0.0)
    # Left bar
    draw_line(x - 5, y - 10, x - 5, y + 10)
    #right bar
    draw_line(x + 5, y - 10, x + 5, y + 10)


def draw_play(x, y):
    glColor3f(1.0, 1.0, 0.0)
    # Triangle
    draw_line(x - 8, y + 10, x + 8, y)
    draw_line(x + 8, y, x - 8, y - 10)
    draw_line(x - 8, y - 10, x - 8, y + 10)


def aabb_collision(box1, box2):
    left1, right1, top1, bottom1 = box1
    left2, right2, top2, bottom2 = box2
    return not (right1 < left2 or right2 < left1 or bottom1 > top2 or bottom2 > top1)

def get_dia_bbox(x, y, size):
    half_w = int(size * 0.6)
    left = x - half_w
    right = x + half_w
    top = y + size
    bottom = y - size
    return (left, right, top, bottom)

def get_cat_bbox(cx, cy, width):
    half_w = width // 2
    left = cx - half_w
    right = cx + half_w
    top = cy  
    bottom = cy - cat_h
    return (left, right, top, bottom)

def has_collided():
    return aabb_collision(get_dia_bbox(dia_x, dia_y, dia_size),
                          get_cat_bbox(cat_x, cat_y, cat_w))



def res_dia():
    global dia_x, dia_y, dia_speed, dia_color
    
    dia_x = random.randint(50, 550)
    dia_y = 800
    dia_speed += 10
    dia_color = [random.uniform(0.6, 1.0),random.uniform(0.6, 1.0),random.uniform(0.6, 1.0)]
    


def res_game():
    global score, game_sta, cat_color, cat_x, dia_speed, dia_y, dia_x, dia_color, cheat_mode
    score = 0
    game_sta = 'active'
    cat_x = 300
    cat_color = [1.0, 1.0, 1.0]
    dia_speed = 100
    dia_x = random.randint(50, 550)
    dia_y = 800
    dia_color = [random.uniform(0.6, 1.0),random.uniform(0.6, 1.0),random.uniform(0.6, 1.0)]
    cheat_mode = False
    print("Starting Over")


def mouse_click(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        
        y = 600 - y

        # Check restart button (arrow)
        if (arr_x - 20 <= x <= arr_x + 20) and \
           (arr_y - 20 <= y <= arr_y + 20):
            res_game()
            return

        # Check exit button (cross)
        if (cros_x - 20 <= x <= cros_x + 20) and \
           (cros_y - 20 <= y <= cros_y + 20):
            print("Goodbye. Final Score:", score)
            glutLeaveMainLoop()  
            return

        # Check pause button
        if (pau_btn_x - 20 <= x <= pau_btn_x + 20) and \
           (pau_btn_y - 20 <= y <= pau_btn_y + 20):
            tog_pau()

def keyboard_handler(key, x, y):
    global cheat_mode
    
    if key == b'c' or key == b'C':
        if game_sta != 'over':
            cheat_mode = not cheat_mode
            if cheat_mode:
                print("CHEAT MODE ACTIVATED!")
            else:
                print("CHEAT MODE DEACTIVATED!")

def tog_pau():
    global game_sta
    if game_sta == 'active':
        game_sta = 'paused'
        print("Game Paused")
    elif game_sta == 'paused':
        game_sta = 'active'
        print("Game Resumed")


def animate():
    global game_sta, score, dia_y, dia_x, cat_x, cat_color, last_time
    current = time.time()
    if last_time is None:
        last_time = current
    dt = current - last_time
    last_time = current

    if game_sta == 'active':
        dia_y -= dia_speed * dt
        
        
        if cheat_mode:
            if cat_x < dia_x - 2: 
                cat_x += cat_speed
                if cat_x > dia_x:
                    cat_x = dia_x
            elif cat_x > dia_x + 2:
                cat_x -= cat_speed
                if cat_x < dia_x:
                    cat_x = dia_x
        else:
            # Normal manual control 
            if key_l:
                cat_x -= cat_speed
            if key_r:
                cat_x += cat_speed

        #  catcher within boundaries
        half_w = cat_w // 2
        cat_x = max(half_w, min(600 - half_w, cat_x))
        
        #  diamond within horizontal boundaries
        dia_half_w = int(dia_size * 0.6)
        if dia_x < dia_half_w:
            dia_x = dia_half_w
        elif dia_x > 600 - dia_half_w:
            dia_x = 600 - dia_half_w

        if has_collided():
            score += 1
            print("Score:", score)
            res_dia()
        elif dia_y < -50:  # Game over when diamond goes below screen
            game_sta = 'over'
            cat_color = [1.0, 0.0, 0.0]
            print("Game Over! Final Score:", score)
            
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT)

    draw_cat(cat_x, cat_y, cat_w)
    draw_cross(cros_x, cros_y)
    draw_arrow(arr_x, arr_y)

    if game_sta != 'over':
        draw_dia(dia_x, int(dia_y), dia_size)

    if game_sta == 'active':
        draw_pause(pau_btn_x, pau_btn_y)
    else:
        draw_play(pau_btn_x, pau_btn_y)
    
    

    glutSwapBuffers()
    animate()


def special_up(key, x, y):
    global key_l, key_r
    if key == GLUT_KEY_LEFT:
        key_l = False
    elif key == GLUT_KEY_RIGHT:
        key_r = False

def special_input(key, x, y):
    global key_l, key_r
    
    if not cheat_mode:
        if key == GLUT_KEY_LEFT:
            key_l = True
        elif key == GLUT_KEY_RIGHT:
            key_r = True

def main():
    global last_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(600, 600)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Catch the Diamonds!")
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(0, 600, 0, 600)
    glutKeyboardFunc(keyboard_handler)
    glutDisplayFunc(display)
    glutSpecialFunc(special_input)
    glutSpecialUpFunc(special_up)
    glutMouseFunc(mouse_click)
    last_time = time.time()
    glutMainLoop()


main()