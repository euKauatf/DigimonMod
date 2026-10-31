package com.digimonaurity.block;

import java.util.List;
import java.util.UUID;

import org.jspecify.annotations.Nullable;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.registry.DigimonBlocks;
import com.digimonaurity.registry.DigimonRegistries;
import com.digimonaurity.wild.WildDigimon;
import com.digimonaurity.wild.WildRegions;
import com.digimonaurity.wild.WildSpawn;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;

/**
 * Coração do Território (ou do Templo do Brasão): quando um Digimon jogador chega perto,
 * invoca o chefe (ou o guardião). Depois de derrotado, volta em 20 minutos (30 no templo).
 */
public class TerritoryAltarBlockEntity extends BlockEntity {
    public static final int RESPAWN_TICKS = 20 * 60 * 20;
    private static final int TRIGGER_RANGE = 8;
    /** Se o chefe sumir (por exemplo, a área foi descarregada), libera depois deste tempo. */
    private static final int MISSING_BOSS_TICKS = 600;

    /** Chefes possíveis quando o bioma não tem selvagens próprios. */
    private static final List<Identifier[]> FALLBACK = List.of(
            new Identifier[] {DigimonAurity.id("agumon"), DigimonAurity.id("agumon")},
            new Identifier[] {DigimonAurity.id("gabumon"), DigimonAurity.id("gabumon")},
            new Identifier[] {DigimonAurity.id("goburimon"), DigimonAurity.id("goburimon")});

    private long readyAt;
    private @Nullable UUID boss;
    private int bossMissingTicks;

    public TerritoryAltarBlockEntity(BlockPos pos, BlockState state) {
        super(DigimonBlocks.TERRITORY_ALTAR_ENTITY.get(), pos, state);
    }

    /** Pronto para invocar um chefe? (usado também pelo sentido digital) */
    public boolean isReady(long now) {
        return boss == null && now >= readyAt;
    }

    public static void serverTick(ServerLevel level, BlockPos pos, TerritoryAltarBlockEntity altar) {
        if (level.getGameTime() % 20 != 0) {
            return;
        }
        if (altar.boss != null) {
            Entity entity = level.getEntity(altar.boss);
            if (entity != null && entity.isAlive()) {
                altar.bossMissingTicks = 0;
            } else if ((altar.bossMissingTicks += 20) > MISSING_BOSS_TICKS) {
                altar.boss = null;
                altar.setChanged();
            }
            return;
        }
        if (level.getGameTime() < altar.readyAt) {
            return;
        }
        List<ServerPlayer> nearby = level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(TRIGGER_RANGE),
                p -> !p.isSpectator() && PlayerDigimon.getForm(p) != null);
        if (!nearby.isEmpty()) {
            altar.summonBoss(level, pos, nearby);
        }
    }

    /** Guardiões do Templo: começam Champion e chegam a Ultimate durante a luta. */
    private static final List<Identifier[]> GUARDIANS = List.of(
            new Identifier[] {DigimonAurity.id("agumon"), DigimonAurity.id("greymon")},
            new Identifier[] {DigimonAurity.id("gabumon"), DigimonAurity.id("garurumon")});

    /** Pedestal do Brasão (templo) em vez de altar de território? */
    public boolean isTemple() {
        return getBlockState().is(DigimonBlocks.CREST_PEDESTAL.get());
    }

    private void summonBoss(ServerLevel level, BlockPos pos, List<ServerPlayer> witnesses) {
        WildDigimon wild = DigimonRegistries.WILD_DIGIMON.get().create(level, EntitySpawnReason.TRIGGERED);
        if (wild == null) {
            return;
        }
        boolean temple = isTemple();
        WildSpawn spawn = temple ? null : WildRegions.pick(level, pos, level.getRandom());
        Identifier line;
        Identifier form;
        if (spawn != null) {
            line = spawn.line();
            form = spawn.form();
        } else {
            List<Identifier[]> options = temple ? GUARDIANS : FALLBACK;
            Identifier[] pick = options.get(level.getRandom().nextInt(options.size()));
            line = pick[0];
            form = pick[1];
        }
        wild.snapTo(pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 3.5, 180f, 0f);
        wild.configureBoss(line, form, pos, temple);
        level.addFreshEntity(wild);
        boss = wild.getUUID();
        bossMissingTicks = 0;
        setChanged();
        level.playSound(null, pos, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, temple ? 1f : 0.6f, temple ? 1f : 1.5f);
        for (ServerPlayer player : witnesses) {
            player.sendSystemMessage(Component.translatable(temple
                            ? "message.digimonaurity.guardian_appeared" : "message.digimonaurity.boss_appeared")
                    .withStyle(ChatFormatting.RED, ChatFormatting.BOLD));
        }
    }

    /** Chamado pelo chefe ao morrer. */
    public void onBossDefeated(long now) {
        boss = null;
        readyAt = now + (isTemple() ? RESPAWN_TICKS * 3 / 2 : RESPAWN_TICKS);
        setChanged();
    }

    @Override
    protected void saveAdditional(ValueOutput output) {
        super.saveAdditional(output);
        output.putLong("ReadyAt", readyAt);
        if (boss != null) {
            output.putString("Boss", boss.toString());
        }
    }

    @Override
    protected void loadAdditional(ValueInput input) {
        super.loadAdditional(input);
        readyAt = input.getLongOr("ReadyAt", 0L);
        String id = input.getStringOr("Boss", "");
        boss = id.isEmpty() ? null : UUID.fromString(id);
    }
}
