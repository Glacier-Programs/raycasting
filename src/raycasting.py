'''
TODO:
- use proper ray casts instead of approximations
- add camera effects
- save chat data
- add start / end
- texture rendering
'''

# engine
import pygame as pg
from pygame.constants import SRCALPHA 
pg.init()

# math
from math import cos, sin, pi
from random import randint

# extras
from GUIPackage.functions import verifyTags

class Map:

    Empty = [[1, 2, 1, 2, 1],
             [2, 0, 0, 0, 2],
             [1, 0, 0, 0, 1],
             [2, 0, 0, 0, 2],
             [1, 2, 1, 2, 1]]
    
    WallInMiddle = [[1, 1, 1, 1, 3, 1],
                    [2, 0, 0, 0, 0, 1],
                    [1, 0, 2, 2, 0, 1],
                    [1, 0, 2, 2, 0, 1],
                    [1, 0, 0, 0, 0, 2],
                    [1, 3, 1, 1, 1, 1]]

    Test1 = [[1, 2, 1, 1, 1, 1, 1, 1],
             [1, 0, 0, 0, 0, 0, 0, 3],
             [1, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 2, 2, 0, 0, 1],
             [1, 0, 0, 2, 2, 0, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 1],
             [3, 0, 0, 0, 0, 0, 0, 1],
             [1, 1, 1, 1, 1, 1, 2, 1]]

    colMap = { 0: (255,255,255), 1 : (255,0,0), 2 : (0,255,0), 3 : (0,0,255) } # using a dictionary even tho a 

    def __init__(self, array : list[list[int]]) -> None:
        self.array = array
    
    @classmethod
    def RandomMap(self, size):
        array = []
        array.append([randint(1,3)])
        for _ in range(size):
            pass
    
    def spotAt(self, x : int, y : int) -> int:
        return self.array[int(y)][int(x)]

class Camera:
    defaultTags = {'applyShadows' : False, 'distanceFog' : False, 'lighting' : False, 'highlightIndividualBlocks' : False}
    def __init__(self, map : Map, rayCount : int = 200, fov : int = pi/4, rot : float = 0, pos : list[float] = [0,0], tags : dict[str:bool] = defaultTags) -> None:
        self.map = map
        self.rayCount = rayCount
        self.fov = fov
        self.rot = rot
        self.pos = pos
        self.tags = tags
        if not verifyTags(Camera, self):
            raise 'Invalid Tags'
    
    def shootRays(self) -> pg.Surface:
        surf = pg.Surface((800, 600))
        surfWidth = 800
        rayWidth = surfWidth / self.fov / self.rayCount
        for i in range( self.fov//self.rayCount ):
            # go from left of screen to right of screen
            angle = self.fov / self.rayCount * i + self.rot
            done = False
            steps = 0
            stepLength = .1
            while not done:
                done = self.map.spotAt( cos(angle)*steps*stepLength + self.pos[0] , sin(angle)*steps*stepLength + self.pos[1]) > 0 # cos is for x, sin is for y
                steps += 1
    
    def shootRaysOntoSurf(self, surf) -> None:
        surfSize = surf.get_size()
        self.rayCount = surfSize[0]
        rayWidth = surfSize[0] / self.rayCount
        for i in range( self.rayCount ):
            # go from left of screen to right of screen
            angle = self.fov / self.rayCount * i + self.rot
            done = False
            steps = 0
            stepLength = .1
            while not done:
                done = self.map.spotAt( cos(angle)*steps*stepLength + self.pos[0] , sin(angle)*steps*stepLength + self.pos[1]) > 0 # cos is for x, sin is for y
                steps += 1
            col = self.map.spotAt( cos(angle)*steps*stepLength + self.pos[0] , sin(angle)*steps*stepLength + self.pos[1])
            yOffSet = steps * 1
            pg.draw.rect(win, Map.colMap[col], pg.Rect( rayWidth*i, yOffSet, rayWidth, surfSize[1] - 2*yOffSet ) )
    
    def shootRaysProperDistanceOntoSurf(self, surf) -> None:
        surfSize = surf.get_size()
        self.rayCount, rc = surfSize[0]
        rayWidth = surfSize[0] / rc
        for ray in range(rc):
            # go from left to right of screen
            angle = self.fov / rc * ray + self.rot

    def applyForce(self, force : list[int]) -> None:
        self.pos[0] += force[0]
        if self.map.spotAt(self.pos[0], self.pos[1]) != 0: self.pos[0] -= force[0]
        self.pos[1] += force[1]
        if self.map.spotAt(self.pos[0], self.pos[1]) != 0: self.pos[1] -= force[1]

    def applyForceForward(self, force : list[int]) -> None:
        self.pos[0] += force[0] * cos(force[0])
        if self.map.spotAt(self.pos[0], self.pos[1]) != 0: self.pos[0] -= force[0]
        self.pos[1] += force[1] * sin(force[1])
        if self.map.spotAt(self.pos[0], self.pos[1]) != 0: self.pos[1] -= force[1]
    
    def applyRotation(self, rot : float) -> None:
        self.rot += rot

class MiniMap:
    def __init__(self, map : Map, cam : Camera, coords : list[int] = [0,0]) -> None:
        self.map = map
        self.cam = cam
        self.coords = coords
        self.sprite = pg.Surface((200, 200), pg.SRCALPHA)
        self.sprite.fill((122,122,122,122))
        self.camSprite = pg.Surface((20, 20))
        self.camSprite.fill((0,0,0))
        self.drawMap()
    
    def drawMap(self) -> None:
        map = self.map.array
        xsize = 200 / len(map[0])
        ysize = 200 / len(map)
        for y in range(len(map)):
            for x in range(len(map)):
                pg.draw.rect(self.sprite, Map.colMap[map[y][x]], pg.Rect(x * xsize, y * ysize, xsize, ysize))
    
    def Render(self, surf) -> None:
        surf.blit(self.sprite, self.coords)
        surf.blit(self.camSprite, [self.cam.pos[0]*200 / len(self.map.array[0]), self.cam.pos[1]*200 / len(self.map.array[0])] )

class DebugMenu:
    def __init__(self) -> None:
        pass

class TextInterpreter:
    def __init__(self) -> None:
        self.vars = {}
        self.line = ''
        self.font = pg.font.SysFont('arial', 35)
        self.sprite = pg.Surface((350, 45), SRCALPHA)
        self.sprite.fill((122, 122, 122, 122))
        self.coords = [5,550]
    
    def make(self) -> None:
        self.vars[self.line[1]] = self.line[2]

    def get(self) -> None:
        if self.line[1] == 'all':
            print(self.vars)
            return

    def set(self) -> None:
        self.vars[self.line[1]] = self.line[2]

    def store(self) -> None:
        self.vars[self.line[1]] = self.vars[self.line[2]]

    def store_global_reference(self, name : str, globalVar : object) -> None:
        self.vars[name] = globalVar
    
    def toggle(self) -> None:
        var = self.line[1]
        if var == 'cam' or var == 'camera' or var == 'player':
            if self.line[2] in self.vars['player'].tags:
                self.vars['player'].tags[self.line[2]] = not self.vars['player'].tags[self.line[2]]
                return

    def interpret(self) -> None:
        self.line = self.line.split(' ')
        if self.line[0] == 'make':
            self.make()
        elif self.line[0] == 'get':
            self.get()
        elif self.line[0] == 'set':
            pass
        elif self.line[0] == 'store':
            self.store()
        elif self.line[0] == 'toggle':
            self.toggle()
        print(self.line)
        self.line = ''
    
    def Render(self, surf : pg.Surface):
        surf.blit(self.sprite, self.coords)
        surf.blit(self.font.render(self.line, False, (255,255,255)), self.coords)

if __name__ == '__main__':
    win = pg.display.set_mode((800, 600))
    pg.display.set_caption('Ray Casting')
    clock = pg.time.Clock()
    
    curMap = Map(Map.Test1)
    player = Camera(curMap, pos=[1,1])
    playerSpeed = 0.01
    playerRotSpeed = 0.001 # 128 for full rotation

    minimap = MiniMap(curMap, player)
    showMap = True

    ti = TextInterpreter()
    writingTi = False
    
    ti.store_global_reference('minimap', minimap)
    ti.store_global_reference('player',  player)
    ti.store_global_reference('map',     curMap)

    while True:
        keys = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()
            elif event.type == pg.KEYDOWN:
                if not writingTi:
                    if event.unicode == 'p':
                        quit()
                    elif event.unicode == 'm':
                        showMap = not showMap
                    elif event.scancode == 40: # right enter
                        writingTi = not writingTi
                    elif event.scancode == 224: # left control
                        pass
                else:
                    if event.scancode != 40 and event.scancode != 42:
                        ti.line += event.unicode
                    elif event.scancode == 42: # backspace
                        ti.line = ti.line[:-1]
                    elif event.scancode == 40: # right enter
                        ti.interpret()
                        writingTi = not writingTi
        
        if not writingTi:
            force = [0,0]
            if keys[pg.K_w]:
                force[1] -= playerSpeed
            elif keys[pg.K_s]:
                force[1] += playerSpeed
            if keys[pg.K_a]:
                force[0] -= playerSpeed
            elif keys[pg.K_d]:
                force[0] += playerSpeed
            player.applyForce(force)

            mxmove = pg.mouse.get_pos()[0] - 400
            pg.mouse.set_pos((400, 300))
            player.applyRotation(mxmove * playerRotSpeed)

        win.fill((255,255,255))
        player.shootRaysOntoSurf(win)
        
        if showMap: minimap.Render(win)
        if writingTi: ti.Render(win)

        pg.display.flip()
        clock.tick(60)