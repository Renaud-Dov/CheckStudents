from typing import Optional

import discord
from discord import ui
from discord.utils import MISSING

from src import Embed
from src.data import Server


def SettingsEmbed(interaction: discord.Interaction):
    data = Server(interaction.guild_id)
    embed = Embed.BasicEmbed(color=discord.Colour.orange(), title="Settings")

    embed.add_field(name="• Private Messages",
                    value=("Enabled" if data.mp else "Disabled"),
                    inline=False)
    embed.add_field(name="• Show present students after call",
                    value=("Enabled" if data.showPresents else "Disabled"),
                    inline=False)
    embed.add_field(name="• Delay", value=f"{data.delay} min", inline=False)
    return embed


class Edit(discord.ui.View):

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="Reset all settings", style=discord.ButtonStyle.green)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = Server(interaction.guild_id)
        data.Reset()
        data.Save_Settings()

        embed = Embed.BasicEmbed(color=discord.Colour.orange(),
                                 title="**__Factory reset:__**\n"
                                       "**Show presents students, Sys Messages and Private Messages :** Activated\n"
                                       "Delay for for late students after a call : 10 minutes")

        await self.interaction.edit_original_response(embed=embed,
                                                      view=Done(self.interaction, Edit(self.interaction),
                                                                SettingsEmbed(interaction)))
        await interaction.response.defer()

    @discord.ui.button(label="Set Delay", style=discord.ButtonStyle.green)
    async def setDelay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetDelay(self.interaction))

    @discord.ui.button(label="Activate/Deactivate system messages", style=discord.ButtonStyle.green)
    async def system(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = Server(interaction.guild.id)
        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Private messages are now disabled" if data.mp
                                 else "Private messages are now enabled")
        data.mp = not data.mp
        data.Save_Settings()

        await self.interaction.edit_original_response(embed=embed,
                                                      view=Done(self.interaction, Edit(self.interaction),
                                                                SettingsEmbed(interaction)))
        await interaction.response.defer()

    @discord.ui.button(label="Activate/Deactivate presents students", style=discord.ButtonStyle.green)
    async def presents(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = Server(interaction.guild_id)
        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Private messages are now disabled" if data.showPresents
                                 else "Private messages are now enabled")
        data.showPresents = not data.showPresents
        data.Save_Settings()

        await self.interaction.edit_original_response(embed=embed, view=Done(self.interaction, Edit(self.interaction),
                                                                             SettingsEmbed(interaction)))
        await interaction.response.defer()


class Done(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, next_view: discord.ui.View,
                 next_embed: Optional[discord.Embed] = MISSING):
        super().__init__()
        self.next_view = next_view
        self.next_embed = next_embed
        self.interaction = interaction

    @discord.ui.button(label="OK", style=discord.ButtonStyle.blurple, emoji="✅")
    async def ok(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.interaction.edit_original_response(view=self.next_view, embed=self.next_embed)
        await interaction.response.defer()


class SetDelay(ui.Modal, title='Set Delay'):
    value = ui.TextInput(label='Delay (in minutes between 0 and 60 min)', default="10", style=discord.TextStyle.short,
                         required=True)

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        data = Server(interaction.guild_id)
        # if value is a number between 0 and 60
        if self.value.value.isdigit():
            value = int(self.value.value)
            if 0 <= value <= 60:

                data.delay = value
                data.Save_Settings()
                embed = Embed.BasicEmbed(color=discord.Color.red(), title=f"Value set to {value} minute(s)")
                await self.interaction.edit_original_response(embed=embed,
                                                              view=Done(self.interaction, Edit(self.interaction),
                                                                        SettingsEmbed(interaction)))
                await interaction.response.defer()
            else:
                embed = Embed.BasicEmbed(color=discord.Color.red(), title="Value must be between 0 and 60")
                await self.interaction.edit_original_response(embed=embed,
                                                              view=Done(self.interaction, Edit(self.interaction),
                                                                        SettingsEmbed(interaction)))
                await interaction.response.defer()
        else:
            embed = Embed.BasicEmbed(color=discord.Color.red(), title="Value must be a integer.")
            await self.interaction.edit_original_response(embed=embed,
                                                          view=Done(self.interaction, Edit(self.interaction),
                                                                    SettingsEmbed(interaction)))
            await interaction.response.defer()
