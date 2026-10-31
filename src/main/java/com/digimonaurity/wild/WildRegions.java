package com.digimonaurity.wild;

import java.util.ArrayList;
import java.util.List;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.digimon.DigimonStage;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.biome.Biome;

/**
 * Geografia do perigo: quanto mais longe do spawn do mundo, mais longe os selvagens evoluem.
 * Assim, voltar a uma região antiga depois de evoluir mostra o quanto você cresceu.
 */
public final class WildRegions {
    /** Até esta distância (em blocos) do spawn, selvagens param no Rookie. */
    public static final int ROOKIE_RADIUS = 500;
    /** Até esta distância, param no Champion; além dela, Ultimate. */
    public static final int CHAMPION_RADIUS = 1500;

    private WildRegions() {
    }

    public static DigimonStage stageCap(LevelAccessor level, BlockPos pos) {
        BlockPos spawn = level.getLevelData().getRespawnData().pos();
        double distance = Math.sqrt(spawn.distSqr(new BlockPos(pos.getX(), spawn.getY(), pos.getZ())));
        if (distance < ROOKIE_RADIUS) {
            return DigimonStage.ROOKIE;
        }
        return distance < CHAMPION_RADIUS ? DigimonStage.CHAMPION : DigimonStage.ULTIMATE;
    }

    /** Sorteia, pelo peso, um selvagem que possa aparecer neste bioma (ou null se nenhum). */
    public static @Nullable WildSpawn pick(LevelAccessor level, BlockPos pos, RandomSource random) {
        Registry<WildSpawn> registry = level.registryAccess().lookup(DigimonRegistries.WILD_SPAWN).orElse(null);
        if (registry == null) {
            return null;
        }
        Holder<Biome> biome = level.getBiome(pos);
        List<WildSpawn> options = new ArrayList<>();
        int total = 0;
        for (WildSpawn spawn : registry) {
            if (spawn.biomes().contains(biome)) {
                options.add(spawn);
                total += spawn.weight();
            }
        }
        if (total == 0) {
            return null;
        }
        int roll = random.nextInt(total);
        for (WildSpawn spawn : options) {
            roll -= spawn.weight();
            if (roll < 0) {
                return spawn;
            }
        }
        return null;
    }
}
