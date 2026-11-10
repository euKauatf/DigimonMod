package com.digimonaurity.combat;

import java.util.List;

import com.digimonaurity.digimon.DigimonAttack;
import com.digimonaurity.entity.DigimonProjectile;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Executa um ataque especial de acordo com o tipo:
 * projétil, sopro em cone, investida ou onda de área.
 * Serve para jogadores e para Digimon selvagens.
 */
public final class AttackExecutor {
    /** Metade do ângulo do cone (35° para cada lado). */
    private static final double CONE_COS = Math.cos(Math.toRadians(35));

    private AttackExecutor() {
    }

    public static void execute(LivingEntity user, DigimonAttack attack) {
        if (!(user.level() instanceof ServerLevel level)) {
            return;
        }
        switch (attack.type()) {
            case PROJECTILE -> level.addFreshEntity(DigimonProjectile.shoot(user, attack));
            case CONE -> cone(level, user, attack);
            case DASH -> dash(level, user, attack);
            case AREA -> area(level, user, attack);
        }
        level.playSound(null, user.getX(), user.getY(), user.getZ(), sound(attack), user.getSoundSource(), 0.8f, 1.1f);
    }

    private static DamageSource source(LivingEntity user) {
        return user instanceof Player player ? user.damageSources().playerAttack(player) : user.damageSources().mobAttack(user);
    }

    /** Alvos vivos perto do usuário (exceto ele mesmo e criaturas mortas). */
    private static List<LivingEntity> targetsAround(ServerLevel level, LivingEntity user, AABB box) {
        return level.getEntitiesOfClass(LivingEntity.class, box, e -> e != user && e.isAlive() && !e.isSpectator());
    }

    /** Sopro em leque: acerta tudo à frente, dentro do alcance e de um ângulo de 70°. */
    private static void cone(ServerLevel level, LivingEntity user, DigimonAttack attack) {
        Vec3 eye = user.getEyePosition();
        Vec3 look = user.getLookAngle();
        double range = attack.range();
        for (LivingEntity target : targetsAround(level, user, user.getBoundingBox().inflate(range))) {
            Vec3 toTarget = target.getBoundingBox().getCenter().subtract(eye);
            double distance = toTarget.length();
            if (distance <= range && toTarget.normalize().dot(look) >= CONE_COS && user.hasLineOfSight(target)) {
                AttackEffects.hit(target, source(user), attack, user, user.getX() - target.getX(), user.getZ() - target.getZ());
            }
        }
        // Leque de partículas
        ParticleOptions particle = AttackEffects.particle(attack.element());
        for (double d = 1; d <= range; d += 0.6) {
            double spread = d * 0.45;
            level.sendParticles(particle, eye.x + look.x * d, eye.y + look.y * d - 0.2, eye.z + look.z * d,
                    3, spread * 0.5, spread * 0.3, spread * 0.5, 0.01);
        }
    }

    /** Investida: impulsiona o usuário para a frente e acerta quem estiver no caminho. */
    private static void dash(ServerLevel level, LivingEntity user, DigimonAttack attack) {
        Vec3 flat = new Vec3(user.getLookAngle().x, 0, user.getLookAngle().z).normalize();
        double range = attack.range();
        Vec3 start = user.position();
        Vec3 end = start.add(flat.scale(range));
        AABB path = new AABB(start, end).inflate(user.getBbWidth() / 2 + 0.6, user.getBbHeight() / 2, user.getBbWidth() / 2 + 0.6)
                .move(0, user.getBbHeight() / 2, 0);
        for (LivingEntity target : targetsAround(level, user, path)) {
            AttackEffects.hit(target, source(user), attack, user, -flat.x, -flat.z);
            target.knockback(0.5, -flat.x, -flat.z, source(user), attack.damage());
        }
        // needsSync faz o servidor enviar o novo movimento (inclusive para o próprio jogador, como no empurrão)
        user.setDeltaMovement(flat.scale(Math.min(3.0, range * 0.35)).add(0, 0.25, 0));
        user.needsSync = true;
        ParticleOptions particle = AttackEffects.particle(attack.element());
        for (double d = 0; d <= range; d += 0.5) {
            level.sendParticles(particle, start.x + flat.x * d, start.y + user.getBbHeight() * 0.5, start.z + flat.z * d,
                    2, 0.2, 0.3, 0.2, 0.01);
        }
    }

    /** Onda de área: acerta e empurra tudo ao redor. */
    private static void area(ServerLevel level, LivingEntity user, DigimonAttack attack) {
        double radius = attack.radius();
        for (LivingEntity target : targetsAround(level, user, user.getBoundingBox().inflate(radius, radius / 2, radius))) {
            if (target.distanceToSqr(user) <= radius * radius) {
                double dx = user.getX() - target.getX();
                double dz = user.getZ() - target.getZ();
                AttackEffects.hit(target, source(user), attack, user, dx, dz);
                target.knockback(0.8, dx, dz, source(user), attack.damage());
            }
        }
        // Anel de partículas que se abre
        ParticleOptions particle = AttackEffects.particle(attack.element());
        for (double r = 1; r <= radius; r += 1) {
            for (int i = 0; i < 16; i++) {
                double a = i / 16.0 * Math.PI * 2;
                level.sendParticles(particle, user.getX() + Math.cos(a) * r, user.getY() + 0.3, user.getZ() + Math.sin(a) * r,
                        1, 0, 0.1, 0, 0.01);
            }
        }
    }

    private static SoundEvent sound(DigimonAttack attack) {
        return switch (attack.type()) {
            case DASH -> SoundEvents.PLAYER_ATTACK_SWEEP;
            case AREA -> SoundEvents.BREEZE_WIND_CHARGE_BURST.value();
            case CONE, PROJECTILE -> switch (attack.element()) {
                case FIRE -> attack.type() == DigimonAttack.Type.CONE ? SoundEvents.FIRECHARGE_USE : SoundEvents.BLAZE_SHOOT;
                case ICE -> attack.type() == DigimonAttack.Type.CONE ? SoundEvents.PLAYER_HURT_FREEZE : SoundEvents.SNOW_GOLEM_SHOOT;
                case BUBBLE -> SoundEvents.BUBBLE_COLUMN_UPWARDS_INSIDE;
                default -> SoundEvents.SNOW_GOLEM_SHOOT;
            };
        };
    }
}
