# Plano de desenvolvimento — Digimon Aurity (NeoForge 26.3)

> Plano incremental. Cada marco termina com algo **jogável e testável**.
> O design completo está em [GDD.md](GDD.md).

## Como trabalhamos

- **Eu (Claude):** escrevo código, modelos 3D, texturas e animações; compilo e explico o que mudou.
- **Você:** testa no jogo, diz o que achou e decide os rumos de design.
- Cada marco é pequeno. Se algo ficar ruim, corrigimos antes de seguir.

## Princípios de arquitetura

1. **Dados, não código, descrevem os Digimon.** Cada forma é um arquivo JSON (estágio, linha, tamanho, velocidade, HP, ataques, evoluções e requisitos). Adicionar um Digimon novo = JSON + modelo + textura (+ código só se ele tiver um ataque com comportamento inédito).
2. **Ataques são comportamentos reutilizáveis** (projétil, sopro em cone, investida, área, escudo…) configurados por parâmetros. Pepper Breath e Blue Blaster podem ser o mesmo comportamento "projétil" com valores e efeitos diferentes.
3. **O servidor decide tudo** (XP, evolução, dano, recargas, marcos). O cliente só desenha e envia comandos. Assim, multiplayer com os amigos funciona desde o início.
4. **Uma dependência essencial:** GeckoLib. O resto vem do vanilla e do NeoForge.
5. **Modelos no estilo do Minecraft:** blocados, limpos e legíveis — combinam com o jogo e são realizáveis.

## Marcos

| # | Marco | Resultado testável |
|---|---|---|
| **0** ✅ | **Fundação** | O mod compila, abre o jogo e aparece na lista de mods |
| **1** ✅ | **Virar o Digimon** *(maior risco técnico)* | Você entra no mundo como Agumon: modelo próprio, animações de parado/andar, tamanho e hitbox corretos, câmera ajustada; outros jogadores veem o Agumon |
| **2** ✅ | **Identidade persistente** | Tela de escolha inicial (Agumon ou Gabumon); linha, forma e nível salvos e sincronizados; comandos de teste |
| **3** ✅ | **Combate básico** | Ataque básico no clique + 1 especial (Pepper Breath) em tecla própria; recarga própria + global; indicador de recarga na tela |
| **4** ✅ | **XP e Digievolução** | Ganhar XP, subir de nível, evoluir/desevoluir Botamon → Koromon → Agumon → Greymon; animação de transformação; HP em %; fome por estágio |
| **5** ✅ | **Segunda linha** | Linha Gabumon até Champion; características elementais (fogo / gelo) |
| **6** ✅ | **Digimon selvagens** | Selvagens com IA simples, spawn por bioma, digievolução no meio da luta, teto por região |
| **7** ✅ | **Marcos e estruturas** | Território de chefe (marco do Champion), Ninho de Digi-Egg, incubadora e troca de linha, sentido digital |
| **8** ✅ | **Ultimate e Mega** | Marcos do Ultimate (metal das profundezas, lua cheia), Templo do Brasão, voo dos Megas |
| **9** 🔧 | **Polimento e teste com amigos** (kits, armas/armaduras e pacote prontos; falta jogar com amigos e ajustar balanceamento) | Balanceamento, efeitos, sons, sessão multiplayer de teste |

**Depois do MVP:** Omnimon → ramos alternativos.

## Riscos conhecidos

- **Substituir o modelo do jogador** com GeckoLib não tem documentação oficial para 26.x. Por isso é o marco 1: se o caminho previsto não funcionar, descobrimos cedo.
- **Atributo de escala vanilla** precisa ser confirmado na 26.3 para tamanho e hitbox.
- **Atualizações do Minecraft** (26.4 já em snapshot): ficamos fixos na 26.3 até o MVP.

## Ferramentas do projeto

- `compilar.bat` — gera o mod em `build\libs\`.
- `empacotar.bat` — gera `distribuicao\mods\` (mod + GeckoLib) para enviar aos amigos, junto com `distribuicao\LEIA-ME.txt`.
- `jogar_teste.bat` — abre um Minecraft de teste com o mod (sem launcher).
- `tools/gerar_modelos.py` — gera modelos, texturas e animações dos Digimon.
- `tools/visualizar.py <nome>` — cria uma prévia em `tools/previas/`.
- Os scripts usam pastas sem acento em `.tmp\` por causa do nome de usuário com acento no Windows.

## Como jogar (quando houver algo para testar)

1. Instalar o Minecraft Java 26.3 e o NeoForge 26.3.
2. Colocar o `.jar` do mod e o do GeckoLib na pasta `mods`.
3. Todos os amigos usam a mesma versão do mod.

*(Instruções detalhadas virão junto com o primeiro marco jogável.)*
