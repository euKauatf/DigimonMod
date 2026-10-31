package com.digimonaurity.digimon;

import java.util.List;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.resources.Identifier;
import net.minecraft.util.ExtraCodecs;

/**
 * Uma linha evolutiva (ex.: Agumon → Greymon → ... → WarGreymon).
 * Definida em data/digimonaurity/digimonaurity/line/&lt;nome&gt;.json.
 *
 * @param forms          formas da linha, da primeira à última
 * @param startingForm   forma com que o jogador nasce ao escolher (ou chocar) esta linha
 * @param starter        se aparece na tela de escolha inicial
 * @param color          cor de destaque na interface (ARGB; no JSON, "#RRGGBB")
 */
public record DigimonLine(List<Identifier> forms, Identifier startingForm, boolean starter, int color) {

    public static final Codec<DigimonLine> CODEC = RecordCodecBuilder.create(i -> i.group(
            Identifier.CODEC.listOf(1, 32).fieldOf("forms").forGetter(DigimonLine::forms),
            Identifier.CODEC.fieldOf("starting_form").forGetter(DigimonLine::startingForm),
            Codec.BOOL.optionalFieldOf("starter", false).forGetter(DigimonLine::starter),
            ExtraCodecs.STRING_RGB_COLOR.optionalFieldOf("color", 0xFFFFFFFF).forGetter(DigimonLine::color)
    ).apply(i, DigimonLine::new));

    public boolean contains(Identifier form) {
        return forms.contains(form);
    }
}
