package com.digimonaurity;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;

/** Parte do mod que só carrega no cliente. Nunca é carregada num servidor dedicado. */
@Mod(value = DigimonAurity.MODID, dist = Dist.CLIENT)
@EventBusSubscriber(modid = DigimonAurity.MODID, value = Dist.CLIENT)
public class DigimonAurityClient {
    public DigimonAurityClient(ModContainer container) {
    }

    @SubscribeEvent
    static void onClientSetup(FMLClientSetupEvent event) {
        DigimonAurity.LOGGER.info("Digimon Aurity: cliente pronto.");
    }
}
