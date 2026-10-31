package com.digimonaurity.network;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.combat.DigimonCombat;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.evolution.DigimonEvolution;
import com.digimonaurity.block.IncubatorBlock;
import com.digimonaurity.registry.DigimonBlocks;
import com.digimonaurity.registry.DigimonRegistries;

import io.netty.buffer.ByteBuf;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * Mensagens entre cliente e servidor.
 * O servidor sempre valida o que o cliente pede; o cliente só exibe telas.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class DigimonNetwork {
    private static final String VERSION = "1";

    private DigimonNetwork() {
    }

    /** Servidor → cliente: abra a tela de escolha do Digimon inicial. */
    public record OpenStarterScreen() implements CustomPacketPayload {
        public static final OpenStarterScreen INSTANCE = new OpenStarterScreen();
        public static final Type<OpenStarterScreen> TYPE = new Type<>(DigimonAurity.id("open_starter_screen"));
        public static final StreamCodec<ByteBuf, OpenStarterScreen> STREAM_CODEC = StreamCodec.unit(INSTANCE);

        @Override
        public Type<OpenStarterScreen> type() {
            return TYPE;
        }
    }

    /** Cliente → servidor: escolhi esta linha como inicial. */
    public record ChooseStarter(Identifier line) implements CustomPacketPayload {
        public static final Type<ChooseStarter> TYPE = new Type<>(DigimonAurity.id("choose_starter"));
        public static final StreamCodec<ByteBuf, ChooseStarter> STREAM_CODEC =
                Identifier.STREAM_CODEC.map(ChooseStarter::new, ChooseStarter::line);

        @Override
        public Type<ChooseStarter> type() {
            return TYPE;
        }
    }

    /** Cliente → servidor: apertei a tecla do ataque especial nesta posição (0 a 2). */
    public record UseAttack(int slot) implements CustomPacketPayload {
        public static final Type<UseAttack> TYPE = new Type<>(DigimonAurity.id("use_attack"));
        public static final StreamCodec<ByteBuf, UseAttack> STREAM_CODEC =
                ByteBufCodecs.VAR_INT.map(UseAttack::new, UseAttack::slot);

        @Override
        public Type<UseAttack> type() {
            return TYPE;
        }
    }

    /** Servidor → cliente: seu ataque foi usado; mostre as recargas (em ticks). */
    public record CooldownStarted(int slot, int slotTicks, int globalTicks) implements CustomPacketPayload {
        public static final Type<CooldownStarted> TYPE = new Type<>(DigimonAurity.id("cooldown_started"));
        public static final StreamCodec<ByteBuf, CooldownStarted> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.VAR_INT, CooldownStarted::slot,
                ByteBufCodecs.VAR_INT, CooldownStarted::slotTicks,
                ByteBufCodecs.VAR_INT, CooldownStarted::globalTicks,
                CooldownStarted::new);

        @Override
        public Type<CooldownStarted> type() {
            return TYPE;
        }
    }

    /** Servidor → clientes próximos: este Digimon atacou; toque a animação de ataque. */
    public record AttackAnimation(int entityId) implements CustomPacketPayload {
        public static final Type<AttackAnimation> TYPE = new Type<>(DigimonAurity.id("attack_animation"));
        public static final StreamCodec<ByteBuf, AttackAnimation> STREAM_CODEC =
                ByteBufCodecs.VAR_INT.map(AttackAnimation::new, AttackAnimation::entityId);

        @Override
        public Type<AttackAnimation> type() {
            return TYPE;
        }
    }

    /** Cliente → servidor: quero digievoluir (+1) ou desevoluir (-1). */
    public record Transform(int direction) implements CustomPacketPayload {
        public static final Type<Transform> TYPE = new Type<>(DigimonAurity.id("transform"));
        public static final StreamCodec<ByteBuf, Transform> STREAM_CODEC =
                ByteBufCodecs.VAR_INT.map(Transform::new, Transform::direction);

        @Override
        public Type<Transform> type() {
            return TYPE;
        }
    }

    /** Servidor → cliente: sua evolução está bloqueada por estes ticks (após morrer). */
    public record EvolutionBlocked(int ticks) implements CustomPacketPayload {
        public static final Type<EvolutionBlocked> TYPE = new Type<>(DigimonAurity.id("evolution_blocked"));
        public static final StreamCodec<ByteBuf, EvolutionBlocked> STREAM_CODEC =
                ByteBufCodecs.VAR_INT.map(EvolutionBlocked::new, EvolutionBlocked::ticks);

        @Override
        public Type<EvolutionBlocked> type() {
            return TYPE;
        }
    }

    /** Servidor → cliente: abra a tela da incubadora. */
    public record OpenIncubator() implements CustomPacketPayload {
        public static final OpenIncubator INSTANCE = new OpenIncubator();
        public static final Type<OpenIncubator> TYPE = new Type<>(DigimonAurity.id("open_incubator"));
        public static final StreamCodec<ByteBuf, OpenIncubator> STREAM_CODEC = StreamCodec.unit(INSTANCE);

        @Override
        public Type<OpenIncubator> type() {
            return TYPE;
        }
    }

    /** Cliente → servidor: quero usar esta linha (só vale perto de uma incubadora). */
    public record SwitchLine(Identifier line) implements CustomPacketPayload {
        public static final Type<SwitchLine> TYPE = new Type<>(DigimonAurity.id("switch_line"));
        public static final StreamCodec<ByteBuf, SwitchLine> STREAM_CODEC =
                Identifier.STREAM_CODEC.map(SwitchLine::new, SwitchLine::line);

        @Override
        public Type<SwitchLine> type() {
            return TYPE;
        }
    }

    /**
     * Servidor → cliente: sinal do sentido digital.
     *
     * @param kind     0 = nada, 1 = território pronto, 2 = Digi-Egg de linha que você não tem, 3 = templo do Brasão
     * @param strength força do sinal, de 0 (longe) a 1 (em cima)
     */
    public record DigitalSense(int kind, float strength) implements CustomPacketPayload {
        public static final Type<DigitalSense> TYPE = new Type<>(DigimonAurity.id("digital_sense"));
        public static final StreamCodec<ByteBuf, DigitalSense> STREAM_CODEC = StreamCodec.composite(
                ByteBufCodecs.VAR_INT, DigitalSense::kind,
                ByteBufCodecs.FLOAT, DigitalSense::strength,
                DigitalSense::new);

        @Override
        public Type<DigitalSense> type() {
            return TYPE;
        }
    }

    @SubscribeEvent
    static void onRegisterPayloads(RegisterPayloadHandlersEvent event) {
        event.registrar(VERSION)
                .playToClient(OpenIncubator.TYPE, OpenIncubator.STREAM_CODEC)
                .playToClient(DigitalSense.TYPE, DigitalSense.STREAM_CODEC)
                .playToServer(SwitchLine.TYPE, SwitchLine.STREAM_CODEC, DigimonNetwork::handleSwitchLine);
        registerCore(event);
    }

    private static void handleSwitchLine(SwitchLine payload, IPayloadContext context) {
        if (!(context.player() instanceof ServerPlayer player)) {
            return;
        }
        BlockPos incubator = player.getData(DigimonRegistries.RUNTIME).incubatorPos;
        boolean nearIncubator = incubator != null
                && player.level().getBlockState(incubator).is(DigimonBlocks.INCUBATOR.get())
                && player.position().closerThan(net.minecraft.world.phys.Vec3.atCenterOf(incubator), IncubatorBlock.MAX_DISTANCE);
        if (!nearIncubator || !PlayerDigimon.getData(player).lines().containsKey(payload.line())
                || player.getData(DigimonRegistries.RUNTIME).isTransforming()) {
            return;
        }
        PlayerDigimon.setActiveLine(player, payload.line());
        player.level().playSound(null, player.blockPosition(), SoundEvents.BEACON_POWER_SELECT, SoundSource.PLAYERS, 1f, 1.2f);
        player.sendSystemMessage(Component.translatable("message.digimonaurity.line_switched",
                Component.translatable("line." + payload.line().getNamespace() + "." + payload.line().getPath() + ".name")));
    }

    private static void registerCore(RegisterPayloadHandlersEvent event) {
        event.registrar(VERSION)
                // O tratamento no cliente é registrado em ClientNetwork (só existe no cliente).
                .playToClient(OpenStarterScreen.TYPE, OpenStarterScreen.STREAM_CODEC)
                .playToClient(CooldownStarted.TYPE, CooldownStarted.STREAM_CODEC)
                .playToClient(AttackAnimation.TYPE, AttackAnimation.STREAM_CODEC)
                .playToClient(EvolutionBlocked.TYPE, EvolutionBlocked.STREAM_CODEC)
                .playToServer(Transform.TYPE, Transform.STREAM_CODEC, (payload, context) -> {
                    if (context.player() instanceof ServerPlayer player && Math.abs(payload.direction()) == 1) {
                        DigimonEvolution.request(player, payload.direction());
                    }
                })
                .playToServer(ChooseStarter.TYPE, ChooseStarter.STREAM_CODEC, DigimonNetwork::handleChooseStarter)
                .playToServer(UseAttack.TYPE, UseAttack.STREAM_CODEC, DigimonNetwork::handleUseAttack);
    }

    private static void handleUseAttack(UseAttack payload, IPayloadContext context) {
        if (context.player() instanceof ServerPlayer player
                && payload.slot() >= 0 && payload.slot() < DigimonForm.MAX_ATTACKS) {
            DigimonCombat.useAttack(player, payload.slot());
        }
    }

    private static void handleChooseStarter(ChooseStarter payload, IPayloadContext context) {
        if (!(context.player() instanceof ServerPlayer player)) {
            return;
        }
        // Só vale para quem ainda não escolheu, e só para linhas marcadas como iniciais.
        if (PlayerDigimon.getData(player).hasChosen()) {
            return;
        }
        DigimonLine line = PlayerDigimon.lookup(player, DigimonRegistries.LINE, payload.line());
        if (line == null || !line.starter()) {
            DigimonAurity.LOGGER.warn("{} pediu uma linha inicial inválida: {}", player.getName().getString(), payload.line());
            openStarterScreen(player);
            return;
        }
        PlayerDigimon.setActiveLine(player, payload.line());
    }

    public static void openStarterScreen(ServerPlayer player) {
        PacketDistributor.sendToPlayer(player, OpenStarterScreen.INSTANCE);
    }

    /** Quem entra sem ter escolhido um Digimon vê a tela de escolha. */
    @SubscribeEvent
    static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && !PlayerDigimon.getData(player).hasChosen()) {
            openStarterScreen(player);
        }
    }
}
