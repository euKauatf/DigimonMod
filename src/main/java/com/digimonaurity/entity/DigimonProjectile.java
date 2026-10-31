package com.digimonaurity.entity;

import com.digimonaurity.digimon.DigimonAttack;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;

/**
 * Projétil dos ataques especiais (Pepper Breath, Blue Blaster...).
 * Voa em linha reta, deixa um rastro de partículas do elemento e aplica o efeito ao acertar.
 */
public class DigimonProjectile extends ThrowableItemProjectile {
    private static final EntityDataAccessor<Integer> ELEMENT =
            SynchedEntityData.defineId(DigimonProjectile.class, EntityDataSerializers.INT);
    private static final byte EVENT_IMPACT = 3;

    private float damage;
    private int effectSeconds;
    private int maxAge = 40;

    public DigimonProjectile(EntityType<? extends DigimonProjectile> type, Level level) {
        super(type, level);
    }

    /** Cria o projétil saindo dos olhos do atacante, já configurado pelo ataque. */
    public static DigimonProjectile shoot(LivingEntity owner, DigimonAttack attack) {
        DigimonProjectile projectile = new DigimonProjectile(DigimonRegistries.PROJECTILE.get(), owner.level());
        projectile.setOwner(owner);
        projectile.setPos(owner.getX(), owner.getEyeY() - 0.15, owner.getZ());
        projectile.entityData.set(ELEMENT, attack.element().ordinal());
        projectile.setItem(new ItemStack(itemFor(attack.element())));
        projectile.damage = attack.damage();
        projectile.effectSeconds = attack.effectSeconds();
        projectile.maxAge = Math.max(5, Math.round(attack.range() / attack.speed()));
        projectile.shootFromRotation(owner, owner.getXRot(), owner.getYRot(), 0f, attack.speed(), 0.5f);
        return projectile;
    }

    /** Para criaturas: mira direto no alvo, com um pouco de imprecisão. */
    public static DigimonProjectile shootAt(LivingEntity owner, DigimonAttack attack, Entity target) {
        DigimonProjectile projectile = shoot(owner, attack);
        double dx = target.getX() - projectile.getX();
        double dy = target.getY(0.5) - projectile.getY();
        double dz = target.getZ() - projectile.getZ();
        projectile.shoot(dx, dy, dz, attack.speed(), 3f);
        return projectile;
    }

    private static Item itemFor(DigimonAttack.Element element) {
        return switch (element) {
            case FIRE -> Items.FIRE_CHARGE;
            case POISON -> Items.SLIME_BALL;
            case EARTH -> Items.COBBLESTONE;
            case ICE, BUBBLE, NONE -> Items.SNOWBALL;
        };
    }

    public DigimonAttack.Element element() {
        int ordinal = entityData.get(ELEMENT);
        DigimonAttack.Element[] values = DigimonAttack.Element.values();
        return ordinal >= 0 && ordinal < values.length ? values[ordinal] : DigimonAttack.Element.NONE;
    }

    private ParticleOptions trailParticle() {
        return switch (element()) {
            case FIRE -> ParticleTypes.FLAME;
            case ICE -> ParticleTypes.SNOWFLAKE;
            case BUBBLE -> ParticleTypes.SPLASH;
            case POISON -> ParticleTypes.ITEM_SLIME;
            case EARTH, NONE -> ParticleTypes.CRIT;
        };
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(ELEMENT, DigimonAttack.Element.NONE.ordinal());
    }

    @Override
    protected Item getDefaultItem() {
        return Items.SNOWBALL;
    }

    /** Voo reto, como um sopro, sem cair. */
    @Override
    protected double getDefaultGravity() {
        return 0.0;
    }

    @Override
    public void tick() {
        super.tick();
        Level level = level();
        if (level.isClientSide()) {
            for (int i = 0; i < 2; i++) {
                level.addParticle(trailParticle(),
                        getX() + (random.nextDouble() - 0.5) * 0.2,
                        getY() + (random.nextDouble() - 0.5) * 0.2,
                        getZ() + (random.nextDouble() - 0.5) * 0.2, 0, 0, 0);
            }
        } else if (tickCount > maxAge) {
            discard();
        }
    }

    @Override
    protected void onHitEntity(EntityHitResult hitResult) {
        super.onHitEntity(hitResult);
        Entity target = hitResult.getEntity();
        target.hurt(damageSources().thrown(this, getOwner()), damage);
        if (effectSeconds > 0) {
            switch (element()) {
                case FIRE -> target.igniteForSeconds(effectSeconds);
                case ICE -> {
                    if (target instanceof LivingEntity living) {
                        living.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, effectSeconds * 20, 1), getOwner());
                        living.setTicksFrozen(Math.max(living.getTicksFrozen(), effectSeconds * 20));
                    }
                }
                case POISON -> {
                    if (target instanceof LivingEntity living) {
                        living.addEffect(new MobEffectInstance(MobEffects.POISON, effectSeconds * 20, 0), getOwner());
                    }
                }
                case EARTH -> {
                    if (target instanceof LivingEntity living) {
                        living.knockback(0.6, getX() - target.getX(), getZ() - target.getZ(),
                                damageSources().thrown(this, getOwner()), damage);
                    }
                }
                case BUBBLE, NONE -> {
                }
            }
        }
    }

    @Override
    protected void onHit(HitResult hitResult) {
        super.onHit(hitResult);
        if (!level().isClientSide()) {
            level().broadcastEntityEvent(this, EVENT_IMPACT);
            discard();
        }
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id == EVENT_IMPACT) {
            ParticleOptions particle = element() == DigimonAttack.Element.FIRE ? ParticleTypes.LAVA : trailParticle();
            for (int i = 0; i < 8; i++) {
                level().addParticle(particle, getX(), getY(), getZ(),
                        (random.nextDouble() - 0.5) * 0.2, random.nextDouble() * 0.2, (random.nextDouble() - 0.5) * 0.2);
            }
        } else {
            super.handleEntityEvent(id);
        }
    }
}
