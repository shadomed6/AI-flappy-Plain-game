import pygame
from pygame.locals import *
import random

pygame.init()
pygame.font.init()

# Clock & FPS
clock = pygame.time.Clock()
fps = 60

# Screen size
screen_width = 760
screen_height = 840
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Plane')

# Game variables
ground_scroll = 0
scroll_speed = 4              
flying = False
game_over = False
tower_gap = 150
tower_frequency = 1600
last_tower = pygame.time.get_ticks() - tower_frequency
score = 0

# Tower pairs for scoring
tower_pairs = []

# Font
font = pygame.font.Font("D:/Desktop/AIgameProject (2)/AIgameProject/ARCADECLASSIC.ttf", 60)



# Images (use full path)
bg = pygame.transform.scale(
    pygame.image.load('D:/Desktop/AIgameProject (2)/AIgameProject/newYorkBG.png'),
    (screen_width, screen_height)
)
button_img = pygame.image.load('D:/Desktop/AIgameProject (2)/AIgameProject/restart.png')
ground_img = pygame.transform.scale(
    pygame.image.load('D:/Desktop/AIgameProject (2)/AIgameProject/road.jpg'),
    (screen_width, 100)
)
def reset_game():
    towers_group.empty()
    flappy.rect.x = 100
    flappy.rect.y=int(screen_height // 2)
    score=0
    return score

 
# Plane class
class Plain(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        self.vel = 0
        self.clicked = False
        for num in range(1, 3):
            img_orig = pygame.image.load(f'D:/Desktop/AIgameProject (2)/AIgameProject/plane{num}.png')
            img = pygame.transform.scale(img_orig, (130, 120))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        global flying, game_over
        if flying:
            self.vel += 0.75
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 770:
                self.rect.y += int(self.vel)

        if not game_over:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
                jump_fx.play() # jump SFX logic
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0

            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
            

        self.mask = pygame.mask.from_surface(self.image)


        
            

# Tower class
class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        img_orig = pygame.image.load('D:/Desktop/AIgameProject (2)/AIgameProject/tower.png')
        self.image = pygame.transform.scale(img_orig, (120, 600))
        self.rect = self.image.get_rect()
        if position == 1:  # top tower
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(tower_gap / 2)]
        else:  # bottom tower
            self.rect.topleft = [x, y + int(tower_gap / 2)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Button class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        # get mouse postion
        pos = pygame.mouse.get_pos()

        #check if mouse is over the button 
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] ==1:
                action = True




        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

# Groups
plain_group = pygame.sprite.Group()
towers_group = pygame.sprite.Group()

# Create plane
flappy = Plain(100, screen_height // 2 - 50)
plain_group.add(flappy)

# Create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)


# --- SOUND SETUP ---
pygame.mixer.init() # Initialize the sound system

# 1. Load the music file

pygame.mixer.music.load('D:/Desktop/AIgameProject (2)/AIgameProject/BGmusic.wav') 

# 2. Set the Volume

pygame.mixer.music.set_volume(0.5) 

# 3. Play the music
# The -1 means "Loop Forever". If you put 0, it plays once and stops.
pygame.mixer.music.play(-1, 0.0)


# --- jump SFX ---
jump_fx = pygame.mixer.Sound('D:/Desktop/AIgameProject (2)/AIgameProject/jump.wav')
jump_fx.set_volume(0.5)


# --- crash SFX ---
crash_fx = pygame.mixer.Sound('D:/Desktop/AIgameProject (2)/AIgameProject/crash.wav')
crash_fx.set_volume(0.5)



# Game loop
run = True
while run:
    clock.tick(fps)

    # Background
    screen.blit(bg, (0, 0))

    # Towers
    towers_group.draw(screen)

    
    

    # Ground
    #screen.blit(ground_img, (ground_scroll, screen_height - 860))
    screen.blit(ground_img, (ground_scroll, 760)) 
    screen.blit(ground_img, (ground_scroll + ground_img.get_width(), 760))
    if game_over == False:
        ground_scroll -= scroll_speed
        if ground_scroll <= -ground_img.get_width():
            ground_scroll = 0

    # Plane
    plain_group.update()
    plain_group.draw(screen)
    


    # Collisions
    if pygame.sprite.groupcollide(plain_group, towers_group, False, False, pygame.sprite.collide_mask) or flappy.rect.top < 0:
        
        if game_over == False:
            crash_fx.play() # crash SFX logic
        game_over = True
        
    if flappy.rect.bottom >= 770:
        
        if game_over == False:
            crash_fx.play() # crash SFX logic
        game_over = True
        flying = False
        


    # Generate towers
    if not game_over and flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_tower > tower_frequency:
            tower_height = random.randint(-100, 100)
            top_tower = Tower(screen_width, screen_height // 2 + tower_height, 1)
            bottom_tower = Tower(screen_width, screen_height // 2 + tower_height, -1)
            towers_group.add(top_tower)
            towers_group.add(bottom_tower)
            tower_pairs.append({'top': top_tower, 'bottom': bottom_tower, 'passed': False})
            last_tower = time_now

        

        towers_group.update()

    # Check score
    for pair in tower_pairs:
        if not pair['passed'] and flappy.rect.left > pair['bottom'].rect.right:
            score += 1
            pair['passed'] = True

    # Display score
    score_text = font.render(f'{score}', True, (255, 255, 255))
    screen.blit(score_text, (screen_width/2, 10))

    # Show restart button if game over
    if game_over == True:  
        if button.draw() == True:
            game_over = False
            score = reset_game()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Start flying if game not started
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not flying and not game_over:
                flying = True

            # Restart game if clicked on button
            if game_over and button.rect.collidepoint(pygame.mouse.get_pos()):
                game_over = False
                flying = False
                towers_group.empty()
                tower_pairs.clear()
                flappy.rect.center = (100, screen_height // 2 )
                flappy.vel = 0
                score = 0
                ground_scroll = 0
                last_tower = pygame.time.get_ticks() - tower_frequency

    pygame.display.update()

pygame.quit()
