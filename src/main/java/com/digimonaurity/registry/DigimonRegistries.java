package com.digimonaurity.registry;

import java.util.function.Supplier;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.combat.AttackCooldowns;
import com.digimonaurity.digimon.DigimonAttack;
import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.entity.DigimonProjectile;
import com.digimonaurity.progression.DigimonRuntime;
import com.digimonaurity.wild.WildDigimon;
import com.digimonaurity.wild.WildSpawn;

import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.RegisterSpawnPlacementsEvent;

import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;
import net.neoforged.neoforge.registries.NewDatapackRegistryEvent;

/** Registros do mod: dados em JSON, entidades e dados presos ao jogador. */
public final class DigimonRegistries {
    /** Formas: data/digimonaurity/digimonaurity/form/*.json */
    public static final ResourceKey<Registry<DigimonForm>> FORM = ResourceKey.createRegistryKey(DigimonAurity.id("form"));
    /** Linhas: data/digimonaurity/digimonaurity/line/*.json */
    public static final ResourceKey<Registry<DigimonLine>> LINE = ResourceKey.createRegistryKey(DigimonAurity.id("line"));
    /** Ataques especiais: data/digimonaurity/digimonaurity/attack/*.json */
    public static final ResourceKey<Registry<DigimonAttack>> ATTACK = ResourceKey.createRegistryKey(DigimonAurity.id("attack"));
    /** Onde nascem os selvagens: data/digimonaurity/digimonaurity/wild_spawn/*.json (só no servidor). */
    public static final ResourceKey<Registry<WildSpawn>> WILD_SPAWN = ResourceKey.createRegistryKey(DigimonAurity.id("wild_spawn"));

    private static final DeferredRegister<AttachmentType<?>> ATTACHMENTS =
            DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, DigimonAurity.MODID);
    private static final DeferredRegister.Entities ENTITIES = DeferredRegister.createEntities(DigimonAurity.MODID);

    /** Dados salvos do jogador: sobrevivem à morte e são enviados a todos que o veem. */
    public static final Supplier<AttachmentType<DigimonData>> DIGIMON_DATA = ATTACHMENTS.register("digimon",
            () -> AttachmentType.builder(() -> DigimonData.EMPTY)
                    .serialize(DigimonData.CODEC)
                    .copyOnDeath()
                    .sync(DigimonData.STREAM_CODEC)
                    .build());

    /** Última forma aplicada à hitbox (não é salva; serve para perceber trocas de forma). */
    public static final Supplier<AttachmentType<String>> APPLIED_FORM = ATTACHMENTS.register("applied_form",
            () -> AttachmentType.builder(() -> "").build());

    /** Recargas dos ataques (só no servidor, não são salvas). */
    public static final Supplier<AttachmentType<AttackCooldowns>> COOLDOWNS = ATTACHMENTS.register("cooldowns",
            () -> AttachmentType.builder(AttackCooldowns::new).build());

    /** Transformação, bloqueios e abates recentes (só no servidor, não são salvos). */
    public static final Supplier<AttachmentType<DigimonRuntime>> RUNTIME = ATTACHMENTS.register("runtime",
            () -> AttachmentType.builder(DigimonRuntime::new).build());

    public static final DeferredHolder<EntityType<?>, EntityType<DigimonProjectile>> PROJECTILE =
            ENTITIES.registerEntityType("projectile", DigimonProjectile::new, MobCategory.MISC,
                    b -> b.sized(0.4f, 0.4f).clientTrackingRange(4).updateInterval(10));

    public static final DeferredHolder<EntityType<?>, EntityType<WildDigimon>> WILD_DIGIMON =
            ENTITIES.registerEntityType("wild_digimon", WildDigimon::new, MobCategory.MONSTER,
                    b -> b.sized(0.7f, 1.4f).clientTrackingRange(8));

    private DigimonRegistries() {
    }

    public static void register(IEventBus modEventBus) {
        ATTACHMENTS.register(modEventBus);
        ENTITIES.register(modEventBus);
        modEventBus.addListener(DigimonRegistries::onNewDatapackRegistry);
        modEventBus.addListener(DigimonRegistries::onEntityAttributes);
        modEventBus.addListener(DigimonRegistries::onSpawnPlacements);
    }

    private static void onEntityAttributes(EntityAttributeCreationEvent event) {
        event.put(WILD_DIGIMON.get(), WildDigimon.createAttributes().build());
    }

    private static void onSpawnPlacements(RegisterSpawnPlacementsEvent event) {
        event.register(WILD_DIGIMON.get(), SpawnPlacementTypes.ON_GROUND, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                WildDigimon::checkWildSpawnRules, RegisterSpawnPlacementsEvent.Operation.REPLACE);
    }

    private static void onNewDatapackRegistry(NewDatapackRegistryEvent event) {
        // O segundo codec envia as definições ao cliente ao entrar no mundo.
        event.worldRegistry(FORM, DigimonForm.CODEC, DigimonForm.CODEC);
        event.worldRegistry(LINE, DigimonLine.CODEC, DigimonLine.CODEC);
        event.worldRegistry(ATTACK, DigimonAttack.CODEC, DigimonAttack.CODEC);
        event.worldRegistry(WILD_SPAWN, WildSpawn.CODEC);
    }
}
