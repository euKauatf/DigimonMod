package com.digimonaurity.client.render;

import com.geckolib.model.DefaultedEntityGeoModel;
import com.geckolib.renderer.GeoReplacedEntityRenderer;

import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.resources.Identifier;

/**
 * Desenha um jogador como uma forma de Digimon.
 * Modelo, textura e animações vêm de:
 *   geckolib/models/entity/&lt;forma&gt;.geo.json
 *   geckolib/animations/entity/&lt;forma&gt;.animation.json
 *   textures/entity/&lt;forma&gt;.png
 */
public class DigimonPlayerRenderer
        extends GeoReplacedEntityRenderer<DigimonAnimatable, AbstractClientPlayer, LivingEntityRenderState> {

    public DigimonPlayerRenderer(EntityRendererProvider.Context context, Identifier formId) {
        super(context, new DefaultedEntityGeoModel<>(formId), new DigimonAnimatable(formId));
    }
}
