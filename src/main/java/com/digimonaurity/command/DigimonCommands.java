package com.digimonaurity.command;

import java.util.Map;
import java.util.Optional;

import com.digimonaurity.digimon.DigimonStage;
import com.digimonaurity.evolution.DigimonEvolution;
import com.digimonaurity.evolution.DigimonMilestones;
import com.digimonaurity.wild.WildDigimon;

import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.phys.Vec3;

import com.digimonaurity.DigimonAurity;
import com.digimonaurity.digimon.DigimonData;
import com.digimonaurity.digimon.DigimonForm;
import com.digimonaurity.digimon.DigimonLine;
import com.digimonaurity.digimon.PlayerDigimon;
import com.digimonaurity.network.DigimonNetwork;
import com.digimonaurity.progression.DigimonProgression;
import com.digimonaurity.registry.DigimonRegistries;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.commands.arguments.IdentifierArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/**
 * Comandos de teste:
 *   /digimon info                 — mostra linha, forma e nível (qualquer jogador)
 *   /digimon escolher             — reabre a escolha inicial e apaga o progresso
 *   /digimon linha &lt;linha&gt;        — troca (ou ganha) uma linha
 *   /digimon forma &lt;forma&gt;        — assume uma forma da linha atual
 *   /digimon nivel &lt;n&gt;            — define o nível da linha atual
 */
@EventBusSubscriber(modid = DigimonAurity.MODID)
public final class DigimonCommands {
    private DigimonCommands() {
    }

    @SubscribeEvent
    static void onRegisterCommands(RegisterCommandsEvent event) {
        register(event.getDispatcher());
    }

    private static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("digimon")
                .then(Commands.literal("info").executes(DigimonCommands::info))
                .then(Commands.literal("escolher")
                        .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .executes(DigimonCommands::reset))
                .then(Commands.literal("linha")
                        .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .then(Commands.argument("linha", IdentifierArgument.id())
                                .suggests((ctx, b) -> SharedSuggestionProvider.suggestResource(
                                        ctx.getSource().registryAccess().lookupOrThrow(DigimonRegistries.LINE).keySet(), b))
                                .executes(DigimonCommands::setLine)))
                .then(Commands.literal("forma")
                        .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .then(Commands.argument("forma", IdentifierArgument.id())
                                .suggests((ctx, b) -> SharedSuggestionProvider.suggestResource(
                                        ctx.getSource().registryAccess().lookupOrThrow(DigimonRegistries.FORM).keySet(), b))
                                .executes(DigimonCommands::setForm)))
                .then(Commands.literal("nivel")
                        .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .then(Commands.argument("nivel", IntegerArgumentType.integer(1, DigimonProgression.MAX_LEVEL))
                                .executes(DigimonCommands::setLevel)))
                .then(Commands.literal("selvagem")
                        .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .then(Commands.argument("forma", IdentifierArgument.id())
                                .suggests((ctx, b) -> SharedSuggestionProvider.suggestResource(
                                        ctx.getSource().registryAccess().lookupOrThrow(DigimonRegistries.FORM).keySet(), b))
                                .executes(DigimonCommands::spawnWild)))
                .then(Commands.literal("marco")
                        .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .then(Commands.argument("marco", IdentifierArgument.id())
                                .suggests((ctx, b) -> SharedSuggestionProvider.suggestResource(
                                        java.util.List.of(DigimonMilestones.TERRITORY_BOSS,
                                                DigimonMilestones.CHROME_DIGIZOID, DigimonMilestones.FULL_MOON,
                                                DigimonMilestones.CREST), b))
                                .executes(ctx -> {
                                    DigimonEvolution.grantMilestone(ctx.getSource().getPlayerOrException(),
                                            IdentifierArgument.getId(ctx, "marco"));
                                    return 1;
                                })))
                .then(Commands.literal("xp")
                        .requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
                        .then(Commands.argument("quantidade", IntegerArgumentType.integer(1, 100000))
                                .executes(DigimonCommands::addXp))));
    }

    /**
     * Chama um selvagem da forma indicada à frente do jogador. Para facilitar o teste da
     * digievolução em combate, o teto é Champion mesmo perto do spawn.
     */
    private static int spawnWild(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = ctx.getSource().getPlayerOrException();
        Identifier formId = IdentifierArgument.getId(ctx, "forma");
        Registry<DigimonLine> lines = player.level().registryAccess().lookupOrThrow(DigimonRegistries.LINE);
        Map.Entry<ResourceKey<DigimonLine>, DigimonLine> line = lines.entrySet().stream()
                .filter(e -> e.getValue().contains(formId)).findFirst().orElse(null);
        if (line == null) {
            ctx.getSource().sendFailure(Component.translatable("command.digimonaurity.unknown_form", formId.toString()));
            return 0;
        }
        WildDigimon wild = DigimonRegistries.WILD_DIGIMON.get().create(player.level(), EntitySpawnReason.COMMAND);
        if (wild == null) {
            return 0;
        }
        Vec3 pos = player.position().add(player.getLookAngle().multiply(4, 0, 4));
        wild.snapTo(pos.x, player.getY(), pos.z, player.getYRot() + 180f, 0f);
        wild.configure(line.getKey().identifier(), formId, !line.getValue().starter(), DigimonStage.CHAMPION);
        player.level().addFreshEntity(wild);
        ctx.getSource().sendSuccess(() -> Component.translatable("command.digimonaurity.wild_spawned",
                DigimonEvolution.formName(formId)), false);
        return 1;
    }

    private static int addXp(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = ctx.getSource().getPlayerOrException();
        int amount = IntegerArgumentType.getInteger(ctx, "quantidade");
        DigimonProgression.addXp(player, amount);
        ctx.getSource().sendSuccess(() -> Component.translatable("command.digimonaurity.xp_added", amount), false);
        return 1;
    }

    private static int info(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = ctx.getSource().getPlayerOrException();
        DigimonData data = PlayerDigimon.getData(player);
        Optional<DigimonData.LineProgress> progress = data.activeProgress();
        if (progress.isEmpty()) {
            ctx.getSource().sendSuccess(() -> Component.translatable("command.digimonaurity.info.none"), false);
            return 0;
        }
        DigimonData.LineProgress p = progress.get();
        ctx.getSource().sendSuccess(() -> Component.translatable("command.digimonaurity.info",
                data.activeLine().get().toString(), p.form().toString(), p.level(), data.lines().size()), false);
        return 1;
    }

    private static int reset(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = ctx.getSource().getPlayerOrException();
        PlayerDigimon.setData(player, DigimonData.EMPTY);
        DigimonNetwork.openStarterScreen(player);
        return 1;
    }

    private static int setLine(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = ctx.getSource().getPlayerOrException();
        Identifier lineId = IdentifierArgument.getId(ctx, "linha");
        if (!PlayerDigimon.setActiveLine(player, lineId)) {
            ctx.getSource().sendFailure(Component.translatable("command.digimonaurity.unknown_line", lineId.toString()));
            return 0;
        }
        ctx.getSource().sendSuccess(() -> Component.translatable("command.digimonaurity.line_set", lineId.toString()), false);
        return 1;
    }

    private static int setForm(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = ctx.getSource().getPlayerOrException();
        Identifier formId = IdentifierArgument.getId(ctx, "forma");
        DigimonData data = PlayerDigimon.getData(player);
        if (data.activeLine().isEmpty()) {
            ctx.getSource().sendFailure(Component.translatable("command.digimonaurity.info.none"));
            return 0;
        }
        Identifier lineId = data.activeLine().get();
        DigimonLine line = PlayerDigimon.lookup(player, DigimonRegistries.LINE, lineId);
        DigimonForm form = PlayerDigimon.lookup(player, DigimonRegistries.FORM, formId);
        if (form == null || line == null || !line.contains(formId)) {
            ctx.getSource().sendFailure(Component.translatable("command.digimonaurity.form_not_in_line",
                    formId.toString(), lineId.toString()));
            return 0;
        }
        PlayerDigimon.setData(player, data.withLine(lineId, data.lines().get(lineId).withForm(formId)));
        ctx.getSource().sendSuccess(() -> Component.translatable("command.digimonaurity.form_set", formId.toString()), false);
        return 1;
    }

    private static int setLevel(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer player = ctx.getSource().getPlayerOrException();
        int level = IntegerArgumentType.getInteger(ctx, "nivel");
        DigimonData data = PlayerDigimon.getData(player);
        if (data.activeLine().isEmpty()) {
            ctx.getSource().sendFailure(Component.translatable("command.digimonaurity.info.none"));
            return 0;
        }
        Identifier lineId = data.activeLine().get();
        PlayerDigimon.setData(player, data.withLine(lineId, data.lines().get(lineId).withLevelAndXp(level, 0)));
        ctx.getSource().sendSuccess(() -> Component.translatable("command.digimonaurity.level_set", level), false);
        return 1;
    }
}
