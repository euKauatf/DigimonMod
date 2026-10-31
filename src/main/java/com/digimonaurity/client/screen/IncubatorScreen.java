package com.digimonaurity.client.screen;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.evolution.DigimonEvolution;
import com.digimonaurity.network.DigimonNetwork;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;
import net.neoforged.neoforge.client.network.ClientPacketDistributor;

/** Incubadora: escolha qual das suas linhas usar. Cada linha guarda seu próprio progresso. */
public class IncubatorScreen extends Screen {
    private static final int ROW_WIDTH = 220;
    private static final int ROW_HEIGHT = 24;

    private record Row(Identifier line, DigimonData.LineProgress progress, int color, int y, boolean active) {
    }

    private final List<Row> rows = new ArrayList<>();

    public IncubatorScreen() {
        super(Component.translatable("screen.digimonaurity.incubator.title"));
    }

    @Override
    protected void init() {
        rows.clear();
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) {
            return;
        }
        DigimonData data = PlayerDigimon.getData(mc.player);
        int y = Math.max(40, height / 2 - data.lines().size() * ROW_HEIGHT / 2);
        int x = (width - ROW_WIDTH) / 2;
        for (Map.Entry<Identifier, DigimonData.LineProgress> entry : data.lines().entrySet()) {
            DigimonLine line = PlayerDigimon.lookup(mc.player, DigimonRegistries.LINE, entry.getKey());
            boolean active = data.activeLine().map(entry.getKey()::equals).orElse(false);
            Row row = new Row(entry.getKey(), entry.getValue(), line == null ? 0xFFFFFFFF : ARGB.opaque(line.color()), y, active);
            rows.add(row);
            Button button = Button.builder(Component.translatable(active
                                    ? "screen.digimonaurity.incubator.active" : "screen.digimonaurity.incubator.use"),
                            b -> {
                                ClientPacketDistributor.sendToServer(new DigimonNetwork.SwitchLine(row.line()));
                                onClose();
                            })
                    .bounds(x + ROW_WIDTH - 70, y + 2, 66, 20).build();
            button.active = !active;
            addRenderableWidget(button);
            y += ROW_HEIGHT + 4;
        }
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float partialTick) {
        graphics.centeredText(font, title, width / 2, 16, 0xFFFFFFFF);
        graphics.centeredText(font, Component.translatable("screen.digimonaurity.incubator.subtitle"), width / 2, 28, 0xFFB8C4D0);
        int x = (width - ROW_WIDTH) / 2;
        for (Row row : rows) {
            graphics.fill(x, row.y(), x + ROW_WIDTH, row.y() + ROW_HEIGHT, 0xC0101820);
            graphics.fill(x, row.y(), x + 3, row.y() + ROW_HEIGHT, row.color());
            Component name = Component.translatable("line." + row.line().getNamespace() + "." + row.line().getPath() + ".name");
            graphics.text(font, name, x + 8, row.y() + 4, row.color(), true);
            graphics.text(font, Component.translatable("screen.digimonaurity.incubator.detail",
                            DigimonEvolution.formName(row.progress().form()), row.progress().level()),
                    x + 8, row.y() + 14, 0xFFD0D8E0, true);
        }
        super.extractRenderState(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
