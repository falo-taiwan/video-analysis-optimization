import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

def draw_star(draw, x, y, size, color):
    """在指定位置繪製一個多角爆炸星形體"""
    points = []
    num_points = 8
    for i in range(num_points * 2):
        angle = i * math.pi / num_points
        r = size if i % 2 == 0 else size / 2
        px = x + r * math.cos(angle)
        py = y + r * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, fill=color)

def create_poc_gif(output_path):
    print("正在重新生成更直覺的「智慧動態抽樣與補幀」圖形化動畫...")
    
    frames = []
    width, height = 640, 360
    
    # 候選中文字型路徑
    font_paths = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    ]
    
    font_title = None
    font_sub = None
    font_mono = None
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                font_title = ImageFont.truetype(path, 16)
                font_sub = ImageFont.truetype(path, 12)
                font_mono = ImageFont.truetype(path, 10)
                break
            except:
                continue

    if font_title is None:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_mono = ImageFont.load_default()

    total_frames = 80

    for i in range(total_frames):
        img = Image.new("RGB", (width, height), "#0B0F19")
        draw = ImageDraw.Draw(img)
        
        # 1. 頂部標題與作者
        draw.text((20, 12), "方案一：動態視覺差抽樣 (Adaptive Sampling) 直觀演示", fill="#00F2FE", font=font_title)
        draw.text((480, 15), "Falo x Force Cheng", fill="#243049", font=font_sub)
        
        # 2. 監視器畫面模擬區 (50 - 170px)
        draw.rectangle([(20, 42), (620, 172)], outline="#243049", width=2)
        draw.text((30, 50), "CCTV: 國1南 30K+650", fill="#9CA3AF", font=font_mono)
        
        # 2.1 繪製公路與車道
        road_y1, road_y2 = 75, 145
        draw.rectangle([(20, road_y1), (620, road_y2)], fill="#1F2937") # 柏油路
        draw.line([(20, road_y1 + 4), (620, road_y1 + 4)], fill="#F59E0B", width=2) # 雙黃線
        draw.line([(20, road_y1 + 8), (620, road_y1 + 8)], fill="#F59E0B", width=2)
        
        for x_dash in range(20, 620, 40):
            draw.line([(x_dash, 110), (x_dash + 20, 110)], fill="#F3F4F6", width=1) # 車道虛線
            
        draw.line([(20, road_y2 - 6), (620, road_y2 - 6)], fill="#F3F4F6", width=2) # 路肩實線

        # 2.2 車輛動態與碰撞
        white_car_x = 440
        white_car_y = 113
        blue_car_x = 50 + int((white_car_x - 40 - 50) * (min(i, 30) / 30.0))
        blue_car_y = 113
        
        # 繪製白車
        draw.rectangle([(white_car_x, white_car_y), (white_car_x + 30, white_car_y + 14)], fill="#E5E7EB", outline="#9CA3AF")
        if i % 6 < 3:
            draw.ellipse([(white_car_x - 2, white_car_y), (white_car_x, white_car_y + 2)], fill="#F59E0B")
            draw.ellipse([(white_car_x + 30, white_car_y), (white_car_x + 32, white_car_y + 2)], fill="#F59E0B")
            draw.text((white_car_x - 5, white_car_y - 12), "故障車", fill="#F59E0B", font=font_mono)

        # 繪製藍車與碰撞
        if i < 30:
            draw.rectangle([(blue_car_x, blue_car_y), (blue_car_x + 30, blue_car_y + 14)], fill="#3B82F6", outline="#1D4ED8")
        else:
            # 碰撞起火
            draw_star(draw, white_car_x - 8, white_car_y + 7, 18, "#EF4444" if i % 4 < 2 else "#F59E0B")
            draw.rectangle([(white_car_x - 20, white_car_y + 2), (white_car_x + 10, white_car_y + 16)], fill="#3B82F6", outline="#1D4ED8")
            draw.text((white_car_x - 25, white_car_y - 14), "⚠️ 發生碰撞", fill="#EF4444", font=font_mono)

        # 拖吊車
        if i > 50:
            tow_x = 20 + int((white_car_x - 60 - 20) * (min(i - 50, 20) / 20.0))
            tow_y = 125
            draw.rectangle([(tow_x, tow_y), (tow_x + 38, tow_y + 14)], fill="#FBBF24", outline="#D97706")
            if i % 4 < 2:
                draw.ellipse([(tow_x + 8, tow_y - 3), (tow_x + 13, tow_y)], fill="#EF4444")

        # 字幕
        subtitle_y = 150
        draw.rectangle([(20, subtitle_y), (620, subtitle_y + 18)], fill="#0B0F19")
        if i < 30:
            sub_text = "[字幕] 前方中間車道有車輛故障停留，請注意避讓..."
            sub_col = "#9CA3AF"
        elif i >= 30 and i < 55:
            sub_text = "[字幕] ⚠️ 發生追撞！後方車流開始回堵，觸發補幀機制！"
            sub_col = "#EF4444"
        else:
            sub_text = "[字幕] 🚨 拖吊車進入現場處理，請配合減速慢行..."
            sub_col = "#F59E0B"
        draw.text((30, subtitle_y + 2), sub_text, fill=sub_col, font=font_sub)

        # 3. 中間：實時畫面變動量 (Motion Delta %) 折線圖 (180 - 245px)
        draw.rectangle([(20, 180), (620, 245)], outline="#243049", fill="#0E1420", width=1)
        draw.text((30, 185), "實時畫面變動率 (Motion Delta %)", fill="#9CA3AF", font=font_mono)
        
        # 繪製 15% 的補幀閾值線 (紅色虛線)
        thresh_y = 230 - int(50 * 0.20) # 20% threshold
        for x_dash in range(120, 610, 10):
            draw.line([(x_dash, thresh_y), (x_dash+5, thresh_y)], fill="#EF4444", width=1)
        draw.text((50, thresh_y - 6), "補幀閾值 (15%)", fill="#EF4444", font=font_mono)

        # 計算並繪製變動率折線
        delta_points = []
        for idx in range(total_frames):
            # 模擬變動率曲線
            if idx < 30:
                # 只有藍車在移動，變動率約為 5%
                val = 5 + math.sin(idx) * 2
            elif idx >= 30 and idx < 55:
                # 碰撞瞬間變動率暴增到 80%~95%
                val = 85 + math.cos(idx * 2) * 8
            else:
                # 事故後靜止，拖吊車慢速移動，變動率約為 8%
                val = 8 + math.sin(idx) * 2
                
            x_pos = 120 + int((610 - 120) * (idx / total_frames))
            y_pos = 235 - int(45 * (val / 100.0))
            delta_points.append((x_pos, y_pos))

        # 只繪製到目前幀 i 的折線
        if len(delta_points[:i+1]) > 1:
            draw.line(delta_points[:i+1], fill="#00F2FE", width=2)
            
        # 繪製目前時間的數值大字
        current_val = 5
        if i >= 30 and i < 55:
            current_val = int(85 + math.cos(i * 2) * 8)
        elif i >= 55:
            current_val = int(8 + math.sin(i) * 2)
        
        draw.text((530, 185), f"目前變動量: {current_val}%", fill="#00F2FE" if current_val < 15 else "#EF4444", font=font_sub)

        # 4. 下半部：擷取影格膠卷 (Filmstrip of Captured Frames) (255 - 330px)
        draw.text((20, 252), "系統影格擷取膠卷 (Captured Storyboard Filmstrip)", fill="#9CA3AF", font=font_mono)
        
        # 膠卷軌道底色
        draw.rectangle([(20, 267), (620, 315)], fill="#0E1420", outline="#243049")
        
        # 繪製已擷取的影格小方塊
        for history_i in range(i + 1):
            h_is_sample = False
            if history_i < 30:
                if history_i % 12 == 0: h_is_sample = True
            elif history_i >= 30 and history_i < 55:
                # 碰撞期間高頻率「補幀」
                if (history_i - 30) % 2 == 0: h_is_sample = True
            else:
                if (history_i - 55) % 12 == 0: h_is_sample = True
                
            if h_is_sample:
                # 依歷史點在膠卷上繪製小縮圖方塊
                t_x = 35 + int((590 - 50) * (history_i / total_frames))
                
                # 依階段上不同的顏色縮圖 (方便視覺理解)
                if history_i < 30:
                    box_color = "#3B82F6" # 藍色行駛圖
                elif history_i >= 30 and history_i < 55:
                    box_color = "#EF4444" # 紅色碰撞圖
                else:
                    box_color = "#FBBF24" # 黃色救援圖
                    
                # 繪製小影格與時間點
                draw.rectangle([(t_x-12, 275), (t_x+12, 295)], fill=box_color, outline="#F3F4F6", width=1)
                
                # 小時間標記
                t_sec = history_i / 8.0 # 假設 10秒共 80 影格
                draw.text((t_x-10, 300), f"{t_sec:.1f}s", fill="#9CA3AF", font=font_mono)

        # 5. 指示器與 Token 節省顯示
        is_sampling_now = False
        if i < 30:
            if i % 12 == 0: is_sampling_now = True
        elif i >= 30 and i < 55:
            if (i - 30) % 2 == 0: is_sampling_now = True
        else:
            if (i - 55) % 12 == 0: is_sampling_now = True

        if is_sampling_now:
            draw.ellipse([(20, 332), (30, 342)], fill="#EF4444")
            draw.text((38, 329), "★ 正在擷取影格並寫入拼圖", fill="#EF4444", font=font_sub)
        else:
            draw.ellipse([(20, 332), (30, 342)], fill="#10B981")
            draw.text((38, 329), "維持常規監聽...", fill="#9CA3AF", font=font_sub)

        # 顯示 Token 節省
        saved_pct = 98.2 if i < 30 or i >= 55 else 92.4
        draw.text((450, 328), f"當前 Token 節省: {saved_pct}%", fill="#10B981", font=font_title)

        frames.append(img)
        
    frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=120, loop=0)
    print(f"直觀圖形化概念動畫重新生成成功，儲存於: {output_path}")

if __name__ == "__main__":
    output_path = "/Users/force/Google_Antigravity/video-analyze/smart_sampling_poc.gif"
    create_poc_gif(output_path)
