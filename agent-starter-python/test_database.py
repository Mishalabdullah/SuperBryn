#!/usr/bin/env python3
"""Quick database connection test script."""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv(".env.local")

print("🔍 Testing Supabase connection...")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')[:30]}...")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20]}...")

try:
    from src.database import DatabaseManager

    async def test_connection():
        db = DatabaseManager()
        print("✅ Database manager initialized successfully!")

        # Test getting a non-existent user (should return None)
        print("\n📞 Testing user profile lookup...")
        user = await db.get_user_profile("0000000000")
        if user is None:
            print("✅ User lookup working (no user found, as expected)")
        else:
            print(f"ℹ️  Found existing test user: {user}")

        print("\n🎉 Database connection successful!")
        print("\nYou're ready to run the agent!")
        return True

    asyncio.run(test_connection())

except Exception as e:
    print(f"\n❌ Database connection failed: {e}")
    print("\n⚠️  Make sure you've:")
    print("1. Created Supabase project")
    print("2. Run the SQL script: agent-starter-python/supabase_setup.sql")
    print("3. Set SUPABASE_URL and SUPABASE_KEY in .env.local")
    exit(1)
