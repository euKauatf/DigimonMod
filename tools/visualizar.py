"""
Renderiza uma prévia isométrica de um modelo .geo.json (pose de descanso) em PNG.

Uso:  python tools/visualizar.py agumon [saida.png]
      python tools/visualizar.py --icones agumon gabumon
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "src", "main", "resources", "assets", "digimonaurity")

LUZ = {(0, 1, 0): 1.0, (0, 0, -1): 0.92, (1, 0, 0): 0.8, (-1, 0, 0): 0.8, (0, 0, 1): 0.7, (0, -1, 0): 0.6}


def carregar(nome):
    with open(os.path.join(ASSETS, "geckolib", "models", "entity", f"{nome}.geo.json"), encoding="utf-8") as f:
        geo = json.load(f)["minecraft:geometry"][0]
    tex = Image.open(os.path.join(ASSETS, "textures", "entity", f"{nome}.png")).convert("RGBA")
    return geo, tex


def faces_do_cubo(cubo):
    """Cada face: (canto superior esquerdo, vetor u, vetor v, normal, nome)."""
    (x0, y0, z0), (w, h, d) = cubo["origin"], cubo["size"]
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    return [
        ((x1, y1, z0), (-w, 0, 0), (0, -h, 0), (0, 0, -1), "north"),
        ((x0, y1, z1), (w, 0, 0), (0, -h, 0), (0, 0, 1), "south"),
        ((x1, y1, z1), (0, 0, -d), (0, -h, 0), (1, 0, 0), "east"),
        ((x0, y1, z0), (0, 0, d), (0, -h, 0), (-1, 0, 0), "west"),
        ((x0, y1, z0), (w, 0, 0), (0, 0, d), (0, 1, 0), "up"),
        ((x0, y0, z1), (w, 0, 0), (0, 0, -d), (0, -1, 0), "down"),
    ]


def renderizar(nome, saida, angulo=35, inclinacao=25, escala=14, fundo=(235, 240, 245, 255)):
    """
    Projeta cada face inteira de uma vez (transformação afim da textura), do fundo para a frente.
    Rotações de cubos e ossos são ignoradas (pose de descanso).
    """
    geo, tex = carregar(nome)
    ay, ax = math.radians(angulo), math.radians(inclinacao)

    def rot(p):
        x, y, z = p
        x, z = x * math.cos(ay) - z * math.sin(ay), x * math.sin(ay) + z * math.cos(ay)
        y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
        return x, y, z

    itens = []
    for osso in geo["bones"]:
        for cubo in osso.get("cubes", []):
            for origem, du, dv, normal, nome_face in faces_do_cubo(cubo):
                if rot(normal)[2] > 0:
                    continue  # de costas para a câmera
                uv = cubo["uv"][nome_face]
                (u, v), (uw, vh) = uv["uv"], uv["uv_size"]
                if vh < 0:
                    v, vh = v + vh, -vh
                cantos = [origem,
                          tuple(origem[k] + du[k] for k in range(3)),
                          tuple(origem[k] + du[k] + dv[k] for k in range(3)),
                          tuple(origem[k] + dv[k] for k in range(3))]
                r = [rot(c) for c in cantos]
                prof = sum(c[2] for c in r) / 4
                itens.append((prof, r, (int(u), int(v), max(1, int(round(uw))), max(1, int(round(vh)))), LUZ.get(normal, 0.8)))

    xs = [c[0] for _, r, _, _ in itens for c in r]
    ys = [c[1] for _, r, _, _ in itens for c in r]
    margem = 20
    largura = int((max(xs) - min(xs)) * escala) + 2 * margem
    altura = int((max(ys) - min(ys)) * escala) + 2 * margem
    img = Image.new("RGBA", (largura, altura), fundo)

    def tela(c):
        return ((c[0] - min(xs)) * escala + margem, (max(ys) - c[1]) * escala + margem)

    itens.sort(key=lambda t: -t[0])
    for _, r, (u, v, uw, vh), luz in itens:
        recorte = tex.crop((u, v, u + uw, v + vh))
        if luz < 1.0:
            rgb = recorte.convert("RGB").point(lambda c, f=luz: int(c * f))
            recorte = Image.merge("RGBA", (*rgb.split(), recorte.split()[3]))
        p0, p1, _, p3 = [tela(c) for c in r]
        # matriz que leva (s, t) da textura ao pixel da tela; invertida para o Image.transform
        a, b = (p1[0] - p0[0]) / uw, (p3[0] - p0[0]) / vh
        c, d = (p1[1] - p0[1]) / uw, (p3[1] - p0[1]) / vh
        det = a * d - b * c
        if abs(det) < 1e-6:
            continue
        ia, ib, ic, id_ = d / det, -b / det, -c / det, a / det
        dados = (ia, ib, -(ia * p0[0] + ib * p0[1]), ic, id_, -(ic * p0[0] + id_ * p0[1]))
        projetado = recorte.transform(img.size, Image.AFFINE, dados, resample=Image.NEAREST)
        mascara = Image.new("L", img.size, 0)
        ImageDraw.Draw(mascara).polygon([tela(cc) for cc in r], fill=255)
        alfa = Image.composite(projetado.split()[3], Image.new("L", img.size, 0), mascara)
        img.paste(projetado, (0, 0), alfa)
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
    print(renderizar(nome, saida.replace(".png", "_frente.png"), angulo=-30))
    print(renderizar(nome, saida.replace(".png", "_tras.png"), angulo=150))
