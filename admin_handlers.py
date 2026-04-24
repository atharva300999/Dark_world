import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_USER_ID
from database import get_user, add_channel, remove_channel, get_all_channels, clear_all_channels

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_USER_ID

# Gift code functions
def create_gift_code(points: int, max_uses: int, expires_days: int, created_by: int) -> str:
    import random
    import string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    expires_at = datetime.now() + timedelta(days=expires_days)
    c.execute(
        "INSERT INTO gift_codes (code, points, max_uses, expires_at, created_by) VALUES (?, ?, ?, ?, ?)",
        (code, points, max_uses, expires_at, created_by),
    )
    conn.commit()
    conn.close()
    return code

def redeem_gift_code(user_id: int, code: str):
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM gift_codes WHERE code = ?", (code,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False, "❌ Invalid gift code!", 0
    gift_code, points, max_uses, used_count, expires_at, _ = row
    if datetime.now() > datetime.fromisoformat(expires_at):
        conn.close()
        return False, "❌ This gift code has expired!", 0
    if used_count >= max_uses:
        conn.close()
        return False, "❌ This gift code has reached its maximum uses!", 0
    user = get_user(user_id)
    redeemed_codes = user["redeemed_codes"]
    if gift_code in redeemed_codes:
        conn.close()
        return False, "❌ You have already redeemed this code!", 0
    redeemed_codes.append(gift_code)
    c.execute("UPDATE gift_codes SET used_count = used_count + 1 WHERE code = ?", (gift_code,))
    c.execute("UPDATE users SET points = points + ?, redeemed_codes = ? WHERE user_id = ?", (points, json.dumps(redeemed_codes), user_id))
    conn.commit()
    conn.close()
    return True, f"✅ Successfully redeemed {points} points!", points

async def admin_create_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "📦 **Create Gift Code**\n\n"
            "Usage: `/createcode <points> <max_uses> <expires_days>`\n\n"
            "Example: `/createcode 50 100 30`\n\n"
            "• points: Gift code er points\n"
            "• max_uses: Kotobar use kora jabe\n"
            "• expires_days: Koto din por expire korbe",
            parse_mode="Markdown"
        )
        return
    try:
        points = int(args[0])
        max_uses = int(args[1])
        expires_days = int(args[2])
        code = create_gift_code(points, max_uses, expires_days, update.effective_user.id)
        await update.message.reply_text(
            f"✅ **Gift code created!**\n\n"
            f"📝 **Code:** `{code}`\n"
            f"⭐ **Points:** {points}\n"
            f"🔄 **Max Uses:** {max_uses}\n"
            f"📅 **Expires:** {expires_days} days\n\n"
            f"Share this code with users!",
            parse_mode="Markdown"
        )
    except ValueError:
        await update.message.reply_text("❌ Please provide valid numbers.")

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text(
            "📢 **Broadcast Message**\n\n"
            "Usage: `/broadcast <message>`\n\n"
            "Example: `/broadcast Welcome to our bot!`",
            parse_mode="Markdown"
        )
        return
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    success_count = 0
    fail_count = 0
    for user in users:
        try:
            await context.bot.send_message(
                user[0], 
                f"📢 **Announcement**\n\n{message}", 
                parse_mode="Markdown"
            )
            success_count += 1
        except Exception:
            fail_count += 1
    await update.message.reply_text(
        f"✅ **Broadcast Complete**\n\n"
        f"✓ Sent: {success_count} users\n"
        f"✗ Failed: {fail_count} users"
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    conn = sqlite3.connect("bot_data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT SUM(points) FROM users")
    total_points = c.fetchone()[0] or 0
    c.execute("SELECT SUM(total_referrals) FROM users")
    total_refs = c.fetchone()[0] or 0
    c.execute("SELECT SUM(total_used_points) FROM users")
    total_used = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM required_channels")
    total_channels = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM gift_codes")
    total_codes = c.fetchone()[0]
    conn.close()
    await update.message.reply_text(
        f"📊 **Bot Statistics**\n\n"
        f"👥 **Total Users:** {total_users}\n"
        f"⭐ **Total Points:** {total_points}\n"
        f"🫂 **Total Referrals:** {total_refs}\n"
        f"💸 **Points Used:** {total_used}\n"
        f"📢 **Force Channels:** {total_channels}\n"
        f"🎁 **Gift Codes:** {total_codes}\n\n"
        f"💰 **Cost per Service:** 1 point"
    )

async def admin_add_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "➕ **Add Points**\n\n"
            "Usage: `/addpoints <user_id> <points>`\n\n"
            "Example: `/addpoints 123456789 20`"
        )
        return
    try:
        target_id = int(args[0])
        points = int(args[1])
        from database import update_user_points
        update_user_points(target_id, points)
        await update.message.reply_text(f"✅ Added {points} points to user `{target_id}`.", parse_mode="Markdown")
        try:
            await context.bot.send_message(target_id, f"🎉 **Admin added {points} points to your account!**", parse_mode="Markdown")
        except:
            pass
    except ValueError:
        await update.message.reply_text("❌ Please provide valid numbers.")

# ============ NEW: CHANNEL MANAGEMENT COMMANDS ============

async def admin_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a channel that users must join (supports both public and private)"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "🔐 **Add Force Join Channel**\n\n"
            "**Public Channel:**\n"
            "`/addchannel public channelusername`\n"
            "Example: `/addchannel public mychannel`\n\n"
            "**Private Channel:**\n"
            "`/addchannel private invite_link`\n"
            "Example: `/addchannel private https://t.me/+abc123xyz`\n\n"
            "⚠️ **Note:**\n"
            "• For public channels, just send the username (without @)\n"
            "• For private channels, send the full invite link\n"
            "• Users must join ALL channels to use the bot"
        )
        return
    
    channel_type = args[0].lower()
    channel_input = args[1]
    
    if channel_type == "public":
        # Remove @ if present
        if channel_input.startswith("@"):
            channel_input = channel_input[1:]
        success = add_channel(channel_input, "public", update.effective_user.id)
        if success:
            await update.message.reply_text(
                f"✅ **Public channel added successfully!**\n\n"
                f"📢 Channel: `@{channel_input}`\n"
                f"🔓 Type: Public\n\n"
                f"Users must join this channel to use the bot.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ Channel `{channel_input}` already exists!", parse_mode="Markdown")
    
    elif channel_type == "private":
        success = add_channel(channel_input, "private", update.effective_user.id)
        if success:
            await update.message.reply_text(
                f"✅ **Private channel added successfully!**\n\n"
                f"📢 Invite Link: {channel_input}\n"
                f"🔒 Type: Private\n\n"
                f"Users must join this channel to use the bot.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ This invite link already exists in the list!")
    
    else:
        await update.message.reply_text("❌ Invalid type! Use `public` or `private`", parse_mode="Markdown")

async def admin_remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a channel from force join list"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "🗑️ **Remove Channel**\n\n"
            "Usage: `/removechannel <channel_username>`\n"
            "Example: `/removechannel mychannel`\n\n"
            "Use `/listchannels` to see all channels"
        )
        return
    
    channel_input = args[0]
    if channel_input.startswith("@"):
        channel_input = channel_input[1:]
    
    success = remove_channel(channel_input)
    if success:
        await update.message.reply_text(f"✅ Channel `{channel_input}` removed successfully!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Channel `{channel_input}` not found!", parse_mode="Markdown")

async def admin_list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all required channels"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    channels = get_all_channels()
    
    if not channels:
        await update.message.reply_text(
            "📢 **Force Join Channels**\n\n"
            "No channels added yet!\n\n"
            "Add a channel using:\n"
            "`/addchannel public username`\n"
            "`/addchannel private invite_link`",
            parse_mode="Markdown"
        )
        return
    
    message = "📢 **Force Join Channels**\n\n"
    for i, (channel, channel_type) in enumerate(channels, 1):
        if channel_type == "public":
            message += f"{i}. `@{channel}` (Public)\n"
        else:
            message += f"{i}. `{channel}` (Private)\n"
    
    message += f"\n**Total:** {len(channels)} channels\n\n"
    message += "Users must join ALL channels to use the bot.\n"
    message += "To remove: `/removechannel <username>`"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def admin_clear_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all required channels"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    channels = get_all_channels()
    if not channels:
        await update.message.reply_text("❌ No channels to clear!")
        return
    
    clear_all_channels()
    await update.message.reply_text(f"✅ Cleared all {len(channels)} channels successfully!")
