package com.digimonaurity.client;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.client.render.DigimonRenderEvents;
import com.digimonaurity.client.screen.IncubatorScreen;
import com.digimonaurity.client.screen.StarterScreen;
import com.digimonaurity.network.DigimonNetwork;

import net.minecraft.client.Minecraft;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.network.event.RegisterClientPayloadHandlersEvent;

/** Como o cliente reage às mensagens do servidor. */
@EventBusSubscriber(modid = DigimonAurity.MODID, value = Dist.CLIENT)
public final class ClientNetwork {
    private ClientNetwork() {
    }

    @SubscribeEvent
    static void onRegisterClientPayloads(RegisterClientPayloadHandlersEvent event) {
        event.register(DigimonNetwork.OpenStarterScreen.TYPE,
                (payload, context) -> Minecraft.getInstance().gui.setScreen(new StarterScreen()));

        event.register(DigimonNetwork.CooldownStarted.TYPE, (payload, context) -> {
            Minecraft mc = Minecraft.getInstance();
            if (mc.level != null) {
                ClientCooldowns.start(mc.level.getGameTime(), payload.slot(), payload.slotTicks(), payload.globalTicks());
            }
        });

        event.register(DigimonNetwork.EvolutionBlocked.TYPE, (payload, context) -> {
            Minecraft mc = Minecraft.getInstance();
            if (mc.level != null) {
                ClientCooldowns.blockEvolution(mc.level.getGameTime(), payload.ticks());
            }
        });

        event.register(DigimonNetwork.OpenIncubator.TYPE,
                (payload, context) -> Minecraft.getInstance().gui.setScreen(new IncubatorScreen()));

        event.register(DigimonNetwork.DigitalSense.TYPE, (payload, context) -> ClientSense.update(payload.kind(), payload.strength()));

        event.register(DigimonNetwork.AttackAnimation.TYPE,
                (payload, context) -> DigimonRenderEvents.playAttackAnimation(payload.entityId()));
    }
}
