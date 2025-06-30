using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.IO;

namespace Unnatural
{
    internal class Bot
    {
        readonly Random random = new Random();
        bool isConfigured = false;
        uint workStep = 0; // save some cpu cycles by splitting work over multiple steps

        void AttackNearestEnemies()
        {
            var ownUnits = World.Entities().Values.Where(x => x.Own && x.ProtoUnit?.dps > 0);
            if (ownUnits.Count() == 0)
                return;

            var enemyUnits = World.Entities().Values.Where(x => x.Enemy && x.Unit.HasValue);
            if (enemyUnits.Count() == 0)
                return;

            foreach (Entity own in ownUnits)
            {
                if (Commands.Orders(own.Id).Length == 0)
                {
                    Entity enemy = enemyUnits.OrderBy(x => Map.DistanceEstimate(own.Pos, x.Pos)).First();
                    Commands.Order(own.Id, Commands.FightToEntity(enemy.Id));
                }
            }
        }

        void AssignRandomRecipes()
        {
            foreach (Entity own in World.Entities().Values.Where(x => x.Own && x.Unit.HasValue))
            {
                if (own.Recipe.HasValue)
                    continue;
                List<uint> recipes = own.ProtoUnit.recipes;
                if (recipes?.Count > 0)
                {
                    var recipe = recipes[random.Next(recipes.Count)];
                    Commands.SetRecipe(own.Id, recipe);
                }
            }
        }

        void Configure()
        {
            if (isConfigured)
                return;
            isConfigured = true;

            Game.SetPlayerName("bot-cs");
            Game.PlayerJoinForce(0); // create new force
            Game.SetForceColor(1f, 0f, 0f);
            // todo choose race
        }

        void Updating(object sender, bool stepping)
        {
            if (Game.GameState() == Interop.UwGameStateEnum.Session)
            {
                Configure();
                return;
            }

            if (!stepping)
                return;

            switch (workStep++ % 10) // save some cpu cycles by splitting work over multiple steps
            {
                case 1:
                    AttackNearestEnemies();
                    break;
                case 5:
                    AssignRandomRecipes();
                    break;
            }
        }

        void Run()
        {
            Game.LogInfo("bot-cs start");
            if (!Game.TryReconnect())
            {
                Game.SetConnectStartGui(true);
                if (!Game.ConnectEnvironment())
                    Game.ConnectNewServer();
            }
            Game.LogInfo("bot-cs done");
        }

        Bot()
        {
            Events.Updating += Updating;
        }

        static int Main(string[] args)
        {
            string root = Environment.GetEnvironmentVariable("UNNATURAL_ROOT");
            if (root == null)
            {
                string cwd = Directory.GetCurrentDirectory();
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows) && Directory.GetFiles(cwd, Interop.LibName + ".dll").Length > 0)
                    root = cwd;
                else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux) && Directory.GetFiles(cwd, "lib" + Interop.LibName + ".so").Length > 0)
                    root = cwd;
            }
            if (root == null)
            {
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
                    root = "C:/Program Files (x86)/Steam/steamapps/common/Unnatural Worlds/bin";
                else
                    root = Environment.GetEnvironmentVariable("HOME") + "/.steam/steam/steamapps/common/Unnatural Worlds/bin";
            }
            Console.WriteLine("looking for uw library in: " + root);
            Directory.SetCurrentDirectory(root);

            Bot bot = new Bot();
            bot.Run();
            return 0;
        }
    }
}
