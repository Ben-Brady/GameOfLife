import numpy as np
import cv2
import argparse
from functools import lru_cache

parser = argparse.ArgumentParser()

parser.add_argument("-s","--size",    type=int, default=20, help="The Width/Height of the grid")
parser.add_argument("-g","--boxsize",type=int, default=10, help="The Size for each position on the grid")
args = parser.parse_args()


boundX,boundY = BOUNDS = (args.size,args.size)
pSIZE = args.boxsize
OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
State = {(x, y):False for x in range(BOUNDS[0]) for y in range(BOUNDS[1])}
BlankState = State.copy()

out = cv2.VideoWriter('playback.avi',cv2.VideoWriter_fourcc(*'XVID'), 20.0, (BOUNDS[0]*4,BOUNDS[1]*4))

def Show(State):
    SIZE = np.array(BOUNDS) * pSIZE
    img = np.zeros((*SIZE,3),dtype=np.uint8)
    Positions = [(x,y) for x in range(BOUNDS[0]) for y in range(BOUNDS[1]) if State[(x,y)]]
    
    for x,y in Positions:
        v = State[x,y] * 255
        img = cv2.rectangle(img,(x*pSIZE,y*pSIZE),((x+1)*pSIZE,(y+1)*pSIZE),(v,v,v),-1)
    
    x,y = Cursor
    img = cv2.rectangle(img,(x*pSIZE,y*pSIZE),((x+1)*pSIZE,(y+1)*pSIZE),(0,0,255),pSIZE//6,cv2.LINE_8)

    out.write(img)
    cv2.imshow("Conway's Game of Life",img)

@lru_cache(maxsize=None)
def _EvalNeighbours(Neighbours:int,alive:bool) -> bool:
    if Neighbours == 3 and not alive:
        return True # Revived
    elif Neighbours not in (2,3):
        return False # Overpopulation/Loneliness
    else:
        return alive

def Evaluate(xy:tuple) -> bool:
    Neighbours = 0
    for Neighbour in GetNeighbours(xy):
        Neighbours += State.get(Neighbour,False)
    
    return _EvalNeighbours(Neighbours,State[xy])

@lru_cache(maxsize=None)
def GetNeighbours(xy):
    Neighbours = []
    for x,y in OFFSETS:
        Neighbour = (xy[0]+x,xy[1]+y)
        if Neighbour in State:
            Neighbours.append(Neighbour)
    
    return Neighbours

def Update(State):
    Next = State.copy()
    toEvaluate = set()
    
    for pos in State:
        if State.get(pos,True):
            toEvaluate.add(pos)
            for neighbour in GetNeighbours(pos):
                toEvaluate.add(neighbour)
    for pos in toEvaluate:
        Next[pos] = Evaluate(pos)
    
    return Next



KeyCodes = {
    ord('w'):(0,-1),
    ord('a'):(-1,0),
    ord('d'):(1,0),
    ord('s'):(0,1)
}
while True:
    Cursor = (0,0)
    while True:
        Show(State)
        key = cv2.waitKey(0) & 0xFF
        if key in KeyCodes:
            offset = KeyCodes[key]
            Cursor = (max(min(boundX-1,Cursor[0] + offset[0]),0),
                      max(min(boundY-1,Cursor[1] + offset[1]),0))
        elif key == ord(' '):
            State[Cursor] = not State[Cursor]
        elif key == ord('c'):
            Cursor = (-2,-2)
            break
        elif key == ord('r'):
            State = BlankState.copy()
        elif key == ord('q'):
            out.release()
            quit()


    Previous = [0 for x in range(5)]
    while State not in Previous and cv2.waitKey(1000//30) & 0xFF != ord('q'):
        Previous.append(State)
        Previous.pop(0)
        State = Update(State)
        Show(State)
