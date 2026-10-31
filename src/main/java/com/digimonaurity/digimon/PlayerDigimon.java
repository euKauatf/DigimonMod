package com.digimonaurity.digimon;

import java.util.Optional;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.core.Registry;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.player.Player;

/** Ponto único para ler e alterar o Digimon de um jogador. */
public final class PlayerDigimon {
    private PlayerDigimon() {
    }

    /**
     * Lê os dados sem criá-los. Usar getData() aqui criaria o valor padrão e tentaria sincronizá-lo,
     * o que quebra durante a construção do jogador (antes de a conexão existir).
     */
    public static DigimonData getData(Player player) {
        return player.getExistingData(DigimonRegistries.DIGIMON_DATA).orElse(DigimonData.EMPTY);
    }

    /** Altera os dados. Só tem efeito real no servidor, que salva e sincroniza com os clientes. */
    public static void setData(Player player, DigimonData data) {
        player.setData(DigimonRegistries.DIGIMON_DATA, data);
    }

    /** Id da forma atual do jogador, se ele já for um Digimon. */
    public static Optional<Identifier> getFormId(Player player) {
        return getData(player).activeProgress().map(DigimonData.LineProgress::form);
    }

    /** Forma atual do jogador, ou null se ele não for um Digimon (ou se os dados ainda não chegaram). */
    public static @Nullable DigimonForm getForm(Player player) {
        return getFormId(player).map(id -> lookup(player, DigimonRegistries.FORM, id)).orElse(null);
    }

    /** Altera o progresso da linha ativa (não faz nada se o jogador ainda não escolheu). */
    public static void updateActiveLine(Player player, java.util.function.UnaryOperator<DigimonData.LineProgress> change) {
        DigimonData data = getData(player);
        if (data.activeLine().isEmpty()) {
            return;
        }
        Identifier lineId = data.activeLine().get();
        DigimonData.LineProgress progress = data.lines().get(lineId);
        if (progress != null) {
            setData(player, data.withLine(lineId, change.apply(progress)));
        }
    }

    public static <T> @Nullable T lookup(Player player, ResourceKey<Registry<T>> registry, Identifier id) {
        return player.level().registryAccess().lookup(registry).map(r -> r.getValue(id)).orElse(null);
    }

    /**
     * Torna o jogador um Digimon da linha indicada, começando na forma inicial da linha.
     * Se ele já tinha progresso nessa linha, retoma de onde parou.
     *
     * @return false se a linha não existir
     */
    public static boolean setActiveLine(Player player, Identifier lineId) {
        DigimonLine line = lookup(player, DigimonRegistries.LINE, lineId);
        if (line == null) {
            return false;
        }
        DigimonData data = getData(player);
        if (!data.lines().containsKey(lineId)) {
            data = data.withLine(lineId, DigimonData.LineProgress.start(line.startingForm()));
        }
        setData(player, data.withActiveLine(lineId));
        return true;
    }
}
