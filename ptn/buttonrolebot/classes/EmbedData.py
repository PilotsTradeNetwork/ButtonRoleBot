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
        self.embed_description = info_dict.get('embed_description', None)
        self.embed_image = info_dict.get('embed_image', None)
        self.embed_thumbnail = info_dict.get('embed_thumbnail', None)
        self.embed_author_name = info_dict.get('embed_author_name', None)
        self.embed_author_avatar = info_dict.get('embed_author_avatar', None)
        self.embed_color = info_dict.get('embed_color', None)

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
        return 'EmbedData: embed_title:{0.embed_title} embed_description:{0.embed_description} ' \
               'embed_image:{0.embed_image} embed_thumbnail:{0.embed_thumbnail} ' \
               'embed_author_name:{0.embed_author_name} embed_author_avatar:{0.embed_author_avatar}' \
               'embed_color:{0.embed_color}'.format(self)

    def __bool__(self):
        """
        Override boolean to check if any values are set, if yes then return True, else False, where false is an empty
        class.

        :rtype: bool
        """
        return any([value for key, value in vars(self).items() if value])
