# ==============================
# مكتبات ديسكورد
# ==============================

import os
import discord
from discord.ext import commands
from discord import app_commands

from keep_alive import keep_alive


# ==============================
# مكتبات الصور
# ==============================

from PIL import Image, ImageDraw, ImageFont, ImageSequence

import io
import aiohttp


# ==============================
# الصلاحيات
# ==============================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True


# ==============================
# إنشاء البوت
# ==============================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ==============================
# آيديات الرتب
# ==============================

MALE_ROLE_ID = 1535217213001441310

FEMALE_ROLE_ID = 1535217212623949885

VERIFIED_ROLE_ID = 1535217213555089439


# ==============================
# آيدي روم الترحيب
# ==============================

WELCOME_CHANNEL_ID = 1523760707047391332


# ==============================
# آيدي الروم الصوتي AFK
# ==============================

VOICE_CHANNEL_ID = 1524099778861072444


# ==============================
# حفظ الدعوات
# ==============================

invites = {}


# ==============================
# عند تشغيل البوت
# ==============================

@bot.event
async def on_ready():

    # حفظ الدعوات
    for guild in bot.guilds:

        try:
            invites[guild.id] = await guild.invites()

        except discord.Forbidden:
            invites[guild.id] = []


    # مزامنة Slash Commands
    try:

        synced = await bot.tree.sync()

        print(
            f"تم مزامنة {len(synced)} أمر Slash"
        )

    except Exception as e:

        print(
            f"خطأ في مزامنة الأوامر: {e}"
        )


    # ==============================
    # دخول روم AFK
    # ==============================

    try:

        voice_channel = await bot.fetch_channel(
            VOICE_CHANNEL_ID
        )


        if isinstance(
            voice_channel,
            discord.VoiceChannel
        ):


            if voice_channel.guild.voice_client is None:

                await voice_channel.connect()

                print(
                    f"✅ دخلت الروم الصوتي: {voice_channel.name}"
                )


            else:

                print(
                    "✅ البوت موجود بالفعل في الروم الصوتي"
                )


        else:

            print(
                "❌ الآيدي ليس روم صوتي"
            )


    except Exception as e:

        print(
            f"❌ خطأ دخول الفويس: {e}"
        )


    print(
        f"{bot.user} شغال!"
    )

# ==============================
# أمر التحقق القديم !verify
# ==============================

@bot.command()
async def verify(ctx):

    await ctx.send(
        "اختر جنسك:",
        view=GenderButtons()
    )


# ==================================================
# أمر /kick
# يعمل فقط لمن لديه Administrator
# ==================================================

@bot.tree.command(
    name="kick",
    description="طرد عضو من السيرفر"
)
@app_commands.checks.has_permissions(
    administrator=True
)
@app_commands.describe(
    member="العضو الذي تريد طرده",
    reason="سبب الطرد"
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "بدون سبب"
):

    try:

        await member.kick(
            reason=reason
        )

        await interaction.response.send_message(
            f"👢 تم طرد {member.mention}\n"
            f"📝 السبب: {reason}"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ ما أقدر أطرد هذا العضو. تأكد أن رتبة البوت أعلى من رتبته.",
            ephemeral=True
        )


# ==================================================
# أمر /ban
# يعمل فقط لمن لديه Administrator
# ==================================================

@bot.tree.command(
    name="ban",
    description="حظر عضو من السيرفر"
)
@app_commands.checks.has_permissions(
    administrator=True
)
@app_commands.describe(
    member="العضو الذي تريد حظره",
    reason="سبب الحظر"
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "بدون سبب"
):

    try:

        await member.ban(
            reason=reason
        )

        await interaction.response.send_message(
            f"🔨 تم حظر {member.mention}\n"
            f"📝 السبب: {reason}"
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ ما أقدر أحظر هذا العضو. تأكد أن رتبة البوت أعلى من رتبته.",
            ephemeral=True
        )


# ==================================================
# أمر /clear
# يعمل فقط لمن لديه Administrator
# ==================================================

@bot.tree.command(
    name="clear",
    description="حذف عدد من الرسائل"
)
@app_commands.checks.has_permissions(
    administrator=True
)
@app_commands.describe(
    amount="عدد الرسائل التي تريد حذفها"
)
async def clear(
    interaction: discord.Interaction,
    amount: app_commands.Range[int, 1, 100]
):

    await interaction.response.send_message(
        f"🧹 جاري حذف {amount} رسالة...",
        ephemeral=True
    )


    try:

        deleted = await interaction.channel.purge(
            limit=amount
        )


        await interaction.edit_original_response(
            content=f"✅ تم حذف {len(deleted)} رسالة."
        )


    except discord.Forbidden:

        await interaction.edit_original_response(
            content="❌ البوت لا يملك صلاحية حذف الرسائل."
        )


# ==================================================
# معالجة أخطاء أوامر Slash
# ==================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    if isinstance(
        error,
        app_commands.MissingPermissions
    ):

        if interaction.response.is_done():

            await interaction.followup.send(
                "❌ هذا الأمر للإداريين فقط.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ هذا الأمر للإداريين فقط.",
                ephemeral=True
            )

        return


    print(
        f"Slash Command Error: {error}"
    )
    # ==============================
# الترحيب عند دخول عضو جديد
# ==============================

@bot.event
async def on_member_join(member):

    channel = member.guild.get_channel(
        WELCOME_CHANNEL_ID
    )

    if channel is None:
        return


    frames = []


    # فتح الخلفية المتحركة
    background = Image.open(
        "VV2.gif"
    )


    # تحميل أفتار العضو
    async with aiohttp.ClientSession() as session:

        async with session.get(
            member.display_avatar.url
        ) as resp:

            avatar_bytes = await resp.read()


    avatar = Image.open(
        io.BytesIO(avatar_bytes)
    ).convert("RGBA")


    avatar = avatar.resize(
        (220, 220)
    )


    mask = Image.new(
        "L",
        (220, 220),
        0
    )

    mask_draw = ImageDraw.Draw(mask)

    mask_draw.ellipse(
        (0, 0, 220, 220),
        fill=255
    )


    border = Image.new(
        "RGBA",
        (240, 240),
        (0, 0, 0, 0)
    )

    border_draw = ImageDraw.Draw(border)

    border_draw.ellipse(
        (5, 5, 235, 235),
        outline=(75, 0, 130, 255),
        width=8
    )


    try:

        font = ImageFont.truetype(
            "arialbd.ttf",
            70
        )

        small_font = ImageFont.truetype(
            "arialbd.ttf",
            45
        )

    except:

        font = None
        small_font = None


    inviter = "غير معروف"


    old_invites = invites.get(
        member.guild.id,
        []
    )


    try:

        new_invites = await member.guild.invites()

    except discord.Forbidden:

        new_invites = []


    for old in old_invites:

        for new in new_invites:

            if (
                old.code == new.code
                and new.uses > old.uses
            ):

                if new.inviter:

                    inviter = new.inviter.mention

                break


    invites[member.guild.id] = new_invites


    for frame in ImageSequence.Iterator(background):

        img = frame.convert("RGBA")

        img = img.resize(
            (1261, 709)
        )


        img.paste(
            avatar,
            (520, 100),
            mask
        )


        img.paste(
            border,
            (510, 90),
            border
        )


        draw = ImageDraw.Draw(img)


        draw.text(
            (630, 390),
            f"👋 {member.name}",
            anchor="mm",
            font=font,
            fill=(255, 255, 255)
        )


        draw.text(
            (630, 470),
            "Welcome To Server ✨",
            anchor="mm",
            font=small_font,
            fill=(75, 0, 130)
        )


        frames.append(img)



    with io.BytesIO() as gif_binary:

        frames[0].save(
            gif_binary,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=background.info.get(
                "duration",
                80
            ),
            loop=0
        )


        gif_binary.seek(0)


        file = discord.File(
            gif_binary,
            filename="welcome.gif"
        )


        await channel.send(
            f"👋 أهلاً بك {member.mention} في السيرفر ✨\n"
            f"📨 تمت دعوتك بواسطة: {inviter}",
            file=file
        )



# ==============================
# تشغيل البوت
# ==============================

keep_alive()

bot.run(
    os.getenv("TOKEN")
)

