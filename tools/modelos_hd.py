"""
Modelos no estilo HD (densidade 2): mais pixels por bloco, degradê, pelos, olhos expressivos.
Cores e detalhes seguem a arte oficial dos Digimon.
Usa o kit de pintura de estilo.py e o gerador de gerar_modelos.py.
"""
from estilo import (ESCURO, BRANCO, Pintura, detalhes, elipse, emblema_gabumon, faixas_curvas, olho,
                    regiao_pelo, segmentos, sorriso, tom)
from gerar_modelos import Cubo, Osso, _animacoes_bipede, gerar

HD = 2


def _garras_mao(x0, y0, z0, cor, espelhar=False):
    """Três garras 3D saindo da mão para baixo e um pouco à frente."""
    passo = 0.65 if not espelhar else -0.65
    return [Cubo([x0 + passo * k, y0, z0], [0.5, 1.3, 0.5], cor) for k in range(3)]


def _garras_pe(x0, y0, z0, cor, largura=3.0):
    """Três garras 3D na ponta do pé, apontando para a frente."""
    passo = (largura - 0.7) / 2
    return [Cubo([x0 + passo * k, y0, z0], [0.7, 0.9, 1.2], cor) for k in range(3)]


# ================================================================ AGUMON ===

def agumon():
    LAR = "#F6A12E"
    LAR_CLARO = "#FFC468"
    LAR_ESC = "#DE8628"
    NARINA = "#B05A1C"
    VERDE = "#22A776"
    GARRA = Pintura("#AEBECB", gradiente=0.3, ruido=2)
    BOCA = "#5A2A1E"

    def pele(*camadas):
        return Pintura(LAR, *camadas)

    barriga = pele(regiao_pelo(LAR_CLARO, 0.18, 0.0, 0.82, 0.92, tufo_cima=False))
    peito = pele(regiao_pelo(LAR_CLARO, 0.2, 0.25, 0.8, 1.0, tufo_cima=False))
    rosto = pele(
        olho(1, 1, VERDE, largura=6, altura=6),
        olho(11, 1, VERDE, espelhado=True, largura=6, altura=6),
        # leve sombra na testa, como a ruga da arte original
        detalhes([(i, 0, LAR_ESC) for i in range(7, 11)]),
    )

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 8, 0], "root", [
            Cubo([-4, 6, -3], [8, 5, 6], pele(), {"north": barriga}),
            Cubo([-3.5, 11, -2.5], [7, 4, 5], pele(), {"north": peito}),
        ]),
        Osso("head", [0, 15, -1], "body", [
            Cubo([-4.5, 15, -5.5], [9, 7, 8], pele(), {"north": rosto}),
            # Focinho com narinas no alto e mandíbula com sorriso de dentinhos
            Cubo([-3, 16.5, -9.5], [6, 2.5, 4.5], pele(),
                 {"north": pele(detalhes([(3, 1, NARINA), (4, 1, NARINA), (7, 1, NARINA), (8, 1, NARINA)]))}),
            Cubo([-3, 15, -9], [6, 1.5, 4], pele(),
                 {"north": pele(sorriso(BOCA, (2, 4, 7, 9), 12, curva=1))}),
        ]),
        Osso("arm_left", [4, 14, -1], "body", [
            Cubo([3.5, 10, -2], [2, 4, 2], pele()),
            Cubo([3.5, 9, -2.5], [2, 1.5, 2.5], Pintura(LAR_ESC)),
            *_garras_mao(3.55, 7.9, -3.1, GARRA),
        ]),
        Osso("arm_right", [-4, 14, -1], "body", [
            Cubo([-5.5, 10, -2], [2, 4, 2], pele()),
            Cubo([-5.5, 9, -2.5], [2, 1.5, 2.5], Pintura(LAR_ESC)),
            *_garras_mao(-4.05, 7.9, -3.1, GARRA, espelhar=True),
        ]),
        Osso("leg_left", [2.5, 7, 0], "root", [
            Cubo([1, 0, -2.5], [3, 7, 4], Pintura(LAR_ESC)),
            Cubo([1, 0, -4], [3, 1.5, 1.5], Pintura(LAR_ESC)),
            *_garras_pe(1.0, 0, -5.1, GARRA),
        ]),
        Osso("leg_right", [-2.5, 7, 0], "root", [
            Cubo([-4, 0, -2.5], [3, 7, 4], Pintura(LAR_ESC)),
            Cubo([-4, 0, -4], [3, 1.5, 1.5], Pintura(LAR_ESC)),
            *_garras_pe(-4.0, 0, -5.1, GARRA),
        ]),
        # Cauda em três segmentos que afinam, mais clara por baixo
        Osso("tail", [0, 8, 3], "body", [
            Cubo([-2, 6, 3], [4, 3, 5], pele(), {"down": Pintura(LAR_CLARO)}),
        ]),
        Osso("tail_tip", [0, 7.5, 8], "tail", [
            Cubo([-1.5, 6.3, 8], [3, 2.4, 4], pele(), {"down": Pintura(LAR_CLARO)}),
        ]),
        Osso("tail_end", [0, 7.5, 12], "tail_tip", [
            Cubo([-1, 6.6, 12], [2, 1.8, 3], pele(), {"down": Pintura(LAR_CLARO)}),
        ]),
    ]
    gerar("agumon", ossos, {f"animation.agumon.{n}": a for n, a in _animacoes_bipede().items()}, densidade=HD)


# =============================================================== GABUMON ===

def gabumon():
    PELO = "#E4EAF6"      # pele de Garurumon: branco-azulado
    LISTRA = "#3B4FA0"    # listras azul-escuras
    AMARELO = "#F3CE48"   # corpo e focinho
    CHIFRE = "#EED37E"
    VERMELHO = "#B5332A"
    GARRA = Pintura("#CF4A86", gradiente=0.3, ruido=2)
    EMBLEMA_AZUL = "#8FD6EA"
    EMBLEMA_ROSA = "#E0508C"

    def pelo(*camadas):
        return Pintura(PELO, *camadas, gradiente=0.12)

    def listrado(quantidade=3, curva=2):
        return pelo(faixas_curvas(LISTRA, quantidade, 2, curva))

    rosto = pelo(
        faixas_curvas(LISTRA, 1, 2, 2, inicio=0.05, fim=0.05),
        olho(1, 3, VERMELHO, largura=5, altura=5),
        olho(12, 3, VERMELHO, espelhado=True, largura=5, altura=5),
        # faixas escuras acima dos olhos, como na pele do Garurumon
        detalhes([(i, 2, LISTRA) for i in range(0, 7)] + [(i, 2, LISTRA) for i in range(11, 18)]),
    )
    focinho = Pintura(AMARELO, detalhes(
        [(i, j, ESCURO) for i in range(4, 8) for j in range(0, 2)]          # nariz grande
        + [(i, 4, "#3A1E14") for i in range(0, 12)]                          # boca
        + [(i, 5, BRANCO) for i in range(0, 12, 2)]                          # dentes em zigue-zague
        + [(i, 3, BRANCO) for i in range(1, 12, 2)]
    ))
    # Corpo amarelo com o emblema na barriga; a pele cai pelos lados
    barriga = Pintura(AMARELO,
                      regiao_pelo(PELO, 0.0, 0.0, 0.16, 1.0, tufo_cima=False),
                      regiao_pelo(PELO, 0.84, 0.0, 1.0, 1.0, tufo_cima=False),
                      emblema_gabumon(EMBLEMA_AZUL, EMBLEMA_ROSA))
    peito = Pintura(AMARELO,
                    regiao_pelo(PELO, 0.0, 0.0, 0.18, 1.0, tufo_cima=False),
                    regiao_pelo(PELO, 0.82, 0.0, 1.0, 1.0, tufo_cima=False))
    orelha = listrado(1, 1)
    orelha_dentro = Pintura(tom(PELO, -0.08), gradiente=0.1)

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 8, 0], "root", [
            Cubo([-4, 6, -3], [8, 5, 6], listrado(2), {"north": barriga}),
            Cubo([-3.5, 11, -2.5], [7, 4, 5], listrado(2), {"north": peito}),
        ]),
        Osso("head", [0, 15, -1], "body", [
            Cubo([-4.5, 15, -5.5], [9, 7, 8], listrado(3), {"north": rosto}),
            # Chifre longo em espiral
            Cubo([-0.75, 22, -4.5], [1.5, 4, 1.5], Pintura(CHIFRE, segmentos("#C9A84E", 4))),
            Cubo([-0.4, 26, -4.15], [0.8, 1.5, 0.8], Pintura(CHIFRE)),
            # Focinho amarelo grande com nariz preto e dentes
            Cubo([-3, 15, -9], [6, 3.5, 3.5], Pintura(AMARELO), {"north": focinho}),
            Cubo([4.5, 19, -3], [2, 3, 1], orelha, {"north": orelha_dentro},
                 rotacao=[0, 0, -30], pivo=[4.5, 19, -2.5]),
            Cubo([-6.5, 19, -3], [2, 3, 1], orelha, {"north": orelha_dentro},
                 rotacao=[0, 0, 30], pivo=[-4.5, 19, -2.5]),
        ]),
        Osso("arm_left", [4, 14, -1], "body", [
            Cubo([3.5, 9, -2], [2, 5, 2], listrado(2, 1)),
            Cubo([3.4, 7.8, -2.6], [2.2, 1.4, 2.6], pelo()),
            *_garras_mao(3.5, 6.8, -3.1, GARRA),
        ]),
        Osso("arm_right", [-4, 14, -1], "body", [
            Cubo([-5.5, 9, -2], [2, 5, 2], listrado(2, 1)),
            Cubo([-5.6, 7.8, -2.6], [2.2, 1.4, 2.6], pelo()),
            *_garras_mao(-4.0, 6.8, -3.1, GARRA, espelhar=True),
        ]),
        Osso("leg_left", [2.5, 7, 0], "root", [
            Cubo([1, 0, -2.5], [3, 7, 4], listrado(2, 1)),
            Cubo([1, 0, -4], [3, 1.5, 1.5], pelo()),
            *_garras_pe(1.0, 0, -5.1, GARRA),
        ]),
        Osso("leg_right", [-2.5, 7, 0], "root", [
            Cubo([-4, 0, -2.5], [3, 7, 4], listrado(2, 1)),
            Cubo([-4, 0, -4], [3, 1.5, 1.5], pelo()),
            *_garras_pe(-4.0, 0, -5.1, GARRA),
        ]),
        Osso("tail", [0, 8, 3], "body", [Cubo([-2, 6, 3], [4, 3, 5], listrado(2, 1))]),
        Osso("tail_tip", [0, 7.5, 8], "tail", [Cubo([-1.5, 6.3, 8], [3, 2.4, 4], listrado(1, 1))]),
        Osso("tail_end", [0, 7.5, 12], "tail_tip", [Cubo([-1, 6.6, 12], [2, 1.8, 3], pelo())]),
    ]
    gerar("gabumon", ossos, {f"animation.gabumon.{n}": a for n, a in _animacoes_bipede().items()}, densidade=HD)


# ======================================================= BEBÊS (Fresh / In-Training) ===

from estilo import boca_aberta, brilho, olho_redondo  # noqa: E402
from gerar_modelos import _animacoes_bolinha  # noqa: E402


def _bolinha(cor_corpo, rosto, largura=8.0, altura=5.5, extras=(), topo=None, base=None, lados=None):
    """Corpo de bolinha arredondada: núcleo + uma camada menor em cima e outra embaixo."""
    lados = lados or cor_corpo
    meio = largura / 2
    return [
        Cubo([-meio, 0.5, -4], [largura, altura, 8], lados, {"north": rosto, "up": topo or lados}),
        Cubo([-meio + 0.5, 0, -3.5], [largura - 1, 0.5, 7], base or lados),
        Cubo([-meio + 0.5, 0.5 + altura, -3.5], [largura - 1, 1, 7], topo or lados),
        *extras,
    ]


def botamon():
    PRETO = "#202024"
    AMBAR = "#E8961E"
    pelo = Pintura(PRETO, ruido=12, gradiente=0.2)
    rosto = Pintura(PRETO, olho_redondo(1, 3, 6, AMBAR, pupila=2),
                    olho_redondo(9, 3, 6, AMBAR, pupila=2, espelhado=True), ruido=12, gradiente=0.2)
    orelhas = [
        Cubo([-3.6, 6.4, -1.2], [2.2, 2.2, 1.6], pelo, rotacao=[0, 0, 18], pivo=[-2.5, 6.5, -0.4]),
        Cubo([1.4, 6.4, -1.2], [2.2, 2.2, 1.6], pelo, rotacao=[0, 0, -18], pivo=[2.5, 6.5, -0.4]),
    ]
    ossos = [Osso("root", [0, 0, 0]), Osso("body", [0, 0, 0], "root", _bolinha(pelo, rosto, extras=orelhas))]
    gerar("botamon", ossos, {f"animation.botamon.{n}": a for n, a in _animacoes_bolinha().items()}, densidade=HD)


def koromon():
    ROSA = "#F4C6D0"
    ROSA_ESC = "#E8A6B6"
    VINHO = "#9A1E3E"
    pele = Pintura(ROSA, gradiente=0.14)
    rosto = Pintura(ROSA, olho_redondo(2, 1, 6, VINHO, pupila=2),
                    olho_redondo(10, 1, 6, VINHO, pupila=2, espelhado=True),
                    boca_aberta(5, 6, 8, 4), gradiente=0.14)
    orelha = Pintura(ROSA_ESC, gradiente=0.2)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 0, 0], "root", _bolinha(pele, rosto, largura=9)),
        # Orelhas longas e finas que caem para trás (animadas)
        Osso("ear_left", [2.5, 7, 1], "body", [Cubo([1.9, 6.7, 0.5], [1.2, 0.8, 9], orelha)], rotacao=[-35, 0, 0]),
        Osso("ear_right", [-2.5, 7, 1], "body", [Cubo([-3.1, 6.7, 0.5], [1.2, 0.8, 9], orelha)], rotacao=[-35, 0, 0]),
    ]
    animacoes = _animacoes_bolinha()
    from gerar_modelos import onda
    animacoes["idle"]["bones"]["ear_left"] = {"rotation": onda(6, 1.6, base=(-35, 0, 0))}
    animacoes["idle"]["bones"]["ear_right"] = {"rotation": onda(6, 1.6, fase=90, base=(-35, 0, 0))}
    animacoes["walk"]["bones"]["ear_left"] = {"rotation": onda(15, 0.5, base=(-35, 0, 0))}
    animacoes["walk"]["bones"]["ear_right"] = {"rotation": onda(15, 0.5, fase=180, base=(-35, 0, 0))}
    gerar("koromon", ossos, {f"animation.koromon.{n}": a for n, a in animacoes.items()}, densidade=HD)


def punimon():
    VERMELHO = "#E25866"
    geleia = Pintura(VERMELHO, brilho(0.3, 0.3, 0.25, 0.2), gradiente=0.22, ruido=2)
    rosto = Pintura(VERMELHO,
                    olho_redondo(2, 3, 5, BRANCO, pupila=2, cilios=True),
                    olho_redondo(9, 3, 5, BRANCO, pupila=2, cilios=True, espelhado=True),
                    brilho(0.25, 0.2, 0.2, 0.15), gradiente=0.22, ruido=2)
    orelha = Pintura(VERMELHO, gradiente=0.2, ruido=2)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 0, 0], "root", _bolinha(geleia, rosto, altura=5)),
        # Orelhinhas de gato (o osso se chama "feelers" por causa das animações)
        Osso("feelers", [0, 6, 0], "body", [
            Cubo([-3.4, 5.9, -1.2], [2, 2, 1.6], orelha, rotacao=[0, 0, 15], pivo=[-2.4, 6, -0.4]),
            Cubo([1.4, 5.9, -1.2], [2, 2, 1.6], orelha, rotacao=[0, 0, -15], pivo=[2.4, 6, -0.4]),
        ]),
    ]
    from gerar_modelos import onda
    animacoes = _animacoes_bolinha()
    animacoes["idle"]["bones"]["feelers"] = {"rotation": onda(4, 1.6, eixo=2)}
    animacoes["walk"]["bones"]["feelers"] = {"rotation": onda(8, 0.5, eixo=2)}
    gerar("punimon", ossos, {f"animation.punimon.{n}": a for n, a in animacoes.items()}, densidade=HD)


def tsunomon():
    LARANJA = "#F2A43C"
    CREME = "#FBEBD9"
    CHIFRE = "#586270"
    pelo = Pintura(LARANJA, ruido=7)
    rosto = Pintura(LARANJA,
                    regiao_pelo(CREME, 0.0, 0.32, 1.0, 1.0, tufo_cima=True),
                    olho_redondo(3, 3, 4, "#B04A2A", esclera=BRANCO, pupila=1, cilios=True),
                    olho_redondo(11, 3, 4, "#B04A2A", esclera=BRANCO, pupila=1, cilios=True, espelhado=True),
                    detalhes([(8, 8, "#5A3A2A"), (9, 9, "#5A3A2A"), (10, 8, "#5A3A2A")]),
                    ruido=7)
    lado = Pintura(LARANJA, regiao_pelo(CREME, 0.0, 0.55, 1.0, 1.0), ruido=7)
    chifre = Pintura(CHIFRE, gradiente=0.3, ruido=3)
    chifre_curvo = [
        Cubo([-1, 6.4, -1.5], [2, 2.5, 2], chifre),
        Cubo([-0.8, 8.9, -1.0], [1.6, 2.5, 1.6], chifre),
        Cubo([-0.6, 11.4, -0.3], [1.2, 2, 1.2], chifre),
        Cubo([-0.4, 13.4, 0.6], [0.8, 1.5, 0.8], chifre),
    ]
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 0, 0], "root", _bolinha(lado, rosto, largura=9, topo=pelo, base=Pintura(CREME), extras=chifre_curvo)),
        # Ossos vazios: mantêm as animações compartilhadas válidas
        Osso("ear_left", [3.5, 6, 0], "body"),
        Osso("ear_right", [-3.5, 6, 0], "body"),
    ]
    gerar("tsunomon", ossos, {f"animation.tsunomon.{n}": a for n, a in _animacoes_bolinha().items()}, densidade=HD)


# ============================================================ LINHA AGUMON (grandes) ===

from estilo import listras, listras_laterais, painel  # noqa: E402

GARRA_BRANCA = Pintura("#F2F2EE", gradiente=0.3, ruido=2)


def _garras(x0, y0, z0, quantidade, passo, tamanho, pintura):
    """Fileira de garras 3D (cubos pequenos) com espaçamento em X."""
    return [Cubo([x0 + passo * k, y0, z0], tamanho, pintura) for k in range(quantidade)]


def _chifre_curvo(x, y, z, lado, pintura, escala=1.0):
    """Chifre que sai para o lado e curva para trás e para cima (Greymon, MetalGreymon)."""
    s = escala
    return [
        Cubo([x, y, z], [2 * s, 2 * s, 5 * s], pintura),
        Cubo([x + lado * 0.7 * s, y + 2 * s, z + 3 * s], [1.6 * s, 2.5 * s, 4 * s], pintura),
        Cubo([x + lado * 1.3 * s, y + 4.5 * s, z + 6 * s], [1.2 * s, 2.5 * s, 3 * s], pintura),
        Cubo([x + lado * 1.6 * s, y + 7 * s, z + 8 * s], [0.8 * s, 2 * s, 2 * s], pintura),
    ]


def greymon():
    LAR = "#F29A34"
    LAR_CLARO = "#FBBF6E"
    LAR_ESC = "#D97E26"
    LISTRA = "#2C3E7C"
    CAPACETE = "#5B3B2C"
    CHIFRE = Pintura("#3E3A38", gradiente=0.3, ruido=3)
    VERDE = "#2FA05A"

    pele = Pintura(LAR, listras_laterais(LISTRA, 3, 0.4))
    costas = Pintura(LAR, faixas_curvas(LISTRA, 3, 2, 2))
    membro = Pintura(LAR, faixas_curvas(LISTRA, 2, 2, 1, inicio=0.3, fim=0.75))
    barriga = Pintura(LAR, regiao_pelo(LAR_CLARO, 0.2, 0.0, 0.8, 0.95, tufo_cima=False), listras_laterais(LISTRA, 2, 0.15))
    capacete = Pintura(CAPACETE, painel(tom(CAPACETE, -0.25)), gradiente=0.2)
    cranio = Pintura(LAR, olho(1, 4, VERDE, raiva=True, largura=5, altura=4),
                     olho(18, 4, VERDE, raiva=True, espelhado=True, largura=5, altura=4))
    focinho = Pintura(LAR, detalhes([(i, 6, BRANCO) for i in range(1, 18, 2)]))
    mandibula = Pintura(LAR_CLARO, detalhes([(i, 0, BRANCO) for i in range(2, 18, 2)]))

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 15, 0], "root", [
            Cubo([-8, 14, -5.5], [16, 9, 13], pele, {"north": barriga, "up": costas, "south": costas}),
            Cubo([-7, 23, -6.5], [14, 8, 11], pele, {"north": barriga, "up": costas, "south": costas}),
        ]),
        Osso("head", [0, 28, -4], "body", [
            Cubo([-4, 27, -9], [8, 5, 6], pele),
            Cubo([-6, 30, -15], [12, 8, 12], pele, {"north": cranio}),
            Cubo([-4.5, 31.5, -22], [9, 3.5, 7], pele, {"north": focinho}),
            Cubo([-4.5, 29, -21], [9, 2.5, 8], Pintura(LAR_CLARO), {"north": mandibula}),
            # Capacete de crânio marrom cobrindo o topo da cabeça e o focinho
            Cubo([-6.5, 36, -16], [13, 4, 13], capacete),
            Cubo([-6.8, 32, -14], [0.8, 5, 9], capacete),
            Cubo([6, 32, -14], [0.8, 5, 9], capacete),
            Cubo([-4.8, 34.5, -22.3], [9.6, 1.5, 7], capacete),
            Cubo([-1, 36, -21], [2, 3, 2], CHIFRE),
            Cubo([-0.6, 39, -20.6], [1.2, 1.5, 1.2], CHIFRE),
            *_chifre_curvo(6, 38, -11, 1, CHIFRE),
            *_chifre_curvo(-8, 38, -11, -1, CHIFRE),
        ]),
        Osso("arm_left", [8, 28, -3], "body", [
            Cubo([7.5, 20, -5], [4, 9, 4], membro),
            Cubo([7.5, 18.5, -6], [4, 2, 3], Pintura(LAR_ESC)),
            *_garras(7.7, 16.8, -6.6, 3, 1.25, [0.8, 1.8, 0.8], GARRA_BRANCA),
        ]),
        Osso("arm_right", [-8, 28, -3], "body", [
            Cubo([-11.5, 20, -5], [4, 9, 4], membro),
            Cubo([-11.5, 18.5, -6], [4, 2, 3], Pintura(LAR_ESC)),
            *_garras(-11.3, 16.8, -6.6, 3, 1.25, [0.8, 1.8, 0.8], GARRA_BRANCA),
        ]),
        Osso("leg_left", [5, 16, 1], "root", [
            Cubo([2, 8, -3.5], [7, 8, 8], membro),
            Cubo([2.5, 0, -2.5], [6, 8, 6], membro),
            Cubo([2, 0, -5], [7, 2, 3], Pintura(LAR_ESC)),
            *_garras(2.3, 0, -6.4, 3, 2.3, [1.2, 1.2, 1.6], GARRA_BRANCA),
        ]),
        Osso("leg_right", [-5, 16, 1], "root", [
            Cubo([-9, 8, -3.5], [7, 8, 8], membro),
            Cubo([-8.5, 0, -2.5], [6, 8, 6], membro),
            Cubo([-9, 0, -5], [7, 2, 3], Pintura(LAR_ESC)),
            *_garras(-8.7, 0, -6.4, 3, 2.3, [1.2, 1.2, 1.6], GARRA_BRANCA),
        ]),
        Osso("tail", [0, 19, 7], "body", [Cubo([-4.5, 14, 6], [9, 8, 10], pele, {"up": costas})]),
        Osso("tail_tip", [0, 17.5, 16], "tail", [Cubo([-3, 15, 16], [6, 5, 10], pele, {"up": costas})]),
        Osso("tail_end", [0, 17, 26], "tail_tip", [Cubo([-1.8, 15.5, 26], [3.6, 3, 8], pele, {"up": costas})]),
    ]
    gerar("greymon", ossos, {f"animation.greymon.{n}": a for n, a in _animacoes_bipede(peso=1.6).items()}, densidade=HD)


def metalgreymon():
    LAR = "#F29A34"
    LAR_CLARO = "#FBBF6E"
    LAR_ESC = "#D97E26"
    LISTRA = "#2C3E7C"
    METAL = "#A2AAB4"
    METAL_ESC = "#6E767F"
    CABELO = "#C8442A"
    ROXO = "#5E3E8E"
    AZUL_OLHO = "#3A8AE8"
    VERDE = "#2FA05A"

    pele = Pintura(LAR, listras_laterais(LISTRA, 3, 0.4))
    costas = Pintura(LAR, faixas_curvas(LISTRA, 3, 2, 2))
    membro = Pintura(LAR, faixas_curvas(LISTRA, 2, 2, 1, inicio=0.3, fim=0.75))
    metal = Pintura(METAL, painel(METAL_ESC), gradiente=0.25, ruido=3)
    metal_liso = Pintura(METAL, gradiente=0.25, ruido=3)
    escuro = Pintura(METAL_ESC, gradiente=0.25, ruido=3)
    cranio = Pintura(LAR, olho(1, 4, AZUL_OLHO, raiva=True, largura=5, altura=4),
                     olho(18, 4, VERDE, raiva=True, espelhado=True, largura=5, altura=4))
    boca = Pintura("#5A1E1E", detalhes([(i, 0, BRANCO) for i in range(1, 18, 2)] + [(i, 1, BRANCO) for i in range(1, 18, 4)]))
    membrana = Pintura(ROXO, listras(tom(ROXO, -0.3), 3, 0.9, 1), gradiente=0.25)
    cabelo = Pintura(CABELO, gradiente=0.3, ruido=6)
    barriga = Pintura(LAR, regiao_pelo(LAR_CLARO, 0.2, 0, 0.8, 0.95, tufo_cima=False))

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 16, 0], "root", [
            Cubo([-8, 14, -5.5], [16, 9, 13], pele, {"north": barriga, "up": costas, "south": costas}),
            Cubo([-7, 23, -6.5], [14, 8, 11], pele, {"up": costas, "south": costas}),
            # Faixa de armadura de metal no peito
            Cubo([-7.6, 23.5, -7], [15.2, 5, 12], metal),
        ]),
        Osso("head", [0, 31, -4], "body", [
            Cubo([-4, 30, -9], [8, 5, 6], pele),
            Cubo([-6, 33, -15], [12, 8, 12], pele, {"north": cranio}),
            # Mandíbulas de metal entreabertas mostrando os dentes
            Cubo([-4.5, 35, -22], [9, 3, 7], metal_liso,
                 {"north": Pintura(METAL, detalhes([(i, 5, BRANCO) for i in range(1, 18, 2)]))}),
            Cubo([-4.5, 31.5, -21], [9, 2.5, 8], metal_liso, {"north": boca}),
            # Capacete de metal com chifres escuros e cabelo vermelho atrás
            Cubo([-6.5, 39.5, -16], [13, 3.5, 13], metal),
            Cubo([-6.8, 35, -14], [0.8, 5, 9], metal_liso),
            Cubo([-1, 38, -21], [2, 3, 2], escuro),
            *_chifre_curvo(6, 41, -11, 1, escuro),
            *_chifre_curvo(-8, 41, -11, -1, escuro),
            Cubo([-3, 38, -4], [6, 5, 3], cabelo),
            Cubo([-2, 36, -1.5], [4, 6, 2.5], cabelo),
        ]),
        # Braço esquerdo: a enorme garra de metal (Trident Arm)
        Osso("arm_left", [8, 28, -3], "body", [
            Cubo([7.5, 20, -5], [5, 9, 5], metal),
            Cubo([7, 15, -7], [6, 5, 7], escuro),
            *_garras(7.3, 9, -7.5, 3, 2, [1.3, 6, 1.3], metal_liso),
        ]),
        Osso("arm_right", [-8, 28, -3], "body", [
            Cubo([-12, 20, -5], [4, 9, 4], membro),
            Cubo([-12, 18.5, -6], [4, 2, 3], Pintura(LAR_ESC)),
            *_garras(-11.8, 16.8, -6.6, 3, 1.25, [0.8, 1.8, 0.8], GARRA_BRANCA),
        ]),
        Osso("wing_left", [3, 30, 5], "body", [
            Cubo([3, 32, 5], [1, 1.5, 17], escuro),
            Cubo([3.2, 17, 5.5], [0.6, 15, 16], membrana),
        ], rotacao=[0, -25, -10]),
        Osso("wing_right", [-3, 30, 5], "body", [
            Cubo([-4, 32, 5], [1, 1.5, 17], escuro),
            Cubo([-3.8, 17, 5.5], [0.6, 15, 16], membrana),
        ], rotacao=[0, 25, 10]),
        Osso("leg_left", [5, 16, 1], "root", [
            Cubo([2, 8, -3.5], [7, 8, 8], membro),
            Cubo([2.5, 0, -2.5], [6, 8, 6], membro),
            Cubo([2, 0, -5], [7, 2, 3], Pintura(LAR_ESC)),
            *_garras(2.3, 0, -6.4, 3, 2.3, [1.2, 1.2, 1.6], GARRA_BRANCA),
        ]),
        Osso("leg_right", [-5, 16, 1], "root", [
            Cubo([-9, 8, -3.5], [7, 8, 8], membro),
            Cubo([-8.5, 0, -2.5], [6, 8, 6], membro),
            Cubo([-9, 0, -5], [7, 2, 3], Pintura(LAR_ESC)),
            *_garras(-8.7, 0, -6.4, 3, 2.3, [1.2, 1.2, 1.6], GARRA_BRANCA),
        ]),
        Osso("tail", [0, 20, 7], "body", [Cubo([-4.5, 15, 7], [9, 8, 10], pele, {"up": costas})]),
        Osso("tail_tip", [0, 17.5, 17], "tail", [Cubo([-3, 15, 17], [6, 5, 10], pele, {"up": costas})]),
        Osso("tail_end", [0, 17, 27], "tail_tip", [Cubo([-1.8, 15.5, 27], [3.6, 3, 8], pele, {"up": costas})]),
    ]
    from gerar_modelos import onda
    animacoes = _animacoes_bipede(peso=1.8)
    for nome, fase in (("wing_left", 0), ("wing_right", 180)):
        base = (0, -25, -10) if nome == "wing_left" else (0, 25, 10)
        animacoes["idle"]["bones"][nome] = {"rotation": onda(4, 3.6, fase=fase, eixo=2, base=base)}
        animacoes["walk"]["bones"][nome] = {"rotation": onda(8, 1.44, fase=fase, eixo=2, base=base)}
    gerar("metalgreymon", ossos, {f"animation.metalgreymon.{n}": a for n, a in animacoes.items()}, densidade=HD)


def wargreymon():
    OURO = "#E8C24A"
    OURO_ESC = "#B8922A"
    PRATA = "#C9CFD6"
    PRATA_ESC = "#8E959D"
    VERMELHO = "#B83A2A"
    LAR = "#F2A23A"
    MARINHO = "#2E3A6E"
    CABELO = "#B8442A"
    VERDE = "#2FA05A"

    ouro = Pintura(OURO, painel(OURO_ESC), gradiente=0.25, ruido=3)
    ouro_liso = Pintura(OURO, gradiente=0.25, ruido=3)
    prata = Pintura(PRATA, painel(PRATA_ESC), gradiente=0.25, ruido=3)
    prata_lisa = Pintura(PRATA, gradiente=0.3, ruido=3)
    vermelho = Pintura(VERMELHO, gradiente=0.2, ruido=3)
    pele = Pintura(LAR)
    # Peitoral prateado com as tiras vermelhas cruzadas
    tiras = []
    for i in range(2, 18):
        for dy in (2, 3):
            tiras += [(i, i // 2 + dy, VERMELHO), (19 - i, i // 2 + dy, VERMELHO)]
    peito = Pintura(PRATA, painel(PRATA_ESC), detalhes(tiras), gradiente=0.25, ruido=3)
    # Elmo prateado com a fenda mostrando o rosto laranja e os olhos verdes
    rosto = [(i, j, LAR) for i in range(2, 12) for j in range(4, 8)]
    rosto += [(3, 5, BRANCO), (4, 5, VERDE), (4, 6, VERDE), (10, 5, BRANCO), (9, 5, VERDE), (9, 6, VERDE)]
    rosto += [(i, 11, LAR) for i in range(4, 10)]
    elmo = Pintura(PRATA, detalhes(rosto), gradiente=0.25, ruido=3)
    escudo = Pintura(MARINHO, painel(OURO), gradiente=0.2, ruido=3)
    cabelo = Pintura(CABELO, gradiente=0.3, ruido=6)
    perna = Pintura(PRATA, faixas_curvas(VERMELHO, 1, 3, 0, inicio=0.45, fim=0.45), gradiente=0.25, ruido=3)

    def ombreira(x, lado):
        return [
            Cubo([x, 20.5, -4], [5.5, 6, 8], ouro),
            Cubo([x + 2 + lado * 0.3, 26.5, -1], [1.6, 5, 1.6], ouro_liso),
            Cubo([x + 2.2 + lado * 0.3, 31.5, -0.8], [1.2, 1.5, 1.2], vermelho),
        ]

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 14, 0], "root", [
            Cubo([-4, 13, -2.5], [8, 3, 5], Pintura(MARINHO)),
            Cubo([-5, 16, -3], [10, 9, 6], prata, {"north": peito}),
            *ombreira(5, 1),
            *ombreira(-10.5, -1),
        ]),
        # Os dois escudos Brave Shield nas costas
        Osso("shield", [0, 20, 3], "body", [
            Cubo([2.5, 12, 3.5], [7, 16, 1.5], escudo, rotacao=[0, -20, 0], pivo=[3, 20, 4]),
            Cubo([-9.5, 12, 3.5], [7, 16, 1.5], escudo, rotacao=[0, 20, 0], pivo=[-3, 20, 4]),
        ]),
        Osso("head", [0, 25, -0.5], "body", [
            Cubo([-3.5, 25, -4], [7, 7, 7], prata_lisa, {"north": elmo}),
            Cubo([-0.5, 29.5, -5.5], [1, 2, 2], prata_lisa),
            Cubo([-3, 32, -2], [1.5, 3.5, 1.5], prata_lisa),
            Cubo([1.5, 32, -2], [1.5, 3.5, 1.5], prata_lisa),
            Cubo([-3, 24, 3], [6, 7, 2.5], cabelo),
            Cubo([-2, 21, 4], [4, 4, 2], cabelo),
        ]),
        # Manoplas douradas com as garras Dramon Destroyer
        Osso("arm_left", [6.5, 23, 0], "body", [
            Cubo([5, 17, -1.5], [3, 6, 3], pele),
            Cubo([4.5, 11.5, -2.5], [4.5, 6, 5], ouro),
            *_garras(4.7, 6.5, -2.8, 3, 1.4, [1, 5, 1], prata_lisa),
        ]),
        Osso("arm_right", [-6.5, 23, 0], "body", [
            Cubo([-8, 17, -1.5], [3, 6, 3], pele),
            Cubo([-9, 11.5, -2.5], [4.5, 6, 5], ouro),
            *_garras(-8.8, 6.5, -2.8, 3, 1.4, [1, 5, 1], prata_lisa),
        ]),
        Osso("leg_left", [2.5, 14, 0], "root", [
            Cubo([0.5, 7, -2], [4, 7, 4], pele),
            Cubo([0.6, 1.5, -2.2], [3.8, 5.5, 4.2], perna),
            Cubo([0.5, 0, -4], [4, 1.5, 5], pele),
            *_garras(0.6, 0, -5, 3, 1.4, [0.9, 1, 1.2], GARRA_BRANCA),
        ]),
        Osso("leg_right", [-2.5, 14, 0], "root", [
            Cubo([-4.5, 7, -2], [4, 7, 4], pele),
            Cubo([-4.4, 1.5, -2.2], [3.8, 5.5, 4.2], perna),
            Cubo([-4.5, 0, -4], [4, 1.5, 5], pele),
            *_garras(-4.4, 0, -5, 3, 1.4, [0.9, 1, 1.2], GARRA_BRANCA),
        ]),
        Osso("tail", [0, 14, 2.5], "body", [Cubo([-1, 12, 2.5], [2, 2, 5], pele)]),
        Osso("tail_tip", [0, 13, 7.5], "tail", [Cubo([-0.75, 12.25, 7.5], [1.5, 1.5, 2], pele)]),
    ]
    gerar("wargreymon", ossos, {f"animation.wargreymon.{n}": a for n, a in _animacoes_bipede(peso=1.0).items()}, densidade=HD)


# ============================================================ LINHA GABUMON (grandes) ===

from estilo import caveira, costura, faixa  # noqa: E402
from gerar_modelos import _animacoes_quadrupede  # noqa: E402


def _espinhos(base_x, y, z, quantidade, passo, pintura, ponta, altura=4.0, inclinacao=-30):
    """Mechas espetadas de pelo/juba (com ponta colorida), inclinadas para trás."""
    cubos = []
    for k in range(quantidade):
        x = base_x + passo * k
        cubos.append(Cubo([x, y, z], [1.6, altura, 1.6], pintura, rotacao=[inclinacao, 0, 0], pivo=[x + 0.8, y, z + 0.8]))
        cubos.append(Cubo([x + 0.3, y + altura, z + 0.3], [1, 1.2, 1], ponta, rotacao=[inclinacao, 0, 0], pivo=[x + 0.8, y, z + 0.8]))
    return cubos


def garurumon():
    PELO = "#EEF0FA"
    LISTRA = "#5B4CA8"
    GARRA = Pintura("#C23C7C", gradiente=0.3, ruido=2)
    BOCA = "#B8283A"
    AMARELO = "#E8B820"

    def pelo(*camadas):
        return Pintura(PELO, *camadas, gradiente=0.12)

    lado = pelo(listras(LISTRA, 4, 0.65, 3))
    costas = pelo(listras_laterais(LISTRA, 5, 0.42))
    perna = pelo(faixas_curvas(LISTRA, 2, 2, 1, inicio=0.2, fim=0.6))
    ponta = Pintura(LISTRA, gradiente=0.2)
    cabeca = pelo(faixas_curvas(LISTRA, 1, 2, 2, inicio=0.05, fim=0.05),
                  olho(1, 5, AMARELO, raiva=True, largura=5, altura=4),
                  olho(12, 5, AMARELO, raiva=True, espelhado=True, largura=5, altura=4))
    focinho = pelo(detalhes([(i, j, ESCURO) for i in range(4, 8) for j in range(0, 2)]))
    mandibula = Pintura(BOCA, detalhes([(1, 0, BRANCO), (10, 0, BRANCO), (2, 0, BRANCO), (9, 0, BRANCO)]))

    def pata(x, z, frente=True):
        larg = 3.5 if frente else 4.5
        return [
            Cubo([x, 1.5, z], [larg, 9, larg], perna),
            Cubo([x, 0, z - 1], [larg, 1.5, larg + 0.5], pelo()),
            *[Cubo([x + 0.2 + (larg - 1.1) / 2 * k, 0, z - 2.2], [0.8, 1, 1.3], GARRA) for k in range(3)],
        ]

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 14, 0], "root", [
            Cubo([-5.5, 9, -10], [11, 10, 20], lado, {"up": costas, "down": pelo()}),
            Cubo([-6, 8, -12], [12, 11, 4], pelo(regiao_pelo(tom(PELO, -0.04), 0.0, 0.0, 1.0, 1.0)), {"up": costas}),
            # Juba espetada no pescoço e nas costas
            *_espinhos(-4, 18, -11, 5, 1.8, pelo(), ponta, altura=4, inclinacao=-35),
        ]),
        Osso("head", [0, 17, -12], "body", [
            Cubo([-4.5, 14, -20], [9, 9, 8], pelo(listras(LISTRA, 3, 0.5, 2)), {"north": cabeca}),
            Cubo([-3, 15, -26], [6, 3.5, 6], pelo(), {"north": focinho}),
            Cubo([-2.8, 13, -25.5], [5.6, 2, 5.5], pelo(), {"up": mandibula, "north": Pintura(BOCA)}),
            Cubo([-4, 23, -15], [2, 3.5, 2], pelo(), {"north": Pintura(tom(PELO, -0.1))}),
            Cubo([2, 23, -15], [2, 3.5, 2], pelo(), {"north": Pintura(tom(PELO, -0.1))}),
            *_espinhos(-3, 22, -13, 4, 1.8, pelo(), ponta, altura=3.5, inclinacao=-50),
        ]),
        Osso("leg_front_left", [3, 10, -7], "root", pata(1.5, -8.5)),
        Osso("leg_front_right", [-3, 10, -7], "root", pata(-5, -8.5)),
        Osso("leg_back_left", [3, 10, 7], "root", pata(1, 5, frente=False)),
        Osso("leg_back_right", [-3, 10, 7], "root", pata(-5.5, 5, frente=False)),
        Osso("tail", [0, 17, 10], "body", [
            Cubo([-1.5, 15.5, 10], [3, 3, 9], pelo(listras(LISTRA, 2, 0.6, 2))),
            Cubo([-1.2, 15.8, 19], [2.4, 2.4, 5], pelo(listras(LISTRA, 1, 0.6, 2))),
            Cubo([-1, 16, 24], [2, 2, 3], ponta),
        ], rotacao=[35, 0, 0]),
    ]
    gerar("garurumon", ossos, {f"animation.garurumon.{n}": a for n, a in _animacoes_quadrupede().items()}, densidade=HD)


def weregarurumon():
    PELO = "#ECEAF8"
    LISTRA = "#5B4CA8"
    JEANS = "#3B5BA8"
    JEANS_ESC = "#2C4688"
    COURO = "#7A4A26"
    COURO_ESC = "#5A361C"
    PRETO = "#2A2A30"
    DOURADO = "#E8B830"
    PRATA = "#C9CFD6"
    GARRA = Pintura("#B8305E", gradiente=0.3, ruido=2)
    AMARELO = "#E8B820"

    def pelo(*camadas):
        return Pintura(PELO, *camadas, gradiente=0.12)

    def jeans(*camadas):
        return Pintura(JEANS, costura(tom(JEANS, 0.35), 0.1), *camadas, gradiente=0.15, ruido=8)

    peito = pelo(regiao_pelo(tom(PELO, 0.05), 0.2, 0.15, 0.8, 1.0),
                 # tira de couro atravessando o peito
                 detalhes([(i, 19 - i, COURO) for i in range(0, 20)] + [(i, 18 - i, COURO) for i in range(0, 19)]))
    braco = pelo(faixas_curvas(LISTRA, 2, 2, 1, inicio=0.2, fim=0.7))
    ponta = Pintura(LISTRA, gradiente=0.2)
    cabeca = pelo(faixas_curvas(LISTRA, 2, 2, 1, inicio=0.05, fim=0.25),
                  olho(0, 6, AMARELO, raiva=True, largura=5, altura=3),
                  olho(9, 6, AMARELO, raiva=True, espelhado=True, largura=5, altura=3))
    focinho = pelo(detalhes([(i, j, ESCURO) for i in range(2, 6) for j in range(0, 2)]
                            + [(i, 5, ESCURO) for i in range(0, 8)] + [(1, 4, BRANCO), (6, 4, BRANCO)]))
    couro = Pintura(COURO, painel(COURO_ESC), gradiente=0.2, ruido=4)
    pe = pelo(listras(LISTRA, 2, 0.4, 2))

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 14, 0], "root", [
            # Cintura de jeans com cinto de couro e fivela dourada
            Cubo([-4.5, 13, -2.5], [9, 3, 5], jeans(),
                 {"north": jeans(detalhes([(i, 1, COURO) for i in range(18)] + [(i, 0, COURO) for i in range(18)]
                                          + [(8, 0, DOURADO), (9, 0, DOURADO), (8, 1, DOURADO), (9, 1, DOURADO)]))}),
            Cubo([-5, 16, -3], [10, 10, 6], pelo(listras(LISTRA, 3, 0.4, 2)), {"north": peito}),
        ]),
        Osso("head", [0, 26, -1], "body", [
            Cubo([-3.5, 26, -4.5], [7, 7, 7], pelo(listras(LISTRA, 2, 0.6, 2)), {"north": cabeca}),
            Cubo([-2, 26, -8.5], [4, 3, 4], pelo(), {"north": focinho}),
            Cubo([-3, 33, -2], [2, 3, 1.5], pelo()),
            Cubo([1, 33, -2], [2, 3, 1.5], pelo()),
            # Cabelo espetado
            *_espinhos(-3.2, 31, -3, 4, 1.8, pelo(), ponta, altura=4, inclinacao=-40),
        ]),
        # Braço esquerdo: manga preta, ombreira de couro e soqueira dourada com espinhos
        Osso("arm_left", [5.5, 25, 0], "body", [
            Cubo([5, 22.5, -2.5], [4, 3.5, 5], couro),
            Cubo([5, 16, -1.5], [3, 7, 3], Pintura(PRETO, faixa(COURO, 0.6, 2), gradiente=0.2)),
            Cubo([4.8, 13.5, -1.7], [3.4, 2.5, 3.4], pelo()),
            Cubo([4.6, 13.2, -2.1], [3.8, 1, 0.6], Pintura(DOURADO, gradiente=0.3)),
            *[Cubo([4.9 + 1.2 * k, 13.3, -2.7], [0.6, 0.6, 0.6], Pintura(DOURADO)) for k in range(3)],
        ]),
        # Braço direito: pelo listrado e bracelete de couro com espinhos de metal
        Osso("arm_right", [-5.5, 25, 0], "body", [
            Cubo([-8, 18, -1.5], [3, 8, 3], braco),
            Cubo([-8.3, 15.5, -1.8], [3.6, 2.5, 3.6], couro),
            Cubo([-9.3, 16.4, -0.6], [1, 0.6, 0.6], Pintura(PRATA)),
            Cubo([-8, 13.5, -1.5], [3, 2, 3], pelo()),
            *_garras(-7.9, 12.3, -1.9, 3, 1, [0.6, 1.2, 0.6], GARRA),
        ]),
        Osso("leg_left", [2.5, 14, 0], "root", [
            # Coxa de jeans com a caveira estampada
            Cubo([0.5, 7, -2], [4, 7, 4], jeans(), {"north": jeans(caveira(0, 5))}),
            Cubo([1, 1.5, -1.5], [3, 5.5, 3], pe),
            Cubo([0.3, 0, -4], [4.4, 1.5, 5.5], pelo()),
            *_garras(0.4, 0, -5.4, 3, 1.5, [1.1, 1.1, 1.6], GARRA),
        ]),
        Osso("leg_right", [-2.5, 14, 0], "root", [
            Cubo([-4.5, 7, -2], [4, 7, 4], jeans(), {"north": jeans(detalhes([(2, 9, JEANS_ESC), (3, 9, JEANS_ESC), (2, 10, JEANS_ESC)]))}),
            Cubo([-4.6, 6.5, -2.3], [4.2, 2, 0.6], couro),  # joelheira
            Cubo([-4, 1.5, -1.5], [3, 5.5, 3], pe),
            Cubo([-4.7, 0, -4], [4.4, 1.5, 5.5], pelo()),
            *_garras(-4.6, 0, -5.4, 3, 1.5, [1.1, 1.1, 1.6], GARRA),
        ]),
        Osso("tail", [0, 15, 2.5], "body", [Cubo([-1, 13, 2.5], [2, 2, 6], pelo(listras(LISTRA, 1, 0.6, 2)))]),
        Osso("tail_tip", [0, 14, 8.5], "tail", [Cubo([-1, 13, 8.5], [2, 2, 3], ponta)]),
    ]
    gerar("weregarurumon", ossos, {f"animation.weregarurumon.{n}": a for n, a in _animacoes_bipede(peso=1.1).items()},
          densidade=HD)


def metalgarurumon():
    METAL = "#A8AAE0"
    METAL_ESC = "#7476B8"
    BRANCO_P = "#F0F0FA"
    LISTRA = "#6A5CB8"
    AMARELO = "#EAD54C"
    AMARELO_ESC = "#C2AE2A"
    NARIZ = "#E8483A"
    LUZ = "#E8542A"
    GARRA = Pintura("#E04050", gradiente=0.3, ruido=2)
    VERMELHO = "#C8282E"

    metal = Pintura(METAL, painel(METAL_ESC), gradiente=0.25, ruido=3)
    metal_liso = Pintura(METAL, gradiente=0.25, ruido=3)
    amarelo = Pintura(AMARELO, painel(AMARELO_ESC), gradiente=0.25, ruido=3)
    amarelo_liso = Pintura(AMARELO, gradiente=0.3, ruido=3)
    pata_listrada = Pintura(BRANCO_P, faixas_curvas(LISTRA, 3, 2, 1, inicio=0.15, fim=0.8), gradiente=0.12)
    cabeca = Pintura(METAL, painel(METAL_ESC),
                     olho(1, 5, VERMELHO, raiva=True, largura=5, altura=4),
                     olho(14, 5, VERMELHO, raiva=True, espelhado=True, largura=5, altura=4), gradiente=0.25, ruido=3)
    mandibula = Pintura(BRANCO_P, detalhes([(i, 0, BRANCO) for i in range(1, 11, 3)]))

    def pata(x, z, frente=True):
        larg = 4 if frente else 5
        return [
            Cubo([x, 6.5, z], [larg, 5, larg], metal),
            Cubo([x + 0.2, 1.5, z + 0.2], [larg - 0.4, 5, larg - 0.4], pata_listrada),
            Cubo([x, 0, z - 1], [larg, 1.5, larg + 0.5], Pintura(BRANCO_P)),
            *[Cubo([x + 0.2 + (larg - 1.2) / 2 * k, 0, z - 2.3], [0.9, 1.1, 1.4], GARRA) for k in range(3)],
        ]

    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 15, 0], "root", [
            Cubo([-6, 10, -11], [12, 10, 22], metal, {"down": Pintura(BRANCO_P)}),
            # Arreio amarelo no peito, lançador de mísseis nas costas
            Cubo([-6.5, 9, -13], [13, 11, 4], amarelo),
            Cubo([-2, 20, -7], [4, 2.5, 10], amarelo),
            Cubo([-0.6, 20.6, -10], [1.2, 1.2, 3], metal_liso),
            # Luzes laranja nos quadris
            Cubo([6, 12, 4], [0.6, 4, 5], Pintura(LUZ, gradiente=0.3)),
            Cubo([-6.6, 12, 4], [0.6, 4, 5], Pintura(LUZ, gradiente=0.3)),
        ]),
        # Asas-lâmina amarelas
        Osso("wing_left", [6, 19, -2], "body", [
            Cubo([6, 18.5, -4], [13, 1, 4], amarelo_liso),
            Cubo([17, 18.5, -5], [3, 1, 5], amarelo_liso),
        ], rotacao=[0, 0, 25]),
        Osso("wing_right", [-6, 19, -2], "body", [
            Cubo([-19, 18.5, -4], [13, 1, 4], amarelo_liso),
            Cubo([-20, 18.5, -5], [3, 1, 5], amarelo_liso),
        ], rotacao=[0, 0, -25]),
        Osso("head", [0, 18, -13], "body", [
            Cubo([-5, 15, -21], [10, 9, 8], metal, {"north": cabeca}),
            Cubo([-3, 15.5, -27], [6, 4, 6], metal_liso),
            Cubo([-2.8, 13.7, -26.5], [5.6, 1.8, 5.5], Pintura(BRANCO_P), {"up": mandibula}),
            Cubo([-1, 18.3, -27.6], [2, 1.6, 1], Pintura(NARIZ, gradiente=0.3)),
            Cubo([-4.5, 24, -16], [2, 4, 3], metal_liso, rotacao=[-20, 0, 0], pivo=[-3.5, 24, -14.5]),
            Cubo([2.5, 24, -16], [2, 4, 3], metal_liso, rotacao=[-20, 0, 0], pivo=[3.5, 24, -14.5]),
        ]),
        Osso("leg_front_left", [3.5, 11, -8], "root", pata(1.5, -9.5)),
        Osso("leg_front_right", [-3.5, 11, -8], "root", pata(-5.5, -9.5)),
        Osso("leg_back_left", [3.5, 11, 8], "root", pata(1, 5.5, frente=False)),
        Osso("leg_back_right", [-3.5, 11, 8], "root", pata(-6, 5.5, frente=False)),
        # Cauda em lâmina amarela
        Osso("tail", [0, 18, 11], "body", [
            Cubo([-0.5, 17, 11], [1, 3, 12], amarelo_liso),
            Cubo([-0.5, 17.5, 23], [1, 4, 3], amarelo_liso),
        ], rotacao=[25, 0, 0]),
    ]
    from gerar_modelos import onda
    animacoes = _animacoes_quadrupede()
    animacoes["idle"]["bones"]["wing_left"] = {"rotation": onda(6, 2.0, eixo=2, base=(0, 0, 25))}
    animacoes["idle"]["bones"]["wing_right"] = {"rotation": onda(6, 2.0, eixo=2, fase=180, base=(0, 0, -25))}
    gerar("metalgarurumon", ossos, {f"animation.metalgarurumon.{n}": a for n, a in animacoes.items()}, densidade=HD)


# ================================================================== INIMIGOS ===

from estilo import manchas  # noqa: E402


def numemon():
    VERDE = "#7DBB3A"
    VERDE_ESC = "#5E9428"
    LINGUA = "#E8708A"
    lesma = Pintura(VERDE, brilho(0.3, 0.25, 0.25, 0.2, 0.3), manchas(VERDE_ESC, [(0.2, 0.6), (0.7, 0.3)]), gradiente=0.2, ruido=3)
    frente = Pintura(VERDE, boca_aberta(4, 10, 8, 5, interior="#3A1A1A", lingua=LINGUA), brilho(0.3, 0.2, 0.2, 0.15, 0.3),
                     gradiente=0.2, ruido=3)
    olho_bola = Pintura(BRANCO, detalhes([(1, 1, ESCURO), (2, 1, ESCURO), (1, 2, ESCURO), (2, 2, ESCURO), (2, 0, BRANCO)]),
                        gradiente=0.1, ruido=1)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 0, 0], "root", [
            Cubo([-4.5, 0, -2], [9, 5, 11], lesma),
            Cubo([-4, 0, -5], [8, 10, 5], lesma, {"north": frente}),
        ]),
        Osso("eyes", [0, 10, -3], "body", [
            Cubo([-3, 10, -3.5], [1, 3, 1], lesma),
            Cubo([2, 10, -3.5], [1, 3, 1], lesma),
            Cubo([-3.5, 13, -4], [2, 2, 2], olho_bola),
            Cubo([1.5, 13, -4], [2, 2, 2], olho_bola),
        ]),
        Osso("arm_left", [4, 6, -3], "body", [Cubo([4, 3, -4], [1.5, 3, 1.5], lesma)]),
        Osso("arm_right", [-4, 6, -3], "body", [Cubo([-5.5, 3, -4], [1.5, 3, 1.5], lesma)]),
    ]
    from gerar_modelos import onda
    animacoes = {
        "idle": {"loop": True, "animation_length": 2.0, "bones": {
            "body": {"scale": ["1", "1 + math.sin(query.anim_time / 2 * 360) * 0.04", "1"]},
            "eyes": {"rotation": onda(8, 2.0, eixo=2)},
        }},
        "walk": {"loop": True, "animation_length": 0.8, "bones": {
            "body": {"scale": ["1", "1 - math.sin(query.anim_time / 0.8 * 360) * 0.06",
                               "1 + math.sin(query.anim_time / 0.8 * 360) * 0.08"]},
            "eyes": {"rotation": onda(10, 0.8)},
            "arm_left": {"rotation": onda(30, 0.8)},
            "arm_right": {"rotation": onda(30, 0.8, fase=180)},
        }},
        "attack": {"loop": False, "animation_length": 0.4, "bones": {
            "body": {"rotation": {"0.0": [0, 0, 0], "0.15": [-15, 0, 0], "0.4": [0, 0, 0]}},
            "arm_right": {"rotation": {"0.0": [0, 0, 0], "0.15": [-120, 0, 0], "0.4": [0, 0, 0]}},
        }},
    }
    gerar("numemon", ossos, {f"animation.numemon.{n}": a for n, a in animacoes.items()}, densidade=HD)


def goburimon():
    VERDE = "#6FA84A"
    VERDE_CLARO = "#93C46A"
    VERDE_ESC = "#52833A"
    TANGA = "#8A5A2B"
    MADEIRA = "#7A5530"
    AMARELO = "#F5D83A"
    pele = Pintura(VERDE, gradiente=0.18)
    barriga = Pintura(VERDE, regiao_pelo(VERDE_CLARO, 0.2, 0.1, 0.8, 1.0, tufo_cima=False))
    rosto = Pintura(VERDE,
                    olho(1, 3, AMARELO, raiva=True, largura=5, altura=3),
                    olho(10, 3, AMARELO, raiva=True, espelhado=True, largura=5, altura=3),
                    boca_aberta(4, 9, 8, 3, interior="#2A1A10", lingua="#A04040"),
                    detalhes([(5, 9, BRANCO), (10, 9, BRANCO)]))
    tanga = Pintura(TANGA, faixas_curvas(tom(TANGA, -0.3), 1, 1, 1, inicio=0.5, fim=0.5), gradiente=0.2, ruido=6)
    clava = Pintura(MADEIRA, listras(tom(MADEIRA, -0.3), 2, 1.0, 1), gradiente=0.25, ruido=8)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 8, 0], "root", [
            Cubo([-3.5, 7, -2], [7, 7, 4], pele, {"north": barriga}),
            Cubo([-3.6, 6, -2.1], [7.2, 2.5, 4.2], tanga),
        ]),
        Osso("head", [0, 14, 0], "body", [
            Cubo([-4, 14, -3.5], [8, 7, 7], pele, {"north": rosto}),
            Cubo([4, 17, -1], [3, 2, 1], Pintura(VERDE_ESC), rotacao=[0, 0, 15], pivo=[4, 18, -0.5]),
            Cubo([-7, 17, -1], [3, 2, 1], Pintura(VERDE_ESC), rotacao=[0, 0, -15], pivo=[-4, 18, -0.5]),
            Cubo([-0.5, 21, -1.5], [1, 2, 1], Pintura("#E8DCC0")),
        ]),
        Osso("arm_left", [4, 13, 0], "body", [Cubo([3.5, 7, -1], [2, 6, 2], pele)]),
        Osso("arm_right", [-4, 13, 0], "body", [
            Cubo([-5.5, 7, -1], [2, 6, 2], pele),
            Cubo([-5.5, 6, -9], [2, 2, 8], clava),
            Cubo([-6, 5.5, -11], [3, 3, 3], clava),
        ]),
        Osso("leg_left", [1.75, 7, 0], "root", [Cubo([0.5, 0, -1.5], [2.5, 7, 3], Pintura(VERDE_ESC))]),
        Osso("leg_right", [-1.75, 7, 0], "root", [Cubo([-3, 0, -1.5], [2.5, 7, 3], Pintura(VERDE_ESC))]),
    ]
    gerar("goburimon", ossos, {f"animation.goburimon.{n}": a for n, a in _animacoes_bipede().items()}, densidade=HD)


def gotsumon():
    PEDRA = "#9A9A96"
    PEDRA_ESC = "#6E6E68"
    MUSGO = "#6E8F4A"

    def rocha(*camadas):
        trincas = detalhes([(2, 1, PEDRA_ESC), (3, 2, PEDRA_ESC), (3, 3, PEDRA_ESC), (9, 4, PEDRA_ESC),
                            (10, 5, PEDRA_ESC), (6, 8, PEDRA_ESC), (7, 8, PEDRA_ESC)])
        return Pintura(PEDRA, trincas, *camadas, gradiente=0.22, ruido=10)

    rosto = rocha(olho_redondo(2, 3, 4, ESCURO, pupila=1, contorno=ESCURO),
                  olho_redondo(10, 3, 4, ESCURO, pupila=1, contorno=ESCURO, espelhado=True),
                  detalhes([(i, 9, "#3A3A36") for i in range(6, 10)]))
    musgo = Pintura(MUSGO, ruido=10, gradiente=0.15)
    ossos = [
        Osso("root", [0, 0, 0]),
        Osso("body", [0, 7, 0], "root", [
            Cubo([-4.5, 6, -3], [9, 8, 6], rocha()),
            Cubo([3.5, 12, -2], [2, 2, 2], rocha()),
        ]),
        Osso("head", [0, 14, 0], "body", [
            Cubo([-4, 14, -3.5], [8, 6, 7], rocha(), {"north": rosto, "up": musgo}),
            Cubo([-2.5, 20, -2], [3, 1.5, 3], musgo),
        ]),
        Osso("arm_left", [5, 13, 0], "body", [Cubo([4.5, 6, -2], [3.5, 7, 4], rocha())]),
        Osso("arm_right", [-5, 13, 0], "body", [Cubo([-8, 6, -2], [3.5, 7, 4], rocha())]),
        Osso("leg_left", [2, 6, 0], "root", [Cubo([0.5, 0, -2], [3.5, 6, 4], Pintura(PEDRA_ESC, ruido=10))]),
        Osso("leg_right", [-2, 6, 0], "root", [Cubo([-4, 0, -2], [3.5, 6, 4], Pintura(PEDRA_ESC, ruido=10))]),
    ]
    gerar("gotsumon", ossos, {f"animation.gotsumon.{n}": a for n, a in _animacoes_bipede(peso=1.3).items()}, densidade=HD)


TODOS = ["agumon", "gabumon", "botamon", "koromon", "punimon", "tsunomon", "greymon", "metalgreymon", "wargreymon",
         "garurumon", "weregarurumon", "metalgarurumon", "numemon", "goburimon", "gotsumon"]


if __name__ == "__main__":
    for _nome in TODOS:
        globals()[_nome]()
