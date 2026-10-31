package com.digimonaurity.combat;

import com.digimonaurity.digimon.DigimonForm;

/** Recargas de um jogador, em "tick do mundo em que libera". Vive só no servidor. */
public class AttackCooldowns {
    private final long[] readyAt = new long[DigimonForm.MAX_ATTACKS];
    private long globalReadyAt;

    public boolean isReady(int slot, long now) {
        return now >= readyAt[slot] && now >= globalReadyAt;
    }

    public void start(int slot, long now, int slotTicks, int globalTicks) {
        readyAt[slot] = now + slotTicks;
        globalReadyAt = now + globalTicks;
    }

    public void clear() {
        java.util.Arrays.fill(readyAt, 0);
        globalReadyAt = 0;
    }
}
