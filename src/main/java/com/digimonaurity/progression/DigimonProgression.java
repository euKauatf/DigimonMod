package com.digimonaurity.progression;

import java.util.Optional;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.evolution.DigimonEvolution;
import com.digimonaurity.registry.DigimonRegistries;
import com.digimonaurity.wild.WildDigimon;

import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.biome.Biome;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Experiência e níveis. Regras (ver GDD):
 * - derrotar criaturas dá XP proporcional à vida delas, cada vez menos se repetir a mesma espécie;
 * - a primeira vitória sobre cada espécie e o primeiro passo em cada bioma dão bônus;
 * - jogadores derrotados não dão XP;
 * - o XP vai para a linha ativa.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class DigimonProgression {
    public static final int MAX_LEVEL = 100;
    public static final int FIRST_SPECIES_BONUS = 15;
    public static final int NEW_BIOME_BONUS = 10;
    private static final int BIOME_CHECK_INTERVAL = 40;

    private DigimonProgression() {
    }

    /** XP necessário para sair deste nível: rápido no começo, mais lento depois. */
    public static int xpToNext(int level) {
        return 8 + Math.round(4f * (float) Math.pow(level, 1.35));
    }

    /** Soma XP à linha ativa, subindo quantos níveis couberem. */
    public static void addXp(ServerPlayer player, int amount) {
        Optional<DigimonData.LineProgress> progress = PlayerDigimon.getData(player).activeProgress();
        if (amount <= 0 || progress.isEmpty()) {
            return;
        }
        int level = progress.get().level();
        int xp = progress.get().xp() + amount;
        int startLevel = level;
        while (level < MAX_LEVEL && xp >= xpToNext(level)) {
            xp -= xpToNext(level);
            level++;
        }
        if (level >= MAX_LEVEL) {
            xp = 0;
        }
        int newLevel = level;
        int newXp = xp;
        PlayerDigimon.updateActiveLine(player, p -> p.withLevelAndXp(newLevel, newXp));

        if (newLevel > startLevel) {
            player.sendSystemMessage(Component.translatable("message.digimonaurity.level_up", newLevel)
                    .withStyle(ChatFormatting.GOLD));
            player.level().playSound(null, player.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.7f, 1.2f);
            DigimonEvolution.announceIfEvolutionUnlocked(player, startLevel, newLevel);
        }
    }

    @SubscribeEvent
    static void onLivingDeath(LivingDeathEvent event) {
        LivingEntity victim = event.getEntity();
        Entity killer = event.getSource().getEntity();
        if (!(killer instanceof ServerPlayer player) || victim instanceof Player || victim.level().isClientSide()) {
            return;
        }
        Optional<DigimonData.LineProgress> progress = PlayerDigimon.getData(player).activeProgress();
        if (progress.isEmpty()) {
            return;
        }
        // Digimon selvagens contam pela forma (Agumon, Greymon...) e valem o dobro dos mobs vanilla.
        boolean digimon = victim instanceof WildDigimon;
        Identifier species = digimon ? ((WildDigimon) victim).formId() : BuiltInRegistries.ENTITY_TYPE.getKey(victim.getType());
        float multiplier = player.getData(DigimonRegistries.RUNTIME).registerKill(species, player.level().getGameTime());
        float divisor = digimon ? 2f : 4f;
        int base = Math.max(1, Math.min(60, Math.round(victim.getMaxHealth() / divisor)));
        int xp = Math.max(1, Math.round(base * multiplier));

        Component name = digimon ? DigimonEvolution.formName(species) : victim.getType().getDescription();
        if (!progress.get().defeatedSpecies().contains(species)) {
            PlayerDigimon.updateActiveLine(player, p -> p.withSpecies(species));
            xp += FIRST_SPECIES_BONUS;
            player.sendSystemMessage(Component.translatable("message.digimonaurity.first_species", name, FIRST_SPECIES_BONUS)
                    .withStyle(ChatFormatting.AQUA));
        }
        player.sendOverlayMessage(Component.translatable("message.digimonaurity.xp_gain", xp, name));
        addXp(player, xp);
    }

    /** A cada 2 segundos, confere se o jogador pisou num bioma novo para esta linha. */
    @SubscribeEvent
    static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.tickCount % BIOME_CHECK_INTERVAL != 0) {
            return;
        }
        Optional<DigimonData.LineProgress> progress = PlayerDigimon.getData(player).activeProgress();
        if (progress.isEmpty() || player.isSpectator()) {
            return;
        }
        Holder<Biome> biome = player.level().getBiome(player.blockPosition());
        Optional<ResourceKey<Biome>> key = biome.unwrapKey();
        if (key.isEmpty() || progress.get().discoveredBiomes().contains(key.get().identifier())) {
            return;
        }
        Identifier biomeId = key.get().identifier();
        PlayerDigimon.updateActiveLine(player, p -> p.withBiome(biomeId));
        player.sendSystemMessage(Component.translatable("message.digimonaurity.new_biome",
                Component.translatable(biomeId.toLanguageKey("biome")), NEW_BIOME_BONUS).withStyle(ChatFormatting.GREEN));
        addXp(player, NEW_BIOME_BONUS);
    }
}
