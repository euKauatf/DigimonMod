package com.digimonaurity.digimon;

import com.mojang.serialization.Codec;

import net.minecraft.util.StringRepresentable;

/** Estágios de evolução, na ordem. */
public enum DigimonStage implements StringRepresentable {
    FRESH("fresh"),
    IN_TRAINING("in_training"),
    ROOKIE("rookie"),
    CHAMPION("champion"),
    ULTIMATE("ultimate"),
    MEGA("mega");

    public static final Codec<DigimonStage> CODEC = StringRepresentable.fromEnum(DigimonStage::values);

    private final String name;

    DigimonStage(String name) {
        this.name = name;
    }

    @Override
    public String getSerializedName() {
        return name;
    }
}
