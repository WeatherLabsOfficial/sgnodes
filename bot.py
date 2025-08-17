import discord
from discord.ext import commands
from utils import generate_vps_id, generate_ssh_credentials, load_data, save_data
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

with open('config.json') as f:
    config = json.load(f)
ADMIN_ID = str(config['admin_id'])

data = load_data()

def has_access(user_id):
    return str(user_id) in data['access'] or str(user_id) == ADMIN_ID

# -------- /deploy COMMAND --------
@bot.command()
async def deploy(ctx, target_user: discord.Member, ram:int, cpu:int, disk:int, expiry_days:int):
    if not has_access(ctx.author.id):
        await ctx.send("🚫 You don't have access to deploy VPS.")
        return

    vps_id = generate_vps_id()
    ssh_user, user_pass = generate_ssh_credentials()
    root_pass = generate_ssh_credentials()[1]
    tmate_session = f"ssh {generate_vps_id()}@lon1.tmate.io"
    vps_ip = "<server-ip>"  # Customize: replace with real VPS IP

    data['vps'][vps_id] = {
        "user_id": str(target_user.id),
        "ram": ram,
        "cpu": cpu,
        "disk": disk,
        "ssh_user": ssh_user,
        "user_pass": user_pass,
        "root_pass": root_pass,
        "tmate": tmate_session,
        "expiry": expiry_days
    }
    save_data(data)

    await ctx.send(f"✅ VPS Deployed! ID: `{vps_id}`")

    # Send rich DM to user
    try:
        vps_message = (
            f"🎉 **SG Nodes VPS Creation Successful**\n"
            f"🆔 **VPS ID:** {vps_id}\n"
            f"💾 **Memory:** {ram}GB\n"
            f"⚡ **CPU:** {cpu} cores\n"
            f"💿 **Disk:** {disk}GB\n"
            f"👤 **Username:** {ssh_user}\n"
            f"🔑 **User Password:** {user_pass}\n"
            f"🔑 **Root Password:** {root_pass}\n"
            f"🔒 **Tmate Session:** {tmate_session}\n"
            f"🔌 **Direct SSH:** ssh {ssh_user}@{vps_ip}\n"
            f"ℹ️ **Note:** This is a SG Nodes VPS instance. You can install and configure additional packages as needed."
        )
        await target_user.send(vps_message)
    except:
        await ctx.send(f"⚠️ Could not DM {target_user.name}, make sure they allow DMs.")

# -------- /addaccess COMMAND --------
@bot.command()
async def addaccess(ctx, member: discord.Member):
    if str(ctx.author.id) != ADMIN_ID:
        await ctx.send("🚫 Only admin can add access.")
        return
    if str(member.id) not in data['access']:
        data['access'].append(str(member.id))
        save_data(data)
        await ctx.send(f"✅ {member.name} now has deploy access.")
    else:
        await ctx.send("⚠️ User already has access.")

# -------- /managevps COMMAND (basic) --------
@bot.command()
async def managevps(ctx, vps_id):
    if vps_id not in data['vps']:
        await ctx.send("❌ VPS ID not found.")
        return

    vps = data['vps'][vps_id]
    if str(ctx.author.id) != vps['user_id'] and str(ctx.author.id) != ADMIN_ID:
        await ctx.send("🚫 You don't own this VPS.")
        return

    options = ["Restart", "Stop", "Reinstall", "Backup"]
    await ctx.send(f"VPS `{vps_id}` options: {', '.join(options)}")

# You can similarly add /delete, /deleteall, /forcedelete, /forcedeleteall, /regenssh, /node, /adminnode

bot.run(config['token'])
