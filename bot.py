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
# أمر دخول الفويس
# ==============================

@bot.tree.command(
    name="join",
    description="دخول رومك الصوتي"
)
async def join(
    interaction: discord.Interaction
):

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "❌ ادخل روم صوتي أولاً",
            ephemeral=True
        )
        return


    channel = interaction.user.voice.channel


    if interaction.guild.voice_client is None:

        await channel.connect()

        await interaction.response.send_message(
            f"✅ دخلت روم: {channel.name}"
        )


    else:

        await interaction.guild.voice_client.move_to(
            channel
        )

        await interaction.response.send_message(
            "✅ تم نقل البوت للروم"
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
# آيدي الروم الصوتي
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



    # مزامنة الأوامر

    try:

        synced = await bot.tree.sync()

        print(
            f"تم مزامنة {len(synced)} أمر Slash"
        )


    except Exception as e:

        print(
            f"خطأ مزامنة الأوامر: {e}"
        )



    # دخول الروم الصوتي تلقائي

    try:

        voice_channel = bot.get_channel(
            VOICE_CHANNEL_ID
        )


        if voice_channel is None:

            print(
                "❌ لم أجد روم الفويس"
            )

            return



        if voice_channel.guild.voice_client is None:

            await voice_channel.connect()

            print(
                f"✅ دخلت الفويس: {voice_channel.name}"
            )


        else:

            print(
                "✅ البوت موجود في الفويس"
            )


    except Exception as e:

        print(
            f"❌ خطأ دخول الفويس: {e}"
        )



    print(
        f"{bot.user} شغال!"
    )

# ==============================
# أمر التحقق !verify
# ==============================

@bot.command()
async def verify(ctx):

    await ctx.send(
        "اختر جنسك:",
        view=GenderButtons()
    )



# ==================================================
# أمر /kick
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
            "❌ لا أستطيع طرد هذا العضو.",
            ephemeral=True
        )



# ==================================================
# أمر /ban
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
            "❌ لا أستطيع حظر هذا العضو.",
            ephemeral=True
        )



# ==================================================
# أمر /clear
# ==================================================

@bot.tree.command(
    name="clear",
    description="حذف الرسائل"
)
@app_commands.checks.has_permissions(
    administrator=True
)
@app_commands.describe(
    amount="عدد الرسائل"
)
async def clear(
    interaction: discord.Interaction,
    amount: app_commands.Range[int,1,100]
):

    await interaction.response.send_message(
        "🧹 جاري الحذف...",
        ephemeral=True
    )


    try:

        deleted = await interaction.channel.purge(
            limit=amount
        )


        await interaction.edit_original_response(
            content=f"✅ تم حذف {len(deleted)} رسالة"
        )


    except discord.Forbidden:

        await interaction.edit_original_response(
            content="❌ لا توجد صلاحية حذف"
        )



# ==================================================
# معالجة أخطاء السلاش
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
                "❌ هذا الأمر للإداريين فقط",
                ephemeral=True
            )


        else:

            await interaction.response.send_message(
                "❌ هذا الأمر للإداريين فقط",
                ephemeral=True
            )


        return



    print(
        f"Slash Error: {error}"
    )



# ==============================
# الترحيب عند دخول عضو
# ==============================

@bot.event
async def on_member_join(member):

    channel = member.guild.get_channel(
        WELCOME_CHANNEL_ID
    )


    if channel is None:

        return



    frames = []


    background = Image.open(
        "VV2.gif"
    )



    async with aiohttp.ClientSession() as session:


        async with session.get(
            member.display_avatar.url
        ) as resp:


            avatar_bytes = await resp.read()



    avatar = Image.open(
        io.BytesIO(avatar_bytes)
    ).convert("RGBA")



    avatar = avatar.resize(
        (220,220)
    )



    mask = Image.new(
        "L",
        (220,220),
        0
    )


    ImageDraw.Draw(mask).ellipse(
        (0,0,220,220),
        fill=255
    )



    border = Image.new(
        "RGBA",
        (240,240),
        (0,0,0,0)
    )


    ImageDraw.Draw(border).ellipse(
        (5,5,235,235),
        outline=(75,0,130,255),
        width=8
    )
    # ==============================
    # الخطوط
    # ==============================

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



    # ==============================
    # معرفة صاحب الدعوة
    # ==============================

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



    # ==============================
    # تجهيز الفريمات
    # ==============================

    for frame in ImageSequence.Iterator(
        background
    ):


        img = frame.convert(
            "RGBA"
        )


        img = img.resize(
            (1261,709)
        )



        img.paste(
            avatar,
            (520,100),
            mask
        )


        img.paste(
            border,
            (510,90),
            border
        )



        draw = ImageDraw.Draw(
            img
        )



        draw.text(
            (630,390),
            f"👋 {member.name}",
            anchor="mm",
            font=font,
            fill=(255,255,255)
        )



        draw.text(
            (630,470),
            "Welcome To Server ✨",
            anchor="mm",
            font=small_font,
            fill=(75,0,130)
        )



        frames.append(
            img
        )



    # ==============================
    # حفظ GIF
    # ==============================

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
            f"👋 أهلاً بك {member.mention} ✨\n"
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
