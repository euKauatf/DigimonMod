package com.digimonaurity.client;

import com.digimonaurity.digimon.DigimonForm;

/**
 * Cópia local das recargas, só para desenhar o indicador.
 * Quem decide se um ataque pode ser usado é sempre o servidor.
 */
public final class ClientCooldowns {
    private static final long[] READY_AT = new long[DigimonForm.MAX_ATTACKS];
    private static final int[] TOTAL = new int[DigimonForm.MAX_ATTACKS];
    private static long globalReadyAt;
    private static int globalTotal;

    private ClientCooldowns() {
    }

    public static void start(long now, int slot, int slotTicks, int globalTicks) {
        if (slot >= 0 && slot < READY_AT.length) {
            READY_AT[slot] = now + slotTicks;
            TOTAL[slot] = Math.max(1, slotTicks);
        }
        globalReadyAt = now + globalTicks;
        globalTotal = Math.max(1, globalTicks);
    }

    /** Fração da recarga que falta (1 = acabou de usar, 0 = pronto), considerando a global. */
    public static float remaining(int slot, long now, float partialTick) {
        float t = now + partialTick;
        float own = Math.max(0, READY_AT[slot] - t) / TOTAL[slot];
        float global = Math.max(0, globalReadyAt - t) / Math.max(1, globalTotal);
        return Math.min(1f, Math.max(own, global));
    }

    /** Segundos que faltam na recarga própria (arredondado para cima), ou 0. */
    public static int secondsLeft(int slot, long now) {
        long ticks = READY_AT[slot] - now;
        return ticks <= 0 ? 0 : (int) Math.ceil(ticks / 20.0);
    }

    private static long evolutionBlockedUntil;

    public static void blockEvolution(long now, int ticks) {
        evolutionBlockedUntil = now + ticks;
    }

    /** Segundos de bloqueio de evolução que faltam (após morrer), ou 0. */
    public static int evolutionBlockedSeconds(long now) {
        long ticks = evolutionBlockedUntil - now;
        return ticks <= 0 ? 0 : (int) Math.ceil(ticks / 20.0);
    }

    public static void reset() {
        java.util.Arrays.fill(READY_AT, 0);
        globalReadyAt = 0;
    }
}
