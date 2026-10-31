# Digimon Aurity no Minecraft — Documento de Design (GDD)

> Mod para Minecraft Java Edition 26.3, inspirado em *Digimon Aurity* (Roblox, 2010–2026).
> Documento vivo: atualizado a cada decisão. Última atualização: 31/10/2026 (fim da Fase 3).

## 1. Visão

O jogador **é** um Digimon — não um treinador. Ele explora o mundo do Minecraft, sobrevive, constrói e luta com os ataques do próprio corpo, conquistando suas Digievoluções através de nível **e** descobertas no mundo. Evoluir e desevoluir são escolhas: cada forma é uma ferramenta, não só um degrau de poder.

**Pilares**
1. Ser o Digimon (corpo, ataques, movimento e limitações próprias).
2. Exploração com significado (marcos, ovos e estruturas movem a progressão).
3. O sandbox continua importando (minerar, construir, sobreviver).
4. Simples, coeso e realizável antes de grande.

**Herança do Aurity que preservamos:** controle direto do Digimon; kit de ataques por forma com recarga; árvores canônicas; evolução com mais de uma chave (nível + ovo/marco); chefes que digievoluem durante a luta; ovos ligados a regiões.
**Herança que rejeitamos:** grind até nível 500, prestige que tira níveis, Bursts por sorteio, paywalls, atributos sem efeito, XP por acerto, linhas inacabadas.

## 2. Escopo do MVP

Duas linhas principais completas:

| Estágio | Linha Agumon (fogo) | Linha Gabumon (gelo) |
|---|---|---|
| Fresh | Botamon | Punimon |
| In-Training | Koromon | Tsunomon |
| Rookie | Agumon | Gabumon |
| Champion | Greymon | Garurumon |
| Ultimate | MetalGreymon | WereGarurumon |
| Mega | WarGreymon | MetalGarurumon |

Foco em um jogador; regras de multiplayer valem quando ele entrar.

## 3. Sistemas definidos

### 3.1 Linhas e progressão
- O jogador escolhe uma das duas linhas no início; a outra é desbloqueada ao encontrar seu **Digi-Egg** no mundo.
- **Cada linha tem nível e progresso próprios** (nível, formas conquistadas, marcos).
- **Compartilhado entre linhas:** inventário, base, mapa e receitas.
- Troca de linha apenas na **incubadora** (bloco).
- Os primeiros níveis de cada linha passam rápido; a curva pesa mais adiante.

### 3.2 Evolução e desevolução
- **Nível é piso.** A partir do Champion, cada evolução também exige um **marco de exploração**.
- Todos os marcos são possíveis **jogando sozinho**.
- Forma conquistada fica liberada para sempre (evoluir/desevoluir livremente dentro da linha).
- **Troca de forma:** animação curta (jogador vulnerável) + recarga. HP mantido em **porcentagem**.

| Evolução | Requisito (princípio) |
|---|---|
| Fresh → In-Training → Rookie | Só nível |
| Rookie → Champion | Nível + marco (ex.: vencer um chefe de território) |
| Champion → Ultimate | Nível + marco (ex.: metal das profundezas / lua cheia) |
| Ultimate → Mega | Nível + Brasão (Coragem / Amizade) no Templo do Brasão |

*Os marcos específicos ainda serão definidos; a tabela ilustra o princípio.*

### 3.3 O Digimon no sandbox (opção C)
- Minerar, construir, craftar, inventário e comer funcionam para todas as formas.
- **Combate vem só do Digimon**: armas e armaduras vanilla não podem ser usadas.
- **Tamanho define acesso** (formas pequenas cabem em qualquer lugar; grandes ficam presas, mas dominam o combate). No cânone, WarGreymon é humanoide e menor que MetalGreymon.
- **Fome escala com o estágio** (poder), não com o tamanho.
- Ferramentas vanilla continuam como estão no MVP.
- **Características elementais:** linha Agumon resiste a fogo/lava (facilita o Nether); linha Gabumon resiste ao frio/neve fofa e congela água sob os pés.

### 3.4 Movimento e câmera
- Cada forma: tamanho, velocidade, pulo e no máximo uma característica de movimento.
- **Voo pleno só nos Megas**, com custo alto de fome. MetalGreymon: no máximo planeio/impulso.
- Linha Gabumon compensa com mobilidade terrestre (Garurumon rápido, WereGarurumon pulo alto).
- Câmera à escolha do jogador (como F5), com distância ajustada ao tamanho da forma.

### 3.5 Combate
- **Ataque básico** no clique esquerdo em criaturas (clique em bloco continua minerando).
- **Até 3 especiais** em teclas próprias, disparados direto, mirados no centro da tela.
- Kit por estágio: Fresh/In-Training 1 especial; Rookie 2; Champion+ 3.
- Recarga própria por ataque **+ recarga global curta**.
- Identidade: Agumon = fogo, dano direto, curta/média distância; Gabumon = gelo, controle (lentidão/congelamento), mobilidade.

### 3.6 XP e inimigos
- Mobs vanilla continuam no mundo e dão **pouco** XP.
- **Digimon selvagens**, ligados a biomas, são a principal fonte de XP de combate.
- **Descobrir dá XP:** primeiro bioma, primeira estrutura, primeira espécie derrotada.
- Retornos decrescentes ao matar a mesma espécie repetidamente.
- XP vai para a linha ativa. XP vem do resultado (derrotar/descobrir), não do número de acertos.
- Selvagens: as 12 formas jogáveis + 2 ou 3 espécies só inimigas.
- **Selvagens digievoluem durante a luta**; o teto depende da **região** (Rookie perto do spawn; Champion/Ultimate em áreas perigosas; Megas raros).

### 3.7 Mundo e orientação
| Estrutura | Função | Onde |
|---|---|---|
| Ninho de Digi-Egg | Ovo da outra linha | Bioma temático (Gabumon: gelado; Agumon: quente) |
| Território de chefe | Marco Rookie → Champion | Espalhados, teto de evolução da região |
| Templo do Brasão | Marco Ultimate → Mega | Raro, longe do spawn |

- **Sentido digital** (sem item): radar de proximidade — indicador, partículas e som se intensificam perto de marcos.

### 3.8 Morte
- Itens caem como no vanilla; nível, formas e marcos são preservados.
- Renasce como **Rookie** da linha ativa, sem poder evoluir por alguns minutos.

### 3.9 Multiplayer
- PvP segue a configuração do servidor e **não dá XP**.
- Todo jogador que causou dano recebe XP e crédito do marco.
- Chefes de território ganham um pouco mais de vida com mais jogadores por perto.
- Sem sistema de grupo no MVP.

### 3.10 Endgame e longevidade
- **Endgame do MVP:** levar as duas linhas ao Mega.
- **Depois do MVP, nesta ordem:**
  1. **Omnimon** — fusão de WarGreymon + MetalGarurumon; exige as duas linhas no Mega + desafio final.
  2. **Ramos alternativos** (SkullGreymon, BlackWarGreymon etc.).
- Novas linhas: a decidir depois.

## 4. Pendentes para o planejamento
- Quais 2–3 espécies serão só inimigas.
- Tamanhos aproximados de cada forma.
- Novos usos para materiais de armas e armaduras.
- Quais estágios entram no primeiro MVP jogável.
- Marcos específicos de cada evolução.

## 5. Adiado
- Garras no lugar das ferramentas.
- Chefes que revelam a direção do Templo do Brasão.
- Sistema de grupo; fusão entre dois jogadores.
- Novas linhas.

## 6. Descartado
- Progresso compartilhado entre linhas.
- Evolução só por nível.
- Marcos que exigem multiplayer.
- Opções A (skin com poderes) e B (corpo muda todas as regras).
- Armas e armaduras vanilla para o Digimon.
- Ataques na hotbar como itens; modo de combate.
- Teto de evolução dos selvagens definido por jogadores presentes ou pelo nível do jogador.
- Digivice como item; bússola direcional; ausência de orientação.
- Punições leve e pesada por morte.
- PvP dando XP.
- Prestige, resets de nível e recompensas aleatórias tipo gacha.

## 7. Decisões técnicas (Fase 4)

- **Uso:** pessoal, para o autor e amigos; sem comercialização nem publicação pública.
- **Versão-alvo:** Minecraft Java 26.3, fixada até o MVP ficar pronto (requer Java 25).
- **Loader:** NeoForge, loader único (sem multi-loader/Architectury).
- **Dependência essencial:** GeckoLib (modelos e animações via Blockbench; MIT; 5.5.7 para 26.3).
- **Dispensadas:** Player Animation Library (substituímos o modelo, não animamos o vanilla), Pehkui (sem versão 26.x; usar atributo de escala vanilla — confirmar em protótipo), Architectury.
- **Multiplayer entre amigos é objetivo real:** toda lógica de jogo é decidida pelo servidor desde o início (o singleplayer também roda um servidor interno).

## 8. Referência: o que se sabe do Aurity original
- Place 43228117, criado em 30/12/2010, grupo "Project: Aurity"; ~15,7 mi visitas; 25 jogadores por servidor; hoje "[Farewell]", substituído por Virtumon Aurity.
- Níveis 0–500; dano escala até 2,5× e HP até 3× o valor base no nível 500 (planilha da comunidade).
- Evolução: nível + ovo da linha + item (Armor Digi-Egg, Burst) + às vezes gamepass/prestige.
- Chefes nasciam Fresh e digievoluíam durante a luta conforme os jogadores na sala.
- **Relato de jogador:** selecionava-se o ataque, clicava-se para lançar, com recarga entre ataques.
- Fontes: wikis Fandom digimonaurityrblx, rblxaurity e digimonaurity; API pública do Roblox; planilha de dano/XP da comunidade.
