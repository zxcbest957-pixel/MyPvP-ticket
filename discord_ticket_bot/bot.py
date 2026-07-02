import os
import asyncio
import logging
import time
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TicketBot")

# Load environment variables
load_dotenv()

# ----------------- Localization Dictionary -----------------
LOCALIZATION = {
    "en": {
        "welcome_title": "⚔️ Clan Application Ticket",
        "welcome_desc": (
            "Welcome {mention} to your clan application ticket!\n\n"
            "To submit your application for the Roblox Bedwars clan, please follow these steps:\n\n"
            "1️⃣ Click the **Enter Application Details** button below to submit your Roblox username and weekly Bedwars contribution capability.\n"
            "2️⃣ After submitting your details, upload a screenshot showing your statistics in **Roblox Bedwars** directly in this channel.\n\n"
            "*Our clan staff will review your stats and contribution as soon as possible.*"
        ),
        "btn_enter_details": "Enter Application Details",
        "btn_close_ticket": "Close Ticket",
        "modal_title": "Clan Application Submission",
        "modal_roblox_lbl": "Roblox Username",
        "modal_roblox_placeholder": "Enter your Roblox username here...",
        "modal_contrib_lbl": "Weekly Clan Contribution",
        "modal_contrib_placeholder": "e.g., 7,000 - 999,000 contribution per week",
        "details_submitted_title": "✅ Nickname & Contribution Submitted",
        "details_submitted_desc": (
            "**Roblox Username:** {username}\n"
            "**Weekly Contribution:** {contribution}\n\n"
            "Please now **upload a screenshot** of your **Roblox Bedwars statistics** in this channel.\n"
            "Simply attach the image and send it as a message."
        ),
        "username_first_warning": "⚠️ {mention}, please enter your Roblox details first by clicking the **Enter Application Details** button before uploading your screenshot.",
        "stats_submitted_title": "📥 Details Submitted",
        "stats_submitted_desc": "Your stats screenshot has been received and is now under review by staff. Please wait.",
        "admin_review_title": "⚔️ Clan Application Review Required",
        "admin_review_desc": "User {mention} has submitted clan application details.",
        "admin_review_discord": "Discord Account",
        "admin_review_roblox": "Roblox Username",
        "admin_review_contrib": "Weekly Contribution",
        "approval_title": "🎉 Clan Application Approved!",
        "approval_desc": (
            "Congratulations {mention}!\n"
            "Your clan application for Roblox account **{roblox_username}** has been approved.\n"
            "We have sent you a clan invite in **Roblox Bedwars**.\n\n"
            "👉 **Please open Roblox Bedwars, accept the clan invite, and then click the button below to confirm and close this ticket!**"
        ),
        "btn_accepted_invite": "I Accepted the Invite",
        "confirm_delete_msg": "🎉 **Congratulations! Welcome to the clan!** This channel will be deleted in 5 seconds.",
        "staff_permission_err": "❌ Only staff can approve applications.",
        "close_permission_err": "❌ You do not have permission to close this ticket.",
        "closing_msg": "🔒 **Closing ticket...** This channel will be deleted in 5 seconds."
    },
    "ru": {
        "welcome_title": "⚔️ Тикет заявки в клан",
        "welcome_desc": (
            "Добро пожаловать {mention} в ваш тикет заявки в клан!\n\n"
            "Чтобы подать заявку в клан по Roblox Bedwars, выполните следующие шаги:\n\n"
            "1️⃣ Нажмите кнопку **Ввести данные заявки** ниже, чтобы указать ваш никнейм Roblox и еженедельный вклад в клан.\n"
            "2️⃣ После отправки данных загрузите скриншот с вашей статистикой в **Roblox Bedwars** прямо в этот канал.\n\n"
            "*Персонал клана рассмотрит вашу статистику и вклад как можно скорее.*"
        ),
        "btn_enter_details": "Ввести данные заявки",
        "btn_close_ticket": "Закрыть тикет",
        "modal_title": "Подача заявки в клан",
        "modal_roblox_lbl": "Никнейм в Roblox",
        "modal_roblox_placeholder": "Введите ваш никнейм в Roblox...",
        "modal_contrib_lbl": "Еженедельный вклад в клан",
        "modal_contrib_placeholder": "Например, 7,000 - 999,000 вклада в неделю",
        "details_submitted_title": "✅ Никнейм и вклад отправлены",
        "details_submitted_desc": (
            "**Никнейм в Roblox:** {username}\n"
            "**Еженедельный вклад:** {contribution}\n\n"
            "Пожалуйста, теперь **загрузите скриншот** вашей **статистики в Roblox Bedwars** в этот канал.\n"
            "Просто прикрепите изображение к сообщению."
        ),
        "username_first_warning": "⚠️ {mention}, пожалуйста, сначала введите данные вашего аккаунта Roblox, нажав на кнопку **Ввести данные заявки** перед загрузкой скриншота.",
        "stats_submitted_title": "📥 Данные отправлены",
        "stats_submitted_desc": "Скриншот вашей статистики получен и находится на рассмотрении персонала. Пожалуйста, подождите.",
        "admin_review_title": "⚔️ Требуется проверка заявки в клан",
        "admin_review_desc": "Пользователь {mention} отправил данные для вступления в клан.",
        "admin_review_discord": "Аккаунт Discord",
        "admin_review_roblox": "Никнейм Roblox",
        "admin_review_contrib": "Еженедельный вклад",
        "approval_title": "🎉 Заявка в клан одобрена!",
        "approval_desc": (
            "Поздравляем, {mention}!\n"
            "Ваша заявка в клан для Roblox аккаунта **{roblox_username}** была одобрена.\n"
            "Мы отправили вам приглашение в клан в **Roblox Bedwars**.\n\n"
            "👉 **Пожалуйста, откройте Roblox Bedwars, примите приглашение в клан, а затем нажмите кнопку ниже, чтобы подтвердить и закрыть этот тикет!**"
        ),
        "btn_accepted_invite": "Я принял приглашение",
        "confirm_delete_msg": "🎉 **Поздравляем! Добро пожаловать в клан!** Этот канал будет удален через 5 секунд.",
        "staff_permission_err": "❌ Только персонал может одобрять заявки.",
        "close_permission_err": "❌ У вас нет прав для закрытия этого тикета.",
        "closing_msg": "🔒 **Закрытие тикета...** Этот канал будет удален через 5 секунд."
    }
}

# Helper functions to manage the ticket state in channel topics
def parse_topic_state(topic: str):
    """
    Parses key-value pairs stored in the channel topic.
    Format: Key: Value | Key2: Value2
    """
    if not topic:
        return {}
    state = {}
    parts = topic.split(" | ")
    for part in parts:
        if ":" in part:
            key, val = part.split(":", 1)
            state[key.strip().lower()] = val.strip()
    return state

def format_topic_state(user_id, roblox_username="Not Provided", weekly_contrib="Not Provided", status="Awaiting Details", lang="en", image_url=None):
    """Formats key-value pairs into a string for the channel topic."""
    topic = f"User ID: {user_id} | Roblox: {roblox_username} | Contribution: {weekly_contrib} | Status: {status} | Lang: {lang}"
    if image_url:
        topic += f" | Image: {image_url}"
    return topic

async def edit_channel_topic_safe(channel, topic):
    """Asynchronously attempts to edit channel topic without blocking the bot's execution flow if rate limited."""
    try:
        await channel.edit(topic=topic)
        logger.info(f"Successfully updated topic for channel {channel.name}")
    except Exception as e:
        logger.warning(f"Non-critical: Failed to update channel topic for #{channel.name} due to Discord rate limits: {e}")

# ----------------- Auto Setup Helpers -----------------

async def get_or_create_ticket_category(guild):
    """Gets the configured ticket category or creates one named '🎟️ Tickets'."""
    category_id_str = os.getenv("TICKET_CATEGORY_ID")
    if category_id_str and category_id_str.isdigit() and category_id_str != "123456789012345678":
        category = guild.get_channel(int(category_id_str))
        if category and isinstance(category, discord.CategoryChannel):
            return category

    # Fallback to name search
    category = discord.utils.get(guild.categories, name="🎟️ Tickets")
    if not category:
        try:
            category = await guild.create_category(name="🎟️ Tickets")
            logger.info(f"Created category '🎟️ Tickets' in guild '{guild.name}'")
        except Exception as e:
            logger.error(f"Failed to create category '🎟️ Tickets': {e}")
    return category

async def get_or_create_staff_role(guild):
    """Gets the configured staff role or creates one named 'Ticket Support'."""
    staff_role_id_str = os.getenv("STAFF_ROLE_ID")
    if staff_role_id_str and staff_role_id_str.isdigit() and staff_role_id_str != "123456789012345678":
        role = guild.get_role(int(staff_role_id_str))
        if role:
            return role

    # Fallback to name search
    role = discord.utils.get(guild.roles, name="Ticket Support")
    if not role:
        try:
            role = await guild.create_role(
                name="Ticket Support",
                color=discord.Color.blue(),
                reason="Auto-created by Ticket Bot for staff review permissions."
            )
            logger.info(f"Created role 'Ticket Support' in guild '{guild.name}'")
        except Exception as e:
            logger.error(f"Failed to create role 'Ticket Support': {e}")
    return role

async def get_or_create_log_channel(guild):
    """Gets the configured log channel or creates one named 'ticket-logs' inside the ticket category."""
    log_channel_id_str = os.getenv("LOG_CHANNEL_ID")
    if log_channel_id_str and log_channel_id_str.isdigit() and log_channel_id_str != "123456789012345678":
        if log_channel_id_str != os.getenv("TICKET_CATEGORY_ID"):
            channel = guild.get_channel(int(log_channel_id_str))
            if channel and isinstance(channel, discord.TextChannel):
                return channel

    # Fallback to name search
    channel = discord.utils.get(guild.text_channels, name="ticket-logs")
    if not channel:
        try:
            category = await get_or_create_ticket_category(guild)
            staff_role = await get_or_create_staff_role(guild)
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            channel = await guild.create_text_channel(
                name="ticket-logs",
                category=category,
                overwrites=overwrites,
                reason="Auto-created by Ticket Bot to output approval history."
            )
            logger.info(f"Created log channel 'ticket-logs' in guild '{guild.name}'")
        except Exception as e:
            logger.error(f"Failed to create log channel 'ticket-logs': {e}")
    return channel

async def get_or_create_verified_role(guild):
    """Gets the configured verified role or creates one named 'MyPvP Member'."""
    verified_role_id_str = os.getenv("VERIFIED_ROLE_ID")
    if verified_role_id_str and verified_role_id_str.isdigit() and verified_role_id_str != "123456789012345678":
        if verified_role_id_str != os.getenv("TICKET_CATEGORY_ID"):
            role = guild.get_role(int(verified_role_id_str))
            if role:
                return role

    # Fallback to name search
    role = discord.utils.get(guild.roles, name="MyPvP Member")
    if not role:
        try:
            role = await guild.create_role(
                name="MyPvP Member",
                color=discord.Color.green(),
                reason="Auto-created by Ticket Bot to assign to approved clan members."
            )
            logger.info(f"Created role 'MyPvP Member' in guild '{guild.name}'")
        except Exception as e:
            logger.error(f"Failed to create role 'MyPvP Member': {e}")
    return role

async def is_staff(interaction: discord.Interaction):
    """Checks if the user has staff permissions (Administrator or holds the staff role)."""
    if interaction.user.guild_permissions.administrator:
        return True
    
    staff_role = await get_or_create_staff_role(interaction.guild)
    if staff_role and staff_role in interaction.user.roles:
        return True
        
    return False

# ----------------- Logging and Lifecycle -----------------

async def log_ticket_action(guild, action, user, channel, roblox_username=None, weekly_contrib=None, staff=None, image_url=None):
    """Logs ticket events (creation, approval, closure) to the log channel."""
    log_channel = await get_or_create_log_channel(guild)
    if not log_channel:
        return

    embed = discord.Embed(
        title=f"📋 Clan Application {action}",
        color=discord.Color.green() if action == "Approved" else discord.Color.red() if action == "Closed" else discord.Color.blue()
    )
    
    user_val = f"{user.mention} ({user.name}#{user.discriminator or '0'})" if hasattr(user, 'mention') else str(user)
    embed.add_field(name="Applicant", value=user_val, inline=True)
    embed.add_field(name="Channel Name", value=channel.name, inline=True)
    
    if roblox_username:
        embed.add_field(name="Roblox Username", value=roblox_username, inline=True)
    if weekly_contrib:
        embed.add_field(name="Weekly Contribution", value=weekly_contrib, inline=False)
    if staff:
        embed.add_field(name="Staff/Reviewer", value=f"{staff.mention} ({staff.name})", inline=True)
    if image_url:
        embed.set_image(url=image_url)
        
    if hasattr(user, 'id'):
        embed.set_footer(text=f"User ID: {user.id}")
    embed.timestamp = discord.utils.utcnow()
    
    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        logger.error(f"Failed to send log message: {e}")

async def delete_channel_after_delay(channel, delay=5):
    """Deletes a channel after a short delay."""
    await asyncio.sleep(delay)
    try:
        await channel.delete(reason="Ticket channel closed/completed.")
        logger.info(f"Deleted ticket channel {channel.name}")
    except Exception as e:
        logger.error(f"Failed to delete channel {channel.name}: {e}")

async def handle_close_ticket(interaction: discord.Interaction):
    """Closes a ticket channel and logs the event."""
    channel = interaction.channel
    
    # Extract state from channel topic
    state = parse_topic_state(channel.topic) if hasattr(channel, "topic") and channel.topic else {}
    user_id_str = state.get("user id")
    lang = state.get("lang", "en")
    strings = LOCALIZATION[lang]
    
    is_creator = (user_id_str == str(interaction.user.id))
    has_permission = is_creator or await is_staff(interaction)

    if not has_permission:
        await interaction.response.send_message(strings["close_permission_err"], ephemeral=True)
        return

    # Acknowledge the interaction immediately to avoid channel edit rate limits blocking deletion
    await interaction.response.send_message(strings["closing_msg"])

    # Fetch roblox username and contribution details from memory or state
    details = interaction.client.ticket_usernames.get(channel.id)
    if details:
        roblox_username, weekly_contrib = details
    else:
        roblox_username = state.get("roblox")
        weekly_contrib = state.get("contribution")

    # Clean up memory state
    interaction.client.ticket_usernames.pop(channel.id, None)

    # Log ticket closure
    creator = None
    if user_id_str:
        try:
            creator = interaction.guild.get_member(int(user_id_str))
        except Exception:
            pass
    
    if not creator:
        class DummyUser:
            def __init__(self, uid):
                self.mention = f"<@{uid}>"
                self.name = f"User({uid})"
                self.discriminator = "0"
                self.id = uid
        creator = DummyUser(int(user_id_str)) if user_id_str else interaction.user

    await log_ticket_action(
        guild=interaction.guild,
        action="Closed",
        user=creator,
        channel=channel,
        roblox_username=roblox_username,
        weekly_contrib=weekly_contrib,
        staff=interaction.user
    )

    # Schedule channel deletion without blocking
    asyncio.create_task(delete_channel_after_delay(channel))

async def handle_lang_selection(interaction: discord.Interaction, lang: str):
    """Processes language selection, updates state, and renders localized welcomer."""
    channel = interaction.channel
    state = parse_topic_state(channel.topic) if hasattr(channel, "topic") and channel.topic else {}
    user_id_str = state.get("user id")

    if not user_id_str or user_id_str != str(interaction.user.id):
        await interaction.response.send_message("❌ Only the applicant can select the language.", ephemeral=True)
        return

    # Acknowledge and delete selection prompt
    await interaction.response.defer()
    try:
        await interaction.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete language select message: {e}")

    # Update topic language state asynchronously
    new_topic = format_topic_state(
        user_id=interaction.user.id,
        lang=lang
    )
    asyncio.create_task(edit_channel_topic_safe(channel, new_topic))

    # Send localized greeting
    strings = LOCALIZATION[lang]
    embed = discord.Embed(
        title=strings["welcome_title"],
        description=strings["welcome_desc"].format(mention=interaction.user.mention),
        color=discord.Color.gold()
    )
    embed.set_footer(text="Clan Application System • Powered by Antigravity")

    # Render view with localized labels
    view = TicketActionView(lang=lang)
    staff_role = await get_or_create_staff_role(interaction.guild)
    try:
        await channel.send(
            content=f"{interaction.user.mention} | {staff_role.mention if staff_role else ''}",
            embed=embed,
            view=view
        )
    except Exception as e:
        logger.error(f"Failed to send greeting message: {e}")

# ----------------- Persistent Views -----------------

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply to Clan", style=discord.ButtonStyle.success, emoji="⚔️", custom_id="ticket_panel:create")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild

        # Auto-fetch or create category and staff role
        category = await get_or_create_ticket_category(guild)
        if not category:
            await interaction.response.send_message(
                "❌ Ticket category channel could not be found or created. Please contact an administrator.",
                ephemeral=True
            )
            return

        # Check if the user already has an active ticket channel in this category
        existing_channel = None
        for channel in category.text_channels:
            if channel.topic:
                state = parse_topic_state(channel.topic)
                if state.get("user id") == str(interaction.user.id):
                    if state.get("status") != "Closed":
                        existing_channel = channel
                        break

        if existing_channel:
            await interaction.response.send_message(
                f"⚠️ You already have an open application: {existing_channel.mention}",
                ephemeral=True
            )
            return

        # Defer interaction to avoid timeout during channel creation
        await interaction.response.defer(ephemeral=True)

        staff_role = await get_or_create_staff_role(guild)

        # Set up ticket channel permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                attach_files=True,
                embed_links=True,
                read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True
            )
        }
        
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_messages=True,
                read_message_history=True
            )

        channel_name = f"apply-{interaction.user.name}"
        channel_name = "".join(c for c in channel_name if c.isalnum() or c in "-_").lower()

        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=format_topic_state(interaction.user.id)
            )
        except Exception as e:
            logger.error(f"Failed to create ticket channel: {e}")
            await interaction.followup.send(f"❌ Failed to create application ticket channel: {e}", ephemeral=True)
            return

        # Choose Language Embed
        lang_embed = discord.Embed(
            title="🌐 Language Selection / Выбор языка",
            description=(
                "Please select your preferred language below.\n\n"
                "Пожалуйста, выберите предпочитаемый язык ниже."
            ),
            color=discord.Color.blue()
        )
        
        view = LanguageSelectionView()
        try:
            await ticket_channel.send(
                content=f"{interaction.user.mention} | {staff_role.mention if staff_role else ''}",
                embed=lang_embed,
                view=view
            )
        except Exception as e:
            logger.error(f"Failed to send language selection message: {e}")

        # Log ticket creation
        await log_ticket_action(
            guild=guild,
            action="Created",
            user=interaction.user,
            channel=ticket_channel
        )

        await interaction.followup.send(
            f"✅ Application ticket created! Go to {ticket_channel.mention} to continue.",
            ephemeral=True
        )

class LanguageSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="English", style=discord.ButtonStyle.primary, emoji="🇺🇸", custom_id="lang_selection:en")
    async def select_en(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_lang_selection(interaction, "en")

    @discord.ui.button(label="Русский", style=discord.ButtonStyle.primary, emoji="🇷🇺", custom_id="lang_selection:ru")
    async def select_ru(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_lang_selection(interaction, "ru")

class ClanApplicationModal(discord.ui.Modal):
    def __init__(self, lang="en"):
        strings = LOCALIZATION[lang]
        super().__init__(title=strings["modal_title"])
        
        self.username_input = discord.ui.TextInput(
            label=strings["modal_roblox_lbl"],
            placeholder=strings["modal_roblox_placeholder"],
            style=discord.TextStyle.short,
            min_length=3,
            max_length=20,
            required=True
        )
        self.add_item(self.username_input)
        
        self.contribution_input = discord.ui.TextInput(
            label=strings["modal_contrib_lbl"],
            placeholder=strings["modal_contrib_placeholder"],
            style=discord.TextStyle.paragraph,
            min_length=3,
            max_length=150,
            required=True
        )
        self.add_item(self.contribution_input)

    async def on_submit(self, interaction: discord.Interaction):
        username = self.username_input.value.strip()
        contribution = self.contribution_input.value.strip()
        channel = interaction.channel
        
        if not hasattr(channel, "topic") or not channel.topic:
            await interaction.response.send_message("❌ This channel is not a valid ticket channel.", ephemeral=True)
            return

        state = parse_topic_state(channel.topic)
        user_id_str = state.get("user id")
        lang = state.get("lang", "en")
        strings = LOCALIZATION[lang]
        
        if not user_id_str or user_id_str != str(interaction.user.id):
            await interaction.response.send_message("❌ Only the ticket creator can submit their Roblox username.", ephemeral=True)
            return

        # Save details in-memory to prevent rate-limit blocking on screenshot uploads
        interaction.client.ticket_usernames[channel.id] = (username, contribution)

        # Asynchronously update topic status (attempt persistence, non-blocking)
        new_topic = format_topic_state(
            user_id=interaction.user.id,
            roblox_username=username,
            weekly_contrib=contribution,
            status="Awaiting Screenshot",
            lang=lang
        )
        asyncio.create_task(edit_channel_topic_safe(channel, new_topic))

        embed = discord.Embed(
            title=strings["details_submitted_title"],
            description=strings["details_submitted_desc"].format(username=username, contribution=contribution),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

class TicketActionView(discord.ui.View):
    def __init__(self, lang="en"):
        super().__init__(timeout=None)
        strings = LOCALIZATION[lang]
        self.enter_nickname.label = strings["btn_enter_details"]
        self.close_ticket.label = strings["btn_close_ticket"]

    @discord.ui.button(label="Enter Application Details", style=discord.ButtonStyle.primary, emoji="✍️", custom_id="ticket_action:enter_username")
    async def enter_nickname(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        state = parse_topic_state(channel.topic) if hasattr(channel, "topic") and channel.topic else {}
        user_id_str = state.get("user id")
        
        if not user_id_str or user_id_str != str(interaction.user.id):
            await interaction.response.send_message("❌ Only the ticket creator can submit their details.", ephemeral=True)
            return
            
        lang = state.get("lang", "en")
        modal = ClanApplicationModal(lang=lang)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_action:close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_close_ticket(interaction)

class AdminReviewView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Approve Application", style=discord.ButtonStyle.success, emoji="✅", custom_id="admin_review:approve")
    async def approve_verification(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        channel = interaction.channel
        
        if not await is_staff(interaction):
            await interaction.response.send_message("❌ Only staff can approve applications.", ephemeral=True)
            return

        state = parse_topic_state(channel.topic) if hasattr(channel, "topic") and channel.topic else {}
        user_id_str = state.get("user id")
        lang = state.get("lang", "en")
        strings = LOCALIZATION[lang]
        
        # Retrieve details from memory or state
        details = interaction.client.ticket_usernames.get(channel.id)
        if details:
            roblox_username, weekly_contrib = details
        else:
            roblox_username = state.get("roblox", "Not Provided")
            weekly_contrib = state.get("contribution", "Not Provided")
            
        image_url = state.get("image")

        # Defer interaction to avoid timeout
        await interaction.response.defer()

        # Clean up memory
        interaction.client.ticket_usernames.pop(channel.id, None)

        # Retrieve user and give role if configured
        creator = None
        role_assigned = False
        verified_role = await get_or_create_verified_role(guild)
        if user_id_str:
            try:
                creator_id = int(user_id_str)
                creator = guild.get_member(creator_id)
                if creator and verified_role:
                    await creator.add_roles(verified_role, reason="Clan application approved by staff")
                    role_assigned = True
            except Exception as e:
                logger.error(f"Error giving verified role: {e}")

        # Attempt to DM the user
        if creator and hasattr(creator, "send"):
            try:
                dm_embed = discord.Embed(
                    title=strings["approval_title"],
                    description=(
                        f"Congratulations! Your clan application for Roblox account **{roblox_username}** has been approved on the server **{guild.name}**.\n\n"
                        f"⚔️ **Next Step:** We have sent you a clan invitation in **Roblox Bedwars**. Please open the game and accept the invitation!"
                    ),
                    color=discord.Color.green()
                )
                await creator.send(embed=dm_embed)
                logger.info(f"Sent approval DM to user {creator.name}")
            except Exception as e:
                logger.warning(f"Could not send DM to user {creator.name}: {e}")

        # Send approval embed in the channel
        success_embed = discord.Embed(
            title=strings["approval_title"],
            description=(
                strings["approval_desc"].format(mention=creator.mention if creator else 'User', roblox_username=roblox_username) +
                (f"\n\nThe {verified_role.mention} role has been assigned to you." if role_assigned and verified_role else "")
            ),
            color=discord.Color.green()
        )
        view = ApplicantInviteView(lang=lang)
        await channel.send(content=creator.mention if creator else None, embed=success_embed, view=view)

        # Log approval
        await log_ticket_action(
            guild=guild,
            action="Approved",
            user=creator if creator else (user_id_str or "Unknown User"),
            channel=channel,
            roblox_username=roblox_username,
            weekly_contrib=weekly_contrib,
            staff=interaction.user,
            image_url=image_url
        )

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="admin_review:close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_close_ticket(interaction)

class ApplicantInviteView(discord.ui.View):
    def __init__(self, lang="en"):
        super().__init__(timeout=None)
        strings = LOCALIZATION[lang]
        self.accepted_invite.label = strings["btn_accepted_invite"]

    @discord.ui.button(label="I Accepted the Invite", style=discord.ButtonStyle.success, emoji="🎮", custom_id="applicant:accepted_invite")
    async def accepted_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        state = parse_topic_state(channel.topic) if hasattr(channel, "topic") and channel.topic else {}
        user_id_str = state.get("user id")
        lang = state.get("lang", "en")
        strings = LOCALIZATION[lang]
        
        if not user_id_str or user_id_str != str(interaction.user.id):
            await interaction.response.send_message("❌ Only the applicant can confirm they accepted the invitation.", ephemeral=True)
            return

        # Acknowledge and schedule channel deletion
        await interaction.response.send_message(strings["confirm_delete_msg"])
        asyncio.create_task(delete_channel_after_delay(channel, 5))

# ----------------- Client / Bot Definition -----------------

class TicketBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="t!", intents=intents)
        # Store usernames in memory to bypass topic editing 429 rate limit delays
        self.ticket_usernames = {}

    async def setup_hook(self):
        # Register persistent views on bot startup
        self.add_view(TicketPanelView())
        self.add_view(TicketActionView())
        self.add_view(AdminReviewView())
        self.add_view(ApplicantInviteView())
        self.add_view(LanguageSelectionView())
        
        # Guild-specific slash command sync
        guild_id_str = os.getenv("GUILD_ID")
        if guild_id_str:
            try:
                guild_id = int(guild_id_str)
                guild_obj = discord.Object(id=guild_id)
                self.tree.copy_global_to(guild=guild_obj)
                await self.tree.sync(guild=guild_obj)
                logger.info(f"Synced commands to guild {guild_id}")
            except ValueError:
                logger.warning("GUILD_ID is not a valid integer. Syncing commands globally.")
                await self.tree.sync()
        else:
            await self.tree.sync()
            logger.info("Synced commands globally")

    async def on_ready(self):
        logger.info(f"Bot connected as {self.user.name} ({self.user.id})")
        logger.info("Ticket bot is running and persistent views have been loaded.")

    async def on_message(self, message: discord.Message):
        # Ignore bot messages
        if message.author.bot:
            return

        channel = message.channel
        
        # Check if we are inside a ticket channel
        if not hasattr(channel, "topic") or not channel.topic:
            return

        state = parse_topic_state(channel.topic)
        user_id_str = state.get("user id")
        if not user_id_str:
            return  # Not a ticket channel

        # Check if the message is from the ticket creator
        if str(message.author.id) != user_id_str:
            return

        # Fetch details and language from memory or state
        lang = state.get("lang", "en")
        strings = LOCALIZATION[lang]
        details = self.ticket_usernames.get(channel.id)
        if details:
            roblox_username, weekly_contrib = details
        else:
            roblox_username = state.get("roblox", "Not Provided")
            weekly_contrib = state.get("contribution", "Not Provided")

        # If Roblox Username is still "Not Provided", prompt them to click the button first
        if roblox_username == "Not Provided":
            if message.attachments:
                await channel.send(
                    content=strings["username_first_warning"].format(mention=message.author.mention)
                )
            return

        # Filter image attachments
        image_attachments = [
            att for att in message.attachments 
            if att.content_type and att.content_type.startswith("image/")
        ]

        if not image_attachments:
            return

        attachment = image_attachments[0]

        # Update screenshot URL in topic asynchronously (non-blocking attempt)
        new_topic = format_topic_state(
            user_id=message.author.id,
            roblox_username=roblox_username,
            weekly_contrib=weekly_contrib,
            status="Under Review",
            lang=lang,
            image_url=attachment.url
        )
        asyncio.create_task(edit_channel_topic_safe(channel, new_topic))

        # Confirm receipt of details
        confirm_embed = discord.Embed(
            title=strings["stats_submitted_title"],
            description=strings["stats_submitted_desc"],
            color=discord.Color.gold()
        )
        await channel.send(embed=confirm_embed)

        # Notify staff for review (bilingual headers for staff clarity)
        staff_role = await get_or_create_staff_role(channel.guild)
        staff_role_mention = staff_role.mention if staff_role else "@here"

        review_embed = discord.Embed(
            title="⚔️ Clan Application Review Required / Требуется проверка заявки",
            description=f"User {message.author.mention} has submitted clan application details.",
            color=discord.Color.orange()
        )
        review_embed.add_field(name="Discord Account / Аккаунт", value=f"{message.author.mention} ({message.author})", inline=True)
        review_embed.add_field(name="Roblox Username / Никнейм", value=f"**{roblox_username}**", inline=True)
        review_embed.add_field(name="Weekly Contribution / Вклад", value=weekly_contrib, inline=False)
        review_embed.set_image(url=attachment.url)
        review_embed.set_footer(text=f"Ticket Channel: #{channel.name}")
        review_embed.timestamp = discord.utils.utcnow()

        review_view = AdminReviewView()
        try:
            await channel.send(content=f"🔔 {staff_role_mention}", embed=review_embed, view=review_view)
        except Exception as e:
            logger.error(f"Failed to send admin review message: {e}")

# Instantiate the bot
bot = TicketBot()

# ----------------- Commands -----------------

@bot.tree.command(name="setup_tickets", description="Sends the ticket creation panel to the current channel.")
@app_commands.default_permissions(administrator=True)
async def setup_tickets_command(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title="📩 Clan Application Portal / Портал заявок в клан",
        description=(
            "Welcome! If you want to join our Roblox Bedwars clan, please create an application ticket.\n\n"
            "Добро пожаловать! Если вы хотите вступить в наш клан по Roblox Bedwars, пожалуйста, создайте тикет заявки.\n\n"
            "👉 Click the button below / Нажмите кнопку ниже"
        ),
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.set_footer(text="Clan Application System • Click below to start")
    
    view = TicketPanelView()
    await interaction.response.send_message("Ticket panel spawned!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

@bot.tree.command(name="close", description="Closes the ticket and deletes the channel.")
async def close_command(interaction: discord.Interaction):
    await handle_close_ticket(interaction)

# ----------------- Keep Alive Web Server (Render Hosting) -----------------

class KeepAliveHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is online.")

    # Override logging to avoid spamming the console
    def log_message(self, format, *args):
        pass

def run_web_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHTTPHandler)
    logger.info(f"Keep-alive web server listening on port {port}")
    server.serve_forever()

def self_ping():
    # Wait 30 seconds for the web server to start up completely
    time.sleep(30)
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        logger.info("self_ping: RENDER_EXTERNAL_URL environment variable is not set. Self-pinging is disabled.")
        return
    
    logger.info(f"self_ping: Started self-pinging loop for {url}")
    while True:
        try:
            with urllib.request.urlopen(url) as response:
                status = response.getcode()
                logger.info(f"self_ping: Successfully pinged self. HTTP Status: {status}")
        except Exception as e:
            logger.error(f"self_ping: Error pinging self: {e}")
        
        # Ping every 10 minutes (600 seconds) to prevent Render's 15 min sleep
        time.sleep(600)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        logger.error("DISCORD_TOKEN is missing or not configured in the environment file.")
    else:
        # Start web server thread
        threading.Thread(target=run_web_server, daemon=True).start()
        # Start self-pinging thread
        threading.Thread(target=self_ping, daemon=True).start()
        
        # Start bot
        bot.run(token)
