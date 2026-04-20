#!/usr/bin/env python
"""
Interactive MySQL Setup Script for ParkManager
"""
import subprocess
import getpass
import sys

def run_mysql_command_with_password(commands, password):
    """Run MySQL commands with root password"""
    try:
        # Create a temporary command file
        cmd_str = "\n".join(commands)
        process = subprocess.Popen(
            ['mysql', '-u', 'root', f'-p{password}'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=cmd_str, timeout=10)
        return process.returncode == 0, stdout, stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("=" * 70)
    print("🚀 ParkManager MySQL Setup")
    print("=" * 70)
    
    print("\nThis script will:")
    print("1. Create a MySQL database named 'parkmanagement'")
    print("2. Create a user 'parkuser' with password 'parkpass123'")
    print("3. Grant all privileges to the user")
    print("4. Run Django migrations to set up tables")
    
    print("\n" + "-" * 70)
    root_password = getpass.getpass("Enter your MySQL root password: ")
    
    print("\n📝 Creating MySQL database and user...")
    
    commands = [
        "CREATE DATABASE IF NOT EXISTS parkmanagement CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "DROP USER IF EXISTS 'parkuser'@'127.0.0.1';",
        "DROP USER IF EXISTS 'parkuser'@'localhost';",
        "CREATE USER 'parkuser'@'127.0.0.1' IDENTIFIED BY 'parkpass123';",
        "CREATE USER 'parkuser'@'localhost' IDENTIFIED BY 'parkpass123';",
        "GRANT ALL PRIVILEGES ON parkmanagement.* TO 'parkuser'@'127.0.0.1' WITH GRANT OPTION;",
        "GRANT ALL PRIVILEGES ON parkmanagement.* TO 'parkuser'@'localhost' WITH GRANT OPTION;",
        "FLUSH PRIVILEGES;",
        "SELECT 'Database and user created successfully' as Status;",
    ]
    
    success, stdout, stderr = run_mysql_command_with_password(commands, root_password)
    
    if success:
        print("✅ MySQL database and user created successfully!")
        print(stdout)
        
        # Now run Django migrations
        print("\n📦 Running Django migrations...")
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'migrate'],
                cwd='.',
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Django migrations completed successfully!")
                print("\n📊 Creating test data...")
                
                # Create admin user
                subprocess.run(
                    [sys.executable, 'create_admin.py'],
                    cwd='.',
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                print("✅ Test data created!")
                print("\n" + "=" * 70)
                print("✅ MySQL Setup Complete!")
                print("=" * 70)
                print("\nYour application is now configured to use MySQL for persistent storage.")
                print("\nDatabase credentials:")
                print("  Database: parkmanagement")
                print("  User: parkuser")
                print("  Password: parkpass123")
                print("  Host: 127.0.0.1")
                print("\nStart your application with: python manage.py runserver 8000")
                print("=" * 70)
            else:
                print(f"❌ Migration failed: {result.stderr}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error running migrations: {e}")
            sys.exit(1)
    else:
        print(f"❌ Failed to create database: {stderr}")
        if "Access denied" in stderr:
            print("\n⚠️  Check that:")
            print("  1. MySQL service is running")
            print("  2. You entered the correct root password")
            print("  3. The 'root' user exists in MySQL")
        sys.exit(1)

if __name__ == '__main__':
    main()
