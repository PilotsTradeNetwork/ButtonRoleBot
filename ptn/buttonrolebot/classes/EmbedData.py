from ptn.buttonrolebot.constants import EMBED_COLOUR_PTN_DEFAULT, DEFAULT_EMBED_DESC
import json

class EmbedData:

    def __init__(self, info_dict=None):
        """
        Class represents an Embed object as returned from user input.

        :param info_dict: Embed data.
        """
        if info_dict:
            # Convert the object to a dictionary
            info_dict = dict(info_dict)
        else:
            info_dict = dict()

        self.embed_title = info_dict.get('embed_title', None)
        self.embed_description = info_dict.get('embed_description', DEFAULT_EMBED_DESC)
        self.embed_image_url = info_dict.get('embed_image_url', None)
        self.embed_footer = info_dict.get('embed_footer', None)
        self.embed_thumbnail_url = info_dict.get('embed_thumbnail_url', None)
        self.embed_author_name = info_dict.get('embed_author_name', None)
        self.embed_author_avatar_url = info_dict.get('embed_author_avatar_url', None)
        self.embed_color = info_dict.get('embed_color', EMBED_COLOUR_PTN_DEFAULT)
        self.embed_json = info_dict.get('embed_json', None)


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


    def set_attribute(self, attribute_name, value):
        """
        Populates attribute_name with value.
        """
        # Check if the attribute name exists
        if hasattr(self, attribute_name):
            # Use setattr to set the attribute dynamically
            setattr(self, attribute_name, value)
        else:
            print(f"⚠ Attribute '{attribute_name}' does not exist in EmbedData")


    def __str__(self):
        """
        Overloads str to return a readable object

        :rtype: str
        """
        return 'EmbedData: embed_title:{0.embed_title} | embed_description:{0.embed_description} | ' \
               'embed_image:{0.embed_image_url} embed_footer:{0.embed_footer} | embed_thumbnail:{0.embed_thumbnail_url} | ' \
               'embed_author_name:{0.embed_author_name} | embed_author_avatar:{0.embed_author_avatar_url} | ' \
               'embed_color:{0.embed_color} | embed_json:{0.embed_json}'.format(self)


    def __bool__(self):
        """
        Override boolean to check if any values are set, if yes then return True, else False, where false is an empty
        class.

        :rtype: bool
        """
        return any([value for key, value in vars(self).items() if value])
