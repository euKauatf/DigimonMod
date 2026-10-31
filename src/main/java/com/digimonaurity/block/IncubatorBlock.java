package com.digimonaurity.block;

import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.network.DigimonNetwork;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Incubadora: o único lugar onde se troca de linha (decisão de design: trocar de linha
 * é uma escolha feita em casa, não um truque no meio da luta).
 */
public class IncubatorBlock extends Block {
    /** Distância máxima até a incubadora para a troca ser aceita. */
    public static final double MAX_DISTANCE = 6.0;

    public IncubatorBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (player instanceof ServerPlayer serverPlayer) {
            if (!PlayerDigimon.getData(serverPlayer).hasChosen()) {
                return InteractionResult.SUCCESS;
            }
            if (PlayerDigimon.getData(serverPlayer).lines().size() < 2) {
                serverPlayer.sendOverlayMessage(Component.translatable("message.digimonaurity.incubator_one_line"));
                return InteractionResult.SUCCESS;
            }
            serverPlayer.getData(DigimonRegistries.RUNTIME).incubatorPos = pos.immutable();
            PacketDistributor.sendToPlayer(serverPlayer, DigimonNetwork.OpenIncubator.INSTANCE);
        }
        return InteractionResult.SUCCESS;
    }
}
