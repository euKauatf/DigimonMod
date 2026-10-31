package com.digimonaurity.wild;

import java.util.EnumSet;
import java.util.List;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.digimon.DigimonAttack;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.digimon.DigimonStage;
import com.digimonaurity.entity.DigimonProjectile;
import com.digimonaurity.registry.DigimonRegistries;
import com.geckolib.animatable.GeoEntity;
import com.geckolib.animatable.instance.AnimatableInstanceCache;
import com.geckolib.animatable.manager.AnimatableManager;
import com.geckolib.animation.AnimationController;
import com.geckolib.animation.RawAnimation;
import com.geckolib.animation.object.PlayState;
import com.geckolib.util.GeckoLibUtil;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Registry;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;

/**
 * Digimon selvagem. Uma única entidade serve para todas as espécies: a forma atual
 * (modelo, tamanho, atributos e ataque) vem do JSON da forma e muda quando ele digievolui.
 *
 * Na luta, ao ficar com pouca vida, digievolui para a próxima forma da linha,
 * desde que o teto de evolução da região permita.
 */
public class WildDigimon extends Monster implements GeoEntity {
    private static final EntityDataAccessor<String> FORM =
            SynchedEntityData.defineId(WildDigimon.class, EntityDataSerializers.STRING);
    private static final byte EVENT_ATTACK = 60;
    private static final int TRANSFORM_TICKS = 30;
    private static final float EVOLVE_BELOW_HEALTH = 0.4f;
    /** Máximo de selvagens perto de um ponto para nascer mais um (evita encher o mundo de dia). */
    private static final int MAX_NEARBY = 3;
    private static final double BASE_SPEED = 0.25;

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    private Identifier line = Identifier.withDefaultNamespace("empty");
    private DigimonStage stageCap = DigimonStage.ROOKIE;
    private boolean aggressive;
    private @Nullable Identifier transformTarget;
    private int transformTicksLeft;
    private int rangedCooldown;
    /** Só no cliente: até quando tocar a animação de ataque. */
    private int attackAnimUntil;

    /** Chefe de território: posição do altar que o invocou (null = selvagem comum). */
    private @Nullable BlockPos bossAltar;
    /** Guardião do Templo do Brasão (chefe mais forte, que dá o Brasão). */
    private boolean guardian;
    /** Jogadores que causaram dano ao chefe; todos recebem o marco. */
    private final java.util.Set<java.util.UUID> damagers = new java.util.HashSet<>();

    private static final Identifier BOSS_HEALTH = com.digimonaurity.DigimonAurity.id("boss_health");
    private static final int BOSS_XP_BONUS = 50;

    public WildDigimon(EntityType<? extends WildDigimon> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 20)
                .add(Attributes.ATTACK_DAMAGE, 3)
                .add(Attributes.MOVEMENT_SPEED, BASE_SPEED)
                .add(Attributes.FOLLOW_RANGE, 24);
    }

    /** Regra de nascimento: precisa haver um selvagem possível no bioma e poucos por perto. */
    public static boolean checkWildSpawnRules(EntityType<WildDigimon> type, LevelAccessor level,
                                              EntitySpawnReason reason, BlockPos pos, RandomSource random) {
        if (!Monster.checkAnyLightMonsterSpawnRules(type, level, reason, pos, random)) {
            return false;
        }
        if (EntitySpawnReason.isSpawner(reason)) {
            return true;
        }
        boolean hasCandidate = level.registryAccess().lookup(DigimonRegistries.WILD_SPAWN)
                .map(r -> r.stream().anyMatch(s -> s.biomes().contains(level.getBiome(pos))))
                .orElse(false);
        return hasCandidate && level.getEntitiesOfClass(WildDigimon.class, new AABB(pos).inflate(48)).size() < MAX_NEARBY;
    }

    // ------------------------------------------------------------------ forma

    public Identifier formId() {
        String id = entityData.get(FORM);
        return id.isEmpty() ? Identifier.withDefaultNamespace("empty") : Identifier.parse(id);
    }

    public @Nullable DigimonForm form() {
        String id = entityData.get(FORM);
        if (id.isEmpty()) {
            return null;
        }
        return level().registryAccess().lookup(DigimonRegistries.FORM)
                .map(r -> r.getValue(Identifier.parse(id))).orElse(null);
    }

    public boolean isTransforming() {
        return transformTarget != null;
    }

    /** Assume uma forma: atributos, tamanho e vida passam a ser os dela. */
    public void setForm(Identifier formId, float healthRatio) {
        entityData.set(FORM, formId.toString());
        DigimonForm form = form();
        if (form == null) {
            return;
        }
        getAttribute(Attributes.MAX_HEALTH).setBaseValue(form.stats().maxHealth());
        getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(form.stats().basicDamage());
        getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(BASE_SPEED * form.stats().speed());
        setHealth(Math.max(1f, getMaxHealth() * healthRatio));
        refreshDimensions();
    }

    /** Escolhe linha, forma e teto ao nascer no mundo. */
    public void configure(Identifier lineId, Identifier startForm, boolean aggressive, DigimonStage cap) {
        this.line = lineId;
        this.aggressive = aggressive;
        this.stageCap = cap;
        setForm(clampToCap(startForm), 1f);
    }

    /**
     * Torna este selvagem um chefe. Agressivo, maior e nunca some sozinho.
     * - Chefe de território: 2,5x a vida, chega a Champion; dá o marco do território.
     * - Guardião do templo: 4x a vida, chega a Ultimate; dá o Brasão da linha.
     */
    public void configureBoss(Identifier lineId, Identifier startForm, BlockPos altar, boolean guardian) {
        this.bossAltar = altar.immutable();
        this.guardian = guardian;
        configure(lineId, startForm, true, guardian ? DigimonStage.ULTIMATE : DigimonStage.CHAMPION);
        getAttribute(Attributes.MAX_HEALTH).addPermanentModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(
                BOSS_HEALTH, guardian ? 3.0 : 1.5, net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
        getAttribute(Attributes.SCALE).setBaseValue(guardian ? 1.5 : 1.35);
        setHealth(getMaxHealth());
        setPersistenceRequired();
        setCustomName(net.minecraft.network.chat.Component.translatable(guardian
                ? "entity.digimonaurity.crest_guardian" : "entity.digimonaurity.territory_boss"));
        setCustomNameVisible(true);
    }

    public boolean isBoss() {
        return bossAltar != null;
    }

    @Override
    public void die(DamageSource source) {
        super.die(source);
        if (bossAltar == null || !(level() instanceof ServerLevel level)) {
            return;
        }
        for (java.util.UUID id : damagers) {
            if (level.getPlayerByUUID(id) instanceof net.minecraft.server.level.ServerPlayer player
                    && player.distanceToSqr(this) < 64 * 64) {
                if (guardian) {
                    announceCrest(player);
                    com.digimonaurity.evolution.DigimonEvolution.grantMilestone(player,
                            com.digimonaurity.evolution.DigimonMilestones.CREST);
                    com.digimonaurity.progression.DigimonProgression.addXp(player, BOSS_XP_BONUS * 3);
                } else {
                    com.digimonaurity.evolution.DigimonEvolution.grantMilestone(player,
                            com.digimonaurity.evolution.DigimonMilestones.TERRITORY_BOSS);
                    com.digimonaurity.progression.DigimonProgression.addXp(player, BOSS_XP_BONUS);
                }
            }
        }
        if (level.getBlockEntity(bossAltar) instanceof com.digimonaurity.block.TerritoryAltarBlockEntity altar) {
            altar.onBossDefeated(level.getGameTime());
        }
    }

    /** O Brasão é da linha que o jogador está usando: Coragem (Agumon) ou Amizade (Gabumon). */
    private static void announceCrest(net.minecraft.server.level.ServerPlayer player) {
        Identifier activeLine = com.digimonaurity.digimon.PlayerDigimon.getData(player).activeLine().orElse(null);
        if (activeLine == null) {
            return;
        }
        net.minecraft.network.chat.Component crest = net.minecraft.network.chat.Component.translatable(
                "crest." + activeLine.getNamespace() + "." + activeLine.getPath());
        player.sendSystemMessage(net.minecraft.network.chat.Component.translatable("message.digimonaurity.crest_obtained", crest)
                .withStyle(net.minecraft.ChatFormatting.GOLD, net.minecraft.ChatFormatting.BOLD));
    }

    /** Se a forma pedida passa do teto, recua na linha até caber. */
    private Identifier clampToCap(Identifier wanted) {
        DigimonLine lineDef = lookup(DigimonRegistries.LINE, line);
        if (lineDef == null) {
            return wanted;
        }
        List<Identifier> forms = lineDef.forms();
        int index = Math.max(0, forms.indexOf(wanted));
        while (index > 0) {
            DigimonForm f = lookup(DigimonRegistries.FORM, forms.get(index));
            if (f != null && f.stage().compareTo(stageCap) <= 0) {
                break;
            }
            index--;
        }
        return forms.isEmpty() ? wanted : forms.get(index);
    }

    private <T> @Nullable T lookup(ResourceKey<Registry<T>> registry, Identifier id) {
        return level().registryAccess().lookup(registry).map(r -> r.getValue(id)).orElse(null);
    }

    @Override
    public @Nullable SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty,
                                                  EntitySpawnReason reason, @Nullable SpawnGroupData groupData) {
        SpawnGroupData data = super.finalizeSpawn(level, difficulty, reason, groupData);
        if (entityData.get(FORM).isEmpty()) {
            WildSpawn spawn = WildRegions.pick(level, blockPosition(), getRandom());
            if (spawn != null) {
                configure(spawn.line(), spawn.form(), spawn.aggressive(), WildRegions.stageCap(level, blockPosition()));
            }
        }
        return data;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(FORM, "");
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> accessor) {
        super.onSyncedDataUpdated(accessor);
        if (FORM.equals(accessor)) {
            refreshDimensions();
        }
    }

    @Override
    protected EntityDimensions getDefaultDimensions(Pose pose) {
        DigimonForm form = form();
        return form == null ? super.getDefaultDimensions(pose) : form.dimensionsFor(Pose.STANDING);
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput output) {
        super.addAdditionalSaveData(output);
        output.putString("Form", entityData.get(FORM));
        output.putString("Line", line.toString());
        output.putString("StageCap", stageCap.getSerializedName());
        output.putBoolean("Aggressive", aggressive);
        if (bossAltar != null) {
            output.putLong("BossAltar", bossAltar.asLong());
            output.putBoolean("Guardian", guardian);
        }
    }

    @Override
    protected void readAdditionalSaveData(ValueInput input) {
        super.readAdditionalSaveData(input);
        line = Identifier.parse(input.getStringOr("Line", "minecraft:empty"));
        aggressive = input.getBooleanOr("Aggressive", false);
        long altar = input.getLongOr("BossAltar", Long.MIN_VALUE);
        bossAltar = altar == Long.MIN_VALUE ? null : BlockPos.of(altar);
        guardian = input.getBooleanOr("Guardian", false);
        String cap = input.getStringOr("StageCap", "rookie");
        for (DigimonStage stage : DigimonStage.values()) {
            if (stage.getSerializedName().equals(cap)) {
                stageCap = stage;
            }
        }
        String form = input.getStringOr("Form", "");
        if (!form.isEmpty()) {
            entityData.set(FORM, form);
            refreshDimensions();
        }
    }

    // ------------------------------------------------------------ comportamento

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new TransformingGoal());
        goalSelector.addGoal(2, new RangedAttackGoal());
        goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.1, false));
        goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8));
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8f));
        goalSelector.addGoal(7, new RandomLookAroundGoal(this));
        targetSelector.addGoal(1, new HurtByTargetGoal(this, WildDigimon.class));
        targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true) {
            @Override
            public boolean canUse() {
                return aggressive && super.canUse();
            }
        });
    }

    @Override
    public boolean doHurtTarget(ServerLevel level, net.minecraft.world.entity.Entity target) {
        boolean hit = super.doHurtTarget(level, target);
        if (hit) {
            level.broadcastEntityEvent(this, EVENT_ATTACK);
        }
        return hit;
    }

    @Override
    public boolean hurtServer(ServerLevel level, DamageSource source, float damage) {
        if (bossAltar != null && source.getEntity() instanceof Player player) {
            damagers.add(player.getUUID());
        }
        boolean hurt = super.hurtServer(level, source, damage);
        if (hurt && isAlive() && !isTransforming() && getHealth() < getMaxHealth() * EVOLVE_BELOW_HEALTH) {
            startEvolution(level);
        }
        return hurt;
    }

    /** Começa a digievoluir, se houver próxima forma dentro do teto da região. */
    private void startEvolution(ServerLevel level) {
        DigimonLine lineDef = lookup(DigimonRegistries.LINE, line);
        if (lineDef == null) {
            return;
        }
        int index = lineDef.forms().indexOf(formId());
        if (index < 0 || index + 1 >= lineDef.forms().size()) {
            return;
        }
        Identifier next = lineDef.forms().get(index + 1);
        DigimonForm nextForm = lookup(DigimonRegistries.FORM, next);
        if (nextForm == null || nextForm.stage().compareTo(stageCap) > 0) {
            return;
        }
        transformTarget = next;
        transformTicksLeft = TRANSFORM_TICKS;
        level.playSound(null, blockPosition(), SoundEvents.BEACON_ACTIVATE, getSoundSource(), 1f, 1.4f);
    }

    @Override
    public void aiStep() {
        super.aiStep();
        if (!(level() instanceof ServerLevel level)) {
            return;
        }
        if (rangedCooldown > 0) {
            rangedCooldown--;
        }
        if (transformTarget == null) {
            return;
        }
        // Mesma espiral de luz da evolução do jogador
        double angle = tickCount / 20.0 * Math.PI * 2;
        double radius = Math.max(0.6, getBbWidth());
        double height = (TRANSFORM_TICKS - transformTicksLeft) / (double) TRANSFORM_TICKS * getBbHeight();
        for (int i = 0; i < 2; i++) {
            double a = angle + i * Math.PI;
            level.sendParticles(ParticleTypes.END_ROD, getX() + Math.cos(a) * radius, getY() + height,
                    getZ() + Math.sin(a) * radius, 1, 0, 0, 0, 0);
        }
        if (--transformTicksLeft <= 0) {
            Identifier target = transformTarget;
            transformTarget = null;
            setForm(target, 0.6f);
            level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, getX(), getY() + getBbHeight() / 2, getZ(),
                    40, 0.5, 0.8, 0.5, 0.3);
            level.playSound(null, blockPosition(), SoundEvents.PLAYER_LEVELUP, getSoundSource(), 1f, 0.8f);
        }
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id == EVENT_ATTACK) {
            attackAnimUntil = tickCount + 8;
        } else {
            super.handleEntityEvent(id);
        }
    }

    /** Parado e sem atacar enquanto digievolui. */
    private class TransformingGoal extends Goal {
        TransformingGoal() {
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK, Flag.JUMP));
        }

        @Override
        public boolean canUse() {
            return isTransforming();
        }

        @Override
        public void tick() {
            getNavigation().stop();
        }
    }

    /** Usa o ataque especial da forma a meia distância, com recarga maior que a do jogador. */
    private class RangedAttackGoal extends Goal {
        RangedAttackGoal() {
            setFlags(EnumSet.of(Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity target = getTarget();
            if (target == null || !target.isAlive() || rangedCooldown > 0 || isTransforming()) {
                return false;
            }
            double distance = distanceToSqr(target);
            return distance > 9 && distance < 256 && hasLineOfSight(target);
        }

        @Override
        public boolean canContinueToUse() {
            return false;
        }

        @Override
        public void start() {
            LivingEntity target = getTarget();
            DigimonForm form = form();
            if (target == null || form == null || form.attacks().isEmpty()
                    || !(level() instanceof ServerLevel level)) {
                return;
            }
            DigimonAttack attack = lookup(DigimonRegistries.ATTACK, form.attacks().getFirst());
            if (attack == null) {
                return;
            }
            getLookControl().setLookAt(target, 30f, 30f);
            level.addFreshEntity(DigimonProjectile.shootAt(WildDigimon.this, attack, target));
            level.broadcastEntityEvent(WildDigimon.this, EVENT_ATTACK);
            rangedCooldown = Math.round(attack.cooldown() * 1.5f) + 10;
        }
    }

    // --------------------------------------------------------------- animação

    /** Animações da forma: [parado, andando, atacando]. Guardadas para não recriar a cada quadro. */
    private static final java.util.Map<String, RawAnimation[]> ANIMATIONS = new java.util.concurrent.ConcurrentHashMap<>();

    private static RawAnimation[] animationsFor(Identifier formId) {
        return ANIMATIONS.computeIfAbsent(formId.getPath(), path -> new RawAnimation[] {
                RawAnimation.begin().thenLoop("animation." + path + ".idle"),
                RawAnimation.begin().thenLoop("animation." + path + ".walk"),
                RawAnimation.begin().thenPlay("animation." + path + ".attack")});
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<WildDigimon>("movimento", 4,
                test -> test.setAndContinue(animationsFor(formId())[test.isMoving() ? 1 : 0])));
        controllers.add(new AnimationController<WildDigimon>("ataque", 2, test -> tickCount < attackAnimUntil
                ? test.setAndContinue(animationsFor(formId())[2])
                : PlayState.STOP));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }
}
