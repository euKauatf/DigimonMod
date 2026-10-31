package com.digimonaurity.digimon;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.util.StringRepresentable;

/**
 * Um ataque especial. Definido em data/digimonaurity/digimonaurity/attack/&lt;nome&gt;.json.
 * Por enquanto todo ataque é um projétil; outros tipos (cone, investida, área) virão depois.
 *
 * @param element       elemento: define visual e efeito ao acertar
 * @param damage        dano ao acertar (2 = 1 coração)
 * @param cooldown      recarga própria, em ticks (20 = 1 segundo)
 * @param speed         velocidade do projétil
 * @param range         distância máxima em blocos antes de sumir
 * @param effectSeconds duração do efeito do elemento (fogo, lentidão)
 */
public record DigimonAttack(Element element, float damage, int cooldown, float speed, float range, int effectSeconds) {

    public static final Codec<DigimonAttack> CODEC = RecordCodecBuilder.create(i -> i.group(
            Element.CODEC.optionalFieldOf("element", Element.NONE).forGetter(DigimonAttack::element),
            Codec.floatRange(0, 1000).fieldOf("damage").forGetter(DigimonAttack::damage),
            Codec.intRange(0, 72000).fieldOf("cooldown").forGetter(DigimonAttack::cooldown),
            Codec.floatRange(0.1f, 10f).optionalFieldOf("speed", 1.5f).forGetter(DigimonAttack::speed),
            Codec.floatRange(1f, 128f).optionalFieldOf("range", 24f).forGetter(DigimonAttack::range),
            Codec.intRange(0, 600).optionalFieldOf("effect_seconds", 0).forGetter(DigimonAttack::effectSeconds)
    ).apply(i, DigimonAttack::new));

    public enum Element implements StringRepresentable {
        NONE("none", 0xFFFFFFFF),
        BUBBLE("bubble", 0xFFD6F2FF),
        FIRE("fire", 0xFFFF7A1A),
        ICE("ice", 0xFF8FDDFF),
        POISON("poison", 0xFF7DBB3A),
        EARTH("earth", 0xFF9A9A96);

        public static final Codec<Element> CODEC = StringRepresentable.fromEnum(Element::values);

        private final String name;
        /** Cor usada no indicador de recarga. */
        public final int color;

        Element(String name, int color) {
            this.name = name;
            this.color = color;
        }

        @Override
        public String getSerializedName() {
            return name;
        }
    }
}
