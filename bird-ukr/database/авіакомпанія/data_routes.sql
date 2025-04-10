-- Імпорт даних про маршрути для бази даних "Авіакомпанія"

-- Спочатку отримаємо ID аеропортів
WITH airport_ids AS (
    SELECT id, код_іата, місто, країна FROM аеропорти
)

-- Вставляємо маршрути (будемо використовувати підзапит для отримання ID аеропортів)
INSERT INTO маршрути (аеропорт_відправлення_id, аеропорт_призначення_id, відстань, приблизний_час_польоту, базова_вартість) VALUES
-- Маршрути з Києва (Бориспіль)
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'LWO'), 540, 60, 1500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'ODS'), 450, 55, 1450.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'DNK'), 430, 50, 1400.00),
((SELECT id FROM аеропорти WHERE код_іата = 'DNK'), (SELECT id FROM аеропорти WHERE код_іата = 'KBP'), 430, 50, 1400.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'HRK'), 410, 50, 1380.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'ZAP'), 510, 60, 1500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'IFO'), 520, 65, 1550.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'CWC'), 530, 65, 1550.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'PLV'), 350, 45, 1300.00),

-- Міжнародні маршрути з Києва (Бориспіль)
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'WAW'), 690, 90, 3500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'WAW'), (SELECT id FROM аеропорти WHERE код_іата = 'KBP'), 690, 90, 3500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'FRA'), 1850, 180, 6500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'KBP'), 1850, 180, 6500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'CDG'), 2150, 210, 7200.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'LHR'), 2400, 230, 7800.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'AMS'), 1980, 200, 6800.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'VIE'), 1050, 120, 4500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'IST'), 1050, 120, 4200.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'BUD'), 900, 110, 4000.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'FCO'), 1800, 185, 6300.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'MAD'), 3100, 270, 8500.00),

-- Далекі маршрути з Києва (Бориспіль)
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'JFK'), 7600, 580, 19500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'JFK'), (SELECT id FROM аеропорти WHERE код_іата = 'KBP'), 7600, 580, 19500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'DXB'), 3500, 300, 12500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'PEK'), 6900, 540, 18500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'BKK'), 7800, 600, 21000.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'CAI'), 2500, 240, 9500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'KBP'), (SELECT id FROM аеропорти WHERE код_іата = 'YYZ'), 7500, 570, 19000.00),

-- Маршрути з Львова
((SELECT id FROM аеропорти WHERE код_іата = 'LWO'), (SELECT id FROM аеропорти WHERE код_іата = 'KBP'), 540, 60, 1500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LWO'), (SELECT id FROM аеропорти WHERE код_іата = 'WAW'), 390, 70, 2800.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LWO'), (SELECT id FROM аеропорти WHERE код_іата = 'FRA'), 1400, 150, 5800.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LWO'), (SELECT id FROM аеропорти WHERE код_іата = 'VIE'), 750, 100, 3800.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LWO'), (SELECT id FROM аеропорти WHERE код_іата = 'BUD'), 550, 90, 3300.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LWO'), (SELECT id FROM аеропорти WHERE код_іата = 'IST'), 1300, 140, 4800.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LWO'), (SELECT id FROM аеропорти WHERE код_іата = 'CDG'), 1800, 190, 6500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LWO'), (SELECT id FROM аеропорти WHERE код_іата = 'FCO'), 1600, 180, 5800.00),

-- Маршрути з Одеси
((SELECT id FROM аеропорти WHERE код_іата = 'ODS'), (SELECT id FROM аеропорти WHERE код_іата = 'KBP'), 450, 55, 1450.00),
((SELECT id FROM аеропорти WHERE код_іата = 'ODS'), (SELECT id FROM аеропорти WHERE код_іата = 'IST'), 680, 100, 3800.00),
((SELECT id FROM аеропорти WHERE код_іата = 'ODS'), (SELECT id FROM аеропорти WHERE код_іата = 'WAW'), 980, 120, 4300.00),
((SELECT id FROM аеропорти WHERE код_іата = 'ODS'), (SELECT id FROM аеропорти WHERE код_іата = 'VIE'), 1150, 140, 4900.00),
((SELECT id FROM аеропорти WHERE код_іата = 'ODS'), (SELECT id FROM аеропорти WHERE код_іата = 'FRA'), 1950, 200, 6900.00),
((SELECT id FROM аеропорти WHERE код_іата = 'ODS'), (SELECT id FROM аеропорти WHERE код_іата = 'TEL'), 1350, 150, 5200.00),

-- Маршрути з аеропорту Київ (Жуляни)
((SELECT id FROM аеропорти WHERE код_іата = 'IEV'), (SELECT id FROM аеропорти WHERE код_іата = 'WAW'), 690, 90, 3500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'IEV'), (SELECT id FROM аеропорти WHERE код_іата = 'BUD'), 900, 110, 4000.00),
((SELECT id FROM аеропорти WHERE код_іата = 'IEV'), (SELECT id FROM аеропорти WHERE код_іата = 'VIE'), 1050, 120, 4500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'IEV'), (SELECT id FROM аеропорти WHERE код_іата = 'DNK'), 430, 50, 1400.00),
((SELECT id FROM аеропорти WHERE код_іата = 'IEV'), (SELECT id FROM аеропорти WHERE код_іата = 'LWO'), 540, 60, 1500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'IEV'), (SELECT id FROM аеропорти WHERE код_іата = 'IST'), 1050, 120, 4200.00),

-- Європейські транзитні маршрути
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'LHR'), 660, 85, 2800.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'CDG'), 480, 70, 2500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'AMS'), 370, 60, 2300.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'MAD'), 1450, 160, 5500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'FCO'), 960, 120, 4200.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'JFK'), 6200, 510, 18000.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'DXB'), 4860, 380, 15500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LHR'), (SELECT id FROM аеропорти WHERE код_іата = 'JFK'), 5550, 450, 16500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LHR'), (SELECT id FROM аеропорти WHERE код_іата = 'AMS'), 370, 60, 2300.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LHR'), (SELECT id FROM аеропорти WHERE код_іата = 'CDG'), 340, 55, 2200.00),
((SELECT id FROM аеропорти WHERE код_іата = 'CDG'), (SELECT id FROM аеропорти WHERE код_іата = 'JFK'), 5850, 470, 17500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'CDG'), (SELECT id FROM аеропорти WHERE код_іата = 'MAD'), 1060, 130, 4500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'CDG'), (SELECT id FROM аеропорти WHERE код_іата = 'FCO'), 1120, 135, 4600.00),
((SELECT id FROM аеропорти WHERE код_іата = 'AMS'), (SELECT id FROM аеропорти WHERE код_іата = 'JFK'), 5860, 470, 17500.00),

-- Американські маршрути
((SELECT id FROM аеропорти WHERE код_іата = 'JFK'), (SELECT id FROM аеропорти WHERE код_іата = 'LAX'), 3980, 350, 12500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'JFK'), (SELECT id FROM аеропорти WHERE код_іата = 'ORD'), 1190, 150, 5500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'JFK'), (SELECT id FROM аеропорти WHERE код_іата = 'MIA'), 1760, 180, 6500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'JFK'), (SELECT id FROM аеропорти WHERE код_іата = 'YYZ'), 570, 90, 3500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LAX'), (SELECT id FROM аеропорти WHERE код_іата = 'ORD'), 2820, 260, 9500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LAX'), (SELECT id FROM аеропорти WHERE код_іата = 'SFO'), 550, 85, 3200.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LAX'), (SELECT id FROM аеропорти WHERE код_іата = 'MEX'), 2500, 240, 8500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LAX'), (SELECT id FROM аеропорти WHERE код_іата = 'NRT'), 8800, 650, 25000.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LAX'), (SELECT id FROM аеропорти WHERE код_іата = 'SYD'), 12050, 850, 32000.00),

-- Азіатські маршрути
((SELECT id FROM аеропорти WHERE код_іата = 'DXB'), (SELECT id FROM аеропорти WHERE код_іата = 'BKK'), 4870, 380, 15500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'DXB'), (SELECT id FROM аеропорти WHERE код_іата = 'SIN'), 5840, 440, 18000.00),
((SELECT id FROM аеропорти WHERE код_іата = 'DXB'), (SELECT id FROM аеропорти WHERE код_іата = 'DEL'), 2180, 210, 8000.00),
((SELECT id FROM аеропорти WHERE код_іата = 'DXB'), (SELECT id FROM аеропорти WHERE код_іата = 'HKG'), 7010, 520, 19500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'DXB'), (SELECT id FROM аеропорти WHERE код_іата = 'NRT'), 8160, 600, 22000.00),
((SELECT id FROM аеропорти WHERE код_іата = 'SIN'), (SELECT id FROM аеропорти WHERE код_іата = 'HKG'), 2560, 240, 8500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'SIN'), (SELECT id FROM аеропорти WHERE код_іата = 'BKK'), 1440, 150, 5500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'SIN'), (SELECT id FROM аеропорти WHERE код_іата = 'SYD'), 6290, 470, 18500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'SIN'), (SELECT id FROM аеропорти WHERE код_іата = 'NRT'), 5360, 410, 16500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'HKG'), (SELECT id FROM аеропорти WHERE код_іата = 'NRT'), 2890, 260, 9500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'HKG'), (SELECT id FROM аеропорти WHERE код_іата = 'SYD'), 7380, 540, 20500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'HKG'), (SELECT id FROM аеропорти WHERE код_іата = 'BKK'), 1710, 180, 6500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'NRT'), (SELECT id FROM аеропорти WHERE код_іата = 'SYD'), 7920, 580, 21500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'NRT'), (SELECT id FROM аеропорти WHERE код_іата = 'ICN'), 1260, 150, 5500.00),

-- Інші важливі міжнародні маршрути
((SELECT id FROM аеропорти WHERE код_іата = 'JFK'), (SELECT id FROM аеропорти WHERE код_іата = 'LHR'), 5550, 450, 16500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LHR'), (SELECT id FROM аеропорти WHERE код_іата = 'SIN'), 10880, 780, 28500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'LHR'), (SELECT id FROM аеропорти WHERE код_іата = 'HKG'), 9630, 720, 26500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'CDG'), (SELECT id FROM аеропорти WHERE код_іата = 'HKG'), 9610, 720, 26500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'SIN'), 10380, 750, 27500.00),
((SELECT id FROM аеропорти WHERE код_іата = 'FRA'), (SELECT id FROM аеропорти WHERE код_іата = 'HKG'), 9230, 700, 25500.00); 