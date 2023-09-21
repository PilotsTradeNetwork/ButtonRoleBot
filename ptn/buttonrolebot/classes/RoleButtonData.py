class RoleButtonData:

    def __init__(self, info_dict=None):
        """
        Class represents a RoleButtonData object as returned from user input.

        :param info_dict: RoleButtonData data.
        """
        if info_dict:
            # Convert the object to a dictionary
            info_dict = dict(info_dict)
        else:
            info_dict = dict()

        self.message = info_dict.get('message', None)
        self.role_id = info_dict.get('role_id', None)
        self.button_label = info_dict.get('button_label', None)
        self.button_emoji = info_dict.get('button_emoji', None)
        self.button_style = info_dict.get('button_style', None)

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

    def __str__(self):
        """
        Overloads str to return a readable object

        :rtype: str
        """
        return 'RoleButtonData: message:{0.message} role_id:{0.role_id} ' \
               'button_label:{0.button_label} button_emoji:{0.button_emoji} ' \
               'button_style:{0.button_style}'.format(self)

    def __bool__(self):
        """
        Override boolean to check if any values are set, if yes then return True, else False, where false is an empty
        class.

        :rtype: bool
        """
        return any([value for key, value in vars(self).items() if value])
