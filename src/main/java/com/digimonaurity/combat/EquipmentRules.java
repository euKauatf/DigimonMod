package com.digimonaurity.combat;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.PlayerDigimon;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.MaceItem;
import net.minecraft.world.item.TridentItem;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.living.LivingEntityUseItemEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.AttackEntityEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * Decisão de design: o combate vem só do Digimon.
 * - Armaduras não podem ser vestidas (voltam para o inventário).
 * - Armas (espada, lança, maça, tridente, arco, besta) não podem ser usadas.
 * - Ferramentas continuam funcionando para minerar; batendo com elas, vale só o dano das garras.
 * Vale em qualquer modo de jogo, exceto Espectador.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class EquipmentRules {
    private static final EquipmentSlot[] ARMOR = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};

    private EquipmentRules() {
    }

    private static boolean isDigimon(Player player) {
        return !player.isSpectator() && PlayerDigimon.getForm(player) != null;
    }

    private static boolean isMeleeWeapon(ItemStack stack) {
        return stack.is(ItemTags.SWORDS) || stack.is(ItemTags.SPEARS)
                || stack.getItem() instanceof MaceItem || stack.getItem() instanceof TridentItem;
    }

    private static boolean isRangedWeapon(ItemStack stack) {
        return stack.getItem() instanceof BowItem || stack.getItem() instanceof CrossbowItem
                || stack.getItem() instanceof TridentItem;
    }

    private static void warnNoWeapons(Player player) {
        if (player instanceof ServerPlayer serverPlayer) {
            serverPlayer.sendOverlayMessage(Component.translatable("message.digimonaurity.no_weapons"));
        }
    }

    // ------------------------------------------------------------- armaduras

    @SubscribeEvent
    static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.tickCount % 20 != 0 || !isDigimon(player)) {
            return;
        }
        boolean removed = false;
        for (EquipmentSlot slot : ARMOR) {
            ItemStack worn = player.getItemBySlot(slot);
            if (worn.isEmpty()) {
                continue;
            }
            player.setItemSlot(slot, ItemStack.EMPTY);
            if (!player.getInventory().add(worn)) {
                player.level().addFreshEntity(new ItemEntity(player.level(), player.getX(), player.getY(), player.getZ(), worn));
            }
            removed = true;
        }
        if (removed) {
            player.sendOverlayMessage(Component.translatable("message.digimonaurity.no_armor"));
        }
    }

    // ----------------------------------------------------------------- armas

    /** Golpe com arma corpo a corpo: cancelado. */
    @SubscribeEvent
    static void onAttack(AttackEntityEvent event) {
        Player player = event.getEntity();
        if (isDigimon(player) && isMeleeWeapon(player.getMainHandItem())) {
            event.setCanceled(true);
            warnNoWeapons(player);
        }
    }

    /** Arco, besta e tridente: não carregam nem disparam. */
    @SubscribeEvent
    static void onRightClickItem(PlayerInteractEvent.RightClickItem event) {
        if (isDigimon(event.getEntity()) && isRangedWeapon(event.getItemStack())) {
            event.setCanceled(true);
            event.setCancellationResult(InteractionResult.FAIL);
            warnNoWeapons(event.getEntity());
        }
    }

    /** Segurança extra: se começar a puxar o arco por outro caminho, para. */
    @SubscribeEvent
    static void onStartUsingItem(LivingEntityUseItemEvent.Start event) {
        if (event.getEntity() instanceof Player player && isDigimon(player) && isRangedWeapon(event.getItem())) {
            event.setCanceled(true);
        }
    }

    /**
     * Golpe com ferramenta (machado, picareta...): tira a parte do dano que veio dela.
     * Mantém a proporção (golpe crítico e golpe "carregado" continuam valendo).
     */
    @SubscribeEvent
    static void onIncomingDamage(LivingIncomingDamageEvent event) {
        if (!(event.getSource().getDirectEntity() instanceof ServerPlayer player)
                || !event.getSource().is(DamageTypes.PLAYER_ATTACK)) {
            return;
        }
        DigimonForm form = PlayerDigimon.getForm(player);
        if (form == null || player.getMainHandItem().isEmpty()) {
            return;
        }
        double withTool = player.getAttributeValue(Attributes.ATTACK_DAMAGE);
        double claws = form.stats().basicDamage();
        if (withTool > claws + 0.01) {
            event.setAmount((float) (event.getAmount() * claws / withTool));
        }
    }
}
