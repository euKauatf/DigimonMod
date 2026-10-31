package com.digimonaurity.client;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonAttack;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;

/**
 * Indicador dos ataques especiais, à direita da hotbar:
 * um quadrado por ataque, com a cor do elemento, a tecla e a recarga escurecendo de cima para baixo.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID, value = Dist.CLIENT)
public final class AttackHud {
    private static final int SIZE = 20;
    private static final int GAP = 3;

    private AttackHud() {
    }

    @SubscribeEvent
    static void onRegisterLayers(RegisterGuiLayersEvent event) {
        event.registerAbove(VanillaGuiLayers.HOTBAR, DigimonAurity.id("attacks"), AttackHud::render);
    }

    private static void render(GuiGraphicsExtractor graphics, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || mc.player.isSpectator()) {
            return;
        }
        DigimonForm form = PlayerDigimon.getForm(mc.player);
        if (form == null || form.attacks().isEmpty()) {
            return;
        }
        long now = mc.level.getGameTime();
        float partial = delta.getGameTimeDeltaPartialTick(false);
        int x = graphics.guiWidth() / 2 + 91 + 8;
        int y = graphics.guiHeight() - SIZE - 1;

        for (int slot = 0; slot < form.attacks().size(); slot++) {
            Identifier attackId = form.attacks().get(slot);
            DigimonAttack attack = PlayerDigimon.lookup(mc.player, DigimonRegistries.ATTACK, attackId);
            int color = attack == null ? 0xFF808080 : attack.element().color;

            graphics.fill(x, y, x + SIZE, y + SIZE, 0xB0000000);
            graphics.fill(x + 2, y + 2, x + SIZE - 2, y + SIZE - 2, color);
            graphics.outline(x, y, SIZE, SIZE, 0xFF202020);

            float remaining = ClientCooldowns.remaining(slot, now, partial);
            if (remaining > 0) {
                int shade = Math.round((SIZE - 4) * remaining);
                graphics.fill(x + 2, y + 2, x + SIZE - 2, y + 2 + shade, 0xC0000000);
                int seconds = ClientCooldowns.secondsLeft(slot, now);
                if (seconds > 0) {
                    graphics.centeredText(mc.font, String.valueOf(seconds), x + SIZE / 2, y + 6, 0xFFFFFFFF);
                }
            }
            Component key = DigimonKeys.ATTACKS[slot].getTranslatedKeyMessage();
            graphics.text(mc.font, key, x + 1, y - 9, 0xFFFFFFFF, true);
            x += SIZE + GAP;
        }
    }
}
