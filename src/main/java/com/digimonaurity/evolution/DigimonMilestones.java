package com.digimonaurity.evolution;

import com.digimonaurity.DigimonAurity;

import net.minecraft.resources.Identifier;

/** Marcos de exploração usados no campo "requires" das formas. */
public final class DigimonMilestones {
    /** Vencer o chefe de um Território (exigido para chegar ao Champion). */
    public static final Identifier TERRITORY_BOSS = DigimonAurity.id("territory_boss");
    /** Absorver Cromo Digizoide, achado minerando fundo (exigido para o MetalGreymon). */
    public static final Identifier CHROME_DIGIZOID = DigimonAurity.id("chrome_digizoid");
    /** Uivar para a lua cheia a céu aberto (exigido para o WereGarurumon). */
    public static final Identifier FULL_MOON = DigimonAurity.id("full_moon");
    /**
     * Brasão da linha, conquistado vencendo o guardião do Templo do Brasão (exigido para o Mega).
     * Como os marcos valem por linha, o mesmo marco é o Brasão da Coragem na linha do Agumon
     * e o da Amizade na linha do Gabumon.
     */
    public static final Identifier CREST = DigimonAurity.id("crest");

    private DigimonMilestones() {
    }
}
