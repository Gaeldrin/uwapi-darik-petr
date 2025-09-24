# Technocracy bot


def on_update_technocracy(bot):
    bot.find_main_base()

    match (
        bot.work_step % 10
    ):  # save some cpu cycles by splitting work over multiple steps
        case 1:
            drillsCount = bot.get_entities_count("drill")
            if drillsCount >= 3:
                return
            metal = 3161943147
            oil = bot.prototypes["Recipe"]["oil"]
            recipes = [
                metal,
                metal,
                oil,
            ]
            drill = 3871229408
            bot.build(drill, recipes[drillsCount - 1])
        case 2:
            if bot.get_entities_count("refinery") >= 1:
                return
            refinery = bot.prototypes["Construction"]["refinery"]
            p = bot.find_recipe_id(bot.prototypes["Recipe"]["oil"], 1)
            if p is not None:
                bot.build(refinery, 0, p)
        case 3:
            factoriesCount = bot.get_entities_count("bots factory")
            if (
                bot.get_units_count("drill") < 3
                or bot.get_units_count("refinery") < 1
                or factoriesCount >= 4
            ):
                return
            botsFactory = bot.prototypes["Construction"]["bots factory"]
            yatag = bot.prototypes["Recipe"]["yatag"]
            lurker = bot.prototypes["Recipe"]["lurker"]
            juggernaut = bot.prototypes["Recipe"]["juggernaut"]
            recipes = [
                yatag,
                yatag,
                lurker,
                juggernaut,
            ]
            metal = 3161943147
            pos1 = bot.find_recipe_id(metal, 1)
            pos2 = bot.find_recipe_id(metal, 2)
            pos = pos1
            if factoriesCount % 2 == 0:
                pos = pos2
            bot.build(botsFactory, recipes[factoriesCount - 1], pos)
        case 9:
            bot.attack_close_enemies(400)
            if (bot.get_entities_count("yatag") > 10):
                bot.attack_nearest_enemies()
