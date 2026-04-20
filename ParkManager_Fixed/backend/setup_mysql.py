#!/usr/bin/env python
"""
MySQL Database Setup Script for ParkManager
Run this to initialize MySQL database for the application
"""
import subprocess
import sys
import os

def run_mysql_command(command, password=None):
    """Run a MySQL command"""
    if password:
        cmd = f'mysql -u root -p{password} -e "{command}"'
    else:
        cmd = f'mysql -u root -e "{command}"'
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_mysql_database():
    """Set up MySQL database for ParkManager"""
    
    print("🔧 Setting up MySQL Database for ParkManager\n")
    
    # MySQL commands to run
    sql_commands = [
        "CREATE DATABASE IF NOT EXISTS parkmanagement;",
        "CREATE USER IF NOT EXISTS 'parkuser'@'127.0.0.1' IDENTIFIED BY 'parkpass123';",
        "GRANT ALL PRIVILEGES ON parkmanagement.* TO 'parkuser'@'127.0.0.1';",
        "GRANT ALL PRIVILEGES ON parkmanagement.* TO 'parkuser'@'localhost';",
        "FLUSH PRIVILEGES;",
        "SELECT 'Database setup completed' as Status;",
    ]
    
    # Try without password first
    print("📝 Attempting to connect to MySQL without password...")
    success, stdout, stderr = run_mysql_command("; ".join(sql_commands))
    
    if success:
        print("✅ MySQL database setup successful!\n")
        print(stdout)
        return True
    else:
        if "Access denied" in stderr:
            print("❌ Access denied. MySQL root user likely has a password set.")
            print("\nPlease run these MySQL commands manually:")
            print("=" * 60)
            print("mysql -u root -p")
            print("(Enter your MySQL root password)")
            print("\nThen paste these commands:")
            print("-" * 60)
            for cmd in sql_commands:
                print(cmd)
            print("-" * 60)
            print("\nAlternatively, if you know the root password, run:")
            print(f"mysql -u root -p<password> << 'EOF'")
            for cmd in sql_commands:
                print(cmd)
            print("EOF")
            return False
        else:
            print(f"❌ Error: {stderr}")
            return False

if __name__ == '__main__':
    success = setup_mysql_database()
    sys.exit(0 if success else 1)
