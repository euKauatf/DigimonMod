package com.digimonaurity.worldgen;

import com.digimonaurity.registry.DigimonBlocks;
import com.mojang.serialization.MapCodec;

import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.feature.Feature;

/**
 * Templo do Brasão: construção rara de pedra e ouro, só longe do spawn.
 * No centro fica o Pedestal do Brasão, que invoca o guardião.
 */
public record CrestTempleFeature() implements Feature {
    public static final MapCodec<CrestTempleFeature> CODEC = MapCodec.unit(CrestTempleFeature::new);
    /** Distância mínima do spawn do mundo, em blocos (o Mega é o fim da jornada). */
    public static final int MIN_DISTANCE = 1000;
    private static final int HALF = 5;

    @Override
    public MapCodec<CrestTempleFeature> codec() {
        return CODEC;
    }

    @Override
    public boolean place(WorldGenLevel level, ChunkGenerator generator, RandomSource random, BlockPos origin) {
        BlockPos spawn = level.getLevelData().getRespawnData().pos();
        double dx0 = origin.getX() - spawn.getX();
        double dz0 = origin.getZ() - spawn.getZ();
        if (dx0 * dx0 + dz0 * dz0 < (double) MIN_DISTANCE * MIN_DISTANCE) {
            return false;
        }
        if (!level.getBlockState(origin.below()).isSolid() || !level.getFluidState(origin).isEmpty()) {
            return false;
        }
        BlockState bricks = Blocks.STONE_BRICKS.defaultBlockState();
        BlockState chiseled = Blocks.CHISELED_STONE_BRICKS.defaultBlockState();
        BlockState gold = Blocks.GOLD_BLOCK.defaultBlockState();
        BlockState slab = Blocks.STONE_BRICK_SLAB.defaultBlockState();
        BlockState air = Blocks.AIR.defaultBlockState();

        for (int dx = -HALF; dx <= HALF; dx++) {
            for (int dz = -HALF; dz <= HALF; dz++) {
                boolean border = Math.abs(dx) == HALF || Math.abs(dz) == HALF;
                boolean center = Math.abs(dx) <= 1 && Math.abs(dz) <= 1;
                // Piso: borda cinzelada, centro de ouro
                setBlock(level, origin.offset(dx, -1, dz), center ? gold : border ? chiseled : bricks);
                // Fundação até o chão
                for (int down = 2; down <= 6 && !level.getBlockState(origin.offset(dx, -down, dz)).isSolid(); down++) {
                    setBlock(level, origin.offset(dx, -down, dz), bricks);
                }
                // Espaço interno livre
                for (int up = 0; up <= 4; up++) {
                    setBlock(level, origin.offset(dx, up, dz), air);
                }
                // Teto de lajes, com uma abertura de vidro no meio
                setBlock(level, origin.offset(dx, 5, dz), center ? Blocks.GLASS.defaultBlockState() : slab);
            }
        }
        // Pilares nos cantos, com topo de ouro
        int p = HALF - 1;
        for (int[] c : new int[][] {{p, p}, {-p, p}, {p, -p}, {-p, -p}}) {
            for (int y = 0; y < 4; y++) {
                setBlock(level, origin.offset(c[0], y, c[1]), y % 2 == 0 ? chiseled : bricks);
            }
            setBlock(level, origin.offset(c[0], 4, c[1]), gold);
        }
        setBlock(level, origin, DigimonBlocks.CREST_PEDESTAL.get().defaultBlockState());
        return true;
    }
}
