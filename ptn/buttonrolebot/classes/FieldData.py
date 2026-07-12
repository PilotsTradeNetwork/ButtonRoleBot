import discord


class FieldData:
    def __init__(self, info_dict=None):
        """
        Class represents field data for a Modal as returned from user input.

        :param info_dict: Field data.
        """
        if info_dict:
            # Convert the object to a dictionary
            info_dict = dict(info_dict)
        else:
            info_dict = dict()

        self.attr = info_dict.get("attr", None)
        self.title = info_dict.get("title", None)
        self.label = info_dict.get("label", None)
        self.placeholder = info_dict.get("placeholder", "Leave blank for none.")
        self.style = info_dict.get("style", discord.TextStyle.long)
        self.required = info_dict.get("required", False)
        self.max_length = info_dict.get("max_length", 512)
        self.default = info_dict.get("default", None)

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
        return (
            "Attr: {0.attr} | Title: {0.title} | Label:{0.label} | Placeholder:{0.placeholder} |"
            " Style:{0.style} | Required:{0.required} | Max_length:{0.max_length} | Default:{0.default}".format(self)
        )

    def __bool__(self):
        """
        Override boolean to check if any values are set, if yes then return True, else False, where false is an empty
        class.

        :rtype: bool
        """
        return any([value for key, value in vars(self).items() if value])
