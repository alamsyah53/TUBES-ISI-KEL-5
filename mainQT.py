import tkinter as tk
from tkinter import ttk
import requests
import threading
import time
import csv
from io import StringIO
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque

# Konfigurasi InfluxDB
INFLUX_QUERY_URL = "http://localhost:8086/api/v2/query"
ORG = "kelisi5"
BUCKET = "iisi5"
TOKEN = "DF3XZjyfxca7uguMUCjhKVrxTmPYQjwmR9YJi9oHKObk5TStGO1P-0aaK1SY1Q0GhMT2pmoGNlH7JLgnKfspgg=="

# Riwayat data
history_length = 50
temp_history = deque(maxlen=history_length)
rh_history = deque(maxlen=history_length)
time_history = deque(maxlen=history_length)

def get_latest_data():
    flux_query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: -1m)
      |> filter(fn: (r) => r._measurement == "monitoring")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
      |> last()
    '''

    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/vnd.flux",
        "Accept": "application/csv"
    }

    try:
        response = requests.post(
            INFLUX_QUERY_URL,
            params={"org": ORG},
            headers=headers,
            data=flux_query
        )

        reader = csv.DictReader(StringIO(response.text))
        data = {}
        for row in reader:
            try:
                field = row["_field"]
                value = float(row["_value"])
                data[field] = value
            except:
                continue

        if "temperature" in data and "humidity" in data:
            return data["temperature"], data["humidity"]
        return None
    except Exception as e:
        print("❌ Exception query Influx:", e)
        return None

def get_data_range(start_time, end_time):
    flux_query = f'''
    from(bucket: "{BUCKET}")
      |> range(start: {start_time}, stop: {end_time})
      |> filter(fn: (r) => r._measurement == "monitoring")
      |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
    '''

    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/vnd.flux",
        "Accept": "application/csv"
    }

    try:
        response = requests.post(
            INFLUX_QUERY_URL,
            params={"org": ORG},
            headers=headers,
            data=flux_query
        )

        reader = csv.DictReader(StringIO(response.text))
        temp_map = {}
        rh_map = {}

        for row in reader:
            try:
                t = row["_time"]
                field = row["_field"]
                value = float(row["_value"])
                if field == "temperature":
                    temp_map[t] = value
                elif field == "humidity":
                    rh_map[t] = value
            except:
                continue

        sorted_keys = sorted(set(temp_map.keys()) & set(rh_map.keys()))
        temps = [temp_map[t] for t in sorted_keys]
        rhs = [rh_map[t] for t in sorted_keys]
        times = [t[11:19] for t in sorted_keys]  # jam:menit:detik

        return temps, rhs, times
    except Exception as e:
        print("❌ Exception query Influx:", e)
        return [], [], []

def update_data():
    while True:
        result = get_latest_data()
        current_time = time.strftime('%H:%M:%S')

        if result:
            temp, rh = result
            label_temp.config(text=f"Suhu: {temp:.1f} °C")
            label_rh.config(text=f"Kelembaban: {rh:.1f} %")
            status_label.config(text="Status: Data berhasil diperbarui")

            temp_history.append(temp)
            rh_history.append(rh)
            time_history.append(current_time)

            plot_graph()
        else:
            label_temp.config(text="Suhu: ---")
            label_rh.config(text="Kelembaban: ---")
            status_label.config(text="Status: Gagal mengambil data")

        time.sleep(2)

def plot_graph():
    ax1.clear()
    ax2.clear()

    fig.patch.set_facecolor('#f0f0f0')
    ax1.set_facecolor('#ffffff')
    ax2.set_facecolor('#ffffff')

    x = list(range(len(time_history)))
    times = list(time_history)

    ax1.plot(x, list(temp_history), label='Suhu (°C)', color='red', marker='o', linestyle='-')
    ax2.plot(x, list(rh_history), label='Kelembaban (%)', color='blue', marker='x', linestyle='-')

    ax1.set_title("Grafik Suhu")
    ax2.set_title("Grafik Kelembaban")
    ax1.set_ylabel("°C")
    ax2.set_ylabel("%")

    interval = 5
    tick_positions = x[::interval]
    tick_labels = times[::interval]

    ax1.set_xticks(tick_positions)
    ax2.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=45, ha="right")
    ax2.set_xticklabels(tick_labels, rotation=45, ha="right")

    for ax in [ax1, ax2]:
        ax.grid(True, linestyle='--', alpha=0.5)

    fig.tight_layout()
    canvas.draw()

def show_history():
    start = entry_start.get()
    end = entry_end.get()
    temps, rhs, times = get_data_range(start, end)

    if temps and rhs:
        temp_history.clear()
        rh_history.clear()
        time_history.clear()

        temp_history.extend(temps)
        rh_history.extend(rhs)
        time_history.extend(times)

        label_temp.config(text="(Hist) Suhu: -- °C")
        label_rh.config(text="(Hist) RH: -- %")
        status_label.config(text="Status: Menampilkan data historis")
        plot_graph()
    else:
        status_label.config(text="Status: Data historis tidak tersedia")

# GUI Setup
root = tk.Tk()
root.title("Monitor Sensor SHT20 - InfluxDB")
root.geometry("800x650")
root.configure(bg="#e0e0e0")

judul = tk.Label(root, text="Monitoring Suhu & Kelembaban Gudang", font=("Helvetica", 16, "bold"), bg="#e0e0e0")
judul.pack(pady=10)

label_temp = tk.Label(root, text="Suhu: -- °C", font=("Helvetica", 14), bg="#e0e0e0")
label_temp.pack()

label_rh = tk.Label(root, text="Kelembaban: -- %", font=("Helvetica", 14), bg="#e0e0e0")
label_rh.pack()

status_label = tk.Label(root, text="Status: Menunggu data...", font=("Helvetica", 12), fg="black", bg="#e0e0e0")
status_label.pack(pady=5)

frame_input = tk.Frame(root, bg="#e0e0e0")
frame_input.pack(pady=10)

tk.Label(frame_input, text="Start (RFC3339):", bg="#e0e0e0").grid(row=0, column=0, padx=5)
entry_start = tk.Entry(frame_input, width=30)
entry_start.grid(row=0, column=1)

tk.Label(frame_input, text="End (RFC3339):", bg="#e0e0e0").grid(row=1, column=0, padx=5)
entry_end = tk.Entry(frame_input, width=30)
entry_end.grid(row=1, column=1)

btn_show = tk.Button(frame_input, text="Tampilkan Riwayat", command=show_history, bg="#007acc", fg="white")
btn_show.grid(row=0, column=2, rowspan=2, padx=10, pady=5)

fig = Figure(figsize=(6, 4), dpi=100)
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

# Mulai thread update realtime
threading.Thread(target=update_data, daemon=True).start()

root.mainloop()

