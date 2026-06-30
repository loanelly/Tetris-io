import pygame, random, math, array
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init(); pygame.font.init()

W, H, B = 850, 760, 30
PW, PH = 300, 660
TX, TY = (W - PW) // 2, H - PH - 20
F_T = pygame.font.SysFont('segoeui', 60, bold=True)
F_M = pygame.font.SysFont('segoeui', 32, bold=True)
F_X = pygame.font.SysFont('segoeui', 24)

# Глобальные настройки звука
music_on = True
sfx_on = True
bg_channel = pygame.mixer.Channel(0)

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

def clear_rows(win, locked):
    cl = [y for y in range(22) if sum(1 for x in range(10) if (x, y) in locked) == 10]
    if cl:
        if sfx_on:
            buf = array.array('h', [int(random.uniform(-1,1)*math.exp(-5*(i/44100))*9830) for i in range(17640)])
            pygame.mixer.Sound(buffer=buf).play()
        for _ in range(2):
            for y in cl: [pygame.draw.rect(win, (255,255,255), (TX + x*B, TY + y*B, B, B)) for x in range(10)]
            pygame.display.update(); pygame.time.delay(40)
        for y in cl:
            for x in range(10): del locked[(x, y)]
            locked.update({(kx, ky + 1 if ky < y else ky): c for (kx, ky), c in locked.copy().items() if ky != y})
    return len(cl)

def draw_prev(surface, p, text, sx):
    surface.blit(F_X.render(text, True, (255,255,255)), (sx, TY + 85))
    if p: [pygame.draw.rect(surface, p.color, (sx + (dx+1)*B, TY + 140 + dy*B, B, B)) for dx, dy in SHAPES[p.name][0]]

def run_menu(win):
    items, sel = ["1. Classic Mode", "2. Speed Up Mode", "3. Settings", "4. Controls Info", "5. Exit"], 0
    while True:
        win.fill((15, 15, 18))
        title = F_T.render("TETRIS MENU", True, (255, 255, 255))
        win.blit(title, (W // 2 - title.get_width() // 2, H // 4 - 50))
        
        for idx, item in enumerate(items):
            color = (220, 50, 50) if idx == sel else (180, 180, 180)
            text = F_M.render(item, True, color)
            # ИСПРАВЛЕНО: Центрирование по ширине экрана
            win.blit(text, (W // 2 - text.get_width() // 2, H // 2 - 30 + idx * 50))
            
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "exit"
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_UP, pygame.K_w]: sel = (sel - 1) % len(items)
                if e.key in [pygame.K_DOWN, pygame.K_s]: sel = (sel + 1) % len(items)
                if e.key in [pygame.K_RETURN, pygame.K_SPACE]: 
                    return ["classic", "speedup", "settings", "controls", "exit"][sel]

def run_settings(win):
    global music_on, sfx_on
    sel = 0
    while True:
        win.fill((15, 15, 18))
        title = F_T.render("SETTINGS", True, (255, 255, 255))
        win.blit(title, (W // 2 - title.get_width() // 2, H // 4 - 50))
        
        items = [
            f"Music: {'ON' if music_on else 'OFF'}",
            f"Sound Effects: {'ON' if sfx_on else 'OFF'}",
            "Back to Menu"
        ]
        
        for idx, item in enumerate(items):
            color = (220, 50, 50) if idx == sel else (180, 180, 180)
            text = F_M.render(item, True, color)
            win.blit(text, (W // 2 - text.get_width() // 2, H // 2 + idx * 50))
            
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "exit"
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_UP, pygame.K_w]: sel = (sel - 1) % len(items)
                if e.key in [pygame.K_DOWN, pygame.K_s]: sel = (sel + 1) % len(items)
                if e.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d]:
                    if sel == 0: music_on = not music_on
                    elif sel == 1: sfx_on = not sfx_on
                    elif sel == 2: return "menu"

def show_controls(win):
    lines = ["CONTROLS INFO", "", "Move: A / D or Arrows", "Drop: S or Down Arrow", "Rotate: W or Up Arrow", "Hold Piece: C", "", "Press any key to return..."]
    while True:
        win.fill((15, 15, 18))
        for idx, l in enumerate(lines):
            font = F_T if idx == 0 else F_X
            color = (220, 50, 50) if idx == 0 else (255, 255, 255)
            text = font.render(l, True, color)
            win.blit(text, (W // 2 - text.get_width() // 2, H // 4 + idx * 40))
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "exit"
            if e.type == pygame.KEYDOWN: return "menu"

def run_game(win, mode):
    locked, score, run, can_p = {}, 0, True, True
    cur_p, nxt_p, hold_p = Piece(random.choice(list(SHAPES))), Piece(random.choice(list(SHAPES))), None
    clock = pygame.time.Clock()
    fall_time, base_spd = 0, 0.27
    
    # Генерация и запуск музыки при условии, что она включена
    if music_on:
        notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00]
        buf = array.array('h')
        for n in notes:
            for i in range(11025): buf.append(int(math.sin(2 * math.pi * n * (i / 44100)) * 1638))
        sound_bg = pygame.mixer.Sound(buffer=buf)
        bg_channel.play(sound_bg, loops=-1)

    CTRLS = {pygame.K_LEFT:(-1,0,0), pygame.K_a:(-1,0,0), pygame.K_RIGHT:(1,0,0), pygame.K_d:(1,0,0), pygame.K_DOWN:(0,1,0), pygame.K_s:(0,1,0), pygame.K_UP:(0,0,1), pygame.K_w:(0,0,1)}

    while run:
        spd = max(0.05, base_spd * (0.9 ** (score // 50))) if mode == "speedup" else base_spd
        fall_time += clock.tick()
        if fall_time / 1000 >= spd:
            fall_time = 0
            if valid(cur_p, locked, dy=1): cur_p.y += 1
            else:
                for pos in cur_p.pos(): locked[pos] = cur_p.color
                score += clear_rows(win, locked) * 10
                cur_p, nxt_p, can_p = nxt_p, Piece(random.choice(list(SHAPES))), True
                if not valid(cur_p, locked): run = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); return "exit"
            if e.type == pygame.KEYDOWN:
                if e.key in CTRLS:
                    dx, dy, dr = CTRLS[e.key]
                    if valid(cur_p, locked, dx, dy, dr):
                        cur_p.x += dx; cur_p.y += dy; cur_p.rotation += dr
                elif e.key == pygame.K_c and can_p:
                    hold_p, cur_p, can_p = Piece(cur_p.name), hold_p or Piece(random.choice(list(SHAPES))), False

        win.fill((15, 15, 18))
        for i in range(1, 22): pygame.draw.line(win, (40,40,40), (TX, TY + i*B), (TX + PW, TY + i*B))
        for j in range(1, 10): pygame.draw.line(win, (40,40,40), (TX + j*B, TY), (TX + j*B, TY + PH))
        for (x, y), c in locked.items(): pygame.draw.rect(win, c, (TX + x*B, TY + y*B, B, B))
        for x, y in cur_p.pos(): pygame.draw.rect(win, cur_p.color, (TX + x*B, TY + y*B, B, B))
        pygame.draw.rect(win, (220, 50, 50), (TX, TY, PW, PH), 3)

        title_game = F_T.render('TETRIS', True, (255,255,255))
        win.blit(title_game, (TX + (PW // 2) - (title_game.get_width() // 2), 10))
        
        win.blit(F_X.render(f'Score: {score}', True, (255,255,255)), (TX + PW + 50, TY + 40))
        draw_prev(win, nxt_p, 'Next Piece:', TX + PW + 50)
        draw_prev(win, hold_p, 'Hold (C):', TX - 180)
        pygame.display.update()

    bg_channel.stop()
    win.fill((15, 15, 18))
    t_over = F_T.render("GAME OVER", True, (220, 50, 50))
    t_score = F_M.render(f"Final Score: {score}", True, (255, 255, 255))
    t_ret = pygame.font.SysFont('segoeui', 20, italic=True).render("Returning to main menu...", True, (120, 120, 120))
    
    win.blit(t_over, (W // 2 - t_over.get_width() // 2, H // 2 - 80))
    win.blit(t_score, (W // 2 - t_score.get_width() // 2, H // 2 + 10))
    win.blit(t_ret, (W // 2 - t_ret.get_width() // 2, H // 2 + 70))
    
    pygame.display.update(); pygame.time.delay(4000)
    return "menu"

def main():
    win = pygame.display.set_mode((W, H))
    pygame.display.set_caption('Tetris-io')
    st = "menu"
    while st != "exit":
        if st == "menu": st = run_menu(win)
        elif st == "settings": st = run_settings(win)
        elif st == "controls": st = show_controls(win)
        elif st in ["classic", "speedup"]: st = run_game(win, st)
    pygame.quit()

if __name__ == "__main__": main()
