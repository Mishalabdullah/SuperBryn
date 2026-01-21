#!/bin/bash

# Local Slot Configuration Test
# Tests the slot generation logic before deployment

echo "🧪 Testing Slot Configuration Locally"
echo "======================================"
echo ""

cd "$(dirname "$0")"

python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from config import AppConfig
from datetime import datetime

print("✅ Loading configuration...")
config = AppConfig()

print("✅ Generating slots...")
slots = config.get_available_slots()

print(f"\n📊 Results:")
print(f"   Total slots: {len(slots)}")
print(f"   Date range: {slots[0]['date']} to {slots[-1]['date']}")
print(f"   Days covered: ~14 weekdays (excluding Sat/Sun)")
print()

print("📅 Checking Lunch Break Exclusion:")
lunch_slots = [s for s in slots if s['time'] in ['12:00', '12:30']]
if lunch_slots:
    print(f"   ❌ ERROR: Found {len(lunch_slots)} lunch slots (should be 0)")
    for slot in lunch_slots[:5]:
        print(f"      - {slot['date']} at {slot['time']}")
else:
    print(f"   ✅ No lunch slots found (12:00-12:30 excluded)")
print()

print("📅 Checking Weekend Exclusion:")
weekend_slots = [s for s in slots if datetime.strptime(s['date'], '%Y-%m-%d').weekday() in [5, 6]]
if weekend_slots:
    print(f"   ❌ ERROR: Found {len(weekend_slots)} weekend slots (should be 0)")
else:
    print(f"   ✅ No weekend slots found (Sat/Sun excluded)")
print()

print("📅 Sample: First 20 slots that will be shown to users:")
print("   " + "-" * 60)
for i, slot in enumerate(slots[:20], 1):
    print(f"   {i:2d}. {slot['display_date']:30s} at {slot['display_time']}")
print()

print("✅ Local test complete!")
print()
print("💡 If all checks passed above, you're ready to deploy:")
print("   cd /home/mishal/Documents/code/suprbryn/agent-starter-python")
print("   lk agent deploy")
EOF
