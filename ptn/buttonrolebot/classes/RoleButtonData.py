# import discord so discord.ButtonStyle has meaning
import discord


class RoleButtonData:

    def __init__(self, info_dict=None):
        """
        Class represents a RoleButtonData object as returned from user input.

        :param info_dict: RoleButtonData data expressed as a dict.
        """
        if info_dict:
            # Convert the object to a dictionary
            info_dict = dict(info_dict)
        else:
            info_dict = dict()

        self.message = info_dict.get('message', None)
        self.role_id = info_dict.get('role_id', None)
        self.role_object = info_dict.get('role_object', None)
        self.button_label = info_dict.get('button_label', None)
        self.button_emoji = info_dict.get('button_emoji', None)
        self.button_style = info_dict.get('button_style', None)
        self.button_action = info_dict.get('button_action', 'toggle')
        self.button_list = []

    def reset(self):
        self.role_id = None
        self.button_label = None
        self.button_emoji = None
        self.button_style = None
        self.button_action = None

    def to_dictionary(self):
        """
        Formats the embed data into a dictionary for easy access.

        :returns: A dictionary representation for the embed data.
        :rtype: dict
        """
        response = {}
        for key, value in vars(self).items():
            if value is not None:
                response[key] = value
        return response

    def get_button_style_name(self):
        """
        Formats discord.ButtonStyle into a form readable by normies 🤓
        """

        style_mapping = {
            discord.ButtonStyle.success: 'Success (Green)',
            discord.ButtonStyle.primary: 'Primary (Blurple)',
            discord.ButtonStyle.secondary: 'Secondary (Grey)',
            discord.ButtonStyle.danger: 'Danger (Red)'
        }

        style = style_mapping.get(self.button_style, None)
        print(f"Style is {style}")

        return style

    def __str__(self):
        """
        Overloads str to return a readable object

        :rtype: str
        """
        return 'RoleButtonData: message:{0.message} | role_id:{0.role_id} | ' \
               'button_label:{0.button_label} | button_emoji:{0.button_emoji} | ' \
               'button_style:{0.button_style} | button_action:{0.button_action}'.format(self)

    def __bool__(self):
        """
        Override boolean to check if any values are set, if yes then return True, else False, where false is an empty
        class.

        :rtype: bool
        """
        return any([value for key, value in vars(self).items() if value])
