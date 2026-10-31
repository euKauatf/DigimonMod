package com.digimonaurity.client.screen;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.network.DigimonNetwork;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.ARGB;
import net.neoforged.neoforge.client.network.ClientPacketDistributor;

/**
 * Tela de escolha do Digimon inicial. Mostra um cartão por linha marcada como "starter".
 * Não pode ser fechada com Esc: o jogador precisa escolher.
 */
public class StarterScreen extends Screen {
    private static final int CARD_WIDTH = 150;
    private static final int CARD_HEIGHT = 200;
    private static final int CARD_GAP = 24;
    /** Tamanho das imagens em textures/gui/starter/&lt;linha&gt;.png */
    private static final int IMAGE_SIZE = 96;

    private final List<Card> cards = new ArrayList<>();

    public StarterScreen() {
        super(Component.translatable("screen.digimonaurity.starter.title"));
    }

    private record Card(Identifier lineId, DigimonLine line, int x, int y) {
        Identifier image() {
            return lineId.withPath("textures/gui/starter/" + lineId.getPath() + ".png");
        }

        String langKey(String suffix) {
            return "line." + lineId.getNamespace() + "." + lineId.getPath() + "." + suffix;
        }
    }

    @Override
    protected void init() {
        cards.clear();
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return;
        }
        List<Map.Entry<ResourceKey<DigimonLine>, DigimonLine>> starters = mc.level.registryAccess()
                .lookupOrThrow(DigimonRegistries.LINE).entrySet().stream()
                .filter(e -> e.getValue().starter())
                .sorted(Comparator.comparing(e -> e.getKey().identifier().toString()))
                .toList();

        int total = starters.size() * CARD_WIDTH + Math.max(0, starters.size() - 1) * CARD_GAP;
        int x = (width - total) / 2;
        int y = Math.max(40, (height - CARD_HEIGHT) / 2 + 10);
        for (Map.Entry<ResourceKey<DigimonLine>, DigimonLine> entry : starters) {
            Card card = new Card(entry.getKey().identifier(), entry.getValue(), x, y);
            cards.add(card);
            addRenderableWidget(Button.builder(
                            Component.translatable("screen.digimonaurity.starter.choose", Component.translatable(card.langKey("name"))),
                            b -> choose(card.lineId()))
                    .bounds(x + 10, y + CARD_HEIGHT - 28, CARD_WIDTH - 20, 20)
                    .build());
            x += CARD_WIDTH + CARD_GAP;
        }
    }

    private void choose(Identifier lineId) {
        ClientPacketDistributor.sendToServer(new DigimonNetwork.ChooseStarter(lineId));
        onClose();
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float partialTick) {
        graphics.centeredText(font, title, width / 2, 16, 0xFFFFFFFF);
        graphics.centeredText(font, Component.translatable("screen.digimonaurity.starter.subtitle"),
                width / 2, 28, 0xFFB8C4D0);

        for (Card card : cards) {
            int accent = ARGB.opaque(card.line().color());
            int x = card.x();
            int y = card.y();
            // Cartão: fundo escuro translúcido com moldura na cor da linha
            graphics.fill(x, y, x + CARD_WIDTH, y + CARD_HEIGHT, 0xC0101820);
            graphics.outline(x, y, CARD_WIDTH, CARD_HEIGHT, accent);
            graphics.fill(x, y, x + CARD_WIDTH, y + 3, accent);

            graphics.blit(RenderPipelines.GUI_TEXTURED, card.image(), x + (CARD_WIDTH - IMAGE_SIZE) / 2, y + 8,
                    0, 0, IMAGE_SIZE, IMAGE_SIZE, IMAGE_SIZE, IMAGE_SIZE);

            graphics.centeredText(font, Component.translatable(card.langKey("name")), x + CARD_WIDTH / 2, y + IMAGE_SIZE + 12, accent);
            graphics.textWithWordWrap(font, Component.translatable(card.langKey("description")),
                    x + 10, y + IMAGE_SIZE + 26, CARD_WIDTH - 20, 0xFFE0E6EC);
        }
        super.extractRenderState(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean shouldCloseOnEsc() {
        return false;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
