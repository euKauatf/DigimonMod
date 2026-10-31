package com.digimonaurity.worldgen;

import java.util.Optional;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.block.DigiEggBlock;
import com.digimonaurity.block.TerritoryAltarBlockEntity;
import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.network.DigimonNetwork;
import com.digimonaurity.registry.DigimonBlocks;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.entity.ai.village.poi.PoiRecord;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Sentido digital: o Digimon "sente" dados por perto. A cada 2 segundos o servidor procura
 * o território pronto ou o Digi-Egg (de linha que o jogador ainda não tem) mais próximo
 * e manda só o tipo e a força do sinal — sem direção, para a exploração continuar valendo.
 */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class DigitalSense {
    public static final int RANGE = 96;
    public static final int TEMPLE_RANGE = 256;
    private static final int INTERVAL = 40;

    private DigitalSense() {
    }

    @SubscribeEvent
    static void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.tickCount % INTERVAL != 0) {
            return;
        }
        DigimonData data = PlayerDigimon.getData(player);
        if (!data.hasChosen()) {
            return;
        }
        ServerLevel level = player.level();
        BlockPos center = player.blockPosition();
        PoiManager pois = level.getPoiManager();
        long now = level.getGameTime();

        // Ovos de linhas que o jogador não tem têm prioridade: são o caminho para a outra linha.
        Optional<BlockPos> egg = pois.getInRange(h -> h.is(DigimonBlocks.DIGIEGG_POI.getKey()), center, RANGE, PoiManager.Occupancy.ANY)
                .map(PoiRecord::getPos)
                .filter(pos -> level.getBlockState(pos).getBlock() instanceof DigiEggBlock eggBlock
                        && !data.lines().containsKey(eggBlock.line()))
                .min((a, b) -> Double.compare(a.distSqr(center), b.distSqr(center)));
        Optional<BlockPos> territory = pois.getInRange(h -> h.is(DigimonBlocks.TERRITORY_POI.getKey()), center, RANGE, PoiManager.Occupancy.ANY)
                .map(PoiRecord::getPos)
                .filter(pos -> level.getBlockEntity(pos) instanceof TerritoryAltarBlockEntity altar && altar.isReady(now))
                .min((a, b) -> Double.compare(a.distSqr(center), b.distSqr(center)));

        int kind = 0;
        double distance = RANGE;
        double range = RANGE;
        if (egg.isPresent()) {
            kind = 2;
            distance = Math.sqrt(egg.get().distSqr(center));
        } else if (territory.isPresent()) {
            kind = 1;
            distance = Math.sqrt(territory.get().distSqr(center));
        } else {
            // Templos são raros e distantes: o sinal deles alcança mais longe.
            Optional<BlockPos> temple = pois.getInRange(h -> h.is(DigimonBlocks.TEMPLE_POI.getKey()), center, TEMPLE_RANGE, PoiManager.Occupancy.ANY)
                    .map(PoiRecord::getPos)
                    .filter(pos -> level.getBlockEntity(pos) instanceof TerritoryAltarBlockEntity altar && altar.isReady(now))
                    .min((a, b) -> Double.compare(a.distSqr(center), b.distSqr(center)));
            if (temple.isPresent()) {
                kind = 3;
                range = TEMPLE_RANGE;
                distance = Math.sqrt(temple.get().distSqr(center));
            }
        }
        float strength = kind == 0 ? 0f : (float) Math.max(0.05, 1.0 - distance / range);
        PacketDistributor.sendToPlayer(player, new DigimonNetwork.DigitalSense(kind, strength));
    }
}
