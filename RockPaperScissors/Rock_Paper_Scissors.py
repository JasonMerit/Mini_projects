import pygame as pg
from pygame.math import Vector2
import random
from quads import QuadTree, Point
import config


def clamp(pos):
    return Vector2(max(config.sprite_size_2, min(pos.x, w-config.sprite_size_2)), 
                   max(config.sprite_size_2, min(pos.y, h-config.sprite_size_2)))

class Team(pg.sprite.Group):
    def __repr__(self):
        return f"Team of {len(self)} {self.sprites()[0].type}s"
    
    # def find_closest(self, player, targets):
    #     if not targets:
    #         return Vector2(float('inf'), float('inf')) 
    #     return min(targets, key=lambda t: (t.pos - Vector2(player.pos)).length_squared()).pos
    
class Player(pg.sprite.Sprite):
    """
    rect is the bounding box of the sprite and is used only
    for visualizing the sprite. Use pos for movement and collision 
    """
    def __init__(self, type, id, pos=None):
        super().__init__()
        self.type = type
        self.team = ['Rock', 'Paper', 'Scissors'][type]
        self.id = f'{self.team[0]}{id}'
        self.image = pg.image.load(f'RockPaperScissors/Assets/{self.team}.png')
        self.image = pg.transform.scale(self.image, (config.sprite_size, config.sprite_size))
        self.rect = self.image.get_rect()

        if pos:
            self.pos = Vector2(pos)
        else:
            x, y = start_positions[type]  # sample from a 2d normal distribution
            self.pos = clamp(Vector2(random.gauss(x, config.start_spread), random.gauss(y, config.start_spread)))
        self.rect.center = self.pos

        if config.play_sound:
            self.channel = pg.mixer.Channel(pg.mixer.Sound.get_num_channels(sounds[self.type]))
    
    @property
    def point(self):
        return Point(self.pos[0], self.pos[1], data=self)
    
    def play_sound(self):
        if config.play_sound:
            self.channel.play(sounds[self.type])
    
    def __repr__(self):
        return f"{self.id} at {self.rect.center}"
    
    def __str__(self):
        return f"{self.id} at {self.rect.center}"
    
    def update(self, prey: Team, predators: Team):
        # Noise
        self.pos += Vector2(random.uniform(-2, 2), random.uniform(-2, 2))

        # Determine closest prey and predator
        attract = self.get_nearest_pos(prey.tree) 
        repel = self.get_nearest_pos(predators.tree)

        # Move towards closest
        prey_dist = (attract - self.pos).length_squared()
        predator_dist = (repel - self.pos).length_squared()
        target = attract if prey_dist < predator_dist else repel

        v = (target - self.pos)
        if v[0] != 0 and v[1] != 0:
            v = v.normalize()
        else:
            return
        self.pos += v if prey_dist < predator_dist else -v#* 5
        self.pos = clamp(self.pos)
        # Repel from other players in team

        # if 10 < (com - p).length_squared() < 1000:
        #     self.rect.center += (com - p).normalize() * 0.1
        # clamp x,y to stay on screen
        self.rect.center = self.pos
    
    def get_nearest_pos(self,  tree: QuadTree) -> Vector2:
        res = tree.nearest_neighbors(self.point, count=1)
        return res[0].data.pos if res else Vector2(float('inf'), float('inf'))

    def get_nearest_point(self, tree: QuadTree) -> Point:
        res = tree.nearest_neighbors(self.point, count=1)
        return res[0] if res else None
        try:
            return res[0]
        except IndexError:
            print("Index error")
            print(self.point, tree, res)
            quit()

    def collided(self, other_team):
        point = self.get_nearest_point(other_team.tree)
        # determine circular collision
        if point and (Vector2(point.x, point.y) - self.pos).length_squared() < config.collide_radius:
            return point.data
    
    def lay_crumb(self):
        """Just for debugging"""
        self.crumb = Vector2(self.rect.center)
        return self.crumb


clock = pg.time.Clock()
pg.init()
GREY = (202, 202, 202)
w, h = config.dim
start_positions = [(w/2, 2*h/3), (w/3, h/3), (2*w/3, h/3)]
SCREEN = pg.display.set_mode((w, h))
SCREEN.fill((GREY))

# Sound
if config.play_sound:
    pg.mixer.init()
    pg.mixer.music.load('RockPaperScissors/Assets/zapsplat_household_manicure_scissors_snip_001_41816.mp3')
    rock_sound = pg.mixer.Sound('RockPaperScissors/Assets/zapsplat_foley_money_us_2_dollar_bill_note_set_down_slap_down_hard_into_hand_001_95477.mp3')
    paper_sound = pg.mixer.Sound('RockPaperScissors/Assets/zapsplat_foley_paper_sheets_x3_construction_sugar_set_down_on_surface_001_42007.mp3')
    scissors_sound = pg.mixer.Sound('RockPaperScissors/Assets/zapsplat_household_manicure_scissors_snip_001_41816.mp3')
    sounds = [rock_sound, paper_sound, scissors_sound]

COUNT = config.count
pg.mixer.set_num_channels(3 * COUNT)
ROCK, PAPER, SCISSORS = range(3)

def process_events():
    global teams
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                quit()
            elif event.key == pg.K_r:
                teams = restart()
            elif event.key == pg.K_SPACE:
                pause()
        # elif event.type == lay_crumb:
        #     for team in (rocks, papers, scissors):
        #         team.lay_crumbs()
        #         team.update_targets()

def pause():
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    quit()
                elif event.key == pg.K_SPACE:
                    return

def restart():
    rocks = Team([Player(ROCK, i) for i in range(COUNT)])
    papers = Team([Player(PAPER, i) for i in range(COUNT)])
    scissors = Team([Player(SCISSORS, i) for i in range(COUNT)])
    return rocks, papers, scissors

# def gameover():
    # wait 2 seconds
    # restart
    # clock.tick(2)
    # teams = restart()
teams = restart()
while True:
    process_events()
    SCREEN.fill(GREY)

    for team in teams:
        # construct quadtrees
        tree = QuadTree((w//2, h//2), w, h, 4)
        
        for s in team:
            if not tree.find(s.point):
                tree.insert(s.point, data=s)
                
            # try:
            #     tree.insert(s.point, data=s)
            # except:
                # s.point.x += 0.1
                # s.point.y += 0.1
                # tree.insert(s.point, data=s)

                # print("Recursion error (duplicate points)")
                # print(s.point)
                # points = tree.nearest_neighbors(s.point, count=2)
                # print(points)
                # print(points[0] == points[1])
                # pause()
                # quit()
        team.tree = tree
        # [team.tree.insert(s.rect.center, data=s) for s in team]

    # Collision
    collided = False
    # player, prey, predator
    for i, j, k in zip([0, 1, 2], [2, 0, 1], [1, 2, 0]):
        t1, t2, t3 = teams[i], teams[j], teams[k]

        # Update positions with respect to prey and predator
        t1.update(t2, t3)

        # Collision detection
        for sprite in t1:
            hit = sprite.collided(t2)
            if hit:
                t1.add(Player(sprite.type, len(t1), hit.pos + Vector2(0.01, 0.01)))
                sprite.play_sound()
                hit.kill()
            
                


        # collisions = pg.sprite.groupcollide(t1, t2, False, True, collided=t1.collide(t2))
        # for winner, hits in collisions.items():
        #     for hit in hits:
        #         t1.add(Player(winner.type, len(t1), 50, hit.pos))
        #         winner.play_sound()
        # if collisions:
        #     collided = True
            pass
        t1.draw(SCREEN)
    
    

    # Gameover - check if 2/3 teams are empty
    if collided:
        one_empty = False
        winning_team = None
        for team in teams:
            if len(team) == 0:
                if one_empty:
                    print(f"{winning_team} wins!")
                    print([len(t) for t in teams])
                    teams = restart()
                else:
                    one_empty = True
            else:
                winning_team = team

    pg.display.flip()
    clock.tick(120)
