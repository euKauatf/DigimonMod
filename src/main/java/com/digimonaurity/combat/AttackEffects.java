package com.digimonaurity.combat;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.digimon.DigimonAttack;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;

/** Efeitos de cada elemento ao acertar, iguais para todos os tipos de ataque. */
public final class AttackEffects {
    private AttackEffects() {
    }

    /**
     * Aplica dano e o efeito do elemento ao alvo.
     *
     * @param pushX direção do empurrão (só para o elemento terra), do alvo para quem atacou
     */
    public static void hit(Entity target, DamageSource source, DigimonAttack attack, @Nullable Entity attacker,
                           double pushX, double pushZ) {
        target.hurt(source, attack.damage());
        int seconds = attack.effectSeconds();
        if (seconds <= 0) {
            return;
        }
        switch (attack.element()) {
            case FIRE -> target.igniteForSeconds(seconds);
            case ICE -> {
                if (target instanceof LivingEntity living) {
                    living.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, seconds * 20, 1), attacker);
                    living.setTicksFrozen(Math.max(living.getTicksFrozen(), seconds * 20));
                }
            }
            case POISON -> {
                if (target instanceof LivingEntity living) {
                    living.addEffect(new MobEffectInstance(MobEffects.POISON, seconds * 20, 0), attacker);
                }
            }
            case EARTH -> {
                if (target instanceof LivingEntity living) {
                    living.knockback(0.6, pushX, pushZ, source, attack.damage());
                }
            }
            case BUBBLE, NONE -> {
            }
        }
    }

    /** Partícula que representa o elemento nos rastros e explosões. */
    public static ParticleOptions particle(DigimonAttack.Element element) {
        return switch (element) {
            case FIRE -> ParticleTypes.FLAME;
            case ICE -> ParticleTypes.SNOWFLAKE;
            case BUBBLE -> ParticleTypes.SPLASH;
            case POISON -> ParticleTypes.ITEM_SLIME;
            case EARTH, NONE -> ParticleTypes.CRIT;
        };
    }
}
