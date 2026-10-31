package com.digimonaurity.client;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.network.DigimonNetwork;
import com.mojang.blaze3d.platform.InputConstants;

import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.network.ClientPacketDistributor;

/** Teclas dos ataques especiais (padrão Z, X e C; podem ser trocadas em Opções → Controles). */
@EventBusSubscriber(modid = DigimonAurity.MODID, value = Dist.CLIENT)
public final class DigimonKeys {
    public static final KeyMapping.Category CATEGORY = KeyMapping.Category.register(DigimonAurity.id("digimon"));

    public static final KeyMapping[] ATTACKS = {
            new KeyMapping("key.digimonaurity.attack_1", InputConstants.KEY_Z, CATEGORY),
            new KeyMapping("key.digimonaurity.attack_2", InputConstants.KEY_X, CATEGORY),
            new KeyMapping("key.digimonaurity.attack_3", InputConstants.KEY_C, CATEGORY),
    };

    public static final KeyMapping EVOLVE = new KeyMapping("key.digimonaurity.evolve", InputConstants.KEY_V, CATEGORY);
    public static final KeyMapping DEVOLVE = new KeyMapping("key.digimonaurity.devolve", InputConstants.KEY_B, CATEGORY);

    private DigimonKeys() {
    }

    @SubscribeEvent
    static void onRegisterKeys(RegisterKeyMappingsEvent event) {
        event.registerCategory(CATEGORY);
        for (KeyMapping key : ATTACKS) {
            event.register(key);
        }
        event.register(EVOLVE);
        event.register(DEVOLVE);
    }

    @SubscribeEvent
    static void onClientTick(ClientTickEvent.Post event) {
        Minecraft mc = Minecraft.getInstance();
        DigimonForm form = mc.player == null ? null : PlayerDigimon.getForm(mc.player);
        boolean canAct = form != null && mc.gui.screen() == null;
        for (int slot = 0; slot < ATTACKS.length; slot++) {
            while (ATTACKS[slot].consumeClick()) {
                if (canAct && form.attack(slot).isPresent()) {
                    ClientPacketDistributor.sendToServer(new DigimonNetwork.UseAttack(slot));
                }
            }
        }
        while (EVOLVE.consumeClick()) {
            if (canAct) {
                ClientPacketDistributor.sendToServer(new DigimonNetwork.Transform(+1));
            }
        }
        while (DEVOLVE.consumeClick()) {
            if (canAct) {
                ClientPacketDistributor.sendToServer(new DigimonNetwork.Transform(-1));
            }
        }
    }
}
