import re

# We will read lines 98 to 284 from the header and extract the commands

lines = []
with open('/tmp/ESP32_Display_Panel/src/board/supported/waveshare/BOARD_WAVESHARE_ESP32_S3_TOUCH_LCD_1_85.h', 'r') as f:
    for i, line in enumerate(f):
        if 96 <= i <= 285:
            lines.append(line.strip())

with open('tools/waveshare_init.py', 'w') as out:
    for line in lines:
        m = re.search(r'\{([^,]+),\s*\(uint8_t \[\]\)\{([^}]+)\},\s*(\d+),\s*(\d+)\}', line)
        if m:
            c = m.group(1).strip()
            data = m.group(2).strip()
            dlen = int(m.group(3))
            delay = int(m.group(4))
            
            # Write out python representation
            out.write(f"    cmd({c}, {data})\n")
            if delay > 0:
                out.write(f"    time.sleep_ms({delay})\n")
