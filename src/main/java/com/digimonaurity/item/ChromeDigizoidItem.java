package com.digimonaurity.item;

import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.evolution.DigimonEvolution;
import com.digimonaurity.evolution.DigimonMilestones;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Cromo Digizoide: metal raro das profundezas. Absorvê-lo (clique direito) conquista
 * o marco exigido para o MetalGreymon. Cai ao minerar minérios abaixo da camada 0.
 */
public class ChromeDigizoidItem extends Item {

    public ChromeDigizoidItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        if (!(player instanceof ServerPlayer serverPlayer) || !PlayerDigimon.getData(serverPlayer).hasChosen()) {
            return InteractionResult.PASS;
        }
        boolean had = PlayerDigimon.getData(serverPlayer).activeProgress()
                .map(p -> p.milestones().contains(DigimonMilestones.CHROME_DIGIZOID)).orElse(true);
        if (had) {
            serverPlayer.sendOverlayMessage(Component.translatable("message.digimonaurity.chrome_owned"));
            return InteractionResult.FAIL;
        }
        ItemStack stack = player.getItemInHand(hand);
        stack.consume(1, player);
        DigimonEvolution.grantMilestone(serverPlayer, DigimonMilestones.CHROME_DIGIZOID);
        return InteractionResult.SUCCESS;
    }
}
