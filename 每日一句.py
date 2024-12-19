import json
import requests
import datetime
import asyncio
import threading
from tkinter import ttk, font
import ttkbootstrap
from PIL import Image, ImageTk
from io import BytesIO
'''
author:https://github.com/ashajia
DateTime: 20241219
'''

# 从API获取数据
def get_data_from_api(url, headers):
    resp = requests.get(url, headers=headers)
    return json.loads(resp.text)

# 获取当前IP地址的地理位置
def get_current_location():
    try:
        response = requests.get("https://www.ip.cn/api/index?ip&type=0")
        data = response.json()
        return data["address"], data["ip"]
    except requests.exceptions.RequestException as e:
        return "YOUR_LOCATION", "UNKNOWN_IP"

# 获取天气数据
def get_weather_data(location):
    url = f"http://api.weatherapi.com/v1/current.json?key=bc13f1efff5c4cbb92b114158241912&q={location}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers)
        data = json.loads(resp.text)
        location = data["location"]["name"]
        temp_c = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]
        icon_url = data["current"]["condition"]["icon"]
        return location, temp_c, condition, icon_url
    except requests.exceptions.RequestException as e:
        return None, None, f"请求失败: {str(e)}", None

# 调整图片大小
def resize_image(image, max_size):
    width, height = image.size
    if width > height:
        new_width = max_size[0]
        new_height = int(height * (max_size[0] / width))
    else:
        new_height = max_size[1]
        new_width = int(width * (max_size[1] / height))
    return image.resize((new_width, new_height))

# 创建主窗口
window = ttkbootstrap.Window(
    title="每日一句 https://github.com/ashajia", themename="solar", size=(550, 750), position=(100, 100), 
    minsize=(0, 0), maxsize=(1920, 1080), resizable=None, alpha=0.8, hdpi=True
)

# 创建状态标签
status_label = ttk.Label(window, text="", wraplength=500)
status_label.place(relx=0.5, rely=0.5, anchor="center")

# 初始化图片变量
image = None
photo = None
icon_photo = None
hot_image = None
hot_photo = None

# 显示图片 https://github.com/ashajia
image_label = ttk.Label(window)
image_label.pack(side="bottom")

# 显示热榜图片的弹窗
def show_hot_image_popup(hot_photo):
    popup = ttkbootstrap.Toplevel(window)
    popup.title("当前热榜 https://github.com/ashajia")
    
    # 获取屏幕尺寸
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    
    # 设置弹窗大小为图片大小
    window_width = hot_photo.width()
    window_height = hot_photo.height()
    
    # 计算弹窗位置使其居中
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 显示图片
    image_label = ttk.Label(popup, image=hot_photo)
    image_label.pack(expand=True, fill="both")
    
    # 添加关闭按钮
    close_button = ttk.Button(popup, text="关闭", command=popup.destroy)
    close_button.pack(pady=5)
    
    # 设置焦点并将窗口置顶
    popup.focus_force()
    popup.transient(window)
    popup.grab_set()

# 更新数据
async def update_data():
    global image, photo, icon_photo
    url = "http://open.iciba.com/dsapi/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }
    today = datetime.date.today()
    day_of_week = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]
    time = datetime.datetime.now().strftime(f"%Y年%m月%d日 {day_of_week} %H:%M:%S")
    
    try:
        # 显示加载中提示
        status_label.config(text="加载中……")
        window.update_idletasks()
        
        # 获取API数据
        data = await asyncio.to_thread(get_data_from_api, url, headers)
        content = data["content"] + "\n" + data["note"]
        lines = content.split('\n')

        # 清空内容框架中的所有子组件
        window.after(0, lambda: [widget.destroy() for widget in content_frame.winfo_children()])

        # 隐藏状态标签
        status_label.config(text="")
        
        # 显示当前时间
        window.after(0, lambda: ttk.Label(content_frame, text=f"今天是 {time}", font=font_obj).pack(anchor='w'))
        window.after(0, lambda: ttk.Separator(content_frame, orient='horizontal').pack(fill='x', pady=5))  # 修改间隔
        # 显示内容
        for line in lines:
            window.after(0, lambda line=line: ttk.Label(content_frame, text=line, font=font_obj, wraplength=500).pack(anchor='w'))
            window.after(0, lambda: ttk.Separator(content_frame, orient='horizontal').pack(fill='x', pady=1))  # 修改间隔
        
        # 获取当前IP地址的地理位置
        location, ip_address = await asyncio.to_thread(get_current_location)
        # 获取天气数据
        location, temp_c, condition, icon_url = await asyncio.to_thread(get_weather_data, location)
        if location:
            # 显示当前IP地址的地理位置
            window.after(0, lambda: ttk.Label(content_frame, text=f"位置: {location}", font=font_obj).pack(anchor='w'))
            window.after(0, lambda: ttk.Label(content_frame, text=f"当前的IP: {ip_address}", font=font_obj).pack(anchor='w'))
            window.after(0, lambda: ttk.Separator(content_frame, orient='horizontal').pack(fill='x', pady=5))  # 修改间隔
            
            # 创建左右两栏框架
            weather_frame = ttk.Frame(content_frame)
            window.after(0, lambda: weather_frame.pack(fill='x', pady=5))
            
            # 左侧文字信息
            text_frame = ttk.Frame(weather_frame)
            window.after(0, lambda: text_frame.pack(side='left', fill='both', expand=True))
            window.after(0, lambda: ttk.Label(text_frame, text=f"温度: {temp_c}°C", font=font_obj).pack(anchor='w'))
            window.after(0, lambda: ttk.Label(text_frame, text=f"天气: {condition}", font=font_obj).pack(anchor='w'))
            
            # 右侧图标
            icon_image = Image.open(BytesIO(requests.get(f"http:{icon_url}", headers=headers).content))
            icon_image = resize_image(icon_image, (128, 128))
            icon_photo = ImageTk.PhotoImage(icon_image)
            window.after(0, lambda: ttk.Label(weather_frame, image=icon_photo).pack(side='right', fill='both', expand=True, padx=10))
        else:
            window.after(0, lambda: ttk.Label(content_frame, text=f"天气数据获取失败: {condition}", font=font_obj).pack(anchor='w'))
        
        # 获取并调整图片大小
        image = await asyncio.to_thread(resize_image, Image.open(BytesIO(requests.get(data["picture"], headers=headers).content)), (600, 600))
        # 将PIL图像对象转换为Tkinter可用的PhotoImage对象
        photo = ImageTk.PhotoImage(image)
        # 更新image_label的图像
        window.after(0, lambda: image_label.config(image=photo))
    except requests.exceptions.RequestException as e:
        status_label.config(text=f"请求失败: {str(e)}")

# 获取热榜图片
async def get_hot_image():
    global hot_image, hot_photo
    try:
        # 构建URL
        url = "https://api.pearktrue.cn/api/60s/image/hot/?type=baidu"
        
        # 显示加载提示
        status_label.config(text="正在加载热榜...")
        window.update_idletasks()
        
        # 获取实际图片URL（处理302跳转）
        response = await asyncio.to_thread(requests.get, url, allow_redirects=True)
        actual_image_url = response.url
        
        # 获取图片
        image_response = await asyncio.to_thread(requests.get, actual_image_url)
        hot_image = Image.open(BytesIO(image_response.content))
        
        # 调整图片大小以适应屏幕（保持宽高比）
        screen_height = window.winfo_screenheight() - 100  # 留出一些边距
        if hot_image.height > screen_height:
            ratio = screen_height / hot_image.height
            new_width = int(hot_image.width * ratio)
            hot_image = hot_image.resize((new_width, screen_height), Image.Resampling.LANCZOS)
            
        hot_photo = ImageTk.PhotoImage(hot_image)
        
        # 在弹窗中显示图片
        window.after(0, lambda: show_hot_image_popup(hot_photo))
        status_label.config(text="")
    except Exception as e:
        status_label.config(text=f"获取热榜失败: {str(e)}")

# 热榜按钮点击事件
def show_hot_news():
    threading.Thread(target=lambda: asyncio.run(get_hot_image())).start()

# 创建内容框架
content_frame = ttk.Frame(window, padding=10)
content_frame.pack(fill="both", expand=True)

# 设置字体
font_obj = font.Font(size=11)  

# 创建刷新按钮和更新函数
def refresh_data():
    status_label.config(text="加载中……")
    window.update_idletasks()
    threading.Thread(target=lambda: asyncio.run(update_data())).start()

refresh_button = ttk.Button(window, text="刷新", command=refresh_data, style="TButton")
refresh_button.place(relx=0.95, rely=0.05, anchor="ne")

# 创建热榜按钮 https://github.com/ashajia
hot_button = ttk.Button(window, text="查看当前热榜", command=show_hot_news, style="TButton")
hot_button.pack(side="bottom", pady=5)

# 启动异步更新数据
def start_update_data():
    status_label.config(text="加载中……")
    window.update_idletasks()
    threading.Thread(target=lambda: asyncio.run(update_data())).start()

window.after(100, start_update_data)

# 运行主循环
window.mainloop()
