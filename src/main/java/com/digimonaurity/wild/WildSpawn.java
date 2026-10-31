package com.digimonaurity.wild;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.core.HolderSet;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.biome.Biome;

/**
 * Onde e como um Digimon selvagem aparece.
 * Definido em data/digimonaurity/digimonaurity/wild_spawn/&lt;nome&gt;.json.
 *
 * @param biomes     biomas onde pode aparecer (lista ou tag)
 * @param line       linha evolutiva usada para digievoluir durante a luta
 * @param form       forma com que nasce (rebaixada se passar do teto da região)
 * @param weight     chance relativa entre os selvagens possíveis naquele bioma
 * @param aggressive se ataca jogadores à vista; neutros só revidam
 */
public record WildSpawn(HolderSet<Biome> biomes, Identifier line, Identifier form, int weight, boolean aggressive) {

    public static final Codec<WildSpawn> CODEC = RecordCodecBuilder.create(i -> i.group(
            Biome.LIST_CODEC.fieldOf("biomes").forGetter(WildSpawn::biomes),
            Identifier.CODEC.fieldOf("line").forGetter(WildSpawn::line),
            Identifier.CODEC.fieldOf("form").forGetter(WildSpawn::form),
            Codec.intRange(1, 1000).optionalFieldOf("weight", 10).forGetter(WildSpawn::weight),
            Codec.BOOL.optionalFieldOf("aggressive", false).forGetter(WildSpawn::aggressive)
    ).apply(i, WildSpawn::new));
}
