package com.digimonaurity.client;

import java.util.Optional;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.digimon.DigimonStage;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.evolution.DigimonEvolution;
import com.digimonaurity.progression.DigimonProgression;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;

/**
 * Painel no canto superior esquerdo: forma, nível, barra de XP e a próxima evolução.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID, value = Dist.CLIENT)
public final class StatusHud {
    private static final int X = 4;
    private static final int Y = 4;
    private static final int WIDTH = 150;
    private static final int BAR_HEIGHT = 5;

    private StatusHud() {
    }

    @SubscribeEvent
    static void onRegisterLayers(RegisterGuiLayersEvent event) {
        event.registerBelow(VanillaGuiLayers.CHAT, DigimonAurity.id("status"), StatusHud::render);
    }

    private static void render(GuiGraphicsExtractor graphics, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || mc.player.isSpectator() || mc.getDebugOverlay().showDebugScreen()) {
            return;
        }
        DigimonData data = PlayerDigimon.getData(mc.player);
        Optional<DigimonData.LineProgress> progressOpt = data.activeProgress();
        DigimonForm form = PlayerDigimon.getForm(mc.player);
        if (progressOpt.isEmpty() || form == null) {
            return;
        }
        DigimonData.LineProgress progress = progressOpt.get();
        DigimonLine line = PlayerDigimon.lookup(mc.player, DigimonRegistries.LINE, data.activeLine().get());
        int accent = line == null ? 0xFFFFFFFF : ARGB.opaque(line.color());
        Font font = mc.font;
        long now = mc.level.getGameTime();

        int height = ClientSense.active() ? 52 : 40;
        graphics.fill(X, Y, X + WIDTH, Y + height, 0x90000000);
        graphics.fill(X, Y, X + 2, Y + height, accent);

        // Linha 1: nome da forma e nível
        int tx = X + 6;
        graphics.text(font, DigimonEvolution.formName(progress.form()), tx, Y + 4, accent, true);
        Component level = Component.translatable("hud.digimonaurity.level", progress.level());
        graphics.text(font, level, X + WIDTH - 4 - font.width(level), Y + 4, 0xFFFFFFFF, true);

        // Linha 2: barra de XP
        int barY = Y + 15;
        int barWidth = WIDTH - 10;
        boolean maxed = progress.level() >= DigimonProgression.MAX_LEVEL;
        int needed = DigimonProgression.xpToNext(progress.level());
        float fraction = maxed ? 1f : Math.min(1f, progress.xp() / (float) needed);
        graphics.fill(tx, barY, tx + barWidth, barY + BAR_HEIGHT, 0xFF202020);
        graphics.fill(tx, barY, tx + Math.round(barWidth * fraction), barY + BAR_HEIGHT, accent);

        // Linha 3: próxima evolução
        graphics.text(font, nextEvolutionHint(mc, progress, now), tx, Y + 25, 0xFFFFFFFF, true);

        // Linha 4: sentido digital (5 barrinhas que acendem com a proximidade)
        if (ClientSense.active()) {
            int sy = Y + 38;
            graphics.text(font, ClientSense.label(), tx, sy, 0xFFB98CFF, true);
            int lit = Math.max(1, Math.round(ClientSense.strength() * 5));
            int bx = X + WIDTH - 4 - 5 * 6;
            for (int i = 0; i < 5; i++) {
                int h = 3 + i * 2;
                graphics.fill(bx + i * 6, sy + 8 - h, bx + i * 6 + 4, sy + 8, i < lit ? 0xFFB98CFF : 0xFF404050);
            }
        }
    }

    private static Component nextEvolutionHint(Minecraft mc, DigimonData.LineProgress progress, long now) {
        Identifier nextId = DigimonEvolution.neighbour(mc.player, +1).orElse(null);
        DigimonForm next = nextId == null ? null : PlayerDigimon.lookup(mc.player, DigimonRegistries.FORM, nextId);
        if (next == null) {
            return Component.translatable("hud.digimonaurity.final_form").withColor(0xFFA0A0A0);
        }
        Component name = DigimonEvolution.formName(nextId);
        int blocked = ClientCooldowns.evolutionBlockedSeconds(now);
        if (blocked > 0 && next.stage().compareTo(DigimonStage.ROOKIE) > 0) {
            return Component.translatable("hud.digimonaurity.blocked", blocked / 60, String.format("%02d", blocked % 60))
                    .withColor(0xFFFF6060);
        }
        if (progress.level() < next.minLevel()) {
            return Component.translatable("hud.digimonaurity.next_at", name, next.minLevel()).withColor(0xFFA0A0A0);
        }
        if (!progress.meets(next)) {
            Identifier missing = next.requires().stream()
                    .filter(m -> !progress.milestones().contains(m)).findFirst().orElse(null);
            return Component.translatable("hud.digimonaurity.need_milestone", DigimonEvolution.milestoneName(missing))
                    .withColor(0xFFFFA040);
        }
        return Component.translatable("hud.digimonaurity.can_evolve",
                DigimonKeys.EVOLVE.getTranslatedKeyMessage(), name).withColor(0xFFFFE066);
    }
}
