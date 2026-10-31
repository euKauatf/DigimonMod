package com.digimonaurity.client.render;

import com.geckolib.animatable.SingletonGeoAnimatable;
import com.geckolib.animatable.instance.AnimatableInstanceCache;
import com.geckolib.animatable.manager.AnimatableManager;
import com.geckolib.animation.AnimationController;
import com.geckolib.animation.RawAnimation;
import com.geckolib.animation.object.PlayState;
import com.geckolib.util.GeckoLibUtil;

import net.minecraft.resources.Identifier;

/**
 * Estado de animação de uma forma de Digimon.
 * Uma instância por forma; o GeckoLib separa o estado de cada jogador pelo id da entidade.
 */
public class DigimonAnimatable implements SingletonGeoAnimatable {
    public static final String ATTACK_CONTROLLER = "ataque";
    public static final String ATTACK_ANIMATION = "attack";

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final RawAnimation idle;
    private final RawAnimation walk;
    private final RawAnimation attack;

    public DigimonAnimatable(Identifier formId) {
        String prefix = "animation." + formId.getPath() + ".";
        this.idle = RawAnimation.begin().thenLoop(prefix + "idle");
        this.walk = RawAnimation.begin().thenLoop(prefix + "walk");
        this.attack = RawAnimation.begin().thenPlay(prefix + "attack");
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>("movimento", 4,
                test -> test.setAndContinue(test.isMoving() ? walk : idle)));
        // Só toca quando disparado (DigimonRenderEvents.playAttackAnimation); por cima do movimento.
        controllers.add(new AnimationController<DigimonAnimatable>(ATTACK_CONTROLLER, 2, test -> PlayState.STOP)
                .triggerableAnim(ATTACK_ANIMATION, attack));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
