import math
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
#variables
wid = 800  
heit = 600  
c_rad = 20  
ship_wid = 40 
ship_heit = 20 
ship_y = 50     
f_speed = 1      
bul_speed = 5     
m_limit = 3     
cs_prob = 0.02 
sc_prob = 0.01 
extra_point = 5 

spaceship_x = wid // 2
bullets = []
circles = []
special_circles = []
score = 0
missed = 0
game_over = False
paused = False
button_size = 30
button_positions = {"restart": (50, heit - 50, button_size, button_size),"pause": (wid // 2 - 15, heit - 50, button_size, button_size),"quit": (wid - 80, heit - 50, button_size, button_size),}

def draw_circle(xc, yc, r, color):
    glColor3fv(color)
    x, y = 0, r
    d = 1 - r
    glBegin(GL_POINTS)
    while x <= y:
        for px, py in [(x, y), (y, x), (-x, y), (-y, x),
                       (x, -y), (y, -x), (-x, -y), (-y, -x)]:
            glVertex2i(xc + px, yc + py)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()

def draw_line(x1, y1, x2, y2, color):
    glColor3fv(color)
    glBegin(GL_LINES)
    glVertex2i(x1, y1)
    glVertex2i(x2, y2)
    glEnd()

def draw_cross(x, y, size, color):
    half = size // 2
    draw_line(x - half, y - half, x + half, y + half, color)
    draw_line(x + half, y - half, x - half, y + half, color)

def draw_pause_or_play(x, y, size, color, is_play):
    half = size // 2
    if is_play:
        glBegin(GL_TRIANGLES)
        glColor3fv(color)
        glVertex2f(x - half, y - half)
        glVertex2f(x + half, y)
        glVertex2f(x - half, y + half)
        glEnd()
    else:
        draw_line(x - half + 5, y - half, x - half + 5, y + half, color)
        draw_line(x + half - 5, y - half, x + half - 5, y + half, color)

def draw_rectangle(x, y, width, height, color):
    draw_line(x, y, x + width, y, color)
    draw_line(x + width, y, x + width, y + height, color)
    draw_line(x + width, y + height, x, y + height, color)
    draw_line(x, y + height, x, y, color)

def draw_text(x, y, text, color):
    glColor3fv(color)
    glRasterPos2i(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def is_inside_rect(mx, my, x, y, width, height):
    return x <= mx <= x + width and y <= my <= y + height

def display():
    global spaceship_x, bullets, circles, special_circles, score, missed, game_over, paused

    glClear(GL_COLOR_BUFFER_BIT)

    if not game_over:
        draw_line(spaceship_x, ship_y, spaceship_x + ship_wid, ship_y, (1, 1, 1))
        draw_line(spaceship_x + ship_wid, ship_y, spaceship_x + ship_wid // 2, ship_y + ship_heit, (1, 1, 1))
        draw_line(spaceship_x + ship_wid // 2, ship_y + ship_heit, spaceship_x, ship_y, (1, 1, 1))

        if not paused:
            new_bullets = []
            for bullet_x, bullet_y in bullets:
                draw_circle(bullet_x, bullet_y, 2, (1, 1, 1))
                bullet_y += bul_speed
                if bullet_y < heit:
                    new_bullets.append((bullet_x, bullet_y))
            bullets = new_bullets

        new_circles = []
        for circle_x, circle_y in circles:
            draw_circle(circle_x, circle_y, c_rad, (0, 1, 0))
            if not paused:
                circle_y -= f_speed
            if circle_y < 0:
                missed += 1
            else:
                new_circles.append((circle_x, circle_y))
        circles = new_circles
        for circle_x, circle_y in circles:
            if circle_y - c_rad <= ship_y + ship_heit and \
               circle_x + c_rad >= spaceship_x and \
               circle_x - c_rad <= spaceship_x + ship_wid:
                game_over = True

        new_special_circles = []
        for circle_x, circle_y, radius, delta_radius in special_circles:
            draw_circle(circle_x, circle_y, radius, (1, 0, 1))
            if not paused:
                circle_y -= f_speed
                radius += delta_radius
                if radius >= 30 or radius <= 10:
                    delta_radius = -delta_radius
            if circle_y < 0:
                missed += 1
            else:
                new_special_circles.append((circle_x, circle_y, radius, delta_radius))
        special_circles = new_special_circles

        for circle_x, circle_y, radius, _ in special_circles:
            if circle_y - radius <= ship_y + ship_heit and \
               circle_x + radius >= spaceship_x and \
               circle_x - radius <= spaceship_x + ship_wid:
                game_over = True

        for i in bullets:
            for circle in circles[:]:
                if math.hypot(circle[0] - i[0], circle[1] - i[1]) <= c_rad:
                    score += 1
                    bullets.remove(i)
                    circles.remove(circle)
                    break
            for circle in special_circles[:]:
                if math.hypot(circle[0] - i[0], circle[1] - i[1]) <= circle[2]:
                    score += extra_point
                    bullets.remove(i)
                    special_circles.remove(circle)
                    break

        if missed >= m_limit:
            game_over = True

    else:
        draw_text(wid // 2 - 50, heit // 2, "GAME OVER", (1, 0, 0))

    restart_x, restart_y, width, height = button_positions["restart"]
    draw_rectangle(restart_x, restart_y, width, height, (0, 1, 0))  
    x, y, _, _ = button_positions["pause"]
    draw_pause_or_play(x, y, button_size, (1, 0.5, 0), not paused)  
    quit_x, quit_y, _, _ = button_positions["quit"]
    draw_cross(quit_x, quit_y, button_size, (1, 0, 0))
    draw_text(10, heit - 20, f"Score: {score}", (1, 1, 0))
    glFlush()

def mouse(button, state, x, y):
    global spaceship_x, bullets, circles, special_circles, score, missed, game_over, paused

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        mx, my = x, heit - y  
        restart_x, restart_y, width, height = button_positions["restart"]
        if is_inside_rect(mx, my, restart_x, restart_y, width, height):
            score, missed = 0, 0
            game_over = False
            bullets.clear()
            circles.clear()
            special_circles.clear()
        elif is_inside_rect(mx, my, *button_positions["pause"][:2], button_size, button_size):
            paused = not paused
        elif is_inside_rect(mx, my, *button_positions["quit"][:2], button_size, button_size):
            print(f"Goodbye. Final Score: {score}")
            glutLeaveMainLoop()

def keyboard(key, x, y):
    global spaceship_x, bullets

    if not game_over and not paused:
        if key == b'a' and spaceship_x > 0:
            spaceship_x -= 10
        elif key == b'd' and spaceship_x < wid - ship_wid: 
            spaceship_x += 10
        elif key == b' ':  
            bullets.append((spaceship_x + ship_wid // 2, ship_y + ship_heit))


def timer(value):
    global circles, special_circles
    if not paused and not game_over:
        if random.random() < cs_prob:
            circles.append((random.randint(c_rad, wid - c_rad), heit))
        if random.random() < sc_prob:
            special_circles.append((random.randint(c_rad, wid - c_rad), heit, c_rad, 1))
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, wid, 0, heit)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(wid, heit)
    glutCreateWindow(b"Shoot The Circles!")
    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, timer, 0)
    init()
    glutMainLoop()

if __name__ == "__main__":
    main()

