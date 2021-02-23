def get_member(ctx, user):
    if user == None:
        return user
    try:
        member = ctx.message.mentions[0]
    except:
        member = ctx.guild.get_member_named(user)
    if not member:
        try:
            member = ctx.guild.get_member(int(user))
        except ValueError:
            pass
    if not member:
        return None
    return member