package com.digimonaurity.progression;

import java.util.HashMap;
import java.util.Map;

import org.jspecify.annotations.Nullable;

import net.minecraft.resources.Identifier;

/**
 * Estado temporário de um jogador no servidor (não é salvo):
 * transformação em andamento, recargas de evolução e o "calor" dos abates recentes.
 */
public class DigimonRuntime {
    /** Forma para a qual o jogador está se transformando, ou null. */
    public @Nullable Identifier transformTarget;
    public long transformDoneAt;
    public long transformReadyAt;
    /** Após morrer, o jogador não pode evoluir além de Rookie até este tick. */
    public long evolutionBlockedUntil;
    /** O voo atual foi liberado pela forma (e não pelo Criativo)? */
    public boolean grantedFlight;
    /** Tempo seguido sob a lua cheia (marco do WereGarurumon). */
    public int moonTicks;
    /** Última incubadora usada; a troca de linha só vale perto dela. */
    public net.minecraft.core.@Nullable BlockPos incubatorPos;

    /** Calor por espécie: sobe a cada abate e esfria com o tempo. Mais calor = menos XP. */
    private final Map<Identifier, Float> killHeat = new HashMap<>();
    private long heatUpdatedAt;

    public boolean isTransforming() {
        return transformTarget != null;
    }

    /** Multiplicador de XP para mais um abate desta espécie (1 = cheio), já registrando o abate. */
    public float registerKill(Identifier species, long now) {
        coolDown(now);
        float heat = killHeat.getOrDefault(species, 0f);
        killHeat.put(species, heat + 1f);
        return 1f / (1f + heat * 0.35f);
    }

    /** Cada espécie perde 1 de calor a cada 30 segundos. */
    private void coolDown(long now) {
        float elapsed = (now - heatUpdatedAt) / 600f;
        heatUpdatedAt = now;
        if (elapsed <= 0) {
            return;
        }
        killHeat.replaceAll((k, v) -> Math.max(0f, v - elapsed));
        killHeat.values().removeIf(v -> v <= 0f);
    }
}
