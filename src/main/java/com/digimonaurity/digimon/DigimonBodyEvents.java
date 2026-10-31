package com.digimonaurity.digimon;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.combat.DigimonCombat;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.EntityEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Corpo físico do Digimon: hitbox e altura dos olhos.
 * Roda no cliente e no servidor, para que os dois concordem sobre colisões.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class DigimonBodyEvents {
    private DigimonBodyEvents() {
    }

    @SubscribeEvent
    static void onEntitySize(EntityEvent.Size event) {
        if (!(event.getEntity() instanceof Player player)) {
            return;
        }
        DigimonForm form = PlayerDigimon.getForm(player);
        if (form != null) {
            event.setNewSize(form.dimensionsFor(event.getPose()));
        }
    }

    /** Recalcula a hitbox sempre que a forma do jogador muda (escolha, evolução, comandos). */
    @SubscribeEvent
    static void onPlayerTick(PlayerTickEvent.Post event) {
        Player player = event.getEntity();
        String current = PlayerDigimon.getForm(player) == null
                ? ""
                : PlayerDigimon.getFormId(player).map(Object::toString).orElse("");
        if (!current.equals(player.getExistingData(DigimonRegistries.APPLIED_FORM).orElse(""))) {
            player.setData(DigimonRegistries.APPLIED_FORM, current);
            player.refreshDimensions();
            if (!player.level().isClientSide()) {
                DigimonCombat.applyFormStats(player, PlayerDigimon.getForm(player));
            }
        }
    }
}
