import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import os
import time
import sys

WIDTH = 3840
HEIGHT = 2160
FPS = 15
DURATION = 10
TOTAL_FRAMES = FPS * DURATION
OUTPUT_FILE = "ghostbyte_surveillance.gif"
PREVIEW_MODE = False

if PREVIEW_MODE:
    WIDTH = 960
    HEIGHT = 540

CX, CY = WIDTH // 2, HEIGHT // 2
S = WIDTH / 3840.0

NEON_GREEN = (0, 255, 65)
ELECTRIC_BLUE = (0, 120, 255)
DEEP_PURPLE = (120, 0, 200)
CYAN = (0, 255, 255)
RED_ACCENT = (255, 30, 60)
WHITE_SUB = (180, 180, 200)
DIM_GREEN = (0, 100, 30)
DIM_BLUE = (0, 50, 100)
DIM_CYAN = (0, 100, 100)
DIM_PURPLE = (60, 0, 100)


def get_font(size):
    sz = max(8, int(size * S))
    for p in [
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/consolab.ttf",
        "C:/Windows/Fonts/cour.ttf",
        "C:/Windows/Fonts/lucon.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                continue
    return ImageFont.load_default()


FONT_TINY = get_font(13)
FONT_SMALL = get_font(20)
FONT_MED = get_font(30)
FONT_LARGE = get_font(72)
FONT_TITLE = get_font(110)
FONT_TITLE_BOLD = get_font(115)


def ease_io(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = max(0.0, min(1.0, t))
    return t * t * t


def lerp(a, b, t):
    return a + (b - a) * t


def ca(color, alpha):
    a = max(0.0, min(1.0, alpha))
    return (int(color[0] * a), int(color[1] * a), int(color[2] * a))


REAL_NAMES = [
    "james_walker", "emily.davis", "mohammed_ali", "sarah.johnson",
    "carlos_garcia", "anna.mueller", "david.kim", "fatima_hassan",
    "alex.turner", "maria_lopez", "john.smith", "yuki_tanaka",
    "lucas_martin", "sofia.rossi", "omar_farooq", "elena.petrova",
    "ryan.chen", "leila_ahmed", "thomas.wright", "nina.berg",
    "mark_johnson", "hana.sato", "kevin.brown", "aya_ibrahim",
    "daniel.lee", "lara.novak", "victor.santos", "chloe.dupont",
    "ivan.volkov", "priya.sharma", "oscar.diaz", "mei_wong",
    "adam.taylor", "sara.eriksson", "ali.reza", "julia.fischer",
    "noah.anderson", "amira.khan", "felix.bauer", "zara.malik",
    "max.schneider", "ines.moreau", "leo.costa", "dana.pop",
    "jack.wilson", "mina.park", "hugo.ferreira", "emma.larsson",
    "rami.haddad", "clara.hoffman", "sam.reed", "nadia.cruz",
    "ethan.hall", "layla.torres", "ben.clark", "vera.jansen",
    "dani.silva", "rosa.martinez", "paul.weber", "tina.nguyen",
]


def rnd_username():
    name = random.choice(REAL_NAMES)
    r = random.random()
    if r < 0.4:
        return f"@{name}"
    elif r < 0.7:
        return name
    elif r < 0.85:
        return f"{name}{random.randint(0,99)}"
    else:
        return f"@{name.split('.')[0]}_{random.randint(10,99)}"


def rnd_hex(n=8):
    return "".join(random.choice("0123456789ABCDEF") for _ in range(n))


def rnd_bin(n=16):
    return "".join(random.choice("01") for _ in range(n))


def rnd_coord():
    return f"{random.uniform(-90,90):.4f},{random.uniform(-180,180):.4f}"


class Node:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(1.5, 3.5)
        self.sz = random.uniform(2, 6) * S

    def bright(self, t):
        return 0.3 + 0.7 * (0.5 + 0.5 * math.sin(t * self.speed + self.phase))


class NetworkWeb:
    def __init__(self):
        self.nodes = [Node() for _ in range(random.randint(65, 90))]
        self.edges = []
        md = 380 * S
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                a, b = self.nodes[i], self.nodes[j]
                d = math.hypot(a.x - b.x, a.y - b.y)
                if d < md:
                    self.edges.append((i, j, d, md))

    def draw(self, draw, t, alpha):
        if alpha < 0.02:
            return
        for i, j, d, md in self.edges:
            a, b = self.nodes[i], self.nodes[j]
            br = min(a.bright(t), b.bright(t))
            ea = alpha * br * (1 - d / md) * 0.35
            if ea < 0.03:
                continue
            c = ca(NEON_GREEN, ea * 0.4)
            draw.line([(a.x, a.y), (b.x, b.y)], fill=c, width=max(1, int(S)))
        for nd in self.nodes:
            b = nd.bright(t)
            sz = nd.sz * (0.5 + 0.5 * b)
            na = alpha * b
            if na < 0.03:
                continue
            gs = sz * 3
            draw.ellipse(
                [nd.x - gs, nd.y - gs, nd.x + gs, nd.y + gs],
                fill=ca(NEON_GREEN, na * 0.12),
            )
            draw.ellipse(
                [nd.x - sz, nd.y - sz, nd.x + sz, nd.y + sz],
                fill=ca(CYAN, na * 0.7),
            )


class SBox:
    def __init__(self, x, y, w, h):
        self.w, self.h = w, h
        self.x = float(x)
        self.y = float(y)
        self.uname = rnd_username()
        self.color = random.choice([NEON_GREEN, ELECTRIC_BLUE, CYAN])
        self.hl_color = None
        self.hl_timer = 0
        self.ci = 0
        self.tspeed = random.uniform(8, 18)
        self.gt = random.uniform(2, 5)
        self.born = random.uniform(0, 1.5)
        self.vx = random.uniform(-80, 80) * S
        self.vy = random.uniform(-80, 80) * S
        self.target_x = self.x
        self.target_y = self.y
        self.retarget_timer = random.uniform(0.5, 2.0)

    def center(self):
        return (self.x + self.w / 2, self.y + self.h / 2)

    def update(self, t, dt):
        self.ci += self.tspeed * dt
        if self.ci > len(self.uname) + 8:
            self.uname = rnd_username()
            self.ci = 0
            self.tspeed = random.uniform(8, 18)
        self.gt -= dt
        if self.gt <= 0:
            self.gt = random.uniform(1.5, 4)
            r = random.random()
            if r < 0.25:
                self.hl_color = RED_ACCENT
                self.hl_timer = 0.35
            elif r < 0.5:
                self.hl_color = NEON_GREEN
                self.hl_timer = 0.25
        if self.hl_timer > 0:
            self.hl_timer -= dt
            if self.hl_timer <= 0:
                self.hl_color = None
        self.retarget_timer -= dt
        if self.retarget_timer <= 0:
            self.retarget_timer = random.uniform(0.8, 2.5)
            margin = 60 * S
            self.target_x = random.uniform(margin, WIDTH - self.w - margin)
            self.target_y = random.uniform(margin, HEIGHT - self.h - margin)
            center_margin = 370 * S
            if abs(self.target_x + self.w / 2 - CX) < center_margin and abs(self.target_y + self.h / 2 - CY) < center_margin:
                if self.target_x + self.w / 2 < CX:
                    self.target_x = CX - center_margin - self.w / 2
                else:
                    self.target_x = CX + center_margin - self.w / 2
        speed = 120 * S
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            self.x += (dx / dist) * speed * dt
            self.y += (dy / dist) * speed * dt

    def draw(self, draw_ctx, t, alpha):
        if alpha < 0.02:
            return
        px = self.x
        py = self.y
        bc = self.hl_color if self.hl_color else self.color
        draw_ctx.rectangle(
            [px, py, px + self.w, py + self.h],
            outline=ca(bc, alpha * 0.45),
            width=max(1, int(S)),
        )
        if self.hl_color:
            draw_ctx.rectangle(
                [px + 1, py + 1, px + self.w - 1, py + self.h - 1],
                fill=ca(self.hl_color, alpha * 0.06),
            )
        shown = int(min(self.ci, len(self.uname)))
        txt = self.uname[:shown]
        if self.ci < len(self.uname) and int(t * 5) % 2 == 0:
            txt += "_"
        if self.gt < 0.15 and random.random() < 0.6 and txt:
            cl = list(txt)
            cl[random.randint(0, len(cl) - 1)] = random.choice("@#$%&!?*~")
            txt = "".join(cl)
        tx = px + 10 * S
        ty = py + self.h / 2 - 10 * S
        draw_ctx.text((tx, ty), txt, fill=ca(self.color, alpha * 0.85), font=FONT_SMALL)


class SurveillanceGrid:
    def __init__(self):
        self.boxes = []
        bw = int(200 * S)
        bh = int(42 * S)
        num_boxes = 40
        margin = 80 * S
        center_margin = 380 * S
        for _ in range(num_boxes):
            for _try in range(20):
                x = random.uniform(margin, WIDTH - bw - margin)
                y = random.uniform(margin, HEIGHT - bh - margin)
                cx_b = x + bw / 2
                cy_b = y + bh / 2
                if abs(cx_b - CX) < center_margin and abs(cy_b - CY) < center_margin:
                    continue
                break
            self.boxes.append(SBox(x, y, bw, bh))

    def update(self, t, dt):
        for b in self.boxes:
            b.update(t, dt)

    def draw_lines(self, draw_ctx, t, alpha, core):
        if alpha < 0.02:
            return
        ccx = core.bx + core.bw / 2
        ccy = core.by + core.bh / 2
        for b in self.boxes:
            ba = alpha * ease_io(max(0, min(1, (t - b.born) / 0.6)))
            if ba < 0.03:
                continue
            bcx, bcy = b.center()
            pulse = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(t * 2.5 + b.born * 5))
            lc = ca(NEON_GREEN, ba * 0.2 * pulse)
            draw_ctx.line([(bcx, bcy), (ccx, ccy)], fill=lc, width=max(1, int(S)))
        for i in range(len(self.boxes)):
            for j in range(i + 1, len(self.boxes)):
                a, b2 = self.boxes[i], self.boxes[j]
                ax, ay = a.center()
                bx2, by2 = b2.center()
                d = math.hypot(ax - bx2, ay - by2)
                if d < 350 * S:
                    ba_i = alpha * ease_io(max(0, min(1, (t - a.born) / 0.6)))
                    ba_j = alpha * ease_io(max(0, min(1, (t - b2.born) / 0.6)))
                    la = min(ba_i, ba_j) * (1 - d / (350 * S)) * 0.15
                    if la > 0.02:
                        draw_ctx.line([(ax, ay), (bx2, by2)], fill=ca(CYAN, la), width=max(1, int(S)))

    def draw(self, draw_ctx, t, alpha):
        for b in self.boxes:
            ba = alpha * ease_io(max(0, min(1, (t - b.born) / 0.6)))
            b.draw(draw_ctx, t, ba)


class GhostbyteCore:
    def __init__(self):
        self.particles = []
        self.bw = int(640 * S)
        self.bh = int(220 * S)
        self.bx = CX - self.bw // 2
        self.by = CY - self.bh // 2
        self.cycle = 4.0
        self._make_particles()

    def _make_particles(self):
        tmp = Image.new("L", (self.bw, self.bh), 0)
        td = ImageDraw.Draw(tmp)
        text = "Ghostbyte"
        bb = td.textbbox((0, 0), text, font=FONT_TITLE)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = (self.bw - tw) // 2
        ty = (self.bh - th) // 2
        td.text((tx, ty), text, fill=255, font=FONT_TITLE)
        arr = np.array(tmp)
        ys, xs = np.where(arr > 100)
        n = min(len(xs), int(2500 * S))
        if len(xs) > n:
            idx = np.random.choice(len(xs), n, replace=False)
            xs, ys = xs[idx], ys[idx]
        for px, py in zip(xs, ys):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60, 280) * S
            self.particles.append(
                {
                    "hx": self.bx + float(px),
                    "hy": self.by + float(py),
                    "vx": math.cos(ang) * spd,
                    "vy": math.sin(ang) * spd,
                    "c": random.choice([NEON_GREEN, CYAN, ELECTRIC_BLUE, WHITE_SUB]),
                    "s": random.uniform(1, 3) * S,
                }
            )

    def draw(self, draw_ctx, t, alpha):
        if alpha < 0.02:
            return
        bx, by, bw, bh = self.bx, self.by, self.bw, self.bh
        bc = ca(CYAN, alpha * 0.4)
        draw_ctx.rectangle([bx, by, bx + bw, by + bh], outline=bc, width=max(1, int(2 * S)))
        for i in range(1, max(2, int(5 * S))):
            draw_ctx.rectangle(
                [bx - i, by - i, bx + bw + i, by + bh + i],
                outline=ca(CYAN, alpha * 0.04),
            )
        ct = (t % self.cycle) / self.cycle
        if ct < 0.35:
            self._draw_text(draw_ctx, t, alpha)
        elif ct < 0.65:
            prog = ease_in((ct - 0.35) / 0.3)
            self._draw_particles_disp(draw_ctx, prog, alpha)
        elif ct < 0.85:
            self._draw_particles_disp(draw_ctx, 1.0, alpha * (0.5 + 0.3 * math.sin(t * 6)))
        else:
            prog = 1.0 - ease_out((ct - 0.85) / 0.15)
            self._draw_particles_disp(draw_ctx, prog, alpha)

    def _draw_text(self, draw_ctx, t, alpha):
        ta = alpha
        if random.random() < 0.07:
            ta *= random.uniform(0.15, 0.5)
        text = "Ghostbyte"
        bb = draw_ctx.textbbox((0, 0), text, font=FONT_TITLE)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = CX - tw // 2
        ty = CY - th // 2
        off = max(1, int(3 * S))
        draw_ctx.text((tx - off, ty), text, fill=ca(RED_ACCENT, ta * 0.25), font=FONT_TITLE)
        draw_ctx.text((tx + off, ty), text, fill=ca(ELECTRIC_BLUE, ta * 0.25), font=FONT_TITLE)
        draw_ctx.text((tx, ty), text, fill=ca(NEON_GREEN, ta * 0.95), font=FONT_TITLE)
        sub = "made by @lfillaz"
        sbb = draw_ctx.textbbox((0, 0), sub, font=FONT_SMALL)
        sw = sbb[2] - sbb[0]
        sx = CX - sw // 2
        sy = CY + th // 2 + int(20 * S)
        draw_ctx.text((sx, sy), sub, fill=ca(CYAN, ta * 0.5), font=FONT_SMALL)

    def _draw_particles_disp(self, draw_ctx, disp, alpha):
        for p in self.particles:
            x = lerp(p["hx"], p["hx"] + p["vx"] * 2.5, disp)
            y = lerp(p["hy"], p["hy"] + p["vy"] * 2.5, disp)
            sz = p["s"] * (1 + disp * 0.4)
            pa = alpha * (1 - disp * 0.25)
            draw_ctx.rectangle([x - sz, y - sz, x + sz, y + sz], fill=ca(p["c"], pa))


class CrypticOverlay:
    def __init__(self):
        self.syms = []
        t = 0
        while t < DURATION:
            for _ in range(random.randint(1, 4)):
                ts = t + random.uniform(0, 0.4)
                dur = random.uniform(0.25, 0.7)
                x = random.randint(int(30 * S), int(WIDTH - 250 * S))
                y = random.randint(int(30 * S), int(HEIGHT - 40 * S))
                txt = random.choice(
                    [
                        f"0x{rnd_hex(8)}",
                        rnd_bin(16),
                        f"[{rnd_coord()}]",
                        f"PKT:{rnd_hex(4)}",
                        f"NODE_{random.randint(0,255):02X}",
                        f"TRACE::{rnd_hex(6)}",
                        f">>>{rnd_bin(8)}",
                        f"SIG:0x{rnd_hex(4)}",
                        f"DECRYPT::{rnd_hex(10)}",
                        f"LAT:{random.uniform(-90,90):.2f}",
                    ]
                )
                col = random.choice([DIM_GREEN, DIM_CYAN, DIM_BLUE, DIM_PURPLE])
                self.syms.append((ts, dur, x, y, txt, col))
            t += random.uniform(0.2, 0.8)

    def draw(self, draw_ctx, t, alpha):
        if alpha < 0.02:
            return
        for ts, dur, x, y, txt, col in self.syms:
            dt2 = t - ts
            if dt2 < 0 or dt2 > dur:
                continue
            fade = 1.0
            if dt2 < 0.08:
                fade = dt2 / 0.08
            elif dt2 > dur - 0.08:
                fade = (dur - dt2) / 0.08
            draw_ctx.text((x, y), txt, fill=ca(col, alpha * fade * 0.7), font=FONT_TINY)


class MatrixCol:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.uniform(-HEIGHT, 0)
        self.spd = random.uniform(120, 350) * S
        self.chars = [chr(random.randint(0x30, 0x7A)) for _ in range(random.randint(5, 18))]
        self.csz = max(8, int(14 * S))

    def update(self, dt):
        self.y += self.spd * dt
        if self.y > HEIGHT + 300:
            self.y = random.uniform(-HEIGHT * 0.5, -100)
            self.x = random.randint(0, WIDTH)
            self.chars = [chr(random.randint(0x30, 0x7A)) for _ in range(random.randint(5, 18))]

    def draw(self, draw_ctx, alpha):
        if alpha < 0.02:
            return
        for i, ch in enumerate(self.chars):
            cy = self.y + i * self.csz
            if cy < -20 or cy > HEIGHT + 20:
                continue
            fade = 1.0 - i / len(self.chars)
            c = ca(DIM_GREEN, alpha * fade * 0.25)
            if random.random() < 0.08:
                ch = chr(random.randint(0x30, 0x7A))
            draw_ctx.text((self.x, cy), ch, fill=c, font=FONT_TINY)


def draw_scanlines(draw_ctx, t, alpha):
    if alpha < 0.02:
        return
    y = int((t * 180 * S) % (HEIGHT + 80)) - 40
    w = max(1, int(S))
    draw_ctx.line([(0, y), (WIDTH, y)], fill=ca(NEON_GREEN, alpha * 0.18), width=w)
    for dy in range(-int(12 * S), int(12 * S), max(1, int(2 * S))):
        fade = 1.0 - abs(dy) / (12 * S)
        draw_ctx.line(
            [(0, y + dy), (WIDTH, y + dy)],
            fill=ca(NEON_GREEN, alpha * 0.04 * fade),
            width=w,
        )
    y2 = int((t * 90 * S + HEIGHT * 0.6) % (HEIGHT + 80)) - 40
    draw_ctx.line([(0, y2), (WIDTH, y2)], fill=ca(ELECTRIC_BLUE, alpha * 0.08), width=w)


def apply_glitch(img, intensity=0.3):
    if intensity < 0.01 or random.random() > 0.45:
        return img
    arr = np.array(img)
    h, w = arr.shape[:2]
    n = random.randint(1, max(1, int(6 * intensity)))
    for _ in range(n):
        y = random.randint(0, h - 1)
        sh = random.randint(1, max(1, int(35 * S * intensity)))
        shift = random.randint(-int(50 * S * intensity), int(50 * S * intensity))
        y2 = min(y + sh, h)
        arr[y:y2] = np.roll(arr[y:y2], shift, axis=1)
    if random.random() < intensity * 0.6:
        off = random.randint(1, max(1, int(6 * S * intensity)))
        res = arr.copy()
        if off < w:
            res[:, off:, 0] = arr[:, :-off, 0]
            res[:, :-off, 2] = arr[:, off:, 2]
        arr = res
    return Image.fromarray(arr)


def draw_vignette(img, strength=0.4):
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape[:2]
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt((X - cx) ** 2 / (cx ** 2) + (Y - cy) ** 2 / (cy ** 2))
    mask = 1.0 - np.clip(dist * strength, 0, 1)
    mask = mask[..., np.newaxis]
    arr = arr * mask
    return Image.fromarray(arr.astype(np.uint8))


class AnimationEngine:
    def __init__(self):
        print("Initializing components...")
        random.seed(42)
        np.random.seed(42)
        self.net = NetworkWeb()
        self.grid = SurveillanceGrid()
        self.core = GhostbyteCore()
        self.crypt = CrypticOverlay()
        self.mcols = [MatrixCol() for _ in range(max(5, int(35 * S)))]
        self.prev_t = 0
        random.seed(None)
        np.random.seed(None)
        print(f"Ready. {WIDTH}x{HEIGHT}, {FPS}fps, {DURATION}s, {TOTAL_FRAMES} frames")

    def alphas(self, t):
        net_a = ease_io(min(1, t / 1.5))
        grid_a = ease_io(max(0, min(1, (t - 1.0) / 1.5)))
        core_a = ease_io(max(0, min(1, (t - 2.5) / 1.0)))
        crypt_a = ease_io(max(0, min(1, (t - 3.0) / 1.0)))
        mat_a = ease_io(max(0, min(1, (t - 1.5) / 1.0))) * 0.45
        scan_a = ease_io(max(0, min(1, (t - 0.5) / 1.0))) * 0.6
        glitch = 0.0
        if 5 < t < 9:
            glitch = 0.12
        if 7 < t < 8.5:
            b = ease_io(min(1, (t - 7) / 0.5)) if t < 7.5 else ease_io((8.5 - t) / 1.0)
            net_a = min(1, net_a * (1 + b * 0.4))
            grid_a = min(1, grid_a * (1 + b * 0.3))
            crypt_a = min(1, crypt_a * (1 + b * 0.6))
            mat_a = min(1, mat_a * (1 + b * 0.8))
            glitch = 0.3 + b * 0.15
        if t > DURATION - 1.5:
            fd = ease_io((DURATION - t) / 1.5)
            net_a *= fd
            grid_a *= fd
            crypt_a *= fd
            mat_a *= fd
            scan_a *= fd
            glitch *= fd
            core_a *= max(fd, 0.3)
        if t > DURATION - 0.5:
            core_a *= ease_io((DURATION - t) / 0.5)
        return dict(
            net=net_a, grid=grid_a, core=core_a,
            crypt=crypt_a, mat=mat_a, scan=scan_a, glitch=glitch
        )

    def render(self, fi):
        t = fi / FPS
        dt = t - self.prev_t if fi > 0 else 1 / FPS
        self.prev_t = t
        img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        dr = ImageDraw.Draw(img)
        a = self.alphas(t)
        self.grid.update(t, dt)
        for mc in self.mcols:
            mc.update(dt)
        for mc in self.mcols:
            mc.draw(dr, a["mat"])
        self.net.draw(dr, t, a["net"])
        draw_scanlines(dr, t, a["scan"])
        self.grid.draw_lines(dr, t, a["grid"], self.core)
        self.grid.draw(dr, t, a["grid"])
        self.core.draw(dr, t, a["core"])
        self.crypt.draw(dr, t, a["crypt"])
        if a["glitch"] > 0.01:
            img = apply_glitch(img, a["glitch"])
        img = draw_vignette(img, 0.35)
        return img

    def export(self, path):
        start = time.time()
        frames = []
        for i in range(TOTAL_FRAMES):
            frame = self.render(i)
            fq = frame.quantize(colors=256, method=2, dither=1)
            frames.append(fq)
            el = time.time() - start
            fps_r = (i + 1) / el if el > 0 else 0
            eta = (TOTAL_FRAMES - i - 1) / fps_r if fps_r > 0 else 0
            sys.stdout.write(
                f"\rFrame {i+1}/{TOTAL_FRAMES} | {fps_r:.1f} f/s | ETA: {eta:.0f}s   "
            )
            sys.stdout.flush()
        print(f"\nSaving to {path}...")
        frames[0].save(
            path,
            save_all=True,
            append_images=frames[1:],
            duration=int(1000 / FPS),
            loop=0,
            optimize=False,
        )
        sz = os.path.getsize(path) / (1024 * 1024)
        tt = time.time() - start
        print(f"Done! {path} — {sz:.1f} MB in {tt:.1f}s")

    def export_frames(self, folder="frames"):
        os.makedirs(folder, exist_ok=True)
        start = time.time()
        for i in range(TOTAL_FRAMES):
            frame = self.render(i)
            frame.save(os.path.join(folder, f"frame_{i:04d}.png"))
            el = time.time() - start
            fps_r = (i + 1) / el if el > 0 else 0
            eta = (TOTAL_FRAMES - i - 1) / fps_r if fps_r > 0 else 0
            sys.stdout.write(
                f"\rFrame {i+1}/{TOTAL_FRAMES} | {fps_r:.1f} f/s | ETA: {eta:.0f}s   "
            )
            sys.stdout.flush()
        print(f"\nFrames saved to {folder}/")
        print("Convert with: ffmpeg -framerate 15 -i frames/frame_%04d.png -vf "
              '"format=yuv420p" -c:v libx264 -crf 18 ghostbyte.mp4')


if __name__ == "__main__":
    print("=" * 55)
    print("  GHOSTBYTE SURVEILLANCE MATRIX")
    print(f"  {WIDTH}x{HEIGHT} | {FPS}fps | {DURATION}s | {TOTAL_FRAMES} frames")
    print(f"  Preview: {PREVIEW_MODE}")
    print("=" * 55)
    engine = AnimationEngine()
    mode = "gif"
    if len(sys.argv) > 1 and sys.argv[1] == "frames":
        mode = "frames"
    if mode == "frames":
        engine.export_frames()
    else:
        engine.export(OUTPUT_FILE)
