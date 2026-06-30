import pygame
import random
#https://github.com/loanelly
pygame.init()
#https://github.com/loanelly
W, H, B = 850, 760, 30
PW, PH = 300, 660
TX, TY = (W - PW) // 2, H - PH - 20
F_X = pygame.font.SysFont('segoeui', 24)

SHAPES = {
    'S': [[(0,0), (1,0), (-1,1), (0,1)], [(0,0), (0,-1), (1,0), (1,1)]],
    'Z': [[(-1,0), (0,0), (0,1), (1,1)], [(1,-1), (1,0), (0,0), (0,1)]],
    'I': [[(-1,0), (0,0), (1,0), (2,0)], [(0,-1), (0,0), (0,1), (0,2)]],
    'O': [[(0,0), (1,0), (0,1), (1,1)]],
    'J': [[(-1,0), (0,0), (1,0), (-1,1)], [(0,-1), (0,0), (0,1), (1,1)], [(-1,0), (0,0), (1,0), (1,-1)], [(-1,-1), (0,-1), (0,0), (0,1)]],
    'L': [[(-1,0), (0,0), (1,0), (1,1)], [(-1,1), (0,1), (0,0), (0,-1)], [(-1,-1), (-1,0), (0,0), (1,0)], [(0,1), (0,0), (0,-1), (1,-1)]],
    'T': [[(-1,0), (0,0), (1,0), (0,1)], [(0,-1), (0,0), (0,1), (1,0)], [(-1,0), (0,0), (1,0), (0,-1)], [(-1,0), (0,0), (0,-1), (0,1)]]
}
COLORS = {k: c for k, c in zip(SHAPES.keys(), [(0,255,0), (255,0,0), (0,255,255), (255,255,0), (255,165,0), (0,0,255), (128,0,128)])}

class Piece:
    def __init__(self, name):
        self.name = name
        self.x, self.y, self.rotation, self.color = 5, 1, 0, COLORS[name]
    def pos(self):
        return [(self.x + dx, self.y + dy) for dx, dy in SHAPES[self.name][self.rotation % len(SHAPES[self.name])]]

def valid(p, locked, dx=0, dy=0, dr=0):
    p.x += dx; p.y += dy; p.rotation += dr
    ok = all(0 <= x < 10 and y < 22 and (x, y) not in locked for x, y in p.pos())
    p.x -= dx; p.y -= dy; p.rotation -= dr
    return ok

def clear_rows(locked):
    cl = [y for y in range(22) if sum(1 for x in range(10) if (x, y) in locked) == 10]
    for y in cl:
        for x in range(10): del locked[(x, y)]
        locked.update({(kx, ky + 1 if ky < y else ky): c for (kx, ky), c in locked.copy().items() if ky != y})
    return len(cl)

def draw_prev(surface, p, text, sx):
    surface.blit(F_X.render(text, True, (255,255,255)), (sx, TY + 85))
    if p: 
        for dx, dy in SHAPES[p.name][0]:
            pygame.draw.rect(surface, p.color, (sx + (dx+1)*B, TY + 140 + dy*B, B, B))

def main():
    win = pygame.display.set_mode((W, H))
    pygame.display.set_caption('Tetris ML Environment')
    
    locked, score, can_hold = {}, 0, True
    cur_p, nxt_p, hold_p = Piece(random.choice(list(SHAPES))), Piece(random.choice(list(SHAPES))), None
    clock = pygame.time.Clock()
    base_spd = 0.27
    fall_time = 0

    CTRLS = {
        pygame.K_LEFT: (-1,0,0), pygame.K_a: (-1,0,0),
        pygame.K_RIGHT: (1,0,0), pygame.K_d: (1,0,0),
        pygame.K_DOWN: (0,1,0),  pygame.K_s: (0,1,0),
        pygame.K_UP: (0,0,1),    pygame.K_w: (0,0,1)
    }

    while True:
        fall_time += clock.tick()
        if fall_time / 1000 >= base_spd:
            fall_time = 0
            if valid(cur_p, locked, dy=1): 
                cur_p.y += 1
            else:
                for pos in cur_p.pos(): locked[pos] = cur_p.color
                score += clear_rows(locked) * 10
                cur_p, nxt_p, can_hold = nxt_p, Piece(random.choice(list(SHAPES))), True
                
                if not valid(cur_p, locked):
                    locked.clear()
                    score = 0
                    can_hold = True
                    cur_p = Piece(random.choice(list(SHAPES)))
                    nxt_p = Piece(random.choice(list(SHAPES)))
                    hold_p = None

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); return
            if e.type == pygame.KEYDOWN:
                if e.key in CTRLS:
                    dx, dy, dr = CTRLS[e.key]
                    if valid(cur_p, locked, dx, dy, dr):
                        cur_p.x += dx; cur_p.y += dy; cur_p.rotation += dr
                elif e.key == pygame.K_c and can_hold:
                    if hold_p is None:
                        hold_p = Piece(cur_p.name)
                        cur_p = nxt_p
                        nxt_p = Piece(random.choice(list(SHAPES)))
                    else:
                        hold_p, cur_p = Piece(cur_p.name), Piece(hold_p.name)
                    can_hold = False

        win.fill((15, 15, 18))
        for i in range(1, 22): pygame.draw.line(win, (40,40,40), (TX, TY + i*B), (TX + PW, TY + i*B))
        for j in range(1, 10): pygame.draw.line(win, (40,40,40), (TX + j*B, TY), (TX + j*B, TY + PH))
        for (x, y), c in locked.items(): pygame.draw.rect(win, c, (TX + x*B, TY + y*B, B, B))
        for x, y in cur_p.pos(): pygame.draw.rect(win, cur_p.color, (TX + x*B, TY + y*B, B, B))
        pygame.draw.rect(win, (220, 50, 50), (TX, TY, PW, PH), 3)

        win.blit(F_X.render(f'Score: {score}', True, (255,255,255)), (TX + PW + 50, TY + 40))
        draw_prev(win, nxt_p, 'Next Piece:', TX + PW + 50)
        draw_prev(win, hold_p, 'Hold (C):', TX - 180)
        pygame.display.update()

if __name__ == "__main__":
    main()
