package com.digimonaurity.client.render;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.Entity;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.CalculateDetachedCameraDistanceEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RenderHandEvent;
import net.neoforged.neoforge.client.event.RenderPlayerEvent;

/** Troca o visual do jogador pelo do Digimon e ajusta câmera e mãos. */
@EventBusSubscriber(modid = DigimonAurity.MODID, value = Dist.CLIENT)
public final class DigimonRenderEvents {
    /** Distância padrão da câmera em terceira pessoa no vanilla, para um jogador de 1,8 bloco. */
    private static final float VANILLA_CAMERA_DISTANCE = 4.0f;
    private static final float VANILLA_PLAYER_HEIGHT = 1.8f;

    /** Um renderizador por forma, criado na primeira vez que alguém aparece com ela. */
    private static final Map<Identifier, DigimonPlayerRenderer> RENDERERS = new HashMap<>();
    private static EntityRendererProvider.@Nullable Context context;

    private DigimonRenderEvents() {
    }

    /** Disparado a cada recarga de recursos (F3+T), junto com os renderizadores do vanilla. */
    @SubscribeEvent
    static void onAddLayers(EntityRenderersEvent.AddLayers event) {
        context = event.getContext();
        RENDERERS.clear();
    }

    /** Registra como o projétil dos ataques é desenhado: o item (bola de fogo ou de neve) voando. */
    @SubscribeEvent
    static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(DigimonRegistries.PROJECTILE.get(), ThrownItemRenderer::new);
        event.registerEntityRenderer(DigimonRegistries.WILD_DIGIMON.get(), WildDigimonRenderer::new);
    }

    /** Toca a animação de ataque no Digimon com este id de entidade, se ele estiver visível. */
    public static void playAttackAnimation(int entityId) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || !(mc.level.getEntity(entityId) instanceof AbstractClientPlayer player)) {
            return;
        }
        DigimonPlayerRenderer renderer = PlayerDigimon.getFormId(player).map(DigimonRenderEvents::rendererFor).orElse(null);
        if (renderer != null) {
            renderer.getAnimatable().getAnimatableInstanceCache().getManagerForId(entityId)
                    .tryTriggerAnimation(DigimonAnimatable.ATTACK_CONTROLLER, DigimonAnimatable.ATTACK_ANIMATION);
        }
    }

    private static @Nullable DigimonPlayerRenderer rendererFor(Identifier formId) {
        if (context == null) {
            return null;
        }
        return RENDERERS.computeIfAbsent(formId, id -> new DigimonPlayerRenderer(context, id));
    }

    @SubscribeEvent
    static void onRenderPlayer(RenderPlayerEvent.Pre<?> event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return;
        }
        Entity entity = mc.level.getEntity(event.getRenderState().id);
        if (!(entity instanceof AbstractClientPlayer player) || PlayerDigimon.getForm(player) == null) {
            return;
        }
        Optional<Identifier> formId = PlayerDigimon.getFormId(player);
        DigimonPlayerRenderer renderer = formId.map(DigimonRenderEvents::rendererFor).orElse(null);
        if (renderer == null) {
            return;
        }

        event.setCanceled(true);
        CameraRenderState camera = mc.gameRenderer.gameRenderState().levelRenderState.cameraRenderState;
        LivingEntityRenderState state = renderer.createRenderState(player, event.getPartialTick());
        renderer.submit(state, event.getPoseStack(), event.getSubmitNodeCollector(), camera);
    }

    /** Esconde os braços do Steve em primeira pessoa. */
    @SubscribeEvent
    static void onRenderHand(RenderHandEvent event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && PlayerDigimon.getForm(mc.player) != null) {
            event.setCanceled(true);
        }
    }

    /** Câmera em terceira pessoa proporcional ao tamanho da forma (nunca mais perto que 3 blocos). */
    @SubscribeEvent
    static void onCameraDistance(CalculateDetachedCameraDistanceEvent event) {
        Minecraft mc = Minecraft.getInstance();
        DigimonForm form = mc.player == null ? null : PlayerDigimon.getForm(mc.player);
        if (form != null) {
            float distance = VANILLA_CAMERA_DISTANCE * form.height() / VANILLA_PLAYER_HEIGHT;
            event.setDistance(Math.max(3.0f, distance));
        }
    }
}
