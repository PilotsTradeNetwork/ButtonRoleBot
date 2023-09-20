

import discord

# generate an embed from a dict
async def _generate_embed_from_dict(embed_dict):
    # create empty embed
    embed = discord.Embed()

    # Populate the embed with values from content_dict
    if 'content_dict' in embed_dict:
        content_dict = embed_dict['content_dict']
        if 'embed_title' in content_dict and content_dict['embed_title']:
            embed.title = content_dict['embed_title']
        if 'embed_description' in content_dict and content_dict['embed_description']:
            embed.description = content_dict['embed_description']
        if 'embed_image' in content_dict and content_dict['embed_image']:
            embed.set_image(url=content_dict['embed_image'])

    # Populate the embed with values from meta_dict
    if 'meta_dict' in embed_dict:
        meta_dict = embed_dict['meta_dict']
        if 'embed_thumbnail' in meta_dict and meta_dict['embed_thumbnail']:
            embed.set_thumbnail(url=meta_dict['embed_thumbnail'])
        if 'embed_author_name' in meta_dict and meta_dict['embed_author_name']:
            if 'embed_author_avatar' in meta_dict and meta_dict['embed_author_avatar']:
                embed.set_author(name=meta_dict['embed_author_name'], icon_url=meta_dict['embed_author_avatar'])
            else:
                embed.set_author(name=meta_dict['embed_author_name'])
        if 'embed_color' in meta_dict:
            embed.color = meta_dict['embed_color']

    return embed