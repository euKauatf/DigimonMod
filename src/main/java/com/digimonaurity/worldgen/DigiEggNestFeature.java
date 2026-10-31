package com.digimonaurity.worldgen;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.feature.Feature;

/**
 * Ninho de Digi-Egg: um círculo de feno e terra com o ovo no meio.
 * O ovo vem do JSON ({"egg": "digimonaurity:gabumon_digiegg"}).
 */
public record DigiEggNestFeature(BlockState egg) implements Feature {
    public static final MapCodec<DigiEggNestFeature> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
            BlockState.CODEC.fieldOf("egg").forGetter(DigiEggNestFeature::egg)
    ).apply(i, DigiEggNestFeature::new));

    @Override
    public MapCodec<DigiEggNestFeature> codec() {
        return CODEC;
    }

    @Override
    public boolean place(WorldGenLevel level, ChunkGenerator generator, RandomSource random, BlockPos origin) {
        if (!level.getBlockState(origin.below()).isSolid() || !level.getFluidState(origin).isEmpty()) {
            return false;
        }
        for (int dx = -2; dx <= 2; dx++) {
            for (int dz = -2; dz <= 2; dz++) {
                int d2 = dx * dx + dz * dz;
                if (d2 > 5) {
                    continue;
                }
                BlockPos ground = origin.offset(dx, -1, dz);
                setBlock(level, ground, d2 <= 1 ? Blocks.HAY_BLOCK.defaultBlockState() : Blocks.COARSE_DIRT.defaultBlockState());
                setBlock(level, ground.above(), Blocks.AIR.defaultBlockState());
                setBlock(level, ground.above(2), Blocks.AIR.defaultBlockState());
            }
        }
        // Borda de "galhos" (cercas de carvalho) ao redor
        for (int[] o : new int[][] {{2, 0}, {-2, 0}, {0, 2}, {0, -2}}) {
            setBlock(level, origin.offset(o[0], 0, o[1]), Blocks.OAK_FENCE.defaultBlockState());
        }
        setBlock(level, origin, egg);
        return true;
    }
}
