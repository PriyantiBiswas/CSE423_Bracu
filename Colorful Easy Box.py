from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

w, h = 800, 600
balls = []
pause = False
ball_speed = 0.2

# Blink control
blink = False
blink_sta= 0
blink_dura = 1.0  # seconds

colors = [
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (1.0, 1.0, 0.0),
    (1.0, 0.5, 0.0),
    (0.5, 0.0, 0.8),
    (1.0, 0.0, 1.0),
    (1.0, 0.2, 0.7),
    (0.2, 0.6, 0.9),
]


class Ball:
    def __init__(self, x, y, color, direcx, direcy):
        self.x = x
        self.y = y
        self.color = color
        self.direcx = direcx
        self.direcy = direcy
        self.size = 8
        self.speed = ball_speed

    def update(self):
        if not pause:
            self.x += self.direcx * self.speed
            self.y += self.direcy * self.speed

            if self.x >= w:
              self.x = w     
              self.direcx *= -1
            elif self.x <= 0:
              self.x = 0
              self.direcx *= -1

            if self.y >= h:
               self.y = h
               self.direcy *= -1
            elif self.y <= 0:
               self.y = 0
               self.direcy *= -1

        
        if blink:
            glColor3f(0.0, 0.0, 0.0)  
        else:
            glColor3f(self.color[0], self.color[1], self.color[2])

        glPointSize(self.size)
        glBegin(GL_POINTS)
        glVertex2f(self.x, self.y)
        glEnd()


def display():
    global blink

    glClear(GL_COLOR_BUFFER_BIT)

    # Stop blink if duration passed
    if blink and (time.time() - blink_sta >= blink_dura):
        blink = False

    for b in balls:
        b.update()

    glutSwapBuffers()
    glutPostRedisplay()


def mouse_listener(button, state, x, y):
    global blink, blink_sta
    if state == GLUT_DOWN:
        y = h - y
        if button == GLUT_RIGHT_BUTTON:
            
            direcx, direcy = random.choice([-1, 1]), random.choice([-1, 1])
            color = random.choice(colors)
            balls.append(Ball(x, y, color, direcx, direcy))
        elif button == GLUT_LEFT_BUTTON:
            
            if balls:  # only if balls exist
                blink = True
                blink_sta = time.time()


def keyboard_listener(key, x, y):
    global pause
    if key == b' ':
        pause = not pause


def special_key_listener(key, x, y):
    if key == GLUT_KEY_UP:
        for b in balls:
            b.speed *= 2
    elif key == GLUT_KEY_DOWN:
        for b in balls:
            b.speed /= 2


def setup_projection():
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1, 1)
    glMatrixMode(GL_MODELVIEW)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(w, h)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"ask 2 - Colorful Easy Box")

    setup_projection()
    glutDisplayFunc(display)
    glutMouseFunc(mouse_listener)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMainLoop()


if __name__ == "__main__":
    main()
