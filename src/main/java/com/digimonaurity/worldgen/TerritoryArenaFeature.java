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
 * Território de chefe: uma arena circular de pedra escura com detalhes "digitais" (ciano),
 * quatro pilares iluminados e o altar no centro.
 */
public record TerritoryArenaFeature() implements Feature {
    public static final MapCodec<TerritoryArenaFeature> CODEC = MapCodec.unit(TerritoryArenaFeature::new);
    private static final int RADIUS = 6;

    @Override
    public MapCodec<TerritoryArenaFeature> codec() {
        return CODEC;
    }

    @Override
    public boolean place(WorldGenLevel level, ChunkGenerator generator, RandomSource random, BlockPos origin) {
        // Só em chão firme e razoavelmente plano: nada de arenas flutuando ou dentro d'água.
        for (int dx = -RADIUS; dx <= RADIUS; dx += RADIUS) {
            for (int dz = -RADIUS; dz <= RADIUS; dz += RADIUS) {
                BlockPos ground = origin.offset(dx, -1, dz);
                if (!level.getBlockState(ground).isSolid() || !level.getFluidState(origin.offset(dx, 0, dz)).isEmpty()) {
                    return false;
                }
            }
        }
        BlockState floor = Blocks.POLISHED_DEEPSLATE.defaultBlockState();
        BlockState ring = Blocks.PRISMARINE_BRICKS.defaultBlockState();
        BlockState pillar = Blocks.DEEPSLATE_BRICKS.defaultBlockState();
        BlockState light = Blocks.SEA_LANTERN.defaultBlockState();

        for (int dx = -RADIUS; dx <= RADIUS; dx++) {
            for (int dz = -RADIUS; dz <= RADIUS; dz++) {
                double distance = Math.sqrt(dx * dx + dz * dz);
                if (distance > RADIUS + 0.5) {
                    continue;
                }
                BlockPos pos = origin.offset(dx, -1, dz);
                // Piso, com um anel ciano na borda e outro perto do centro
                boolean ringTile = distance > RADIUS - 0.5 || (distance > 2.5 && distance < 3.5 && (dx + dz) % 2 == 0);
                setBlock(level, pos, ringTile ? ring : floor);
                // Preenche buracos embaixo e limpa o espaço acima
                for (int down = 2; down <= 4 && !level.getBlockState(origin.offset(dx, -down, dz)).isSolid(); down++) {
                    setBlock(level, origin.offset(dx, -down, dz), Blocks.DEEPSLATE.defaultBlockState());
                }
                for (int up = 0; up <= 4; up++) {
                    setBlock(level, origin.offset(dx, up, dz), Blocks.AIR.defaultBlockState());
                }
            }
        }
        // Quatro pilares nas diagonais
        int p = RADIUS - 2;
        for (int[] corner : new int[][] {{p, p}, {-p, p}, {p, -p}, {-p, -p}}) {
            for (int y = 0; y < 3; y++) {
                setBlock(level, origin.offset(corner[0], y, corner[1]), pillar);
            }
            setBlock(level, origin.offset(corner[0], 3, corner[1]), light);
        }
        setBlock(level, origin, DigimonBlocks.TERRITORY_ALTAR.get().defaultBlockState());
        return true;
    }
}
