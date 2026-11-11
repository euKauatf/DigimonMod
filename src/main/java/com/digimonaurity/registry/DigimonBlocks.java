package com.digimonaurity.registry;

import java.util.Set;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.block.DigiEggBlock;
import com.digimonaurity.block.IncubatorBlock;
import com.digimonaurity.block.TerritoryAltarBlock;
import com.digimonaurity.block.TerritoryAltarBlockEntity;
import com.digimonaurity.item.ChromeDigizoidItem;
import com.digimonaurity.worldgen.CrestTempleFeature;
import com.digimonaurity.worldgen.DigiEggNestFeature;
import com.digimonaurity.worldgen.TerritoryArenaFeature;
import com.google.common.collect.ImmutableSet;
import com.mojang.serialization.MapCodec;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.BuildCreativeModeTabContentsEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Blocos do mod, seus itens, entidades de bloco, pontos de interesse e tipos de geração de mundo. */
public final class DigimonBlocks {
    private static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(DigimonAurity.MODID);
    private static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(DigimonAurity.MODID);
    private static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, DigimonAurity.MODID);
    private static final DeferredRegister<PoiType> POI_TYPES =
            DeferredRegister.create(Registries.POINT_OF_INTEREST_TYPE, DigimonAurity.MODID);
    private static final DeferredRegister<MapCodec<? extends Feature>> FEATURE_TYPES =
            DeferredRegister.create(Registries.FEATURE_TYPE, DigimonAurity.MODID);

    // --------------------------------------------------------------- blocos

    public static final DeferredBlock<TerritoryAltarBlock> TERRITORY_ALTAR = BLOCKS.registerBlock("territory_altar",
            TerritoryAltarBlock::new, p -> p.mapColor(MapColor.COLOR_CYAN).strength(-1f, 3600000f).lightLevel(s -> 10));

    /** Pedestal no centro do Templo do Brasão; mesma lógica do altar, com um guardião mais forte. */
    public static final DeferredBlock<TerritoryAltarBlock> CREST_PEDESTAL = BLOCKS.registerBlock("crest_pedestal",
            TerritoryAltarBlock::new, p -> p.mapColor(MapColor.GOLD).strength(-1f, 3600000f).lightLevel(s -> 15));

    public static final DeferredBlock<DigiEggBlock> AGUMON_DIGIEGG = BLOCKS.registerBlock("agumon_digiegg",
            p -> new DigiEggBlock(DigimonAurity.id("agumon"), p),
            p -> p.mapColor(MapColor.COLOR_ORANGE).strength(-1f, 3600000f).lightLevel(s -> 7).noOcclusion());

    public static final DeferredBlock<DigiEggBlock> GABUMON_DIGIEGG = BLOCKS.registerBlock("gabumon_digiegg",
            p -> new DigiEggBlock(DigimonAurity.id("gabumon"), p),
            p -> p.mapColor(MapColor.COLOR_LIGHT_BLUE).strength(-1f, 3600000f).lightLevel(s -> 7).noOcclusion());

    public static final DeferredBlock<DigiEggBlock> VEEMON_DIGIEGG = BLOCKS.registerBlock("veemon_digiegg",
            p -> new DigiEggBlock(DigimonAurity.id("veemon"), p),
            p -> p.mapColor(MapColor.COLOR_BLUE).strength(-1f, 3600000f).lightLevel(s -> 7).noOcclusion());

    public static final DeferredBlock<IncubatorBlock> INCUBATOR = BLOCKS.registerBlock("incubator",
            IncubatorBlock::new, p -> p.mapColor(MapColor.METAL).strength(3f, 6f).sound(SoundType.METAL).lightLevel(s -> 6));

    public static final DeferredItem<BlockItem> INCUBATOR_ITEM = ITEMS.registerSimpleBlockItem("incubator", INCUBATOR);
    public static final DeferredItem<BlockItem> TERRITORY_ALTAR_ITEM = ITEMS.registerSimpleBlockItem("territory_altar", TERRITORY_ALTAR);
    public static final DeferredItem<BlockItem> CREST_PEDESTAL_ITEM = ITEMS.registerSimpleBlockItem("crest_pedestal", CREST_PEDESTAL);
    public static final DeferredItem<BlockItem> AGUMON_DIGIEGG_ITEM = ITEMS.registerSimpleBlockItem("agumon_digiegg", AGUMON_DIGIEGG);
    public static final DeferredItem<BlockItem> GABUMON_DIGIEGG_ITEM = ITEMS.registerSimpleBlockItem("gabumon_digiegg", GABUMON_DIGIEGG);
    public static final DeferredItem<BlockItem> VEEMON_DIGIEGG_ITEM = ITEMS.registerSimpleBlockItem("veemon_digiegg", VEEMON_DIGIEGG);

    /** Marco do MetalGreymon; cai ao minerar minérios abaixo da camada 0. */
    public static final DeferredItem<ChromeDigizoidItem> CHROME_DIGIZOID =
            ITEMS.registerItem("chrome_digizoid", ChromeDigizoidItem::new);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TerritoryAltarBlockEntity>> TERRITORY_ALTAR_ENTITY =
            BLOCK_ENTITIES.register("territory_altar",
                    () -> new BlockEntityType<>(TerritoryAltarBlockEntity::new, Set.of(TERRITORY_ALTAR.get(), CREST_PEDESTAL.get())));

    // ------------------------------------------- pontos de interesse (radar)

    public static final DeferredHolder<PoiType, PoiType> TERRITORY_POI = POI_TYPES.register("territory",
            () -> new PoiType(ImmutableSet.copyOf(TERRITORY_ALTAR.get().getStateDefinition().getPossibleStates()), 0, 1));
    public static final DeferredHolder<PoiType, PoiType> TEMPLE_POI = POI_TYPES.register("crest_temple",
            () -> new PoiType(ImmutableSet.copyOf(CREST_PEDESTAL.get().getStateDefinition().getPossibleStates()), 0, 1));
    public static final DeferredHolder<PoiType, PoiType> DIGIEGG_POI = POI_TYPES.register("digiegg",
            () -> new PoiType(ImmutableSet.<net.minecraft.world.level.block.state.BlockState>builder()
                    .addAll(AGUMON_DIGIEGG.get().getStateDefinition().getPossibleStates())
                    .addAll(GABUMON_DIGIEGG.get().getStateDefinition().getPossibleStates())
                    .addAll(VEEMON_DIGIEGG.get().getStateDefinition().getPossibleStates())
                    .build(), 0, 1));

    // ------------------------------------------------- geração de mundo

    public static final DeferredHolder<MapCodec<? extends Feature>, MapCodec<TerritoryArenaFeature>> TERRITORY_ARENA =
            FEATURE_TYPES.register("territory_arena", () -> TerritoryArenaFeature.CODEC);
    public static final DeferredHolder<MapCodec<? extends Feature>, MapCodec<DigiEggNestFeature>> DIGIEGG_NEST =
            FEATURE_TYPES.register("digiegg_nest", () -> DigiEggNestFeature.CODEC);
    public static final DeferredHolder<MapCodec<? extends Feature>, MapCodec<CrestTempleFeature>> CREST_TEMPLE =
            FEATURE_TYPES.register("crest_temple", () -> CrestTempleFeature.CODEC);

    private DigimonBlocks() {
    }

    public static void register(IEventBus modEventBus) {
        BLOCKS.register(modEventBus);
        ITEMS.register(modEventBus);
        BLOCK_ENTITIES.register(modEventBus);
        POI_TYPES.register(modEventBus);
        FEATURE_TYPES.register(modEventBus);
        modEventBus.addListener(DigimonBlocks::onCreativeTabs);
    }

    private static void onCreativeTabs(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.FUNCTIONAL_BLOCKS) {
            event.accept(INCUBATOR_ITEM);
        }
        if (event.getTabKey() == CreativeModeTabs.INGREDIENTS) {
            event.accept(CHROME_DIGIZOID);
        }
        if (event.getTabKey() == CreativeModeTabs.OP_BLOCKS) {
            event.accept(TERRITORY_ALTAR_ITEM);
            event.accept(CREST_PEDESTAL_ITEM);
            event.accept(AGUMON_DIGIEGG_ITEM);
            event.accept(GABUMON_DIGIEGG_ITEM);
            event.accept(VEEMON_DIGIEGG_ITEM);
        }
    }

    /** Ovo correspondente a uma linha (para o radar ignorar ovos de linhas que o jogador já tem). */
    public static Block eggFor(net.minecraft.resources.Identifier line) {
        return switch (line.getPath()) {
            case "gabumon" -> GABUMON_DIGIEGG.get();
            case "veemon" -> VEEMON_DIGIEGG.get();
            default -> AGUMON_DIGIEGG.get();
        };
    }
}
