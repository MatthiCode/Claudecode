#!/usr/bin/env python3
"""TERRE PERDUE - un jeu solo de survie / exploration en ASCII.

Ton avion s'est écrasé sur une île inconnue. Survis, explore, trouve une
batterie dans les ruines et rapporte-la à la balise radio (R) pour appeler
les secours.

Lancer :  python3 terre_perdue.py [graine]
"""
import curses
import math
import random
import sys

W, H = 140, 70
DAY = 240          # durée d'un jour en tours
NIGHT_START = 150  # le soir tombe

WATER, SAND, GRASS, FOREST, MOUNT, SWAMP = "~", ".", '"', "T", "^", "%"
WALKABLE = {SAND, GRASS, MOUNT, SWAMP}


# --------------------------------------------------------------- génération
def make_noise(rng, scale):
    gw, gh = W // scale + 3, H // scale + 3
    g = [[rng.random() for _ in range(gw)] for _ in range(gh)]

    def f(x, y):
        fx, fy = x / scale, y / scale
        x0, y0 = int(fx), int(fy)
        tx, ty = fx - x0, fy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = g[y0][x0] * (1 - tx) + g[y0][x0 + 1] * tx
        b = g[y0 + 1][x0] * (1 - tx) + g[y0 + 1][x0 + 1] * tx
        return a * (1 - ty) + b * ty
    return f


def gen_world(rng):
    e1, e2, e3 = make_noise(rng, 24), make_noise(rng, 11), make_noise(rng, 5)
    m1, m2 = make_noise(rng, 18), make_noise(rng, 7)
    tiles = [[WATER] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            # île : on baisse l'altitude vers les bords
            d = math.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2))
            e = 0.55 * e1(x, y) + 0.3 * e2(x, y) + 0.15 * e3(x, y) - d * 0.45 + 0.18
            m = 0.65 * m1(x, y) + 0.35 * m2(x, y)
            if e < 0.30:
                t = WATER
            elif e < 0.35:
                t = SAND
            elif e > 0.62:
                t = MOUNT
            elif m > 0.62 and e < 0.45:
                t = SWAMP
            elif m > 0.5:
                t = FOREST
            else:
                t = GRASS
            tiles[y][x] = t
    return tiles


class Game:
    def __init__(self, seed=None):
        self.seed = seed if seed is not None else random.randrange(10 ** 6)
        self.rng = random.Random(self.seed)
        self.tiles = gen_world(self.rng)
        self.objs = {}      # (x,y) -> {"k": kind, ...}
        self.struct = {}    # (x,y) -> {"k": "fire"/"shelter", "ttl": n}
        self.mobs = []
        self.seen = set()
        self.log = []
        self.turn = 0
        self.over = None    # "win" / "dead"
        self.cause = ""
        self.place_player()
        self.populate()
        self.msg("Tu t'éveilles sur une plage, près de l'épave. Il faut survivre.")
        self.msg("Cherche une BATTERIE dans les ruines (&) et rapporte-la à la balise (R).")
        self.reveal()

    # ----------------------------------------------------------- mise en place
    def land(self, x, y, kinds=(SAND, GRASS, FOREST, MOUNT, SWAMP)):
        return 0 <= x < W and 0 <= y < H and self.tiles[y][x] in kinds

    def place_player(self):
        pts = [(x, y) for y in range(H) for x in range(W) if self.tiles[y][x] == SAND]
        # plage proche d'un bord, côté ouest de préférence
        pts.sort(key=lambda p: p[0])
        self.px, self.py = pts[self.rng.randrange(min(40, len(pts)))]
        self.start = (self.px, self.py)
        self.hp, self.food, self.water, self.energy, self.warm = 100, 80, 80, 90, 80
        self.inv = {"bois": 0, "pierre": 0, "baies": 0, "viande crue": 0,
                    "viande cuite": 0, "lance": 0, "hache": 0, "batterie": 0}

    def free_land(self, minDist=0, kinds=(SAND, GRASS, FOREST, MOUNT, SWAMP)):
        for _ in range(5000):
            x, y = self.rng.randrange(W), self.rng.randrange(H)
            if self.land(x, y, kinds) and (x, y) not in self.objs and \
                    math.hypot(x - self.px, y - self.py) >= minDist:
                return x, y
        return self.px, self.py

    def populate(self):
        rng = self.rng
        for y in range(H):
            for x in range(W):
                t = self.tiles[y][x]
                r = rng.random()
                if t == GRASS and r < 0.035:
                    self.objs[(x, y)] = {"k": "bush", "n": 2}
                elif t == MOUNT and r < 0.12:
                    self.objs[(x, y)] = {"k": "rock", "n": 3}
                elif t == FOREST:
                    self.objs[(x, y)] = {"k": "tree", "n": 3}
        # ruines : une contient la batterie, la balise est loin
        far = lambda: self.free_land(45, (GRASS, SAND, MOUNT))
        rx, ry = self.free_land(55, (GRASS, MOUNT))
        self.objs[(rx, ry)] = {"k": "radio"}
        self.radio = (rx, ry)
        self.tiles[ry][rx] = MOUNT
        self.ruins = []
        for i in range(7):
            p = self.free_land(12, (GRASS, SAND, MOUNT))
            self.objs[p] = {"k": "ruin", "loot": "batterie" if i == 0 else None}
            self.ruins.append(p)
        for _ in range(55):
            p = self.free_land(5, (GRASS, FOREST, SAND))
            self.mobs.append({"k": "lapin", "x": p[0], "y": p[1], "hp": 3})
        for _ in range(10):
            p = self.free_land(25, (GRASS, FOREST, MOUNT))
            self.mobs.append({"k": "loup", "x": p[0], "y": p[1], "hp": 22, "home": p})

    # ------------------------------------------------------------------ utilitaires
    def msg(self, s):
        self.log.append(s)
        self.log = self.log[-60:]

    def is_night(self):
        return (self.turn % DAY) >= NIGHT_START

    def day_no(self):
        return self.turn // DAY + 1

    def vis_radius(self):
        return 5 if self.is_night() else 10

    def light_sources(self):
        return [p for p, s in self.struct.items() if s["k"] == "fire"]

    def near_fire(self, r=2):
        return any(abs(fx - self.px) <= r and abs(fy - self.py) <= r
                   for fx, fy in self.light_sources())

    def on_shelter(self):
        return self.struct.get((self.px, self.py), {}).get("k") == "shelter"

    def reveal(self):
        r = self.vis_radius()
        for y in range(max(0, self.py - r), min(H, self.py + r + 1)):
            for x in range(max(0, self.px - r), min(W, self.px + r + 1)):
                if (x - self.px) ** 2 + (y - self.py) ** 2 <= r * r:
                    self.seen.add((x, y))
        for fx, fy in self.light_sources():
            for y in range(fy - 4, fy + 5):
                for x in range(fx - 4, fx + 5):
                    if 0 <= x < W and 0 <= y < H and (x - fx) ** 2 + (y - fy) ** 2 <= 16:
                        self.seen.add((x, y))

    def visible(self, x, y):
        if (x - self.px) ** 2 + (y - self.py) ** 2 <= self.vis_radius() ** 2:
            return True
        return any((x - fx) ** 2 + (y - fy) ** 2 <= 16 for fx, fy in self.light_sources())

    def mob_at(self, x, y):
        for m in self.mobs:
            if m["x"] == x and m["y"] == y:
                return m
        return None

    def hurt(self, n, cause):
        self.hp -= n
        if self.hp <= 0 and not self.over:
            self.over, self.cause = "dead", cause

    # ------------------------------------------------------------------ actions
    def move(self, dx, dy):
        if self.over:
            return
        nx, ny = self.px + dx, self.py + dy
        if not (0 <= nx < W and 0 <= ny < H):
            return
        m = self.mob_at(nx, ny)
        if m:
            self.attack(m)
            return self.tick()
        o = self.objs.get((nx, ny))
        t = self.tiles[ny][nx]
        if o:
            k = o["k"]
            if k == "tree":
                n = 2 if self.inv["hache"] else 1
                self.inv["bois"] += n
                o["n"] -= 1
                self.energy -= 2
                self.msg(f"Tu coupes du bois (+{n}).")
                if o["n"] <= 0:
                    del self.objs[(nx, ny)]
                    self.tiles[ny][nx] = GRASS
                    self.msg("L'arbre est épuisé.")
                return self.tick()
            if k == "rock":
                self.inv["pierre"] += 1
                o["n"] -= 1
                self.energy -= 2
                self.msg("Tu ramasses une pierre (+1).")
                if o["n"] <= 0:
                    del self.objs[(nx, ny)]
                return self.tick()
            if k == "bush":
                if o["n"] > 0:
                    g = self.rng.randint(1, 3)
                    self.inv["baies"] += g
                    o["n"] -= 1
                    self.msg(f"Tu cueilles {g} baies.")
                else:
                    self.msg("Ce buisson est vide.")
                return self.tick()
            if k == "ruin":
                if o.get("done"):
                    self.msg("Tu as déjà fouillé ces ruines.")
                else:
                    o["done"] = True
                    self.search(o)
                return self.tick()
            if k == "radio":
                if self.inv["batterie"]:
                    self.over = "win"
                    self.msg("Tu branches la batterie... la radio crépite : SOS envoyé !")
                else:
                    self.msg("La balise radio est morte. Il lui faut une BATTERIE.")
                return self.tick()
        if t == WATER:
            self.water = min(100, self.water + 30)
            self.msg("Tu bois de l'eau. (Elle est un peu saumâtre...)")
            if self.rng.random() < 0.08:
                self.hurt(4, "Une eau douteuse t'a rendu malade.")
                self.msg("Aïe, mal au ventre.")
            return self.tick()
        # déplacement
        self.px, self.py = nx, ny
        cost = {MOUNT: 1.2, SWAMP: 0.8, FOREST: 0.4}.get(t, 0.2)
        self.energy -= cost
        if t == SWAMP and self.rng.random() < 0.04:
            self.hurt(3, "Piqûres d'insectes du marais.")
            self.msg("Des insectes du marais te piquent.")
        self.tick()

    def search(self, ruin):
        if ruin.get("loot") == "batterie":
            self.inv["batterie"] += 1
            self.msg("*** Tu trouves une BATTERIE en état de marche ! ***")
            self.msg("Direction la balise radio (R). Touche 'm' pour la carte.")
            return
        r = self.rng.random()
        if r < 0.4:
            self.inv["pierre"] += 2
            self.msg("Des gravats : +2 pierres.")
        elif r < 0.7:
            self.inv["baies"] += 4
            self.msg("Des rations moisies mais mangeables : +4 baies.")
        elif r < 0.85:
            self.inv["viande cuite"] += 1
            self.msg("Une boîte de conserve ! (+1 viande cuite)")
        else:
            self.msg("Rien d'utile.")
        if self.rng.random() < 0.35 and self.radio:
            self.msg("Un vieux plan indique la balise radio vers " + self.radio_dir() + ".")

    def radio_dir(self):
        dx, dy = self.radio[0] - self.px, self.radio[1] - self.py
        ns = "nord" if dy < -4 else "sud" if dy > 4 else ""
        ew = "ouest" if dx < -4 else "est" if dx > 4 else ""
        return (ns + "-" + ew).strip("-") or "tout près"

    def attack(self, m):
        dmg = self.rng.randint(4, 7) + (9 if self.inv["lance"] else 0)
        m["hp"] -= dmg
        self.energy -= 1
        if m["hp"] <= 0:
            self.mobs.remove(m)
            if m["k"] == "lapin":
                self.inv["viande crue"] += 1
                self.msg("Tu tues un lapin. (+1 viande crue)")
            else:
                self.inv["viande crue"] += 2
                self.msg("Tu abats le loup ! (+2 viande crue)")
        else:
            self.msg(f"Tu frappes {m['k']} ({dmg}).")

    def eat(self):
        if self.over:
            return
        for k, v in (("viande cuite", 40), ("baies", 12), ("viande crue", 25)):
            if self.inv[k] > 0:
                self.inv[k] -= 1
                self.food = min(100, self.food + v)
                if k == "viande crue" and self.rng.random() < 0.5:
                    self.hurt(8, "Intoxication à la viande crue.")
                    self.msg("Tu manges de la viande crue... mauvaise idée (-8 PV).")
                else:
                    self.msg(f"Tu manges ({k}) +{v} faim.")
                return self.tick()
        self.msg("Tu n'as rien à manger.")

    RECIPES = {
        "1": ("Feu de camp", {"bois": 3}, "fire"),
        "2": ("Abri", {"bois": 8}, "shelter"),
        "3": ("Lance", {"bois": 1, "pierre": 2}, "lance"),
        "4": ("Hache", {"bois": 2, "pierre": 3}, "hache"),
        "5": ("Cuire la viande (près d'un feu)", {"viande crue": 1}, "cook"),
    }

    def craft(self, key):
        if self.over or key not in self.RECIPES:
            return
        name, cost, what = self.RECIPES[key]
        if any(self.inv[k] < v for k, v in cost.items()):
            self.msg("Il te manque des ressources : " +
                     ", ".join(f"{v} {k}" for k, v in cost.items()))
            return
        if what in ("fire", "shelter") and ((self.px, self.py) in self.struct):
            self.msg("Il y a déjà une construction ici.")
            return
        if what in ("lance", "hache") and self.inv[what]:
            self.msg("Tu l'as déjà.")
            return
        if what == "cook" and not self.near_fire(1):
            self.msg("Il faut être juste à côté d'un feu.")
            return
        for k, v in cost.items():
            self.inv[k] -= v
        if what == "fire":
            self.struct[(self.px, self.py)] = {"k": "fire", "ttl": 300}
            self.msg("Tu allumes un feu de camp. Il tiendra un moment.")
        elif what == "shelter":
            self.struct[(self.px, self.py)] = {"k": "shelter", "ttl": 99999}
            self.msg("Tu bâtis un abri. Bon pour dormir.")
        elif what == "cook":
            self.inv["viande cuite"] += 1
            self.msg("Tu cuis la viande. Délicieux.")
        else:
            self.inv[what] = 1
            self.msg(f"Tu fabriques : {name}.")
        self.tick()

    def rest(self):
        """Repos : jusqu'à 12 tours, interrompu par un danger."""
        if self.over:
            return
        for _ in range(12):
            before = self.hp
            self.energy = min(100, self.energy + (3.5 if self.on_shelter() else 1.6))
            self.tick(resting=True)
            if self.over or self.hp < before or any(
                    m["k"] == "loup" and abs(m["x"] - self.px) + abs(m["y"] - self.py) < 6
                    for m in self.mobs):
                self.msg("Tu es interrompu !")
                break

    # ------------------------------------------------------------------ monde vivant
    def tick(self, resting=False):
        if self.over:
            return
        self.turn += 1
        k = 0.6 if resting else 1.0
        self.food -= 0.30 * k
        self.water -= 0.42 * k
        if self.energy < 0:
            self.energy = 0
        self.energy = max(0, self.energy - 0.05)
        # chaleur
        if self.near_fire(2) or self.on_shelter():
            self.warm = min(100, self.warm + 3)
        elif self.is_night():
            self.warm -= 0.9
        else:
            self.warm = min(100, self.warm + 0.4)
        # états
        if self.food <= 0:
            self.food = 0
            self.hurt(1, "Mort de faim.")
        if self.water <= 0:
            self.water = 0
            self.hurt(1.5, "Mort de soif.")
        if self.warm <= 0:
            self.warm = 0
            self.hurt(1, "Mort de froid.")
        if self.energy <= 0:
            self.hurt(0.5, "Épuisement total.")
        elif self.food > 30 and self.water > 30 and self.warm > 30 and self.hp < 100:
            self.hp = min(100, self.hp + 0.25)
        # avertissements
        if self.turn % 25 == 0:
            for v, txt in ((self.food, "Tu as faim."), (self.water, "Tu as soif."),
                           (self.warm, "Tu grelottes."), (self.energy, "Tu es épuisé.")):
                if v < 25:
                    self.msg(txt)
        if self.turn % DAY == NIGHT_START:
            self.msg("La nuit tombe... les loups rôdent. Allume un feu !")
        if self.turn % DAY == 0:
            self.msg(f"Jour {self.day_no()} : le soleil se lève.")
        # structures
        for p in list(self.struct):
            s = self.struct[p]
            s["ttl"] -= 1
            if s["ttl"] <= 0:
                del self.struct[p]
                self.msg("Un feu s'est éteint.")
        # repousse
        if self.turn % 120 == 0:
            for o in self.objs.values():
                if o["k"] == "bush" and o["n"] < 2:
                    o["n"] += 1
        self.move_mobs()
        self.reveal()

    def move_mobs(self):
        rng = self.rng
        night = self.is_night()
        for m in list(self.mobs):
            d = abs(m["x"] - self.px) + abs(m["y"] - self.py)
            if m["k"] == "lapin":
                if d < 5:     # fuit
                    dx = (m["x"] > self.px) - (m["x"] < self.px)
                    dy = (m["y"] > self.py) - (m["y"] < self.py)
                    step = (dx, 0) if rng.random() < 0.5 else (0, dy)
                elif rng.random() < 0.3:
                    step = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                else:
                    continue
                self.try_move(m, *step)
            else:
                aggro = 9 if night else 5
                if d <= aggro:
                    sx = (self.px > m["x"]) - (self.px < m["x"])
                    sy = (self.py > m["y"]) - (self.py < m["y"])
                    if d == 1:
                        if rng.random() < 0.7:
                            dmg = rng.randint(5, 10)
                            self.msg(f"Un loup te mord ! (-{dmg})")
                            self.hurt(dmg, "Dévoré par un loup.")
                        continue
                    # le feu les effraie
                    nx, ny = m["x"] + (sx if rng.random() < 0.5 else 0), m["y"] + (sy if True else 0)
                    if rng.random() < 0.5:
                        nx, ny = m["x"] + sx, m["y"]
                    if any(abs(nx - fx) <= 2 and abs(ny - fy) <= 2 for fx, fy in self.light_sources()):
                        continue
                    self.try_move(m, nx - m["x"], ny - m["y"])
                elif rng.random() < 0.2:
                    self.try_move(m, *rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]))
        # apparition de loups la nuit
        if night and self.turn % 20 == 0 and sum(1 for m in self.mobs if m["k"] == "loup") < 14:
            for _ in range(20):
                a = rng.random() * 6.283
                x, y = int(self.px + math.cos(a) * 14), int(self.py + math.sin(a) * 14)
                if self.land(x, y, (GRASS, FOREST, SAND)) and not self.mob_at(x, y):
                    self.mobs.append({"k": "loup", "x": x, "y": y, "hp": 22})
                    break

    def try_move(self, m, dx, dy):
        nx, ny = m["x"] + dx, m["y"] + dy
        if (dx or dy) and self.land(nx, ny, (SAND, GRASS, MOUNT, SWAMP)) \
                and (nx, ny) not in self.objs and not self.mob_at(nx, ny) \
                and (nx, ny) != (self.px, self.py):
            m["x"], m["y"] = nx, ny


# ---------------------------------------------------------------------- affichage
GLYPH = {WATER: ("~", 4), SAND: (".", 3), GRASS: ('"', 2), FOREST: ("T", 2),
         MOUNT: ("^", 7), SWAMP: ("%", 5)}


def bar(v, n=12):
    k = int(max(0, min(100, v)) / 100 * n + 0.5)
    return "[" + "#" * k + "-" * (n - k) + "]"


def tile_char(g, x, y):
    """(caractère, couleur, dim) d'une case"""
    vis = g.visible(x, y)
    if (x, y) == (g.px, g.py):
        return "@", 6, curses.A_BOLD
    dim = 0 if vis else curses.A_DIM
    if vis:
        m = g.mob_at(x, y)
        if m:
            return ("r", 7, curses.A_BOLD) if m["k"] == "lapin" else ("W", 1, curses.A_BOLD)
    s = g.struct.get((x, y))
    if s:
        return ("*", 1, curses.A_BOLD) if s["k"] == "fire" else ("H", 3, curses.A_BOLD)
    o = g.objs.get((x, y))
    if o:
        k = o["k"]
        if k == "tree":
            return "T", 2, dim
        if k == "bush":
            return ("b" if o["n"] > 0 else ","), 5, dim
        if k == "rock":
            return "o", 7, dim
        if k == "ruin":
            return "&", 3, dim | curses.A_BOLD
        if k == "radio":
            return "R", 1, dim | curses.A_BOLD
    ch, col = GLYPH[g.tiles[y][x]]
    return ch, col, dim


def draw(scr, g, mode="play"):
    scr.erase()
    sh, sw = scr.getmaxyx()
    side = 30
    vw, vh = max(10, sw - side - 1), max(8, sh - 8)
    ox, oy = g.px - vw // 2, g.py - vh // 2
    for sy in range(vh):
        for sx in range(vw):
            x, y = ox + sx, oy + sy
            if not (0 <= x < W and 0 <= y < H) or (x, y) not in g.seen:
                continue
            ch, col, at = tile_char(g, x, y)
            try:
                scr.addch(sy, sx, ch, curses.color_pair(col) | at)
            except curses.error:
                pass
    # panneau latéral
    X = vw + 2
    night = g.is_night()
    t = g.turn % DAY
    lines = [
        ("TERRE PERDUE", curses.A_BOLD),
        (f"Jour {g.day_no()}  {'NUIT' if night else 'jour'}  ({t}/{DAY})", 0),
        ("", 0),
        (f"PV     {bar(g.hp)} {int(g.hp)}", 0),
        (f"Faim   {bar(g.food)} {int(g.food)}", 0),
        (f"Soif   {bar(g.water)} {int(g.water)}", 0),
        (f"Energ. {bar(g.energy)} {int(g.energy)}", 0),
        (f"Chaleur{bar(g.warm)} {int(g.warm)}", 0),
        ("", 0),
        ("SAC", curses.A_BOLD),
    ]
    for k, v in g.inv.items():
        if v:
            lines.append((f" {k}: {v}", 0))
    lines += [("", 0), ("TOUCHES", curses.A_BOLD),
              (" ZQSD/WASD/flèches: bouger", 0), (" (contre un objet = agir)", 0),
              (" f manger   r repos", 0), (" c fabriquer  m carte", 0),
              (" x quitter", 0)]
    for i, (s, at) in enumerate(lines[:sh - 1]):
        try:
            scr.addstr(i, X, s[:side], at)
        except curses.error:
            pass
    # journal
    for i, s in enumerate(g.log[-5:]):
        try:
            scr.addstr(sh - 6 + i, 0, s[:sw - 1], curses.A_BOLD if i == len(g.log[-5:]) - 1 else 0)
        except curses.error:
            pass
    if mode == "craft":
        box = ["== FABRIQUER ==", ""] + [
            f"{k}) {n}  [" + ", ".join(f"{v} {i}" for i, v in c.items()) + "]"
            for k, (n, c, _) in g.RECIPES.items()] + ["", "autre touche: annuler"]
        for i, s in enumerate(box):
            try:
                scr.addstr(2 + i, 3, " " + s.ljust(52), curses.A_REVERSE)
            except curses.error:
                pass
    scr.refresh()


def draw_map(scr, g):
    scr.erase()
    sh, sw = scr.getmaxyx()
    sx, sy = max(1, W // max(1, sw - 2) + 1), max(1, H // max(1, sh - 3) + 1)
    sx = max(sx, 1)
    for y in range(0, H, 2):
        for x in range(0, W, 1):
            if y // 2 >= sh - 2 or x >= sw - 1:
                continue
            if (x, y) not in g.seen and (x, y + 1) not in g.seen:
                continue
            ch, col, _ = tile_char(g, x, y)
            if (x, y) in g.objs and g.objs[(x, y)]["k"] in ("tree", "bush", "rock"):
                ch, col = GLYPH[g.tiles[y][x]]
            try:
                scr.addch(y // 2, x, ch, curses.color_pair(col))
            except curses.error:
                pass
    px, py = g.px, g.py // 2
    try:
        scr.addch(py, px, "@", curses.color_pair(6) | curses.A_BOLD)
        scr.addstr(sh - 1, 0, "Carte (moitié résolution verticale)  - une touche pour revenir -")
    except curses.error:
        pass
    scr.refresh()
    scr.getch()


def end_screen(scr, g):
    scr.erase()
    sh, sw = scr.getmaxyx()
    if g.over == "win":
        txt = ["", "  SECOURS EN ROUTE !", "",
               f"  Tu as survivé {g.turn} tours ({g.day_no()} jour(s)).",
               "  Un hélicoptère t'arrache à l'île.", "", "  VICTOIRE"]
    else:
        txt = ["", "  TU ES MORT.", "", f"  Cause : {g.cause}",
               f"  Tu as tenu {g.turn} tours ({g.day_no()} jour(s)).", "",
               f"  Graine de l'île : {g.seed}"]
    for i, s in enumerate(txt):
        try:
            scr.addstr(2 + i, 2, s, curses.A_BOLD)
        except curses.error:
            pass
    try:
        scr.addstr(sh - 2, 2, "Appuie sur une touche...")
    except curses.error:
        pass
    scr.refresh()
    scr.getch()


def main(scr, seed):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for i, c in enumerate((curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW,
                           curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN,
                           curses.COLOR_WHITE), start=1):
        curses.init_pair(i, c, -1)
    g = Game(seed)
    keys = {ord("w"): (0, -1), ord("z"): (0, -1), curses.KEY_UP: (0, -1),
            ord("s"): (0, 1), curses.KEY_DOWN: (0, 1),
            ord("a"): (-1, 0), ord("q"): (-1, 0), curses.KEY_LEFT: (-1, 0),
            ord("d"): (1, 0), curses.KEY_RIGHT: (1, 0)}
    while not g.over:
        draw(scr, g)
        k = scr.getch()
        if k in keys:
            g.move(*keys[k])
        elif k == ord("f"):
            g.eat()
        elif k == ord("r"):
            g.rest()
        elif k == ord(" "):
            g.tick()
        elif k == ord("m"):
            draw_map(scr, g)
        elif k == ord("c"):
            draw(scr, g, "craft")
            g.craft(chr(scr.getch()))
        elif k == ord("x"):
            return
    draw(scr, g)
    end_screen(scr, g)


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    curses.wrapper(main, seed)
