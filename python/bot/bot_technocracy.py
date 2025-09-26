# Technocracy bot
import math


def on_update_technocracy(bot):
    bot.find_main_base()
    fabricatorsCount = bot.get_entities_count("fabricator")
    airFactoryCount = bot.get_entities_count("air factory")
    drillsDoneCount = bot.get_done_entities_count("drill")
    drillsCount = bot.get_entities_count("drill")
    factoriesCount = bot.get_entities_count("bots factory")

    match (
        bot.work_step % 10
    ):  # save some cpu cycles by splitting work over multiple steps
        case 1:
            if drillsCount >= (airFactoryCount + 1) * 3:
                return
            metal = 3161943147
            oil = bot.prototypes["Recipe"]["oil"]
            recipes = [
                metal,
                metal,
                oil,
            ]
            drill = 3871229408
            recipe = recipes[(drillsCount - 1) % 3]
            if recipe == oil and drillsCount >= 3:
                recipe = metal
            if drillsCount >= 5:
                return
            bot.build(drill, recipe)
        case 2:
            if bot.get_entities_count("refinery") >= drillsCount // 3:
                return
            refinery = bot.prototypes["Construction"]["refinery"]
            p = bot.find_recipe_id(bot.prototypes["Recipe"]["oil"], 1)
            if p is not None:
                bot.build(refinery, 0, p)
        case 3:
            if (
                bot.get_units_count("refinery") < drillsCount // 3
                or factoriesCount >= drillsDoneCount
            ):
                return
            botsFactory = bot.prototypes["Construction"]["bots factory"]
            lurker = bot.prototypes["Recipe"]["lurker"]
            juggernaut = bot.prototypes["Recipe"]["juggernaut"]
            tripod = bot.prototypes["Recipe"]["tripod"]
            recipes = [
                juggernaut,
                lurker,
                tripod,
            ]
            metal = 3161943147
            shift = 0
            if drillsDoneCount > 3:
                shift = 3
            pos1 = bot.find_recipe_id(metal, (shift + 0) % drillsDoneCount)
            pos2 = bot.find_recipe_id(metal, (shift + 1) % drillsDoneCount)
            pos = pos1
            if factoriesCount % 2 == 0:
                pos = pos2
            if pos is not None:
                bot.build(botsFactory, recipes[(factoriesCount - 1) % 3], pos)
        case 4:
            if (
                bot.get_units_count("drill") < 3
                or bot.get_units_count("refinery") < 1
                or bot.get_entities_count("bots factory") < 3
                or fabricatorsCount >= 2
            ):
                return
            fabricator = bot.prototypes["Construction"]["fabricator"]
            p = bot.find_recipe_id(bot.prototypes["Recipe"]["oil"], 1)
            if p is not None:
                bot.build(fabricator, 0, p)
        case 5:
            if fabricatorsCount < 2 or len(bot.get_constructions("talos")) > 0:
                return
            talos = bot.prototypes["Construction"]["talos"]
            bot.build(talos, 0, bot.find_random_building())
        case 6:
            bot.set_normal_priority_to_all()
        case 7:
            if fabricatorsCount < 2 or airFactoryCount >= 1:
                return
            airFactory = bot.prototypes["Construction"]["air factory"]
            atv = bot.prototypes["Recipe"]["ATV"]
            bot.build(airFactory, atv)
        case 9:
            if bot.get_entities_count("lurker") > 20:
                bot.attack_nearest_enemies()
            else:
                bot.attack_close_enemies(1000)
