package com.digimonaurity.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;

/** Último sinal do sentido digital recebido do servidor, e o "ping" do radar. */
public final class ClientSense {
    private static int kind;
    private static float strength;

    private ClientSense() {
    }

    /** Chega a cada 2 segundos. Toca um ping mais agudo quanto mais perto. */
    public static void update(int newKind, float newStrength) {
        kind = newKind;
        strength = newStrength;
        if (kind != 0) {
            Minecraft.getInstance().getSoundManager().play(
                    SimpleSoundInstance.forUI(SoundEvents.NOTE_BLOCK_PLING.value(), 0.6f + strength, 0.25f + strength * 0.35f));
        }
    }

    public static boolean active() {
        return kind != 0;
    }

    public static float strength() {
        return strength;
    }

    public static Component label() {
        return Component.translatable(switch (kind) {
            case 2 -> "hud.digimonaurity.sense.egg";
            case 3 -> "hud.digimonaurity.sense.temple";
            default -> "hud.digimonaurity.sense.territory";
        });
    }
}
