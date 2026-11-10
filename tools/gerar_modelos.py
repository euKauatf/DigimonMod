"""
Gera modelos (.geo.json), animações (.animation.json) e texturas (.png) dos Digimon
no formato do GeckoLib, a partir de descrições em código (caixas coloridas).

Uso:  python tools/gerar_modelos.py   (gera todos os Digimon de modelos_hd.py)

Convenções do formato (Bedrock geometry 1.12.0, usado pelo GeckoLib):
- 16 unidades = 1 bloco. O modelo olha para -Z (norte).
- "origin" de um cubo é o canto mínimo [x, y, z]; "pivot" é o ponto de rotação do osso.
- Cada face de cada cubo recebe um retângulo próprio na textura (UV por face),
  o que permite desenhar olhos, barriga e marcas exatamente onde queremos.
"""
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "src", "main", "resources", "assets", "digimonaurity")
PASTA_MODELOS = os.path.join(ASSETS, "geckolib", "models", "entity")
PASTA_ANIMACOES = os.path.join(ASSETS, "geckolib", "animations", "entity")
PASTA_TEXTURAS = os.path.join(ASSETS, "textures", "entity")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def escurecer(cor, f):
    return tuple(max(0, int(c * f)) for c in cor[:3]) + (255,)


# ---------------------------------------------------------------- pintura ---

class Face:
    """Pintor de uma face: cor base, borda escurecida e desenhos opcionais."""

    def __init__(self, cor, borda=0.78, desenho=None):
        self.cor = hex_rgb(cor) if isinstance(cor, str) else cor
        self.borda = borda
        self.desenho = desenho  # função(img, x, y, w, h)

    def pintar(self, img, x, y, w, h):
        for i in range(w):
            for j in range(h):
                img.putpixel((x + i, y + j), self.cor)
        if self.borda and w > 2 and h > 2:
            # Sombra na base da face; laterais só em faces largas (evita listras em pernas finas).
            escura = escurecer(self.cor, self.borda)
            for i in range(w):
                img.putpixel((x + i, y + h - 1), escura)
            if w >= 5:
                lateral = escurecer(self.cor, (1 + self.borda) / 2)
                for j in range(h):
                    img.putpixel((x, y + j), lateral)
                    img.putpixel((x + w - 1, y + j), lateral)
        if self.desenho:
            self.desenho(img, x, y, w, h)


def px(img, x, y, cor):
    img.putpixel((x, y), hex_rgb(cor))


def retangulo(img, x, y, w, h, cor):
    for i in range(w):
        for j in range(h):
            px(img, x + i, y + j, cor)


# ------------------------------------------------------------------ cubos ---

FACES = ("north", "south", "east", "west", "up", "down")


class Cubo:
    def __init__(self, origem, tamanho, cor, faces=None, inflar=0.0, rotacao=None, pivo=None):
        self.origem = origem
        self.tamanho = tamanho
        self.base = Face(cor) if isinstance(cor, str) else cor
        self.faces = faces or {}  # nome da face -> Face (ou Pintura do estilo HD)
        self.inflar = inflar
        self.rotacao = rotacao  # rotação própria do cubo (ex.: orelhas inclinadas)
        self.pivo = pivo

    def dimensoes_face(self, face):
        w, h, d = self.tamanho
        return {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h),
                "up": (w, d), "down": (w, d)}[face]


class Osso:
    def __init__(self, nome, pivo, pai=None, cubos=None, rotacao=None):
        self.nome = nome
        self.pivo = pivo
        self.pai = pai
        self.cubos = cubos or []
        self.rotacao = rotacao


# --------------------------------------------------------------- empacotar ---

def empacotar(ossos, largura=128, densidade=1):
    """
    Distribui todos os retângulos de face na textura (empacotamento em prateleiras).
    densidade = pixels de textura por unidade do modelo (1 = padrão do Minecraft, 2 = HD).
    """
    pedidos = []
    for osso in ossos:
        for cubo in osso.cubos:
            for face in FACES:
                w, h = cubo.dimensoes_face(face)
                w, h = max(1, int(round(w * densidade))), max(1, int(round(h * densidade)))
                pedidos.append((cubo, face, w, h))
    pedidos.sort(key=lambda p: -p[3])
    x = y = altura_prateleira = 0
    posicoes = {}
    for cubo, face, w, h in pedidos:
        if x + w > largura:
            x, y = 0, y + altura_prateleira
            altura_prateleira = 0
        posicoes[(id(cubo), face)] = (x, y, w, h)
        x += w
        altura_prateleira = max(altura_prateleira, h)
    altura = y + altura_prateleira
    altura_final = 16
    while altura_final < altura:
        altura_final *= 2
    return posicoes, largura, altura_final


def gerar(nome, ossos, animacoes, largura_textura=None, densidade=1):
    largura_textura = largura_textura or 128 * densidade
    posicoes, tw, th = empacotar(ossos, largura_textura, densidade)
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))

    ossos_json = []
    for osso in ossos:
        cubos_json = []
        for cubo in osso.cubos:
            uv = {}
            for face in FACES:
                x, y, w, h = posicoes[(id(cubo), face)]
                (cubo.faces.get(face) or cubo.base).pintar(img, x, y, w, h)
                if face == "down":
                    uv[face] = {"uv": [x, y + h], "uv_size": [w, -h]}
                else:
                    uv[face] = {"uv": [x, y], "uv_size": [w, h]}
            c = {"origin": cubo.origem, "size": cubo.tamanho, "uv": uv}
            if cubo.inflar:
                c["inflate"] = cubo.inflar
            if cubo.rotacao:
                c["rotation"] = cubo.rotacao
                c["pivot"] = cubo.pivo or cubo.origem
            cubos_json.append(c)
        o = {"name": osso.nome, "pivot": osso.pivo}
        if osso.pai:
            o["parent"] = osso.pai
        if osso.rotacao:
            o["rotation"] = osso.rotacao
        if cubos_json:
            o["cubes"] = cubos_json
        ossos_json.append(o)

    geo = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": f"geometry.{nome}",
                "texture_width": tw,
                "texture_height": th,
                "visible_bounds_width": 4,
                "visible_bounds_height": 4,
                "visible_bounds_offset": [0, 1, 0],
            },
            "bones": ossos_json,
        }],
    }

    for pasta in (PASTA_MODELOS, PASTA_ANIMACOES, PASTA_TEXTURAS):
        os.makedirs(pasta, exist_ok=True)
    with open(os.path.join(PASTA_MODELOS, f"{nome}.geo.json"), "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=1)
    with open(os.path.join(PASTA_ANIMACOES, f"{nome}.animation.json"), "w", encoding="utf-8") as f:
        json.dump({"format_version": "1.8.0", "animations": animacoes}, f, indent=1)
    img.save(os.path.join(PASTA_TEXTURAS, f"{nome}.png"))
    print(f"{nome}: textura {tw}x{th}, {len(ossos)} ossos")


# ------------------------------------------------------------- animações ---

def onda(amplitude, periodo, fase=0.0, eixo=0, base=(0, 0, 0)):
    """Expressão Molang de oscilação senoidal num eixo (graus ou unidades)."""
    vals = [str(v) for v in base]
    vals[eixo] = f"{base[eixo]} + math.sin((query.anim_time / {periodo}) * 360 + {fase}) * {amplitude}"
    return vals


# ================================================================ AGUMON ===

LARANJA = "#F4A62A"
LARANJA_ESC = "#D9821A"
CREME = "#FBE3A6"
VERDE = "#3FB54A"
BRANCO = "#F4F4F0"
ROXO = "#7B4FA0"
BOCA = "#5A2A1E"


def _animacoes_bipede(peso=1.0):
    """Animações de bípede. peso > 1 deixa tudo mais lento e com passos mais curtos (Digimon grandes)."""
    p = peso
    return {
        "idle": {
            "loop": True,
            "animation_length": 2.0 * p,
            "bones": {
                "body": {"position": onda(0.25 * p, 2.0 * p, eixo=1)},
                "head": {"rotation": onda(2, 2.0 * p, fase=60)},
                "tail": {"rotation": onda(6, 2.0 * p, eixo=1)},
                "tail_tip": {"rotation": onda(8, 2.0 * p, fase=45, eixo=1)},
                "arm_left": {"rotation": onda(3, 2.0 * p)},
                "arm_right": {"rotation": onda(3, 2.0 * p, fase=180)},
            },
        },
        "walk": {
            "loop": True,
            "animation_length": 0.8 * p,
            "bones": {
                "leg_left": {"rotation": onda(30 / p, 0.8 * p)},
                "leg_right": {"rotation": onda(30 / p, 0.8 * p, fase=180)},
                "arm_left": {"rotation": onda(20 / p, 0.8 * p, fase=180)},
                "arm_right": {"rotation": onda(20 / p, 0.8 * p)},
                "body": {"position": onda(0.5 * p, 0.4 * p, eixo=1),
                         "rotation": onda(3, 0.8 * p, eixo=2)},
                "head": {"rotation": onda(3, 0.4 * p)},
                "tail": {"rotation": onda(10, 0.8 * p, eixo=1)},
                "tail_tip": {"rotation": onda(12, 0.8 * p, fase=60, eixo=1)},
            },
        },
        # Golpe rápido: inclina o corpo, projeta a cabeça e os braços para a frente e volta.
        "attack": {
            "loop": False,
            "animation_length": 0.4,
            "bones": {
                "body": {"rotation": {"0.0": [0, 0, 0], "0.12": [12, 0, 0], "0.4": [0, 0, 0]}},
                "head": {"rotation": {"0.0": [0, 0, 0], "0.1": [-15, 0, 0], "0.2": [10, 0, 0], "0.4": [0, 0, 0]}},
                "arm_left": {"rotation": {"0.0": [0, 0, 0], "0.12": [-60, 0, -10], "0.4": [0, 0, 0]}},
                "arm_right": {"rotation": {"0.0": [0, 0, 0], "0.12": [-60, 0, 10], "0.4": [0, 0, 0]}},
                "tail": {"rotation": {"0.0": [0, 0, 0], "0.12": [-10, 0, 0], "0.4": [0, 0, 0]}},
            },
        },
    }


# ======================================================== FRESH / IN-TRAINING ===

def _animacoes_bolinha():
    """Bolinhas (Fresh/In-Training): respiram esticando e andam pulando."""
    return {
        "idle": {
            "loop": True,
            "animation_length": 1.6,
            "bones": {
                "body": {"scale": [
                    "1 + math.sin(query.anim_time / 1.6 * 360) * 0.04",
                    "1 - math.sin(query.anim_time / 1.6 * 360) * 0.05",
                    "1 + math.sin(query.anim_time / 1.6 * 360) * 0.04"]},
            },
        },
        "walk": {
            "loop": True,
            "animation_length": 0.5,
            "bones": {
                "body": {
                    "position": ["0", "math.abs(math.sin(query.anim_time / 0.5 * 180)) * 2.5", "0"],
                    "scale": ["1", "1 + math.abs(math.sin(query.anim_time / 0.5 * 180)) * 0.08", "1"],
                },
            },
        },
        "attack": {
            "loop": False,
            "animation_length": 0.3,
            "bones": {
                "body": {"scale": {"0.0": [1, 1, 1], "0.1": [1.15, 0.85, 1.15], "0.3": [1, 1, 1]}},
            },
        },
    }


def _animacoes_quadrupede():
    """Quadrúpedes: pernas em pares diagonais, cauda abanando, cabeça avançando no ataque."""
    return {
        "idle": {
            "loop": True,
            "animation_length": 2.0,
            "bones": {
                "body": {"position": onda(0.3, 2.0, eixo=1)},
                "head": {"rotation": onda(3, 2.0, fase=60)},
                "tail": {"rotation": onda(12, 1.0, eixo=1, base=(35, 0, 0))},
            },
        },
        "walk": {
            "loop": True,
            "animation_length": 0.6,
            "bones": {
                "leg_front_left": {"rotation": onda(28, 0.6)},
                "leg_back_right": {"rotation": onda(28, 0.6)},
                "leg_front_right": {"rotation": onda(28, 0.6, fase=180)},
                "leg_back_left": {"rotation": onda(28, 0.6, fase=180)},
                "body": {"position": onda(0.6, 0.3, eixo=1)},
                "head": {"rotation": onda(4, 0.3)},
                "tail": {"rotation": onda(15, 0.6, eixo=1, base=(25, 0, 0))},
            },
        },
        "attack": {
            "loop": False,
            "animation_length": 0.4,
            "bones": {
                "head": {"rotation": {"0.0": [0, 0, 0], "0.1": [-20, 0, 0], "0.22": [15, 0, 0], "0.4": [0, 0, 0]}},
                "body": {"position": {"0.0": [0, 0, 0], "0.15": [0, 0, -2], "0.4": [0, 0, 0]}},
            },
        },
    }


if __name__ == "__main__":
    import modelos_hd

    for nome in modelos_hd.TODOS:
        getattr(modelos_hd, nome)()
