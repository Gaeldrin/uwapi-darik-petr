# Technocracy bot


def on_update_technocracy(bot):
    bot.find_main_base()

    match (
        bot.work_step % 10
    ):  # save some cpu cycles by splitting work over multiple steps
        case 1:
            if bot.get_entities_count("drill") >= 4:
                return
            bot.build(bot.prototypes["Construction"]["drill"])
        case 2:
            if bot.get_entities_count("refinery") >= 1:
                return
            refinery = bot.prototypes["Construction"]["refinery"]
            p = bot.find_recipe_id(bot.prototypes["Recipe"]["oil"], 1)
            if p is not None:
                bot.build(refinery, 0, p)
        case 3:
            if (
                bot.get_units_count("drill") < 4
                or bot.get_units_count("refinery") < 1
                or bot.get_entities_count("bots factory") >= 2
            ):
                return
            botsFactory = bot.prototypes["Construction"]["bots factory"]
            ytag = bot.prototypes["Recipe"]["yatag"]
            metal = 3161943147
            bot.build(botsFactory, ytag, bot.find_recipe_id(metal, 1))
            bot.build(botsFactory, ytag, bot.find_recipe_id(metal, 2))
        case 4:
            if (
                bot.get_units_count("drill") < 4
                or bot.get_units_count("refinery") < 1
                or bot.get_entities_count("bots factory") >= 3
            ):
                return
            botsFactory = bot.prototypes["Construction"]["bots factory"]
            lurker = 2480574658
            juggernaut = 3277593549
            metal = 3161943147
            bot.build(botsFactory, lurker, bot.find_recipe_id(metal, 1))
        case 5:
            if (
                bot.get_units_count("drill") < 4
                or bot.get_units_count("refinery") < 1
                or bot.get_entities_count("bots factory") >= 4
            ):
                return
            botsFactory = bot.prototypes["Construction"]["bots factory"]
            juggernaut = 3277593549
            metal = 3161943147
            bot.build(botsFactory, juggernaut, bot.find_recipe_id(metal, 2))
        case 9:
            if (bot.get_entities_count("yatag") > 5):
                bot.attack_nearest_building()
