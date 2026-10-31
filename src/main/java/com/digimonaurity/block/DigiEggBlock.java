package com.digimonaurity.block;

import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Digi-Egg encontrado nos ninhos. Ao tocar nele, o jogador ganha a linha do ovo
 * (sem trocar a atual). O ovo continua no ninho para que amigos também possam pegar.
 */
public class DigiEggBlock extends Block {
    private static final VoxelShape SHAPE = Block.box(5, 0, 5, 11, 9, 11);
    private final Identifier line;

    public DigiEggBlock(Identifier line, Properties properties) {
        super(properties);
        this.line = line;
    }

    public Identifier line() {
        return line;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(player instanceof ServerPlayer serverPlayer) || !(level instanceof ServerLevel serverLevel)) {
            return InteractionResult.SUCCESS;
        }
        DigimonData data = PlayerDigimon.getData(serverPlayer);
        DigimonLine lineDef = PlayerDigimon.lookup(serverPlayer, DigimonRegistries.LINE, line);
        Component lineName = Component.translatable("line." + line.getNamespace() + "." + line.getPath() + ".name");
        if (!data.hasChosen() || lineDef == null) {
            return InteractionResult.SUCCESS;
        }
        if (data.lines().containsKey(line)) {
            serverPlayer.sendOverlayMessage(Component.translatable("message.digimonaurity.egg_owned", lineName));
            return InteractionResult.SUCCESS;
        }
        PlayerDigimon.setData(serverPlayer, data.withLine(line, DigimonData.LineProgress.start(lineDef.startingForm())));
        serverPlayer.sendSystemMessage(Component.translatable("message.digimonaurity.egg_found", lineName)
                .withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD));
        serverLevel.playSound(null, pos, SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 0.8f, 1.2f);
        serverLevel.sendParticles(ParticleTypes.HAPPY_VILLAGER, pos.getX() + 0.5, pos.getY() + 0.6, pos.getZ() + 0.5,
                20, 0.4, 0.4, 0.4, 0.1);
        return InteractionResult.SUCCESS;
    }
}
