from cogs.preferences.user import UserPreferences


def setup(bot):
    bot.add_cog(UserPreferences(bot))
