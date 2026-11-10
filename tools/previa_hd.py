"""Gera modelos HD escolhidos e monta uma prévia lado a lado: python tools/previa_hd.py botamon koromon ..."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelos_hd
import visualizar
from PIL import Image

nomes = sys.argv[1:]
imgs = []
for n in nomes:
    getattr(modelos_hd, n)()
    p = os.path.join(visualizar.RAIZ, "tools", "previas", f"{n}_hd.png")
    visualizar.renderizar(n, p, angulo=-25, inclinacao=12, escala=16)
    imgs.append(Image.open(p))
h = max(i.height for i in imgs)
o = Image.new("RGBA", (sum(i.width for i in imgs) + 30 * len(imgs), h), (235, 240, 245, 255))
x = 0
for i in imgs:
    o.paste(i, (x, h - i.height))
    x += i.width + 30
saida = os.path.join(visualizar.RAIZ, "tools", "previas", "grupo_hd.png")
o.save(saida)
print(saida)
