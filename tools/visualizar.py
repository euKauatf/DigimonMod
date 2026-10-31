"""
Renderiza uma prévia isométrica de um modelo .geo.json (pose de descanso) em PNG.

Uso:  python tools/visualizar.py agumon [saida.png]
"""
import json
import math
import os
import sys
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "src", "main", "resources", "assets", "digimonaurity")


def carregar(nome):
    with open(os.path.join(ASSETS, "geckolib", "models", "entity", f"{nome}.geo.json"), encoding="utf-8") as f:
        geo = json.load(f)["minecraft:geometry"][0]
    tex = Image.open(os.path.join(ASSETS, "textures", "entity", f"{nome}.png")).convert("RGBA")
    return geo, tex


def quads_do_cubo(cubo, tex):
    (x0, y0, z0), (w, h, d) = cubo["origin"], cubo["size"]
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    # face -> (canto superior esquerdo, vetor "direita" (u), vetor "baixo" (v), normal)
    faces = {
        "north": ((x1, y1, z0), (-w, 0, 0), (0, -h, 0), (0, 0, -1)),
        "south": ((x0, y1, z1), (w, 0, 0), (0, -h, 0), (0, 0, 1)),
        "east": ((x1, y1, z1), (0, 0, -d), (0, -h, 0), (1, 0, 0)),
        "west": ((x0, y1, z0), (0, 0, d), (0, -h, 0), (-1, 0, 0)),
        "up": ((x0, y1, z0), (w, 0, 0), (0, 0, d), (0, 1, 0)),
        "down": ((x0, y0, z1), (w, 0, 0), (0, 0, -d), (0, -1, 0)),
    }
    for nome, (o, du, dv, n) in faces.items():
        uv = cubo["uv"][nome]
        (u, v), (uw, vh) = uv["uv"], uv["uv_size"]
        if vh < 0:
            v, vh = v + vh, -vh
        uw, vh = max(1, int(round(abs(uw)))), max(1, int(round(vh)))
        for i in range(uw):
            for j in range(vh):
                cor = tex.getpixel((int(u) + i, int(v) + j))
                if cor[3] == 0:
                    continue
                a, b = i / uw, j / vh
                a2, b2 = (i + 1) / uw, (j + 1) / vh

                def p(s, t):
                    return tuple(o[k] + du[k] * s + dv[k] * t for k in range(3))
                yield [p(a, b), p(a2, b), p(a2, b2), p(a, b2)], cor, n


def renderizar(nome, saida, angulo=35, inclinacao=25, escala=14, fundo=(235, 240, 245, 255)):
    geo, tex = carregar(nome)
    ay, ax = math.radians(angulo), math.radians(inclinacao)

    def rot(pt):
        x, y, z = pt
        x, z = x * math.cos(ay) - z * math.sin(ay), x * math.sin(ay) + z * math.cos(ay)
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        return x, y, z

    luz = {(0, 1, 0): 1.0, (0, 0, -1): 0.92, (1, 0, 0): 0.8, (-1, 0, 0): 0.8, (0, 0, 1): 0.7, (0, -1, 0): 0.6}
    poligonos = []
    for osso in geo["bones"]:
        for cubo in osso.get("cubes", []):
            for quad, cor, n in quads_do_cubo(cubo, tex):
                nr = rot(n)
                if nr[2] > 0:  # face de costas para a câmera (câmera olha para +Z)
                    continue
                pts = [rot(p) for p in quad]
                prof = sum(p[2] for p in pts) / 4
                f = luz.get(tuple(n), 0.8)
                c = tuple(int(cor[k] * f) for k in range(3)) + (255,)
                poligonos.append((prof, [(p[0], p[1]) for p in pts], c))

    xs = [x for _, pts, _ in poligonos for x, _ in pts]
    ys = [y for _, pts, _ in poligonos for _, y in pts]
    margem = 20
    W = int((max(xs) - min(xs)) * escala) + 2 * margem
    H = int((max(ys) - min(ys)) * escala) + 2 * margem
    img = Image.new("RGBA", (W, H), fundo)
    dr = ImageDraw.Draw(img)
    poligonos.sort(key=lambda t: -t[0])
    for _, pts, c in poligonos:
        tela = [((x - min(xs)) * escala + margem, (max(ys) - y) * escala + margem) for x, y in pts]
        dr.polygon(tela, fill=c)
    img.save(saida)
    return saida


def gerar_icone(nome, tamanho=96):
    """Ícone quadrado com fundo transparente, usado na tela de escolha (textures/gui/starter/)."""
    pasta = os.path.join(ASSETS, "textures", "gui", "starter")
    os.makedirs(pasta, exist_ok=True)
    saida = os.path.join(pasta, f"{nome}.png")
    renderizar(nome, saida, angulo=-30, escala=16, fundo=(0, 0, 0, 0))
    img = Image.open(saida)
    lado = max(img.size)
    quadrado = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    quadrado.paste(img, ((lado - img.width) // 2, (lado - img.height) // 2))
    quadrado.resize((tamanho, tamanho), Image.LANCZOS).save(saida)
    return saida


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--icones":
        for n in sys.argv[2:]:
            print(gerar_icone(n))
        sys.exit()
    nome = sys.argv[1] if len(sys.argv) > 1 else "agumon"
    saida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(RAIZ, "tools", "previas", f"{nome}.png")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    frente = renderizar(nome, saida.replace(".png", "_frente.png"), angulo=-30)
    lado = renderizar(nome, saida.replace(".png", "_tras.png"), angulo=150)
    print(frente)
    print(lado)
