# Add these new admin command handlers in main.py:

# Channel management commands (NEW)
app.add_handler(CommandHandler("addchannel", admin_add_channel))
app.add_handler(CommandHandler("removechannel", admin_remove_channel))
app.add_handler(CommandHandler("listchannels", admin_list_channels))
app.add_handler(CommandHandler("clearchannels", admin_clear_channels))
