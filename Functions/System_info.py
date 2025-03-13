import datetime
import platform
import psutil  # For battery (install with `pip install psutil`)
import socket  # For network information


def get_battery_level():
    """Retrieves battery level if available, otherwise returns 'N/A'."""
    try:
        battery = psutil.sensors_battery()
        # Try both 'status' and 'power_plugged' attributes
        status = getattr(battery, 'status', None)  # Try 'status' first
        if status is None:
            status = 'Charging' if battery.power_plugged else 'Discharging'  # Fallback
        return f"{battery.percent}% ({status})"
    except (AttributeError, psutil.NoSuchBatterySensor):
        return "N/A"

def get_network_info():
    """Retrieves basic network information."""
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return f"Hostname: {hostname}\nIP Address: {ip_address}"
    except socket.gaierror:
        return "Failed to retrieve network information."

def get_disk_usage(path="/"):  # Default path: root directory
    """Retrieves disk usage for a specified path."""
    try:
        usage = psutil.disk_usage(path)
        total = usage.total / (1024 * 1024 * 1024)  # Convert to GB
        used = usage.used / (1024 * 1024 * 1024)
        free = usage.free / (1024 * 1024 * 1024)
        return f"Total: {total:.2f} GB\nUsed: {used:.2f} GB\nFree: {free:.2f} GB"
    except (PermissionError, FileNotFoundError):
        return f"Failed to access disk usage information for '{path}'."

def get_running_processes(limit=5):
    """Retrieves information about top CPU-consuming processes."""
    try:
        processes = sorted(psutil.process_iter(['name', 'cpu_percent']), key=lambda p: p.info['cpu_percent'], reverse=True)[:limit]
        info = ""
        for process in processes:
            info += f"PID: {process.pid}\tName: {process.name()}\n"
        return info if info else "No processes found."
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "Failed to retrieve process information (insufficient permissions)."

def get_uptime():
    """Calculates system uptime in human-readable format."""
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    now = datetime.datetime.now()
    delta = now - boot_time
    days = delta.days
    hours = delta.seconds // 3600 % 24
    minutes = delta.seconds // 60 % 60
    seconds = delta.seconds % 60
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

def display_info(Query):
    """Displays system information in a clear and visually appealing format."""
    current_time = datetime.datetime.now()
    day_of_week = current_time.strftime("%A")
    date_formatted = current_time.strftime("%d %B %Y")
    time_formatted = current_time.strftime("%H:%M:%S")

    os_name = platform.system() + " " + platform.release()
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    battery_level = get_battery_level()
    network_info = get_network_info()
    disk_usage = get_disk_usage()
    running_processes = get_running_processes()
    uptime = get_uptime()

    if "day" in Query:
        return f"The Day is: {day_of_week} Sir!"
    elif "date" in Query:
        return f"Today's Date is: {date_formatted} Sir!"
    elif "os" in Query:
        return f"The Operating System is: {os_name} Sir!"
    elif "cpu" in Query:
        return f"The CPU Usage is: {cpu_usage}% Sir!"
    elif "memory" in Query:
        return f"The Memory Usage is: {memory_usage}% Sir!"
    elif "battery" in Query:
        return f"The Battery Level is: {battery_level} Sir!"
    elif "network" in Query:
        return f"The Network Information is:\n{network_info} Sir!"
    elif "disk" in Query:
        return f"The Disk Usage is:\n{disk_usage} Sir!"
    elif "processes" in Query:
        return f"The Running Processes are:\n{running_processes} Sir!"
    elif "uptime" in Query:
        return f"The System Uptime is:\n{uptime} Sir!"
    elif "time" in Query:
        return f"The Time is: {time_formatted} Sir!"
    else:
        return "N/A"

def main():
    """Main loop for user interaction."""
    while True:
        print("\nSystem Information Menu:")
        print("1. View System Information")
        print("2. Exit")

        choice = input("Enter your choice (1 or 2): ")
        if choice == "1":
            print(display_info("uptime"))
        elif choice == "2":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()