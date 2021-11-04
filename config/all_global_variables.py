class Arguments:
    jumble_countdown = None

class DiscordGuilds:
    heckinchonkers_id = 668621889593278464

class DiscordChannels:
    bot_testing_channel_id = 671324383234621451
    delivery_channel_id = 670425054613602324
    moonshine_channel_id = 679498684525707285
    bounty_channel_id = 679498799148040202
    nature_channel_id = 737688182430105681
    announcements_channel_id = 675874726157090866
    heftychonks_channel_id = 677184836279992321
    heftychonks_rules_channel_id = 677184743418363942
    megachonkers_channel_id = 677710626168111104
    aheckinadmin_channel_id = 677704222493376545
    stb_channel_id = 670425120409649163
    general_channel_id = 746711941392760923
    squareboard_channel_id = 694878448686202910

class RoleMessages:
    list_of_role_messages = [669866460847276043, 762745355392909323, 775724165322768425]

class ActiveChannels(object):
    delivery_active_channel = DiscordChannels.delivery_channel_id
    moonshine_active_channel = DiscordChannels.moonshine_channel_id
    bounty_active_channel = DiscordChannels.bounty_channel_id
    nature_active_channel = DiscordChannels.nature_channel_id
    stb_active_channel = DiscordChannels.stb_channel_id
    general_active_channel = DiscordChannels.general_channel_id

    @classmethod
    def set_all_channels_to_test(cls):
        cls.delivery_active_channel = DiscordChannels.bot_testing_channel_id
        cls.moonshine_active_channel = DiscordChannels.bot_testing_channel_id
        cls.bounty_active_channel = DiscordChannels.bot_testing_channel_id
        cls.nature_active_channel = DiscordChannels.bot_testing_channel_id
        cls.stb_active_channel = DiscordChannels.bot_testing_channel_id
        cls.general_active_channel = DiscordChannels.bot_testing_channel_id

    @classmethod
    def set_channels_to_test(cls, *channels):
        # TODO Add kwargs for one or more channel arguments and set cls variables respectively
        pass

class DiscordRoles:
    delivery_role_id = 669707245621215244
    heftychonks_role_id = 676955530337452111
    heckinadmin_role_id = 676206304259342377
    chonkerbot_role_id = 668887526915833856
    megachonkers_role_id = 675467855122137098
    jumblies_role_id = 775724493179715616
    fast_fingers_role_id = 781700777626042378


class ActivityStrings:
    delivery_str = 'delivery'
    moonshine_str = 'moonshine'
    bounty_str = 'bounty'
    nature_str = 'naturalist'
    posse_str = 'general'


class FilePaths:
    commands_cog_file_path = 'rdo_role_commands_cogs.all_commands'
    naturalist_commands_cog_file_path = 'rdo_role_commands_cogs.naturalist_commands'
    json_queue_template = "./files/json/queue_template.json"
    json_queue_updated = "./files/json/queue_updated.json"
    csv_animals = "./files/txt/animals.csv"
    json_thanks = "./files/json/thanks.json"
    json_psn = "./files/json/psn.json"
    csv_rdo_words = "./files/txt/rdowords.csv"
    txt_winelines = "./files/txt/winelines.txt"
    txt_eightball = "./files/txt/eightball.txt"
    json_pics_n_gifs = "./files/json/pics_n_gifs.json"


