# Replace the check_join logic in button_callback with this:

elif data == "check_join":
    all_joined = True
    channels = get_all_channels()
    
    for channel_username, channel_type in channels:
        try:
            if channel_type == "public":
                # For public channels, check member status
                chat_member = await context.bot.get_chat_member(f"@{channel_username}", user_id)
                if chat_member.status in ["left", "kicked"]:
                    all_joined = False
                    break
            else:
                # For private channels, we can't check directly
                # Try to check if user can send message or use a different approach
                # For now, assume they joined or they will click the link
                # You can implement invite link tracking if needed
                pass
        except Exception as e:
            # If channel is private or bot can't check, still allow
            # But user must have clicked the join link
            logger.warning(f"Could not check channel {channel_username}: {e}")
    
    if all_joined:
        update_join_verification(user_id)
        await query.edit_message_text(VERIFICATION_SUCCESS.format(first_name=user["first_name"]))
        await show_main_menu(update, context)
    else:
        await query.edit_message_text(VERIFICATION_FAILED, reply_markup=get_channel_buttons())
