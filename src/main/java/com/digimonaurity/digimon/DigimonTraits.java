package com.digimonaurity.digimon;

import com.digimonaurity.DigimonAurity;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import com.digimonaurity.progression.DigimonRuntime;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.network.chat.Component;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.entity.player.Abilities;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Características elementais das formas:
 * - resistência a fogo e lava (linha Agumon);
 * - resistência ao frio e água congelando sob os pés (linha Gabumon).
 * Os valores vêm de "stats" no JSON de cada forma.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class DigimonTraits {
    private static final int FROST_RADIUS = 2;
    /** Cansaço por tick voando (4 de cansaço = meia coxinha): cerca de 1 coxinha a cada 8 s. */
    private static final float FLIGHT_EXHAUSTION = 0.05f;
    private static final int MIN_FOOD_TO_FLY = 6;

    private DigimonTraits() {
    }

    @SubscribeEvent
    static void onIncomingDamage(LivingIncomingDamageEvent event) {
        if (!(event.getEntity() instanceof Player player)) {
            return;
        }
        DigimonForm form = PlayerDigimon.getForm(player);
        if (form == null) {
            return;
        }
        float resistance = 0f;
        if (event.getSource().is(DamageTypeTags.IS_FIRE)) {
            resistance = form.stats().fireResistance();
        } else if (event.getSource().is(DamageTypeTags.IS_FREEZING)) {
            resistance = form.stats().coldResistance();
        }
        if (resistance > 0f) {
            event.setAmount(event.getAmount() * (1f - resistance));
        }
    }

    @SubscribeEvent
    static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        DigimonForm form = PlayerDigimon.getForm(player);
        updateFlight(player, form);
        if (form == null) {
            return;
        }
        // Imunes ao frio não ficam congelando (neve fofa, ataques de gelo)
        if (form.stats().coldResistance() >= 1f && player.getTicksFrozen() > 0) {
            player.setTicksFrozen(0);
        }
        // Linha de fogo não fica pegando fogo à toa: o fogo apaga mais rápido
        if (form.stats().fireResistance() >= 0.75f && player.isOnFire() && !player.isInLava()) {
            player.setRemainingFireTicks(Math.min(player.getRemainingFireTicks(), 20));
        }
        // Planeio: segurando o pulo enquanto cai, desce devagar (asas do MetalGreymon)
        if (form.stats().glide() && !player.onGround() && !player.isInWater()
                && player.getLastClientInput().jump() && player.getDeltaMovement().y < 0) {
            player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 10, 0, false, false));
        }
        if (form.stats().frostWalker() && player.onGround() && !player.isSpectator()) {
            freezeWaterAround(player.level(), player.blockPosition().below(), player);
        }
    }

    /**
     * Voo dos Megas: liberado enquanto a forma voa e a fome está acima de 3 coxinhas.
     * Voando, gasta comida rápido. Ao trocar de forma (ou com fome), o voo é retirado.
     * Jogadores no Criativo/Espectador não são afetados.
     */
    private static void updateFlight(ServerPlayer player, @org.jspecify.annotations.Nullable DigimonForm form) {
        if (player.isCreative() || player.isSpectator()) {
            return;
        }
        DigimonRuntime runtime = player.getData(DigimonRegistries.RUNTIME);
        Abilities abilities = player.getAbilities();
        boolean formFlies = form != null && form.stats().flight();
        boolean canFly = formFlies && player.getFoodData().getFoodLevel() > MIN_FOOD_TO_FLY;
        if (canFly && !abilities.mayfly) {
            abilities.mayfly = true;
            player.onUpdateAbilities();
            runtime.grantedFlight = true;
        } else if (!canFly && runtime.grantedFlight) {
            abilities.mayfly = false;
            abilities.flying = false;
            player.onUpdateAbilities();
            runtime.grantedFlight = false;
            if (formFlies) {
                player.sendOverlayMessage(Component.translatable("message.digimonaurity.too_hungry_to_fly"));
            }
        }
        if (abilities.flying && runtime.grantedFlight) {
            player.causeFoodExhaustion(FLIGHT_EXHAUSTION);
        }
    }

    /** Igual à encantamento Passos Gelados: água parada vira gelo que derrete sozinho. */
    private static void freezeWaterAround(ServerLevel level, BlockPos center, Player player) {
        BlockState frosted = Blocks.FROSTED_ICE.defaultBlockState();
        for (BlockPos pos : BlockPos.betweenClosed(center.offset(-FROST_RADIUS, 0, -FROST_RADIUS),
                center.offset(FROST_RADIUS, 0, FROST_RADIUS))) {
            if (pos.distSqr(center) > FROST_RADIUS * FROST_RADIUS + 1) {
                continue;
            }
            BlockState state = level.getBlockState(pos);
            if (state.is(Blocks.WATER) && level.getFluidState(pos).isSource()
                    && level.getBlockState(pos.above()).isAir()
                    && frosted.canSurvive(level, pos)
                    && level.isUnobstructed(frosted, pos, CollisionContext.empty())) {
                level.setBlockAndUpdate(pos.immutable(), frosted);
            }
        }
    }
}
