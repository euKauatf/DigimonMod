package com.digimonaurity.evolution;

import java.util.List;
import java.util.Optional;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.digimon.DigimonStage;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.network.DigimonNetwork;
import com.digimonaurity.progression.DigimonRuntime;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Digievolução e desevolução dentro da linha ativa.
 * - Evoluir: próxima forma da linha, se o nível permitir.
 * - Desevoluir: forma anterior, sempre permitido.
 * - Transformar leva 1,5 s (o jogador fica lento e sem atacar) e tem recarga de 5 s.
 * - Depois de morrer, o jogador renasce como Rookie e não passa disso por 3 minutos.
 * Os marcos de exploração (a partir do Champion) entram no marco 7 do plano.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class DigimonEvolution {
    public static final int TRANSFORM_TICKS = 30;
    public static final int TRANSFORM_COOLDOWN = 100;
    public static final int DEATH_BLOCK_TICKS = 3 * 60 * 20;

    private DigimonEvolution() {
    }

    /** Forma vizinha na linha: direction +1 = evoluir, -1 = desevoluir. */
    public static Optional<Identifier> neighbour(Player player, int direction) {
        DigimonData data = PlayerDigimon.getData(player);
        Optional<DigimonData.LineProgress> progress = data.activeProgress();
        if (progress.isEmpty()) {
            return Optional.empty();
        }
        DigimonLine line = PlayerDigimon.lookup(player, DigimonRegistries.LINE, data.activeLine().get());
        if (line == null) {
            return Optional.empty();
        }
        List<Identifier> forms = line.forms();
        int index = forms.indexOf(progress.get().form()) + direction;
        return index >= 0 && index < forms.size() && forms.indexOf(progress.get().form()) >= 0
                ? Optional.of(forms.get(index))
                : Optional.empty();
    }

    /** Pedido do jogador (teclas V e B). */
    public static void request(ServerPlayer player, int direction) {
        DigimonRuntime runtime = player.getData(DigimonRegistries.RUNTIME);
        long now = player.level().getGameTime();
        if (runtime.isTransforming() || PlayerDigimon.getForm(player) == null) {
            return;
        }
        if (now < runtime.transformReadyAt) {
            player.sendOverlayMessage(Component.translatable("message.digimonaurity.transform_cooldown",
                    seconds(runtime.transformReadyAt - now)));
            return;
        }
        Identifier targetId = neighbour(player, direction).orElse(null);
        DigimonForm target = targetId == null ? null : PlayerDigimon.lookup(player, DigimonRegistries.FORM, targetId);
        if (target == null) {
            player.sendOverlayMessage(Component.translatable(direction > 0
                    ? "message.digimonaurity.no_next_form" : "message.digimonaurity.no_previous_form"));
            return;
        }
        if (direction > 0) {
            DigimonData.LineProgress progress = PlayerDigimon.getData(player).activeProgress().orElse(null);
            int level = progress == null ? 1 : progress.level();
            if (level < target.minLevel()) {
                player.sendOverlayMessage(Component.translatable("message.digimonaurity.need_level",
                        formName(targetId), target.minLevel()));
                return;
            }
            if (progress != null && !progress.meets(target)) {
                Identifier missing = target.requires().stream()
                        .filter(m -> !progress.milestones().contains(m)).findFirst().orElse(null);
                player.sendOverlayMessage(Component.translatable("message.digimonaurity.need_milestone",
                        formName(targetId), milestoneName(missing)));
                return;
            }
            if (target.stage().compareTo(DigimonStage.ROOKIE) > 0 && now < runtime.evolutionBlockedUntil) {
                player.sendOverlayMessage(Component.translatable("message.digimonaurity.evolution_blocked",
                        seconds(runtime.evolutionBlockedUntil - now)));
                return;
            }
        }
        runtime.transformTarget = targetId;
        runtime.transformDoneAt = now + TRANSFORM_TICKS;
        player.level().playSound(null, player.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1f, 1.4f);
        player.sendOverlayMessage(Component.translatable(direction > 0
                ? "message.digimonaurity.evolving" : "message.digimonaurity.devolving"));
    }

    @SubscribeEvent
    static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        DigimonRuntime runtime = player.getData(DigimonRegistries.RUNTIME);
        if (!runtime.isTransforming()) {
            return;
        }
        ServerLevel level = player.level();
        long now = level.getGameTime();
        // Espiral de luz subindo pelo corpo enquanto transforma
        double angle = (now % 20) / 20.0 * Math.PI * 2;
        double radius = Math.max(0.6, player.getBbWidth());
        double height = (TRANSFORM_TICKS - (runtime.transformDoneAt - now)) / (double) TRANSFORM_TICKS * player.getBbHeight();
        for (int i = 0; i < 2; i++) {
            double a = angle + i * Math.PI;
            level.sendParticles(ParticleTypes.END_ROD, player.getX() + Math.cos(a) * radius, player.getY() + height,
                    player.getZ() + Math.sin(a) * radius, 1, 0, 0, 0, 0);
        }
        player.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 5, 3, false, false));

        if (now >= runtime.transformDoneAt) {
            Identifier target = runtime.transformTarget;
            Identifier before = PlayerDigimon.getFormId(player).orElse(null);
            runtime.transformTarget = null;
            runtime.transformReadyAt = now + TRANSFORM_COOLDOWN;
            if (target != null) {
                PlayerDigimon.updateActiveLine(player, p -> p.withForm(target));
                level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, player.getX(), player.getY() + player.getBbHeight() / 2,
                        player.getZ(), 40, 0.5, 0.8, 0.5, 0.3);
                level.sendParticles(ParticleTypes.END_ROD, player.getX(), player.getY() + 1, player.getZ(), 30, 0.6, 1, 0.6, 0.1);
                level.playSound(null, player.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 1f, 0.8f);
                if (before != null) {
                    player.sendOverlayMessage(Component.translatable("message.digimonaurity.transformed",
                            formName(before), formName(target)).withStyle(ChatFormatting.GOLD));
                }
            }
        }
    }

    /** Morte: renasce como Rookie da linha ativa e não pode passar disso por alguns minutos. */
    @SubscribeEvent
    static void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || event.isEndConquered()) {
            return;
        }
        DigimonForm form = PlayerDigimon.getForm(player);
        DigimonData data = PlayerDigimon.getData(player);
        if (form == null || form.stage().compareTo(DigimonStage.ROOKIE) <= 0) {
            return;
        }
        DigimonLine line = PlayerDigimon.lookup(player, DigimonRegistries.LINE, data.activeLine().get());
        Identifier rookie = line == null ? null : line.forms().stream()
                .filter(id -> {
                    DigimonForm f = PlayerDigimon.lookup(player, DigimonRegistries.FORM, id);
                    return f != null && f.stage() == DigimonStage.ROOKIE;
                })
                .findFirst().orElse(null);
        if (rookie == null) {
            return;
        }
        PlayerDigimon.updateActiveLine(player, p -> p.withForm(rookie));
        DigimonRuntime runtime = player.getData(DigimonRegistries.RUNTIME);
        runtime.evolutionBlockedUntil = player.level().getGameTime() + DEATH_BLOCK_TICKS;
        PacketDistributor.sendToPlayer(player, new DigimonNetwork.EvolutionBlocked(DEATH_BLOCK_TICKS));
        player.sendSystemMessage(Component.translatable("message.digimonaurity.death_rookie", formName(rookie),
                DEATH_BLOCK_TICKS / 20 / 60).withStyle(ChatFormatting.RED));
    }

    /** Avisa quando subir de nível libera a próxima forma (se os marcos já estiverem feitos). */
    public static void announceIfEvolutionUnlocked(ServerPlayer player, int oldLevel, int newLevel) {
        Identifier nextId = neighbour(player, +1).orElse(null);
        DigimonForm next = nextId == null ? null : PlayerDigimon.lookup(player, DigimonRegistries.FORM, nextId);
        DigimonData.LineProgress progress = PlayerDigimon.getData(player).activeProgress().orElse(null);
        if (next != null && progress != null && next.minLevel() > oldLevel && next.minLevel() <= newLevel) {
            player.sendSystemMessage(progress.meets(next)
                    ? Component.translatable("message.digimonaurity.can_evolve", formName(nextId))
                            .withStyle(ChatFormatting.YELLOW, ChatFormatting.BOLD)
                    : Component.translatable("message.digimonaurity.level_ok_need_milestone", formName(nextId),
                            milestoneName(next.requires().getFirst())).withStyle(ChatFormatting.YELLOW));
        }
    }

    /** Concede um marco à linha ativa do jogador e avisa se isso liberou a próxima evolução. */
    public static void grantMilestone(ServerPlayer player, Identifier milestone) {
        DigimonData.LineProgress progress = PlayerDigimon.getData(player).activeProgress().orElse(null);
        if (progress == null || progress.milestones().contains(milestone)) {
            return;
        }
        PlayerDigimon.updateActiveLine(player, p -> p.withMilestone(milestone));
        player.sendSystemMessage(Component.translatable("message.digimonaurity.milestone", milestoneName(milestone))
                .withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.BOLD));
        player.level().playSound(null, player.blockPosition(), SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 0.8f, 1f);

        Identifier nextId = neighbour(player, +1).orElse(null);
        DigimonForm next = nextId == null ? null : PlayerDigimon.lookup(player, DigimonRegistries.FORM, nextId);
        DigimonData.LineProgress updated = PlayerDigimon.getData(player).activeProgress().orElse(null);
        if (next != null && updated != null && updated.meets(next) && updated.level() >= next.minLevel()) {
            player.sendSystemMessage(Component.translatable("message.digimonaurity.can_evolve", formName(nextId))
                    .withStyle(ChatFormatting.YELLOW, ChatFormatting.BOLD));
        }
    }

    public static Component formName(@Nullable Identifier formId) {
        return formId == null ? Component.literal("?")
                : Component.translatable("form." + formId.getNamespace() + "." + formId.getPath());
    }

    public static Component milestoneName(@Nullable Identifier milestone) {
        return milestone == null ? Component.literal("?")
                : Component.translatable("milestone." + milestone.getNamespace() + "." + milestone.getPath());
    }

    private static long seconds(long ticks) {
        return (ticks + 19) / 20;
    }
}
