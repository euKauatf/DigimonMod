package com.digimonaurity.digimon;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;

/**
 * Tudo o que o mod guarda sobre um jogador. Imutável: cada mudança cria um novo valor,
 * o que faz o NeoForge salvar e sincronizar automaticamente.
 *
 * @param activeLine linha que o jogador está usando agora (vazio = ainda não escolheu)
 * @param lines      progresso em cada linha que o jogador possui
 */
public record DigimonData(Optional<Identifier> activeLine, Map<Identifier, LineProgress> lines) {

    public static final DigimonData EMPTY = new DigimonData(Optional.empty(), Map.of());

    public static final MapCodec<DigimonData> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            Identifier.CODEC.optionalFieldOf("active_line").forGetter(DigimonData::activeLine),
            Codec.unboundedMap(Identifier.CODEC, LineProgress.CODEC).optionalFieldOf("lines", Map.of())
                    .forGetter(DigimonData::lines)
    ).apply(i, DigimonData::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, DigimonData> STREAM_CODEC =
            ByteBufCodecs.fromCodecWithRegistries(CODEC.codec());

    public DigimonData {
        lines = Map.copyOf(lines);
    }

    public boolean hasChosen() {
        return activeLine.isPresent();
    }

    public Optional<LineProgress> activeProgress() {
        return activeLine.map(lines::get);
    }

    /** Copia com o progresso de uma linha substituído (ou adicionado). */
    public DigimonData withLine(Identifier line, LineProgress progress) {
        Map<Identifier, LineProgress> copy = new HashMap<>(lines);
        copy.put(line, progress);
        return new DigimonData(activeLine, copy);
    }

    public DigimonData withActiveLine(Identifier line) {
        return new DigimonData(Optional.of(line), lines);
    }

    /**
     * Progresso do jogador em uma linha. Cada linha é uma campanha própria:
     * descobertas e primeiras vitórias contam separadamente por linha.
     *
     * @param form             forma atual dentro da linha
     * @param level            nível da linha
     * @param xp               experiência acumulada no nível atual
     * @param discoveredBiomes biomas já visitados com esta linha
     * @param defeatedSpecies  espécies de criatura já derrotadas com esta linha
     * @param milestones       marcos de exploração conquistados com esta linha (ex.: chefe de território)
     */
    public record LineProgress(Identifier form, int level, int xp,
                               Set<Identifier> discoveredBiomes, Set<Identifier> defeatedSpecies,
                               Set<Identifier> milestones) {
        // Precisa vir antes de CODEC: campos estáticos são inicializados na ordem em que aparecem.
        private static final Codec<Set<Identifier>> ID_SET =
                Identifier.CODEC.listOf().xmap(Set::copyOf, List::copyOf);

        public static final Codec<LineProgress> CODEC = RecordCodecBuilder.create(i -> i.group(
                Identifier.CODEC.fieldOf("form").forGetter(LineProgress::form),
                Codec.INT.optionalFieldOf("level", 1).forGetter(LineProgress::level),
                Codec.INT.optionalFieldOf("xp", 0).forGetter(LineProgress::xp),
                ID_SET.optionalFieldOf("discovered_biomes", Set.of()).forGetter(LineProgress::discoveredBiomes),
                ID_SET.optionalFieldOf("defeated_species", Set.of()).forGetter(LineProgress::defeatedSpecies),
                ID_SET.optionalFieldOf("milestones", Set.of()).forGetter(LineProgress::milestones)
        ).apply(i, LineProgress::new));

        public LineProgress {
            discoveredBiomes = Set.copyOf(discoveredBiomes);
            defeatedSpecies = Set.copyOf(defeatedSpecies);
            milestones = Set.copyOf(milestones);
        }

        public static LineProgress start(Identifier form) {
            return new LineProgress(form, 1, 0, Set.of(), Set.of(), Set.of());
        }

        public LineProgress withForm(Identifier newForm) {
            return new LineProgress(newForm, level, xp, discoveredBiomes, defeatedSpecies, milestones);
        }

        public LineProgress withLevelAndXp(int newLevel, int newXp) {
            return new LineProgress(form, newLevel, newXp, discoveredBiomes, defeatedSpecies, milestones);
        }

        public LineProgress withBiome(Identifier biome) {
            return new LineProgress(form, level, xp, plus(discoveredBiomes, biome), defeatedSpecies, milestones);
        }

        public LineProgress withSpecies(Identifier species) {
            return new LineProgress(form, level, xp, discoveredBiomes, plus(defeatedSpecies, species), milestones);
        }

        public LineProgress withMilestone(Identifier milestone) {
            return new LineProgress(form, level, xp, discoveredBiomes, defeatedSpecies, plus(milestones, milestone));
        }

        /** Tem todos os marcos exigidos por uma forma? */
        public boolean meets(DigimonForm target) {
            return milestones.containsAll(target.requires());
        }

        private static Set<Identifier> plus(Set<Identifier> set, Identifier extra) {
            Set<Identifier> copy = new HashSet<>(set);
            copy.add(extra);
            return copy;
        }
    }
}
