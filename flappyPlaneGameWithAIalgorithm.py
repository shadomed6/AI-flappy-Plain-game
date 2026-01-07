import pygame
from pygame.locals import *
import random

# AI algorithm imports
import pygame
from pygame.locals import *
import random
import pickle  
import os      



epsilon = 0.1   
epsilon_min = 0.01
epsilon_decay = 0.9995  # Reduces randomness slightly every frame

alpha = 0.8     # Learning Rate
gamma = 0.9     # Discount Factor 


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
font = pygame.font.Font("ARCADECLASSIC.ttf", 60)



# Images 
bg = pygame.transform.scale(
    pygame.image.load('newYorkBG.png'),
    (screen_width, screen_height)
)
button_img = pygame.image.load('restart.png')
ground_img = pygame.transform.scale(
    pygame.image.load('road.jpg'),
    (screen_width, 100)
)
def reset_game():
    towers_group.empty()
    flappy.rect.x = 100
    flappy.rect.y=int(screen_height // 2)
    score=0
    return score

 

# Plane class with AI added
class plane(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        self.vel = 0
        self.clicked = False
        
        # the brain
        self.q_table = {} 
        self.load_brain() 
        
        for num in range(1, 3):
            img_orig = pygame.image.load(f'plane{num}.png')
            img = pygame.transform.scale(img_orig, (130, 120))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.mask = pygame.mask.from_surface(self.image)
        self.current_state = (0,0,0)
        self.last_action = 0

    def load_brain(self):
        if os.path.exists('brain.pickle'):
            with open('brain.pickle', 'rb') as f:
                self.q_table = pickle.load(f)

    def save_brain(self):
        with open('brain.pickle', 'wb') as f:
            pickle.dump(self.q_table, f)

    def get_state(self, towers_group):
        # 1. Find the target pipe
        target_pipe = None
        min_dist = 9999
        
        for tower in towers_group:
            # Only look at bottom towers 
            if tower.position == -1:
                # If the pipe is not behind us yet
                if tower.rect.right > self.rect.left:
                    dist = tower.rect.left - self.rect.left
                    if dist < min_dist:
                        min_dist = dist
                        target_pipe = tower
        
        if target_pipe:
            # calculate gap center
            gap_center_y = target_pipe.rect.top - 75
            # Divide by BIGGER numbers to make the brain smaller
            dx = int(min_dist / 50)  
            
            # Vertical distance to gap center 
            dy = int((gap_center_y - self.rect.centery) / 30)
            
            # Velocity
            vel = int(self.vel / 4)
            
            # Cap the values so the table doesn't explode
            if dx > 10: dx = 10
            if dy > 10: dy = 10
            if dy < -10: dy = -10
            
            return (dx, dy, vel)
            
        return (0, 0, 0) # Fallback

    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0, 0] 
        return self.q_table[state]

    def ai_action(self, towers_group):
        state = self.get_state(towers_group)
        self.current_state = state 
        
        # Greedy logic
        if random.random() < epsilon:
            return random.choice([0, 1])
        else:
            q_values = self.get_q_values(state)
            # If unsure, flap,helps prevent falling forever
            if q_values[0] == q_values[1]:
                return 1 
            return q_values.index(max(q_values))

    def update_brain(self, reward, towers_group):
        new_state = self.get_state(towers_group)
        old_val = self.get_q_values(self.current_state)[self.last_action]
        future_max = max(self.get_q_values(new_state))
        
        # Bellman Equation
        new_val = (1 - alpha) * old_val + alpha * (reward + gamma * future_max)
        self.q_table[self.current_state][self.last_action] = new_val

    def update(self, action_input):
        if action_input == 1:
            self.vel = -10
            self.clicked = True
            jump_fx.play()
        
        if flying:
            self.vel += 0.75
            if self.vel > 8: self.vel = 8
            if self.rect.bottom < 770:
                self.rect.y += int(self.vel)

        if not game_over:
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)
        
        self.mask = pygame.mask.from_surface(self.image)


        
            

# Tower class
class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        # adding AI code to know which tower is top and which is bottom
        self.position = position

        img_orig = pygame.image.load('tower.png')
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
plane_group = pygame.sprite.Group()
towers_group = pygame.sprite.Group()

# Create plane
flappy = plane(100, screen_height // 2 - 50)
plane_group.add(flappy)

# Create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)


# --- SOUND SETUP ---
pygame.mixer.init() # Initialize the sound system

# 1. Load the music file

pygame.mixer.music.load('BGmusic.wav') 

# 2. Set the Volume

pygame.mixer.music.set_volume(0.5) 

# 3. Play the music
# The -1 means "Loop Forever". If you put 0, it plays once and stops.
pygame.mixer.music.play(-1, 0.0)


# --- jump SFX ---
jump_fx = pygame.mixer.Sound('jump.wav')
jump_fx.set_volume(0.5)


# --- crash SFX ---
crash_fx = pygame.mixer.Sound('crash.wav')
crash_fx.set_volume(0.5)





# Game loop with AI added
run = True
while run:
    # speed
    clock.tick(60) 

    screen.blit(bg, (0, 0))
    towers_group.draw(screen)

    # Ground scrolling
    screen.blit(ground_img, (ground_scroll, 760)) 
    screen.blit(ground_img, (ground_scroll + ground_img.get_width(), 760))
    if not game_over:
        ground_scroll -= scroll_speed
        if ground_scroll <= -ground_img.get_width():
            ground_scroll = 0

    if flying and not game_over:
        action = flappy.ai_action(towers_group)
        flappy.update(action)
        
        
        reward = 1 # Small reward for every frame it stays alive
        
        # Check if we passed a pipe this frame
        if len(tower_pairs) > 0:
            pair = tower_pairs[0]
            # If we are exactly past the right side of the pipe
            if not pair['passed'] and flappy.rect.left > pair['bottom'].rect.right:
                reward = 200 # bonus for passing a tower
                pair['passed'] = True
                score += 1
            
        flappy.update_brain(reward, towers_group)
        
    else:
        flappy.update(0)

    plane_group.draw(screen)

    # Collision
    hit_pipe = pygame.sprite.groupcollide(plane_group, towers_group, False, False, pygame.sprite.collide_mask)
    hit_top = flappy.rect.top < 0
    hit_ground = flappy.rect.bottom >= 770

    if hit_pipe or hit_top or hit_ground:
        if not game_over:
            game_over = True
            crash_fx.play()
            
            # punishment
            flappy.update_brain(-700, towers_group)
            flappy.save_brain()

            # Restart
            game_over = False
            flying = True
            towers_group.empty()
            tower_pairs = []
            flappy.rect.center = (100, screen_height // 2)
            flappy.vel = 0
            score = 0
            last_tower = pygame.time.get_ticks()

    # Generator
    if not game_over and flying:
        time_now = pygame.time.get_ticks()
        if time_now - last_tower > tower_frequency:
            tower_height = random.randint(-100, 100)
            top = Tower(screen_width, screen_height // 2 + tower_height, 1)
            btm = Tower(screen_width, screen_height // 2 + tower_height, -1)
            towers_group.add(top)
            towers_group.add(btm)
            tower_pairs.append({'bottom': btm, 'passed': False})
            last_tower = time_now
        towers_group.update()
        
    # Clean up old pipes
    if len(tower_pairs) > 0:
        if tower_pairs[0]['bottom'].rect.right < 0:
            tower_pairs.pop(0)

    # show score
    score_text = font.render(f'{score}', True, (255, 255, 255))
    screen.blit(score_text, (screen_width/2, 10))

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying:
            flying = True
    
    pygame.display.update()

pygame.quit()

