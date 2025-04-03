import tkinter as tk
from tkinter import messagebox
import paramiko
import threading
from wakeonlan import send_magic_packet

# Пароль для подключения по SSH
ssh_password = 'Dsv010vf'

# Список компьютеров (IP-адреса или имена хостов)
computers = [
    {'name': 'db30', 'ip': '192.168.2.222', 'mac': '38:D5:47:1C:9C:27', 'status': 'unknown'},
    {'name': 'debian', 'ip': '192.168.4.38', 'mac': 'D4:5D:64:26:70:83', 'status': 'unknown'},
    {'name': 'host3', 'ip': '192.168.4.21', 'mac': '00:1E:67:AE:82:42', 'status': 'unknown'},
]

# Функция для проверки состояния компьютера
def check_computer_status(ip, status_label):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username='root', password=ssh_password, timeout=5)
        ssh.close()
        status_label.config(bg='green')
        return 'on'
    except:
        status_label.config(bg='red')
        return 'off'

# Функция для обновления статуса всех компьютеров
def update_status():
    for computer in computers:
        status_label = computer['status_label']
        ip = computer['ip']
        threading.Thread(target=check_computer_status, args=(ip, status_label)).start()
    root.after(5000, update_status)

# Функция для выключения всех компьютеров
def shutdown_class():
    for computer in computers:
        ip = computer['ip']
        status_label = computer['status_label']
        if check_computer_status(ip, status_label) == 'on':
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, username='root', password=ssh_password, timeout=5)
                ssh.exec_command('shutdown now')
                ssh.close()
                status_label.config(bg='red')
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось выключить компьютер {ip}: {e}")

# Функция для включения всех компьютеров
def power_on_class():
    for computer in computers:
        mac = computer['mac']
        status_label = computer['status_label']
        try:
            # Отправляем "магический пакет" для включения компьютера
            send_magic_packet(mac)
          #  messagebox.showinfo("Успех", f"Компьютер с MAC {mac} получил команду на включение.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить Wake-on-LAN пакет для {mac}: {e}")

# Создание GUI
root = tk.Tk()
root.title("Управление компьютерами")

# Создание элементов интерфейса
for computer in computers:
    frame = tk.Frame(root)
    frame.pack(pady=5)

    ip_label = tk.Label(frame, text=computer['name'])
    ip_label.pack(side=tk.LEFT, padx=10)

    status_label = tk.Label(frame, text='    ', bg='gray')
    status_label.pack(side=tk.LEFT)
    computer['status_label'] = status_label

# Кнопка для выключения всех компьютеров
shutdown_button = tk.Button(root, text="SHUTDOWN CLASS", command=shutdown_class)
shutdown_button.pack(pady=10)

# Кнопка для включения всех компьютеров
power_on_button = tk.Button(root, text="POWER ON CLASS", command=power_on_class)
power_on_button.pack(pady=10)

# Первоначальное обновление статуса
update_status()

# Запуск основного цикла GUI
root.mainloop()