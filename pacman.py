
from board import boards
from math import pi as PI

import pygame

pygame.init()

WIDTH = 600
HEIGHT = 760

screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
level = boards
levelY = len(level)
levelX =  len(level[0])
h = min(((HEIGHT) // levelY),((WIDTH // levelX)))
w = h

flicker = False
player_speed_coeff = 0.1

background_color = "#181E25"
border_color = "#C6FF69"
dot_color = "#425061"
grid_color = "#425061"

score = 0

moving = False
counter = 0
maxCounter = 60
player_images = []
for i in range(1, 3):
    player_images.append(pygame.transform.scale(pygame.image.load(f"assets/player_images/{i}.svg"), (w,h)))

ghost_image = pygame.transform.scale(pygame.image.load(f"assets/ghost/1.svg"), (w,h))

direction = 0
turns_allowed = [False, False, False, False]

def get_ghost_pos():
    res = []
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 10:
                player_x = (j) * w
                player_y = (i) * h
                res.append((player_x,player_y))
    return res
                

def get_default_pos():
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == -1:
                player_x = (j) * w
                player_y = (i) * h
                return (player_x,player_y)

player_x = get_default_pos()[0]
player_y = get_default_pos()[1]

ghosts_positions = get_ghost_pos()

def get_h(x,y):
    (X,Y) = get_cell(player_x, player_y)
    return abs(x - X) + abs(y - Y)

def node_is_allowed(x,y):
    if(x >= levelX or y>= levelY or x<1 or y< 1): return False
    node = level[y][x] 
    if(node < 3 or node == 9 or node == 10):
        return True
    else:
        return False


def get_nodes(node):
    nodes = []
    x = node.x
    y = node.y
    if(node_is_allowed(x,y+1)):
        nodes.append(Node(x,y+1, node))  
    if(node_is_allowed(x,y-1)):
        nodes.append(Node(x,y-1, node))  
    if(node_is_allowed(x+1,y,)):
        nodes.append(Node(x+1,y, node))
    if(node_is_allowed(x-1,y)):
        nodes.append(Node(x-1,y, node))
    return nodes

class Node:
    def __init__(self,x,y,parent):
        self.x = x
        self.y = y
        if(parent != None):
            self.g = parent.g + 1
        else: 
            self.g = 0
        self.h = get_h(x,y)
        self.f = self.g + self.h
        self.parent = parent

def findmin(set):
    set = list(set)
    s0 = set[0]
    for s in set:
        if(s.f < s0.f):
            s0 = s
    return s0



def find_path(x,y):
    X, Y = get_cell(player_x, player_y)
    openList = set()
    closedList = set()
    q = Node(x, y, None)
    q.h = get_h(x,y)
    q.f = q.h
    openList.add(q)
    while(openList):
        q = findmin(openList)
        openList.remove(q)
        closedList.add(q)

        nodes = get_nodes(q)
        for n in nodes:
            if(n.x == X and n.y == Y):
                path = []
                path.append((n.x,n.y))
                while n.parent != None:
                    n = n.parent
                    path.append((n.x,n.y))
                path.reverse()
                return path
            else:
                toSkip = False
                for o in openList:
                    if (o.x == n.x and o.y == n.y and o.f < n.f):
                        toSkip = True
                for o in closedList:
                    if (o.x == n.x and o.y == n.y and o.f < n.f):
                        toSkip = True
                if(toSkip == False):
                    openList.add(n)
        

    return [(x,y), (x,y)]

def move_ghosts(ghosts_positions):
    res = []
    for (ghost_x, ghost_y) in ghosts_positions:
        (x,y) = get_cell(ghost_x, ghost_y)
        path = find_path(x,y)

        X,Y = path[1]
        _x = ghost_x
        _y = ghost_y
        if(X == x+1):
            _x += player_speed_coeff * w / 2
        if(X == x-1):
            _x -= player_speed_coeff * w / 2
        if(Y == y+1):
            _y += player_speed_coeff * h / 2
        if(Y == y-1):
            _y -= player_speed_coeff * h / 2 
        res.append((_x,_y))

    return res


def draw_ghost():
    for (ghost_x, ghost_y) in ghosts_positions:
        screen.blit(ghost_image, (ghost_x, ghost_y))


def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if direction == 0:
        screen.blit(player_images[counter < maxCounter//2], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter < maxCounter//2], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter <  maxCounter//2], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter <  maxCounter//2], 270), (player_x, player_y))

def get_cell(pos_x, pos_y):
    x = (int)((pos_x + w/2) // w)
    y = (int)((pos_y + h/2) // h)
    return (x,y)


def check_position(centerx, centery):
    turns = [False, False, False, False]

    x = (int)((centerx) // w)
    y = (int)((centery) // h)

    if direction == 0:
        if level[y][int((centerx - w/2) // w) + 1] < 3:
            turns[0] = True
    if direction == 1:
        if level[y][int((centerx + w/2) // w) - 1] < 3:
            turns[1] = True
    if direction == 2:
        if level[int((centery + w/2) // w) - 1][x] < 3:
            turns[2] = True
    if direction == 3:
        if level[int((centery - w/2) // w) + 1][x] < 3:
            turns[3] = True
    return turns


def move_player(play_x, play_y):

    # r, l, u, d
    if direction == 0 and turns_allowed[0]:           
        play_x += player_speed_coeff * w
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed_coeff * w
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed_coeff * h
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed_coeff * h
    return play_x, play_y

pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
font = pygame.font.SysFont('Comic Sans MS', 30)

def draw_board():
    text_surface = font.render("Score: " + str(score), False, border_color)
    screen.blit(text_surface, (0,HEIGHT - 50))

    for i in range(len(level)):
        for j in range(len(level[i])):
            pygame.draw.line(screen, grid_color, (j * w, i * h),(j * w, (i+1) * h), 1)
            pygame.draw.line(screen, grid_color, (j * w, i * h),((j+1) * w, (i) * h), 1)
      
            if level[i][j] == 1:
                pygame.draw.circle(screen, dot_color, (j * w + (0.5 * w), i * h + (0.5 * h)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, dot_color, (j * w + (0.5 * w), i * h + (0.5 * h)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, border_color, (j * w + (0.5 * w), i * h),
                                 (j * w + (0.5 * w), i * h + h), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, border_color, (j * w, i * h + (0.5 * h)),
                                 (j * w + w, i * h + (0.5 * h)), 3)
            if level[i][j] == 5:
                pygame.draw.line(screen, border_color, ((j)*w, (i+0.5)*h), ((j+0.5)*w, (i+0.5)*h),3)
                pygame.draw.line(screen, border_color, ((j+0.5)*w, (i+0.5)*h), ((j+0.5)*w, (i+1)*h),3)
            if level[i][j] == 6:
                pygame.draw.line(screen, border_color, ((j+1)*w, (i+0.5)*h), ((j+0.5)*w, (i+0.5)*h),3)
                pygame.draw.line(screen, border_color, ((j+0.5)*w, (i+0.5)*h), ((j+0.5)*w, (i+1)*h),3)
            if level[i][j] == 7:
                pygame.draw.line(screen, border_color, ((j+1)*w, (i+0.5)*h), ((j+0.5)*w, (i+0.5)*h),3)
                pygame.draw.line(screen, border_color, ((j+0.5)*w, (i+0.5)*h), ((j+0.5)*w, i*h),3)
            if level[i][j] == 8:
                pygame.draw.line(screen, border_color, ((j)*w, (i+0.5)*h), ((j+0.5)*w, (i+0.5)*h),3)
                pygame.draw.line(screen, border_color, ((j+0.5)*w, (i+0.5)*h), ((j+0.5)*w, i*h),3)
            if level[i][j] == 9:
                pygame.draw.line(screen, dot_color, (j * w, i * h + (0.5 * h)),
                                 (j * w + w, i * h + (0.5 * h)), 3)
                
          
                

startup_counter = 0
direction_command = 0
run = True

def draw_score():
    screen.fill("green")
    text_surface = font.render("A ghost ate you.", False, (0, 0, 0))
    screen.blit(text_surface, (0,0))  
    text_surface = font.render("Your score: " + str(score), False, (0, 0, 0))
    screen.blit(text_surface, (0,50))



while run:
    timer.tick(fps)
    if counter < maxCounter :
        counter += 1
        if(counter == maxCounter-3):
            flicker = True
        
    else:
        flicker = False
        counter = 0

    screen.fill(background_color)
    draw_board()
    draw_player()
    draw_ghost()

    if startup_counter < 180:
        moving = False
        startup_counter += 1
    else:
        moving = True

    (x,y) = get_cell(player_x, player_y)

    if(level[y][x] == 1 or level[y][x] == 2):
        if(level[y][x] == 1):
            score += 1
        else:
            score += 5
        level[y][x] = 0

    for (X,Y) in ghosts_positions:
        if((x,y) == (get_cell(X,Y))):
            moving = False
            draw_score()

    if(direction == 0 and level[y][x] == -2):
        player_x = 0

    if(direction == 1 and level[y][x] == -3):
        player_x = levelX * w - 1.5 * w
    
    if moving:
        player_x, player_y = move_player(player_x, player_y)
        ghosts_positions = move_ghosts(ghosts_positions)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    if direction_command == 0 :
        direction = 0
    if direction_command == 1 :
        direction = 1
    if direction_command == 2 :
        direction = 2
    if direction_command == 3 :
        direction = 3

    center_x = player_x + w/2
    center_y = player_y + h/2

    turns_allowed = check_position(center_x, center_y)
    #turns_allowed = [True,True,True,True]
    pygame.display.flip()

pygame.quit()