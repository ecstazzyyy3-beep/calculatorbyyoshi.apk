# calc_pygame_full.py
# Полноекранний калькулятор у стилі Android (як на скріншоті)
# Оптимізований для Pydroid 3 + pygame

import pygame, math, sys, re

pygame.init()
pygame.display.set_caption("Calculator")

# === Основні налаштування ===
info = pygame.display.Info()
W, H = info.current_w, info.current_h   # розмір екрана телефону
screen = pygame.display.set_mode((W, H))
pygame.font.init()

# Масштаб (щоб адаптувати кнопки до екрану)
scale_x = W / 400
scale_y = H / 700
S = min(scale_x, scale_y)

font_main = pygame.font.SysFont("arial", int(34*S))
font_btn = pygame.font.SysFont("arial", int(22*S), bold=True)

# Кольори
BLACK = (10, 10, 10)
GRAY = (45, 45, 45)
BLUE = (15, 90, 130)
LIGHTBLUE = (30, 120, 160)
GREEN = (70, 200, 120)
TEXT_COLOR = (255, 255, 255)

# === Кнопки ===
layout = [
    ["√", "π", "^", "!"],
    ["Deg", "sin", "cos", "tan"],
    ["Inv", "e", "ln", "log"],
    ["AC", "()", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ",", "⌫", "="]
]

btn_w, btn_h = int(85*S), int(60*S)
gap = int(10*S)
x0, y0 = int(15*S), int(250*S)

BUTTONS = []
for row_i, row in enumerate(layout):
    for col_i, text in enumerate(row):
        bx = x0 + col_i * (btn_w + gap)
        by = y0 + row_i * (btn_h + gap)
        color = BLUE
        if text in "0123456789,":
            color = GRAY
        elif text == "=":
            color = GREEN
        elif text in ["AC", "()", "%", "÷", "×", "-", "+"]:
            color = LIGHTBLUE
        BUTTONS.append({"text": text, "rect": pygame.Rect(bx, by, btn_w, btn_h), "color": color})

expr = ""
output = ""
deg_mode = True
inv_mode = False

# === Безпечний eval ===
def safe_eval(expression):
    expression = expression.replace("^", "**").replace("×", "*").replace("÷", "/").replace(",", ".")
    expression = expression.replace("√", "math.sqrt").replace("π", "math.pi").replace("e", "math.e")
    expression = re.sub(r"(\d+)%", r"(\1/100)", expression)
    for f in ["sin", "cos", "tan", "asin", "acos", "atan", "ln", "log"]:
        expression = re.sub(fr"\b{f}\b", f"math.{f if f!='ln' else 'log'}", expression)
    try:
        val = eval(expression, {"__builtins__": None, "math": math})
        if isinstance(val, float) and abs(val - int(val)) < 1e-10:
            val = int(val)
        return val
    except Exception:
        return "Error"

# === Малювання ===
def draw_rounded_rect(surf, rect, color, radius):
    x, y, w, h = rect
    pygame.draw.rect(surf, color, (x + radius, y, w - 2*radius, h))
    pygame.draw.rect(surf, color, (x, y + radius, w, h - 2*radius))
    pygame.draw.circle(surf, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surf, color, (x + w - radius, y + radius), radius)
    pygame.draw.circle(surf, color, (x + radius, y + h - radius), radius)
    pygame.draw.circle(surf, color, (x + w - radius, y + h - radius), radius)

def render():
    screen.fill(BLACK)
    # Екран виводу
    expr_surf = font_main.render(expr if expr else "0", True, TEXT_COLOR)
    res_surf = font_main.render(str(output), True, (180, 180, 180))
    screen.blit(expr_surf, (20*S, 100*S))
    if output != "":
        screen.blit(res_surf, (20*S, 150*S))
    # Кнопки
    for b in BUTTONS:
        draw_rounded_rect(screen, b["rect"], b["color"], int(25*S))
        txt = font_btn.render(b["text"], True, TEXT_COLOR)
        tw, th = txt.get_size()
        screen.blit(txt, (b["rect"].x + (btn_w - tw)//2, b["rect"].y + (btn_h - th)//2))
    pygame.display.flip()

# === Основний цикл ===
clock = pygame.time.Clock()

while True:
    render()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            pos = e.pos
            for b in BUTTONS:
                if b["rect"].collidepoint(pos):
                    t = b["text"]
                    if t == "AC":
                        expr, output = "", ""
                    elif t == "=":
                        res = safe_eval(expr)
                        output = res
                        expr = str(res) if res != "Error" else expr
                    elif t == "⌫":
                        expr = expr[:-1]
                    elif t == "()" :
                        expr += "(" if expr.count("(") == expr.count(")") else ")"
                    elif t == "Deg":
                        deg_mode = not deg_mode
                        b["text"] = "Rad" if not deg_mode else "Deg"
                    elif t == "Inv":
                        inv_mode = not inv_mode
                    else:
                        expr += t
    clock.tick(30)