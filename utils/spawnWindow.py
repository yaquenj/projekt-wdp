import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import tkintermapview
from .api_calls import getCoordinatesByName, getWeather, getNameByCoordinates
from .weather_images import get_image_name, ImageCode
from .config_manager import readConfig, saveConfig, createDefaultConfig
from .factors import Factors

# pierwsze odpalenie, config
try:
    config = readConfig()
    firstRun = False
except:
    config = createDefaultConfig()
    firstRun = True

# jednostki
unit_temp = "C" if config["preferences"]["unit"] == "metric" else "F"
unit_speed = "km/h" if config["preferences"]["unit"] == "metric" else "mph"
unit_pressure = "hPa" if config["preferences"]["unit"] == "metric" else "inHg"
unit_distance = "km" if config["preferences"]["unit"] == "metric" else "mi"

def load_icon(path, size=(30, 30)):
    try:
        if os.path.exists(path):
            image = Image.open(path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        else:
            print(f"Icon not found: {path}")
            return None
    except Exception as e:
        print(f"Błąd podczas ładowania ikony: {path}: {e}")
        return None

class MainFrame:
    def __init__(self, root):
        self.root = root
        self.root.title("Pogoton - Zobacz jutro dziś!")
        self.root.geometry("750x625")

        # menu
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Preferencje użytkownika", command=on_preferences)
        settings_menu.add_command(label="Ustaw lokalizację", command=on_location)
        menubar.add_cascade(label="Ustawienia", menu=settings_menu)

        # preloadowanie ikon
        self.icon_temp = load_icon(f'./media/{get_image_name(ImageCode.HOT)}')
        self.icon_humidity = load_icon(f'./media/{get_image_name(ImageCode.HUMIDITY)}')
        self.icon_wind = load_icon(f'./media/{get_image_name(ImageCode.WIND)}')
        self.icon_error = load_icon(f'./media/{get_image_name(ImageCode.ERROR)}')
        self.icon_cold = load_icon(f'./media/{get_image_name(ImageCode.COLD)}')
        self.icon_pressure = load_icon(f'./media/{get_image_name(ImageCode.PRESSURE)}')
        self.icon_dew_point = load_icon(f'./media/{get_image_name(ImageCode.DEW_POINT)}')
        self.icon_length = load_icon(f'./media/{get_image_name(ImageCode.VISIBILITY)}')
        # DUŻE ikony
        self.big_icon_sun = load_icon(f'./media/{get_image_name(ImageCode.SUN)}', (80, 80))
        self.big_icon_sun_cloud = load_icon(f'./media/{get_image_name(ImageCode.SUN_CLOUD)}', (80, 80))
        self.big_icon_cloud = load_icon(f'./media/{get_image_name(ImageCode.CLOUD)}', (80, 80))
        self.big_icon_fog = load_icon(f'./media/{get_image_name(ImageCode.FOG)}', (80, 80))
        self.big_icon_drizzle = load_icon(f'./media/{get_image_name(ImageCode.DRIZZLE)}', (80, 80))
        self.big_icon_freezing_drizzle = load_icon(f'./media/{get_image_name(ImageCode.FREEZING_DRIZZLE)}', (80, 80))
        self.big_icon_light_rain = load_icon(f'./media/{get_image_name(ImageCode.LIGHT_RAIN)}', (80, 80))
        self.big_icon_rain = load_icon(f'./media/{get_image_name(ImageCode.RAIN)}', (80, 80))
        self.big_icon_freezing_rain = load_icon(f'./media/{get_image_name(ImageCode.FREEZING_RAIN)}', (80, 80))
        self.big_icon_snow = load_icon(f'./media/{get_image_name(ImageCode.SNOW)}', (80, 80))
        self.big_icon_hail = load_icon(f'./media/{get_image_name(ImageCode.HAIL)}', (80, 80))
        self.big_icon_storm = load_icon(f'./media/{get_image_name(ImageCode.STORM)}', (80, 80))
        self.big_icon_thunderstorm = load_icon(f'./media/{get_image_name(ImageCode.THUNDERSTORM)}', (80, 80))
        self.big_icon_question = load_icon(f'./media/question.png', (80, 80))

        # mapowanie kodów pogody na ikony
        self.weather_icon_map = {
            ImageCode.SUN.value: self.big_icon_sun,
            ImageCode.SUN_CLOUD.value: self.big_icon_sun_cloud,
            ImageCode.CLOUD.value: self.big_icon_cloud,
            ImageCode.FOG.value: self.big_icon_fog,
            ImageCode.DRIZZLE.value: self.big_icon_drizzle,
            ImageCode.FREEZING_DRIZZLE.value: self.big_icon_freezing_drizzle,
            ImageCode.LIGHT_RAIN.value: self.big_icon_light_rain,
            ImageCode.RAIN.value: self.big_icon_rain,
            ImageCode.FREEZING_RAIN.value: self.big_icon_freezing_rain,
            ImageCode.SNOW.value: self.big_icon_snow,
            ImageCode.HAIL.value: self.big_icon_hail,
            ImageCode.STORM.value: self.big_icon_storm,
            ImageCode.THUNDERSTORM.value: self.big_icon_thunderstorm,
        }

        # główny kontener
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # dwie kolumny dla pogody
        main_frame.columnconfigure(0, weight=1, uniform="weather")
        main_frame.columnconfigure(1, weight=1, uniform="weather")
        main_frame.rowconfigure(0, weight=1)

        self.weather_box_1 = self.create_weather_box(main_frame, "Pogoda dzisiaj")
        self.weather_box_1.grid(row=0, column=0, sticky='nsew', padx=5)

        self.weather_box_2 = self.create_weather_box(main_frame, "Pogoda jutro")
        self.weather_box_2.grid(row=0, column=1, sticky='nsew', padx=5)

        # odswiezanie
        refresh_button = ttk.Button(main_frame, text="Odśwież", command=self.refresh_weather)
        refresh_button.grid(row=1, column=0, columnspan=2, sticky='s', pady=5)

        # odśwież pogode 100ms na starcie, nie od razu bo sie dluzej wczytuje okno, a to denerwuje niepotrzebnie
        self.root.after(100, self.refresh_weather)


    def create_weather_box(self, parent, day_title):
        frame = ttk.LabelFrame(parent, text=day_title, padding="10")

        # tytul kolumny z pogoda - dzis lub jtr
        title = ttk.Label(frame, text=day_title, font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # wybierz factory z configu jesli nie ma to domyslne
        selected_factors = config["preferences"].get("factors", [
            Factors.TEMPERATURE.value,
            Factors.APPARENT_TEMPERATURE.value,
            Factors.HUMIDITY.value,
            Factors.WIND.value,
            Factors.PRESSURE.value
        ])

        # nazwa pogody??? nie wiem jak to nazwac - informacje ogolne o pogodzie np slonecznie
        info_label = tk.Label(frame, text="Ładowanie...", font=("Arial", 14), image=self.big_icon_question, compound="top", pady=10)
        info_label.pack()

        # slownik labeli do pozniejszego zmieniania wartosci
        labels_dict = {'info': info_label}

        # TEMPERATURA
        if Factors.TEMPERATURE.value in selected_factors:
            temperature_label = tk.Label(frame, text=f' Temperatura: --°{unit_temp}', image=self.icon_temp,
                                         compound="left")
            temperature_label.pack(pady=5)
            labels_dict['temperature'] = temperature_label

        # TEMPERATURA ODCZUWALNA
        if Factors.APPARENT_TEMPERATURE.value in selected_factors:
            apparent_temperature = tk.Label(frame, text=f'Temperatura odczuwalna: --°{unit_temp}', image=self.icon_temp, compound="left")
            apparent_temperature.pack(pady=5)
            labels_dict['apparent_temperature'] = apparent_temperature

        # PUNKT ROSY
        if Factors.DEW_POINT.value in selected_factors:
            dew_point_label = tk.Label(frame, text=f'Punkt rosy: --°{unit_temp}', image=self.icon_dew_point, compound="left")
            dew_point_label.pack(pady=5)
            labels_dict['dew_point'] = dew_point_label

        # WILGOTNOŚĆ
        if Factors.HUMIDITY.value in selected_factors:
            humidity_label = tk.Label(frame, text=" Wilgotność: --%", image=self.icon_humidity, compound="left")
            humidity_label.pack(pady=5)
            labels_dict['humidity'] = humidity_label

        # WIATR
        if Factors.WIND.value in selected_factors:
            wind_label = tk.Label(frame, text=f' Wiatr: -- {unit_speed}', image=self.icon_wind, compound="left")
            wind_label.pack(pady=5)
            labels_dict['wind'] = wind_label

        # CIŚNIENIE
        if Factors.PRESSURE.value in selected_factors:
            pressure_label = tk.Label(frame, text=f' Ciśnienie atmosferyczne: -- {unit_pressure}',
                                      image=self.icon_pressure, compound="left")
            pressure_label.pack(pady=5)
            labels_dict['pressure'] = pressure_label

        # WIDOCZNOŚĆ
        if Factors.VISIBILITY.value in selected_factors:
            visibility_label = tk.Label(frame, text=f' Widoczność: -- {unit_distance}', image=self.icon_length,
                                        compound="left")
            visibility_label.pack(pady=5)
            labels_dict['visibility'] = visibility_label

        frame.labels = labels_dict

        return frame

    def refresh_weather(self):
        try:
            lat = config["location"]["lat"]
            lon = config["location"]["lon"]
            location_name = config["location"]["name"]

            weather_data = getWeather((lat, lon))

            if not weather_data:
                messagebox.showerror("Błąd", "Nie udało się pobrać danych pogodowych")
                return

            # jesli jest - update pogody dla dzisiaj
            if len(weather_data) > 0:
                self.update_weather_box(self.weather_box_1, weather_data[0], location_name)

            # to samo dla jutra
            if len(weather_data) > 1:
                self.update_weather_box(self.weather_box_2, weather_data[1], location_name)

        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas odświeżania pogody: {str(e)}")
            print(f"Błąd w refresh_weather: {e}")

    def update_weather_box(self, weather_box, weather_info, location_name):
        labels = weather_box.labels

        # aktualizuje opis pogody np pochmurnie
        weather_description = weather_info.get('description', 'Brak danych')
        labels['info'].config(text=weather_description)

        # zmiana ikonki pogody
        weather_image_code = weather_info.get('image_code')
        if weather_image_code is not None:
            weather_icon = self.weather_icon_map.get(weather_image_code, self.big_icon_sun)
            labels['info'].config(image=weather_icon)

        if 'temperature' in labels:
            temp = weather_info.get('temperature', '--')
            labels['temperature'].config(text=f' Temperatura: {temp}°{unit_temp}')

        if 'apparent_temperature' in labels:
            apparent_temp = weather_info.get('apparent_temperature', '--')
            labels['apparent_temperature'].config(text=f'Temperatura odczuwalna: {apparent_temp}°{unit_temp}')

        if 'dew_point' in labels:
            dew_point = weather_info.get('dew_point', '--')
            labels['dew_point'].config(text=f'Punkt rosy: {dew_point}°{unit_temp}')

        if 'humidity' in labels:
            humidity = weather_info.get('humidity', '--')
            labels['humidity'].config(text=f' Wilgotność: {humidity}%')

        if 'wind' in labels:
            wind_speed = weather_info.get('wind_speed', '--')
            labels['wind'].config(text=f' Wiatr: {wind_speed} {unit_speed}')

        if 'pressure' in labels:
            pressure = weather_info.get('pressure', '--')
            labels['pressure'].config(text=f' Ciśnienie atmosferyczne: {pressure} {unit_pressure}')

        if 'visibility' in labels:
            visibility = weather_info.get('visibility', '--')
            labels['visibility'].config(text=f' Widoczność: {visibility} {unit_distance}')

def spawnWindow():
    root = tk.Tk()
    root.iconbitmap("icon.ico")
    MainFrame(root)
    if firstRun:
        messagebox.showinfo(
            "Witaj w Pogoton!",
            "Wygląda na to, że uruchamiasz aplikację po raz pierwszy.\n\n"
            "Teraz zostaniesz poproszony o:\n"
            "1. Wybór preferencji pogodowych\n"
            "2. Ustawienie lokalizacji\n\n"
            "Te ustawienia możesz później zmienić w menu Ustawienia."
        )
        prefs = PreferencesWindow()
        root.wait_window(prefs.window)
        LocationWindow()
    root.mainloop()


class PreferencesWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Preferencje użytkownika")
        self.window.geometry("400x450")
        self.window.resizable(False, False)
        self.window.grab_set()  # Okno modalne - nie uzyje innych poki to sie nie zamknie

        self.config = readConfig()
        current_unit = self.config["preferences"]["unit"]
        current_factors = self.config["preferences"].get("factors", [])

        # glowna ramka
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)

        # ramka jednostek
        unit_frame = ttk.LabelFrame(main_frame, text="Jednostki miary", padding="10")
        unit_frame.pack(fill="x", pady=(0, 20))

        self.unit_var = tk.StringVar(value=current_unit) # zmienna tekstowa zarządzana przez radiobuttony

        ttk.Radiobutton(
            unit_frame,
            text="Metryczne (°C, km/h, hPa, km)",
            variable=self.unit_var,
            value="metric"
        ).pack(anchor="w", pady=5)

        ttk.Radiobutton(
            unit_frame,
            text="Imperialne (°F, mph, inHg, mi)",
            variable=self.unit_var,
            value="imperial"
        ).pack(anchor="w", pady=5)

        # ramka factorow pogody
        factors_frame = ttk.LabelFrame(main_frame, text="Czynniki pogodowe (wybierz 2-6)", padding="10")
        factors_frame.pack(fill="both", expand=True, pady=(0, 20))

        # dictionary do przechowywania zmiennych checkbox'ów
        self.factor_vars = {}

        available_factors = [
            (Factors.TEMPERATURE, "Temperatura"),
            (Factors.APPARENT_TEMPERATURE, "Temperatura odczuwalna"),
            (Factors.DEW_POINT, "Punkt rosy"),
            (Factors.HUMIDITY, "Wilgotność"),
            (Factors.WIND, "Prędkość wiatru"),
            (Factors.PRESSURE, "Ciśnienie atmosferyczne"),
            (Factors.VISIBILITY, "Widoczność"),
        ]

        for factor, label in available_factors:
            var = tk.BooleanVar(value=factor.value in current_factors)
            self.factor_vars[factor.value] = var

            cb = ttk.Checkbutton(
                factors_frame,
                text=label,
                variable=var
            )
            cb.pack(anchor='w', pady=3)

        # przyciski na dole anuluj zapisz
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')

        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.window.destroy
        ).pack(side='right')

        ttk.Button(
            button_frame,
            text="Zapisz",
            command=self.save_preferences
        ).pack(side='right', padx=5)

    def save_preferences(self):
        selected_factors = []
        for factor_value, var in self.factor_vars.items():
            if var.get():
                selected_factors.append(factor_value)

        if len(selected_factors) < 2:
            messagebox.showerror(
                "Błąd",
                "Musisz wybrać co najmniej 2 czynniki pogodowe!"
            )
            return

        if len(selected_factors) > 6:
            messagebox.showerror(
                "Błąd",
                "Możesz wybrać maksymalnie 6 czynników pogodowych!"
            )
            return

        # zapisz config
        self.config["preferences"]["unit"] = self.unit_var.get()
        self.config["preferences"]["factors"] = selected_factors
        saveConfig(self.config)

        messagebox.showinfo(
            "Sukces",
            "Preferencje zostały zapisane!\n\nZmiany będą widoczne po zrestartowaniu aplikacji."
        )

        self.window.destroy()

def on_preferences():
    PreferencesWindow()

class LocationWindow:
    def __init__(self):
        self.selected_marker = None
        self.window = tk.Toplevel()
        self.window.title("Ustawienia lokalizacji")
        self.window.grab_set()

        # glowna ramka
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)

        # ramka wyszukiwarki
        search_frame = ttk.LabelFrame(main_frame, text="Wyszukiwanie lokalizacji", padding=10)
        search_frame.pack(fill="both", expand=True, pady=(0, 20))

        ttk.Label(search_frame, text="Wyszukaj lokalizację:").pack(anchor="w", pady=(0, 5))

        self.search_entry = ttk.Entry(search_frame, font=("Arial", 11))
        self.search_entry.pack(fill="x", pady=(0, 5))

        ttk.Button(search_frame, text="Szukaj", command=self.search_location).pack(anchor="e")

        # ramka listy wyszukanych miast
        results_frame = ttk.LabelFrame(main_frame, text="Wyniki wyszukiwania", padding="10")

        results_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.results_listbox = tk.Listbox(results_frame, height=8, font=("Arial", 10))
        self.results_listbox.pack(fill="both", expand=True)
        self.results_listbox.bind('<<ListboxSelect>>', lambda e: self.findAndSetLocation()) # zaznaczenie na mapie po wybraniu miasta

        self.results_data = []

        # ramka mapy
        map_frame = ttk.LabelFrame(main_frame, text="Mapa", padding=10)
        map_frame.pack(fill="both", expand=True, pady=(0, 20))

        map_widget = tkintermapview.TkinterMapView(map_frame, width=800, height=300, corner_radius=0)
        map_widget.pack(fill="both", expand=True)
        map_widget.set_position(50.0194727, 21.9886574) # Domyślnie politechnika

        self.map_widget = map_widget

        # przyciski na dole anuluj zapisz
        button_frame = ttk.Frame(main_frame, padding=5)
        button_frame.pack(fill="x", side="bottom", pady=10)

        ttk.Button(
            button_frame,
            text="Anuluj",
            command=self.window.destroy
        ).pack(side="right")

        ttk.Button(
            button_frame,
            text="Zapisz",
            command=self.save_location
        ).pack(side="right", padx=5)

        def add_marker_event(coords):
            map_widget.delete_all_marker()
            map_widget.set_marker(coords[0], coords[1])
            location_data = getNameByCoordinates(coords[0], coords[1])
            if location_data:
                loc = location_data[0].get("name", "Nieznana lokalizacja")
                country = location_data[0].get("country", "Nieznany kraj")
                self.setLocation(loc, country, coords[0], coords[1])

        map_widget.add_left_click_map_command(add_marker_event)

    def findAndSetLocation(self):
        try:
            index = self.results_listbox.curselection()[0]
            location_data = self.results_data[int(index)]
            lat = location_data.get("latitude")
            lon = location_data.get("longitude")
            name = location_data.get("name")
            country = location_data.get("country")
            self.setLocation(name, country, lat, lon)
        except Exception as e:
            print(f"Error in findAndSetLocation: {e}")

    def setLocation(self, name, country, lat, lon):
        self.map_widget.delete_all_marker()
        marker = self.map_widget.set_marker(lat, lon)
        marker.city_name = name
        marker.country_name = country
        self.selected_marker = marker
        self.map_widget.set_position(lat, lon)
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, f"{name}, {country}")

    def save_location(self):
        if not self.selected_marker:
            messagebox.showerror(
                "Błąd",
                "Musisz wybrać lokalizację na mapie!"
            )
            return

        # zapisz config
        config = readConfig()
        config["location"]["name"] = self.selected_marker.city_name
        config["location"]["lat"] = self.selected_marker.position[0]
        config["location"]["lon"] = self.selected_marker.position[1]
        config["location"]["country"] = self.selected_marker.country_name
        saveConfig(config)

        messagebox.showinfo(
            "Sukces",
            "Lokalizacja została zapisana! Uruchom aplikację ponownie!"
        )
        
        self.window.destroy()

    def search_location(self):
        query = self.search_entry.get().strip()

        if not query:
            messagebox.showwarning("Uwaga", "Wpisz nazwę lokalizacji!")
            return

        # usuwa poprzednie wyniki
        self.results_listbox.delete(0, "end")
        self.results_data = []

        results = getCoordinatesByName(query)

        if not results or 'results' not in results:
            messagebox.showinfo("Brak wyników", "Nie znaleziono lokalizacji o podanej nazwie.")
            return

        # max 5 wynikow
        locations = results['results'][:5]

        for location in locations:
            name = location.get('name', 'Nieznana')
            country = location.get('country', '')
            admin1 = location.get('admin1', '') # wojewodztwo

            # Format wyświetlania
            display_text = f"{name}, {country}"
            if admin1:
                display_text = f"{name}, {admin1}, {country}"

            self.results_listbox.insert("end", display_text)
            self.results_data.append(location)

        # autoamtycznie zaznacza 1 wynik
        if self.results_data:
            self.results_listbox.selection_set(0)
            self.map_widget.set_position(self.results_data[0]['latitude'], self.results_data[0]['longitude'])
            self.setLocation(self.results_data[0]['name'], self.results_data[0]['country'],self.results_data[0]['latitude'], self.results_data[0]['longitude'])

    def select_location(self):
        selection = self.results_listbox.curselection() # indeksy wybranych miast

        if not selection:
            messagebox.showwarning("Uwaga", "Wybierz lokalizację z listy!")
            return

        index = selection[0]
        location = self.results_data[index]

        name = location.get('name', 'Nieznana')
        country = location.get('country', '')
        lat = location.get('latitude')
        lon = location.get('longitude')

        if lat is None or lon is None:
            messagebox.showerror("Błąd", "Nie można pobrać współrzędnych lokalizacji.")
            return

        # zaznacza marker na mapce
        self.setLocation(name, country, lat, lon)

        messagebox.showinfo("Sukces",
                            f"Lokalizacja ustawiona na:\n{name}, {country}\n\nOdśwież pogodę aby zobaczyć zmiany.")
        self.window.destroy()


def on_location():
    LocationWindow()
