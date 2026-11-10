package com.digimonaurity.combat;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonAttack;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.network.DigimonNetwork;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/** Regras de combate e atributos do lado do servidor. */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class DigimonCombat {
    /** Recarga global após qualquer ataque especial: 0,5 s. */
    public static final int GLOBAL_COOLDOWN = 10;

    /** Valores do Steve; os modificadores da forma somam a diferença. */
    private static final double VANILLA_PUNCH = 1.0;
    private static final double VANILLA_HEALTH = 20.0;

    private static final Identifier FORM_DAMAGE = DigimonAurity.id("form_damage");
    private static final Identifier FORM_HEALTH = DigimonAurity.id("form_health");
    private static final Identifier FORM_SPEED = DigimonAurity.id("form_speed");

    private DigimonCombat() {
    }

    /** Tenta usar o ataque especial da tecla indicada. O servidor decide se pode. */
    public static void useAttack(ServerPlayer player, int slot) {
        DigimonForm form = PlayerDigimon.getForm(player);
        if (form == null || player.isSpectator() || !player.isAlive()
                || player.getData(DigimonRegistries.RUNTIME).isTransforming()) {
            return;
        }
        Identifier attackId = form.attack(slot).orElse(null);
        DigimonAttack attack = attackId == null ? null : PlayerDigimon.lookup(player, DigimonRegistries.ATTACK, attackId);
        if (attack == null) {
            return;
        }
        AttackCooldowns cooldowns = player.getData(DigimonRegistries.COOLDOWNS);
        long now = player.level().getGameTime();
        if (!cooldowns.isReady(slot, now)) {
            return;
        }
        cooldowns.start(slot, now, attack.cooldown(), GLOBAL_COOLDOWN);

        AttackExecutor.execute(player, attack);

        PacketDistributor.sendToPlayer(player, new DigimonNetwork.CooldownStarted(slot, attack.cooldown(), GLOBAL_COOLDOWN));
        PacketDistributor.sendToPlayersTrackingEntityAndSelf(player, new DigimonNetwork.AttackAnimation(player.getId()));
    }

    /**
     * Aplica os atributos da forma: dano básico, vida máxima e velocidade.
     * Chamado sempre que a forma muda. A vida é mantida em porcentagem
     * (um Agumon com metade da vida vira um Greymon com metade da vida).
     */
    public static void applyFormStats(Player player, @Nullable DigimonForm form) {
        float healthRatio = player.getMaxHealth() > 0 ? player.getHealth() / player.getMaxHealth() : 1f;
        DigimonForm.Stats stats = form == null ? null : form.stats();

        setModifier(player, Attributes.ATTACK_DAMAGE, FORM_DAMAGE,
                stats == null ? null : stats.basicDamage() - VANILLA_PUNCH, AttributeModifier.Operation.ADD_VALUE);
        setModifier(player, Attributes.MAX_HEALTH, FORM_HEALTH,
                stats == null ? null : stats.maxHealth() - VANILLA_HEALTH, AttributeModifier.Operation.ADD_VALUE);
        setModifier(player, Attributes.MOVEMENT_SPEED, FORM_SPEED,
                stats == null ? null : (double) stats.speed() - 1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);

        if (player.isAlive()) {
            player.setHealth(Math.max(1f, healthRatio * player.getMaxHealth()));
        }
        player.getData(DigimonRegistries.COOLDOWNS).clear();
    }

    private static void setModifier(Player player, Holder<Attribute> attribute, Identifier id,
                                    @Nullable Double amount, AttributeModifier.Operation operation) {
        AttributeInstance instance = player.getAttribute(attribute);
        if (instance == null) {
            return;
        }
        instance.removeModifier(id);
        if (amount != null && amount != 0) {
            instance.addTransientModifier(new AttributeModifier(id, amount, operation));
        }
    }

    /** Formas mais fortes gastam mais comida (fome escala com o estágio). */
    @SubscribeEvent
    static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        DigimonForm form = PlayerDigimon.getForm(player);
        if (form != null && form.stats().hungerDrain() > 0) {
            player.causeFoodExhaustion(form.stats().hungerDrain());
        }
    }
}
