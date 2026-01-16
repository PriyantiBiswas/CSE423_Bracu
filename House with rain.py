from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

w, h = 800, 600
rain_angle = 0.0
bg_color = 0.1  # night by default
rain_drop = []

# Raindrop positions
for i in range(250):  #raindrops
    x = random.randint(-250, 250)
    y = random.randint(-250, 250)
    rain_drop.append([x, y])


def draw_ground():
    glColor3f(0.5, 0.3, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(-250, -250)
    glVertex2f(-250, -100)
    glVertex2f(250, -250)
    glVertex2f(250, -250)
    glVertex2f(-250, -100)
    glVertex2f(250, -100)
    glEnd()


def draw_trees():
    glColor3f(0.0, 0.7, 0.0)

    # Left trees

    glBegin(GL_TRIANGLES)
    glVertex2f(-260, -100)
    glVertex2f(-210, -100)
    glVertex2f(-235, -20)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(-200, -100)
    glVertex2f(-150, -100)
    glVertex2f(-175, -20)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(-140, -100)
    glVertex2f(-90, -100)
    glVertex2f(-115, -20)
    glEnd()

    # Middle trees
    glBegin(GL_TRIANGLES)
    glVertex2f(-80, -100)
    glVertex2f(-30, -100)
    glVertex2f(-55, -20)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(-20, -100)
    glVertex2f(30, -100)
    glVertex2f(5, -20)
    glEnd()

    # Right trees
    glBegin(GL_TRIANGLES)
    glVertex2f(40, -100)
    glVertex2f(90, -100)
    glVertex2f(65, -20)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(100, -100)
    glVertex2f(150, -100)
    glVertex2f(125, -20)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(160, -100)
    glVertex2f(210, -100)
    glVertex2f(185, -20)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(220, -100)
    glVertex2f(270, -100)
    glVertex2f(245, -20)
    glEnd()


def draw_house():
    # House body
    glColor3f(0.7, 0.6, 0.5)
    glBegin(GL_TRIANGLES)
    glVertex2f(-75, -100)
    glVertex2f(75, -100)
    glVertex2f(75, 50)
    glVertex2f(75, 50)
    glVertex2f(-75, 50)
    glVertex2f(-75, -100)
    glEnd()

    # Roof
    glColor3f(0.6, 0.2, 0.2)
    glBegin(GL_TRIANGLES)
    glVertex2f(-90, 50)
    glVertex2f(90, 50)
    glVertex2f(0, 130)
    glEnd()

    # Door
    glColor3f(0.4, 0.3, 0.2)
    glBegin(GL_TRIANGLES)
    glVertex2f(-15, -100)
    glVertex2f(15, -100)
    glVertex2f(15, -30)
    glVertex2f(15, -30)
    glVertex2f(-15, -30)
    glVertex2f(-15, -100)
    glEnd()

    # Windows 
    glColor3f(0.0, 0.8, 1.0)

    # Left window
    glBegin(GL_TRIANGLES)
    glVertex2f(-55, -15)
    glVertex2f(-35, -15)
    glVertex2f(-35, 5)
    glVertex2f(-35, 5)
    glVertex2f(-55, 5)
    glVertex2f(-55, -15)
    glEnd()

    # Right window
    glBegin(GL_TRIANGLES)
    glVertex2f(35, -15)
    glVertex2f(55, -15)
    glVertex2f(55, 5)
    glVertex2f(55, 5)
    glVertex2f(35, 5)
    glVertex2f(35, -15)
    glEnd()

    # Window crosses
    glColor3f(0.0, 0.0, 0.0)
    

    # Left
    glBegin(GL_LINES)
    glVertex2f(-45, 5)
    glVertex2f(-45, -15)
    glVertex2f(-55, -5)
    glVertex2f(-35, -5)
    glEnd()

    # Right
    glBegin(GL_LINES)
    glVertex2f(45, 5)
    glVertex2f(45, -15)
    glVertex2f(35, -5)
    glVertex2f(55, -5)
    glEnd()

    # Door knob
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(0.0, 0.0, 0.0)
    glVertex2f(10, -60)
    glEnd()

def draw_background():
    glBegin(GL_TRIANGLES)
    glColor3f(bg_color, bg_color, bg_color )

    # Triangle 1
    glVertex2f(-250, -250)
    glVertex2f(250, -250)
    glVertex2f(250, 250)

    # Triangle 2
    glVertex2f(-250, -250)
    glVertex2f(-250, 250)
    glVertex2f(250, 250)

    glEnd()


def drop_rain():
    
    glColor3f(0.5, 0.7, 1.0)
    glBegin(GL_LINES)
    for drop in rain_drop:
        glVertex2f(drop[0], drop[1])  # starting point
        glVertex2f(drop[0] + rain_angle * 10, drop[1] - 5)  # wind addes
        
    glEnd()


def update_rain():
    for drop in rain_drop:
        drop[1] -= 0.5         # fall down
        drop[0] += rain_angle * 0.05  # for wind hele jao

        if drop[1] <= -250:
            drop[1] = 250 


def keyboard_listener(key, x, y):
    global bg_color
    if key == b'w':   # day
        bg_color = 0.9
    elif key == b's': # night
        bg_color = 0.0


def special_key_listener(key, x, y):
    global rain_angle
    if key == GLUT_KEY_LEFT:
        rain_angle -= 0.01
    elif key == GLUT_KEY_RIGHT:
        rain_angle += 0.01


def display():
     
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    draw_background()
    draw_ground()
    draw_trees()
    draw_house()
    drop_rain()

    glutSwapBuffers()


def animate():
    update_rain()
    glutPostRedisplay()


def setup_projection():
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(w, h)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Task 1: House in Rainfall")

    setup_projection()

    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)

    glutMainLoop()


if __name__ == "__main__":
    main()
