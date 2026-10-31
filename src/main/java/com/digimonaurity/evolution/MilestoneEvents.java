package com.digimonaurity.evolution;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.progression.DigimonRuntime;
import com.digimonaurity.registry.DigimonBlocks;
import com.digimonaurity.registry.DigimonRegistries;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.attribute.EnvironmentAttributes;
import net.minecraft.world.entity.animal.wolf.WolfSoundVariants;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.MoonPhase;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.level.BlockDropsEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/** Como se conquistam os marcos do mundo (além do chefe de território). */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class MilestoneEvents {
    /** Chance de achar Cromo Digizoide por minério quebrado abaixo da camada 0. */
    private static final float CHROME_CHANCE = 0.12f;
    /** Segundos uivando sob a lua cheia para conquistar o marco. */
    private static final int MOON_SECONDS = 10;
    private static final int MOON_CHECK = 40;

    private MilestoneEvents() {
    }

    @SubscribeEvent
    static void onBlockDrops(BlockDropsEvent event) {
        if (!(event.getBreaker() instanceof ServerPlayer player) || PlayerDigimon.getForm(player) == null) {
            return;
        }
        BlockPos pos = event.getPos();
        ServerLevel level = event.getLevel();
        if (pos.getY() >= 0 || !event.getState().is(Tags.Blocks.ORES) || level.getRandom().nextFloat() >= CHROME_CHANCE) {
            return;
        }
        event.getDrops().add(new ItemEntity(level, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5,
                new ItemStack(DigimonBlocks.CHROME_DIGIZOID.get())));
        player.sendOverlayMessage(Component.translatable("message.digimonaurity.chrome_found"));
    }

    /** Sob a lua cheia, a céu aberto, à noite: depois de alguns segundos, o Digimon uiva. */
    @SubscribeEvent
    static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.tickCount % MOON_CHECK != 0) {
            return;
        }
        DigimonData.LineProgress progress = PlayerDigimon.getData(player).activeProgress().orElse(null);
        if (progress == null || progress.milestones().contains(DigimonMilestones.FULL_MOON)) {
            return;
        }
        ServerLevel level = player.level();
        BlockPos head = BlockPos.containing(player.getEyePosition());
        DigimonRuntime runtime = player.getData(DigimonRegistries.RUNTIME);
        boolean fullMoon = level.isDarkOutside()
                && level.environmentAttributes().getValue(EnvironmentAttributes.MOON_PHASE, head) == MoonPhase.FULL_MOON
                && level.canSeeSky(head);
        if (!fullMoon) {
            runtime.moonTicks = 0;
            return;
        }
        runtime.moonTicks += MOON_CHECK;
        int seconds = runtime.moonTicks / 20;
        if (seconds < MOON_SECONDS) {
            // Só mostra o progresso para quem precisa desse marco na próxima forma
            Identifier next = DigimonEvolution.neighbour(player, +1).orElse(null);
            DigimonForm nextForm = next == null ? null : PlayerDigimon.lookup(player, DigimonRegistries.FORM, next);
            if (nextForm != null && nextForm.requires().contains(DigimonMilestones.FULL_MOON)) {
                player.sendOverlayMessage(Component.translatable("message.digimonaurity.moon_progress", seconds, MOON_SECONDS));
            }
            return;
        }
        level.playSound(null, player.blockPosition(),
                SoundEvents.WOLF_SOUNDS.get(WolfSoundVariants.SoundSet.BIG).adultSounds().growlSound().value(),
                SoundSource.PLAYERS, 1.5f, 0.6f);
        DigimonEvolution.grantMilestone(player, DigimonMilestones.FULL_MOON);
    }
}
