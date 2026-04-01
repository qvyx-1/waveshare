import re

with open("/tmp/ESP32_Display_Panel/src/board/supported/waveshare/BOARD_WAVESHARE_ESP32_S3_TOUCH_LCD_1_85.h") as f:
    text = f.read()

match = re.search(r'#define ESP_PANEL_BOARD_LCD_VENDOR_INIT_CMD\(\) \\\n    \{ \\(.*?)    \}', text, re.DOTALL)
if not match:
    # Just read lines
    lines = text.split('\n')
    start = False
    for line in lines:
        if '#define ESP_PANEL_BOARD_LCD_VENDOR_INIT_CMD()' in line:
            start = True
            print("    # --- WAVESHARE ST77916 Vendor Init Sequence ---")
            continue
        if start:
            if '}' in line and not line.strip().startswith('{'):
                break
            m = re.search(r'\{([^,]+),\s*\(uint8_t \[\]\)\{([^}]+)\},\s*(\d+),\s*(\d+)\}', line)
            if m:
                c = m.group(1).strip()
                data_str = m.group(2).strip()
                delay = int(m.group(4))
                
                print(f"    cmd({c}, {data_str})")
                if delay > 0:
                    print(f"    time.sleep_ms({delay})")

