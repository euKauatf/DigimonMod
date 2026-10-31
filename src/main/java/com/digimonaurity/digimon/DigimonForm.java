package com.digimonaurity.digimon;

import java.util.List;
import java.util.Optional;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.Pose;

/**
 * Uma forma de Digimon que o jogador pode assumir (ex.: Agumon, Greymon).
 * Definida em data/digimonaurity/digimonaurity/form/&lt;nome&gt;.json.
 * O nome do arquivo também é o nome do modelo, da textura e das animações.
 *
 * @param stage       estágio de evolução
 * @param body        tamanho do corpo (hitbox e olhos)
 * @param minLevel    nível mínimo da linha para assumir esta forma
 * @param stats       vida, dano básico, velocidade e fome
 * @param attacks     ataques especiais, na ordem das teclas (no máximo 3)
 * @param requires    marcos de exploração necessários para evoluir para esta forma (além do nível)
 */
public record DigimonForm(DigimonStage stage, Body body, int minLevel, Stats stats, List<Identifier> attacks,
                          List<Identifier> requires) {

    public static final int MAX_ATTACKS = 3;

    public static final Codec<DigimonForm> CODEC = RecordCodecBuilder.create(i -> i.group(
            DigimonStage.CODEC.fieldOf("stage").forGetter(DigimonForm::stage),
            Body.CODEC.fieldOf("body").forGetter(DigimonForm::body),
            Codec.intRange(1, 1000).optionalFieldOf("min_level", 1).forGetter(DigimonForm::minLevel),
            Stats.CODEC.optionalFieldOf("stats", Stats.DEFAULT).forGetter(DigimonForm::stats),
            Identifier.CODEC.listOf(0, MAX_ATTACKS).optionalFieldOf("attacks", List.of()).forGetter(DigimonForm::attacks),
            Identifier.CODEC.listOf().optionalFieldOf("requires", List.of()).forGetter(DigimonForm::requires)
    ).apply(i, DigimonForm::new));

    /**
     * @param width     largura da hitbox, em blocos
     * @param height    altura da hitbox, em blocos
     * @param eyeHeight altura dos olhos (câmera em primeira pessoa), em blocos
     */
    public record Body(float width, float height, float eyeHeight) {
        public static final Codec<Body> CODEC = RecordCodecBuilder.create(i -> i.group(
                Codec.floatRange(0.1f, 8f).fieldOf("width").forGetter(Body::width),
                Codec.floatRange(0.1f, 8f).fieldOf("height").forGetter(Body::height),
                Codec.floatRange(0.05f, 8f).fieldOf("eye_height").forGetter(Body::eyeHeight)
        ).apply(i, Body::new));
    }

    /**
     * @param maxHealth      vida máxima (20 = 10 corações, como o Steve)
     * @param basicDamage    dano do ataque básico (clique esquerdo)
     * @param speed          multiplicador da velocidade de andar (1 = normal)
     * @param hungerDrain    cansaço extra por tick; formas fortes gastam mais comida (0 = normal)
     * @param fireResistance fração do dano de fogo e lava ignorada (0 a 1)
     * @param coldResistance fração do dano de congelamento ignorada; 1 = imune a congelar
     * @param frostWalker    congela a água sob os pés ao andar
     * @param glide          plana ao segurar o pulo no ar (sem dano de queda)
     * @param flight         voo livre (pulo duplo, como no Criativo), com custo alto de fome
     */
    public record Stats(float maxHealth, float basicDamage, float speed, float hungerDrain,
                        float fireResistance, float coldResistance, boolean frostWalker, boolean glide, boolean flight) {
        public static final Stats DEFAULT = new Stats(20f, 2f, 1f, 0f, 0f, 0f, false, false, false);
        public static final Codec<Stats> CODEC = RecordCodecBuilder.create(i -> i.group(
                Codec.floatRange(1f, 1024f).optionalFieldOf("max_health", 20f).forGetter(Stats::maxHealth),
                Codec.floatRange(0f, 1000f).optionalFieldOf("basic_damage", 2f).forGetter(Stats::basicDamage),
                Codec.floatRange(0.1f, 4f).optionalFieldOf("speed", 1f).forGetter(Stats::speed),
                Codec.floatRange(0f, 1f).optionalFieldOf("hunger_drain", 0f).forGetter(Stats::hungerDrain),
                Codec.floatRange(0f, 1f).optionalFieldOf("fire_resistance", 0f).forGetter(Stats::fireResistance),
                Codec.floatRange(0f, 1f).optionalFieldOf("cold_resistance", 0f).forGetter(Stats::coldResistance),
                Codec.BOOL.optionalFieldOf("frost_walker", false).forGetter(Stats::frostWalker),
                Codec.BOOL.optionalFieldOf("glide", false).forGetter(Stats::glide),
                Codec.BOOL.optionalFieldOf("flight", false).forGetter(Stats::flight)
        ).apply(i, Stats::new));
    }

    public float width() {
        return body.width();
    }

    public float height() {
        return body.height();
    }

    /** Ataque na posição da tecla (0, 1 ou 2), se existir. */
    public Optional<Identifier> attack(int slot) {
        return slot >= 0 && slot < attacks.size() ? Optional.of(attacks.get(slot)) : Optional.empty();
    }

    /** Hitbox desta forma para cada pose do jogador. */
    public EntityDimensions dimensionsFor(Pose pose) {
        float w = body.width();
        float h = body.height();
        float eye = body.eyeHeight();
        return switch (pose) {
            case SLEEPING -> EntityDimensions.fixed(0.2f, 0.2f).withEyeHeight(0.2f);
            case CROUCHING -> EntityDimensions.scalable(w, h * 0.85f).withEyeHeight(eye * 0.85f);
            case SWIMMING, FALL_FLYING, SPIN_ATTACK -> {
                float low = Math.min(w, h);
                yield EntityDimensions.scalable(w, low).withEyeHeight(low * 0.8f);
            }
            default -> EntityDimensions.scalable(w, h).withEyeHeight(eye);
        };
    }
}
