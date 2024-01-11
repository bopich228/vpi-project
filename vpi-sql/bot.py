import discord
from discord import app_commands
from vpimain import Game

MY_GUILD = discord.Object(id=1157327909992804456)  # replace with your guild id
auth_user_ids = [642112940295847984, 1162034396019314799]


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.tree.command()
async def turn(interaction: discord.Interaction):
    """Совершает ход"""
    status = Game.turn()
    if status.name == "no_table":
        await interaction.response.send_message("Ошибка. Перезапустите игру.")
    else:
        await interaction.response.send_message("Ход сделан.")


@client.tree.command()
async def смерть(interaction: discord.Interaction):
    """НЕ ТРОГАЙТЕ"""
    Game.debug_pop()
    await interaction.response.send_message("Тучи сгущаются.")


@client.tree.command()
async def restart(interaction: discord.Interaction):
    if interaction.user.id in auth_user_ids:
        """Перезапускает игру. ВНИМАНИЕ! ВЫ ТОЧНО УВЕРЕНЫ?"""
        Game.rollback()
        await interaction.response.send_message(
            "Игра перезапущена и откачена к начальному состоянию."
        )
    else:
        await interaction.response.send_message("Ты тварь дрожащая и права не имеешь.")


@client.tree.command()
@app_commands.describe(
    first_value="название планеты",
)
async def planet(interaction: discord.Interaction, first_value: str):
    """Информация о планете."""
    system, resources, status = Game.fetch_Planet(first_value)
    if status.name == "no_elem":
        await interaction.response.send_message("Такой планеты нету.")
    elif status.name == "no_table":
        await interaction.response.send_message("Ошибка. Перезапустите игру.")
    else:
        await interaction.response.send_message(
            f"""Планета {first_value} находится в системе {system}.
            \n Общий прирост {abs(resources[0])}; базовая продукция {resources[1]}; гражданская продукция {resources[2]}; военная продукция {resources[3]}; накопленных ресурсов {round(abs(resources[4]), 2)}.
            \n Население {round(resources[5], 2)}. Коэффициент занятости {round(resources[5]/(abs(resources[0])+resources[2]+resources[3]), 2)}."""
        )


@client.tree.command()
@app_commands.describe(
    first_value="название системы",
)
async def system(interaction: discord.Interaction, first_value: str):
    """Информация о системе."""
    polity, planets, st, status = Game.fetch_System(first_value)
    if status.name == "no_elem":
        await interaction.response.send_message("Такой системы нету.")
    elif status.name == "no_table":
        await interaction.response.send_message("Ошибка. Перезапустите игру.")
    else:
        await interaction.response.send_message(
            f"Система {first_value} - часть империи {polity}. \nВ системе находятся следующие планеты: {planets} {st}"
        )


@client.tree.command()
@app_commands.describe(
    first_value="название планеты",
)
async def buildings(interaction: discord.Interaction, first_value: str):
    """Информация о постройках на планете."""
    builds, status = Game.planet_Buildings(first_value)
    if status.name == "no_elem":
        await interaction.response.send_message("Такой системы нету.")
    elif status.name == "no_table":
        await interaction.response.send_message("Ошибка. Перезапустите игру.")
    else:
        await interaction.response.send_message(
            f"На планете {first_value} находятся следующие постройки: {builds}"
        )


@client.tree.command()
@app_commands.describe(
    first_value="название планеты",
)
async def demographics(interaction: discord.Interaction, first_value: str):
    """Информация о населении планеты."""
    bf, stl, pln, status = Game.planet_demos(first_value)
    if status.name == "no_elem":
        await interaction.response.send_message("Такой планеты нету.")
    elif status.name == "no_table":
        await interaction.response.send_message("Ошибка. Перезапустите игру.")
    elif status.name == "invalid_elem":
        await interaction.response.send_message("Нет данных по населению прошлых лет.")
    else:
        if bf == []:
            await interaction.response.send_message(
                f"""Текущее население на планете {first_value} - {round(pln[5], 2)}.
        За последний год население изменилось на {round((1-(stl[5]/pln[5])), 2)*100}% c {round(stl[5], 2)}."""
            )
        else:
            await interaction.response.send_message(
                f"""Текущее население на планете {first_value} - {round(pln[5], 2)}.
        За последний год население изменилось на {round((1-(stl[5]/pln[5]))*100, 2)}% c {round(stl[5], 2)}.
        За последние пять лет население изменилось на {round((1-(bf[5]/pln[5]))*100, 2)}% с {round(bf[5], 2)}"""
            )


@client.tree.command()
@app_commands.describe(
    first_value="название планеты",
)
async def finances(interaction: discord.Interaction, first_value: str):
    """Информация о финансах империи."""
    bf, stl, pln, status = Game.polity_finances(first_value)
    if status.name == "no_elem":
        await interaction.response.send_message("Такой империи нету.")
    elif status.name == "no_table":
        await interaction.response.send_message("Ошибка. Перезапустите игру.")
    elif status.name == "invalid_elem":
        await interaction.response.send_message("Нет данных по бюджету прошлых лет.")
    else:
        if bf == -100000.0:
            await interaction.response.send_message(
                f"""В настоящий момент баланс империи {first_value} - {round(pln, 2)}. За последний год баланс изменился на {round(pln-stl, 2)} c {round(stl, 2)}"""
            )
        else:
            await interaction.response.send_message(
                f"""В настоящий момент баланс империи {first_value} - {round(pln, 2)}. За последний год баланс изменился на {round(pln-stl, 2)} c {round(stl, 2)}
        За последние пять лет баланс изменился на {round(pln-bf, 2)} с {round(bf, 2)}"""
            )


@client.tree.command()
@app_commands.describe(
    first_value="название планеты",
)
async def caqlculate_ql(interaction: discord.Interaction, first_value: str):
    """Информация об уровне жизни на планете."""
    builds, status = Game.calculate_ql(first_value)
    if status.name == "no_elem":
        await interaction.response.send_message(
            "Такой планеты нету либо там вообще жить негде."
        )
    elif status.name == "no_table":
        await interaction.response.send_message("Ошибка. Перезапустите игру.")
    else:
        await interaction.response.send_message(
            f"На планете {first_value} уровень жизни равен {builds}."
        )


@client.tree.command()
@app_commands.describe(
    first_value="название империи",
)
async def polity(interaction: discord.Interaction, first_value: str):
    """Информация об империи."""
    creds, systems, status = Game.fetch_Polity(first_value)
    if status.name == "no_elem":
        await interaction.response.send_message("Такой империи нету.")
    elif status.name == "no_table":
        await interaction.response.send_message("Ошибка. Перезапустите игру.")
    else:
        await interaction.response.send_message(
            f"Империя {first_value} имеет баланс в {creds} кредитов. \nВ состав империи входят следующие системы: {systems}"
        )


@client.tree.command()
@app_commands.describe(
    first_value="название планеты", second_value="количество добавляемой продукции"
)
async def planet_add_bp(
    interaction: discord.Interaction, first_value: str, second_value: int
):
    if interaction.user.id in auth_user_ids:
        """Добавляем продукцию."""
        status = Game.add_BP(first_value, second_value)
        if status.name == "no_elem":
            await interaction.response.send_message("Такой планеты нету.")
        elif status.name == "no_table":
            await interaction.response.send_message("Ошибка. Перезапустите игру.")
        else:
            await interaction.response.send_message(
                f"Базовая продукция увеличена на {second_value} на планете {first_value}"
            )
    else:
        await interaction.response.send_message("Ты тварь дрожащая и права не имеешь.")


@client.tree.command()
@app_commands.describe(first_value="название планеты", second_value="название здания")
async def planet_build(
    interaction: discord.Interaction, first_value: str, second_value: str
):
    if interaction.user.id in auth_user_ids:
        """Начинаем строительство на планете."""
        status = Game.build_Building(first_value, second_value)
        if status.name == "no_table":
            await interaction.response.send_message("Ошибка. Перезапустите игру.")
        elif status.name == "no_elem":
            await interaction.response.send_message("Такой планеты нету.")
        elif status.name == "invalid_elem":
            await interaction.response.send_message("Такого здания не бывает.")
        elif status.name == "redundant_elem":
            await interaction.response.send_message(
                "Достигнут лимит зданий данного типа."
            )
        else:
            await interaction.response.send_message(
                f"Постройка здания {second_value} успешно начата на планете {first_value}."
            )
    else:
        await interaction.response.send_message("Ты тварь дрожащая и права не имеешь.")


@client.tree.command()
@app_commands.describe(
    first_value="название системы",
)
async def system_build(interaction: discord.Interaction, first_value: str):
    if interaction.user.id in auth_user_ids:
        """Построить в системе станцию."""
        status = Game.build_Station(first_value)
        if status.name == "no_table":
            await interaction.response.send_message("Ошибка. Перезапустите игру.")
        elif status.name == "no_elem":
            await interaction.response.send_message("Такой системы нету.")
        elif status.name == "redundant_elem":
            await interaction.response.send_message("В системе уже есть станция.")
        else:
            await interaction.response.send_message(
                f"Пoстройка станции в системе {first_value} успешно начата."
            )
    else:
        await interaction.response.send_message("Ты тварь дрожащая и права не имеешь.")


@client.tree.command()
@app_commands.describe(
    first_value="название cистемы", second_value="название новой правящей империи"
)
async def transfer(
    interaction: discord.Interaction, first_value: str, second_value: str
):
    if interaction.user.id in auth_user_ids:
        """Передаем систему от одной империи к другой."""
        oldsys, status = Game.transfer_System(first_value, second_value)
        if status.name == "no_elem":
            await interaction.response.send_message(
                "Проверьте правильность параметров; системы либо империи не существует."
            )
        elif status.name == "no_table":
            await interaction.response.send_message("Ошибка. Перезапустите игру.")
        if status.name == "invalid_elem":
            await interaction.response.send_message(
                f"Система {first_value} уже находится под контролем империи {second_value}."
            )
        else:
            await interaction.response.send_message(
                f"Система {first_value} передана от империи {oldsys} империи {second_value}."
            )
    else:
        await interaction.response.send_message("Ты тварь дрожащая и права не имеешь.")


@client.tree.command()
@app_commands.describe(
    first_value="название первой империи", second_value="название второй империи"
)
async def shengen(
    interaction: discord.Interaction, first_value: str, second_value: str
):
    if interaction.user.id in auth_user_ids:
        """Передаем систему от одной империи к другой."""
        status = Game.agree(first_value, second_value)
        if status.name == "no_elem":
            await interaction.response.send_message(
                "Проверьте правильность параметров; империи не существует."
            )
        elif status.name == "no_table":
            await interaction.response.send_message("Ошибка. Перезапустите игру.")
        else:
            await interaction.response.send_message(
                f"Заключено миграционное соглашение между империями {first_value} и {second_value}."
            )
    else:
        await interaction.response.send_message("Ты тварь дрожащая и права не имеешь.")


@client.tree.command()
@app_commands.describe(
    first_value="название первой планеты", second_value="название второй планеты"
)
async def deport(interaction: discord.Interaction, first_value: str, second_value: str):
    if interaction.user.id in auth_user_ids:
        """Начинает депортацию населения с первой на вторую планеты."""
        status = Game.deport(first_value, second_value)
        if status.name == "no_elem":
            await interaction.response.send_message(
                "Проверьте правильность параметров; одной из планет не существует."
            )
        elif status.name == "no_table":
            await interaction.response.send_message("Ошибка. Перезапустите игру.")
        elif status.name == "redundant_elem":
            await interaction.response.send_message(
                "Перемещение масс население между этими планетами уже имеет место."
            )
        elif status.name == "invalid_elem":
            await interaction.response.send_message(
                "Планеты не входят в состав одной империи."
            )
        else:
            await interaction.response.send_message(
                f"Начата депортация населения с планеты {first_value} на планету {second_value}."
            )
    else:
        await interaction.response.send_message("Ты тварь дрожащая и права не имеешь.")


client.run("MTE5MDY1MDk3MjQ3Nzg0OTY5Mg.Gu1UAB.B9iQHcbcmbfwi3wzTC87YI6xeRD9qW9XMTPxpI")
