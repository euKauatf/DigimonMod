package com.digimonaurity.block;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.registry.DigimonBlocks;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

/** Altar no centro de cada Território. A lógica fica em {@link TerritoryAltarBlockEntity}. */
public class TerritoryAltarBlock extends Block implements EntityBlock {

    public TerritoryAltarBlock(Properties properties) {
        super(properties);
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new TerritoryAltarBlockEntity(pos, state);
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T extends BlockEntity> @Nullable BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        if (level.isClientSide() || type != DigimonBlocks.TERRITORY_ALTAR_ENTITY.get()) {
            return null;
        }
        return (BlockEntityTicker<T>) (BlockEntityTicker<TerritoryAltarBlockEntity>)
                (lvl, pos, st, altar) -> TerritoryAltarBlockEntity.serverTick((ServerLevel) lvl, pos, altar);
    }
}
