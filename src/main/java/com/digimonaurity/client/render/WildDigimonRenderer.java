package com.digimonaurity.client.render;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.wild.WildDigimon;
import com.geckolib.constant.dataticket.DataTicket;
import com.geckolib.model.GeoModel;
import com.geckolib.renderer.GeoEntityRenderer;
import com.geckolib.renderer.base.GeoRenderState;

import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.resources.Identifier;

/**
 * Desenha os Digimon selvagens. O modelo, a textura e as animações são escolhidos
 * a cada quadro pela forma atual, então a troca na digievolução é instantânea.
 */
public class WildDigimonRenderer extends GeoEntityRenderer<WildDigimon, LivingEntityRenderState> {

    public WildDigimonRenderer(EntityRendererProvider.Context context) {
        super(context, new FormModel());
    }

    /** Modelo que segue a forma da entidade (mesmos arquivos usados pelos jogadores). */
    static class FormModel extends GeoModel<WildDigimon> {
        private static final DataTicket<Identifier> FORM = DataTicket.create("digimonaurity_form", Identifier.class);

        @Override
        public void addAdditionalStateData(WildDigimon animatable, @Nullable Object relatedObject, GeoRenderState renderState) {
            renderState.addGeckolibData(FORM, animatable.formId());
        }

        private static Identifier form(GeoRenderState renderState) {
            Identifier id = renderState.getGeckolibData(FORM);
            return id == null || id.getPath().equals("empty") ? Identifier.fromNamespaceAndPath("digimonaurity", "numemon") : id;
        }

        @Override
        public Identifier getModelResource(GeoRenderState renderState) {
            return form(renderState).withPrefix("entity/");
        }

        @Override
        public Identifier getTextureResource(GeoRenderState renderState) {
            Identifier id = form(renderState);
            return id.withPath("textures/entity/" + id.getPath() + ".png");
        }

        @Override
        public Identifier getAnimationResource(WildDigimon animatable) {
            Identifier id = animatable.formId();
            return (id.getPath().equals("empty") ? Identifier.fromNamespaceAndPath("digimonaurity", "numemon") : id)
                    .withPrefix("entity/");
        }
    }
}
