import discord
from discord.ext import commands
import random
import json
import os

# --- CẤU HÌNH HỆ THỐNG ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = "thien_thu_cac.json"

# Hệ thống cảnh giới (Từ Phàm Nhân tới Tiên Nhân)
CANH_GIOI = [
    "Phàm Nhân", "Luyện Khí", "Trúc Cơ", "Kim Đan", "Nguyên Anh", 
    "Hóa Thần", "Luyện Hư", "Hợp Thể", "Đại Thừa", "Độ Kiếp", "Tiên Nhân"
]

# Hệ thống phẩm cấp vũ khí
PHAM_CAP = {
    "Phàm": {"icon": "⚪", "weight": 60},
    "Linh": {"icon": "🟢", "weight": 25},
    "Bảo": {"icon": "🔵", "weight": 10},
    "Cổ": {"icon": "🟣", "weight": 4},
    "Thần": {"icon": "🟡", "weight": 1}
}

TEN_VK = ["Kiếm", "Đao", "Thương", "Cung", "Trượng", "Quạt", "Chuông"]

# --- QUẢN LÝ DỮ LIỆU ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_data = load_data()

# --- SỰ KIỆN CHÍNH ---
@bot.event
async def on_ready():
    print(f"=== {bot.user.name} ĐÃ XUẤT THẾ ===")

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    uid = str(message.author.id)
    # Cơ chế: Nhắn 1 tin là +1 tu vi liên tục
    if uid in user_data:
        user_data[uid]["tu_vi"] += 1
        save_data(user_data) # Lưu ngay lập tức
            
    await bot.process_commands(message)

# --- CÁC THẦN THÔNG (COMMANDS) ---

@bot.command()
async def nhapdao(ctx):
    """Khai mở linh căn"""
    uid = str(ctx.author.id)
    if uid not in user_data:
        user_data[uid] = {
            "name": ctx.author.name,
            "level": 0,
            "tu_vi": 0,
            "linh_thach": 100,
            "tui_do": {"trung": 0, "vu_khi": []}
        }
        save_data(user_data)
        await ctx.send(f"📜 Chúc mừng **{ctx.author.name}** đã cảm nhận được linh khí, bước vào con đường nghịch thiên cải mệnh!")
    else:
        await ctx.send("Đạo hữu đã là người trong giới tu chân rồi.")

@bot.command()
async def thongtin(ctx):
    """Kiểm tra tu vi và túi đồ"""
    uid = str(ctx.author.id)
    if uid not in user_data: return await ctx.send("Hãy dùng `!nhapdao` để bắt đầu.")
    
    data = user_data[uid]
    rank = CANH_GIOI[data["level"]]
    inv = data["tui_do"]
    
    embed = discord.Embed(title=f"Linh Bảng: {data['name']}", color=0x3498db)
    embed.add_field(name="Cảnh Giới", value=f"**{rank}**", inline=True)
    embed.add_field(name="Tu Vi", value=f"✨ {data['tu_vi']}", inline=True)
    embed.add_field(name="Linh Thạch", value=f"💎 {data['linh_thach']}", inline=True)
    
    # Hiển thị túi đồ
    vk_str = "\n".join([f"{v['pham']} {v['ten']}" for v in inv["vu_khi"]]) if inv["vu_khi"] else "Trống"
    embed.add_field(name="Túi Đồ", value=f"🥚 Trứng Dị Thú: {inv['trung']}\n⚔️ Vũ Khí:\n{vk_str}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def dokiep(ctx):
    """Đột phá lên cảnh giới mới"""
    uid = str(ctx.author.id)
    if uid not in user_data: return
    
    lv = user_data[uid]["level"]
    if lv >= len(CANH_GIOI) - 1:
        return await ctx.send("Đạo hữu đã đạt cấp Tiên Nhân, vạn cổ bất biến!")

    # Cần tu vi tăng dần theo cấp
    req = (lv + 1) * 200 
    if user_data[uid]["tu_vi"] < req:
        return await ctx.send(f"⚠️ Tu vi chưa đủ! Cần **{req}** (Hiện có: {user_data[uid]['tu_vi']})")

    # Tỷ lệ thành công
    rate = max(0.1, 0.8 - (lv * 0.08))
    
    if random.random() < rate:
        user_data[uid]["level"] += 1
        user_data[uid]["tu_vi"] = 0
        
        # Thưởng lên cấp
        lt_thuong = (lv + 1) * 500
        user_data[uid]["linh_thach"] += lt_thuong
        
        # Nhận trứng và vũ khí ngẫu nhiên
        user_data[uid]["tui_do"]["trung"] += 1
        
        plist = list(PHAM_CAP.keys())
        pweights = [PHAM_CAP[p]["weight"] for p in plist]
        pham_res = random.choices(plist, weights=pweights)[0]
        
        new_vk = {
            "ten": f"{random.choice(TEN_VK)} {CANH_GIOI[lv+1]}",
            "pham": PHAM_CAP[pham_res]["icon"]
        }
        user_data[uid]["tui_do"]["vu_khi"].append(new_vk)
        
        save_data(user_data)
        await ctx.send(f"⚡ **THÀNH CÔNG!** Đạo hữu đã đột phá lên **{CANH_GIOI[lv+1]}**!\n🎁 Thưởng: `{lt_thuong} Linh Thạch`, `1 Trứng Dị Thú` và Vũ khí `{new_vk['pham']} {new_vk['ten']}`")
    else:
        user_data[uid]["tu_vi"] = int(user_data[uid]["tu_vi"] * 0.5)
        save_data(user_data)
        await ctx.send(f"💀 **ĐỘ KIẾP THẤT BẠI!** Đạo hữu bị thiên lôi đánh trúng, mất nửa số tu vi.")

# --- KẾT THÚC ---
bot.run('YOUR_BOT_TOKEN_HERE')
