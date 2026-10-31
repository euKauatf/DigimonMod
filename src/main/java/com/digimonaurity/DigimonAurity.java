package com.digimonaurity;

import org.slf4j.Logger;

import com.digimonaurity.registry.DigimonBlocks;
import com.digimonaurity.registry.DigimonRegistries;
import com.mojang.logging.LogUtils;

import net.minecraft.resources.Identifier;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;

/**
 * Ponto de entrada do mod. Roda no cliente e no servidor.
 * Código que só existe no cliente (renderização, teclas, telas) fica em {@link DigimonAurityClient}.
 */
@Mod(DigimonAurity.MODID)
public class DigimonAurity {
    public static final String MODID = "digimonaurity";
    public static final Logger LOGGER = LogUtils.getLogger();

    public DigimonAurity(IEventBus modEventBus, ModContainer modContainer) {
        modEventBus.addListener(this::commonSetup);
        DigimonRegistries.register(modEventBus);
        DigimonBlocks.register(modEventBus);
    }

    private void commonSetup(FMLCommonSetupEvent event) {
        LOGGER.info("Digimon Aurity carregado.");
    }

    /** Cria um identificador no namespace do mod, ex.: id("agumon") -> digimonaurity:agumon. */
    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(MODID, path);
    }
}
