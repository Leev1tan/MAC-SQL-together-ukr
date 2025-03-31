-- Імпорт даних про аеропорти для бази даних "Авіакомпанія"

INSERT INTO аеропорти (код_іата, код_ікао, назва, місто, країна, часовий_пояс, кількість_терміналів, кількість_злітно_посадкових_смуг, географічні_координати) VALUES
-- Українські аеропорти
('KBP', 'UKBB', 'Міжнародний аеропорт «Бориспіль»', 'Київ', 'Україна', 'Europe/Kiev', 2, 2, '50.345000, 30.894722'),
('IEV', 'UKKK', 'Міжнародний аеропорт «Київ» імені Ігоря Сікорського', 'Київ', 'Україна', 'Europe/Kiev', 1, 1, '50.401944, 30.449444'),
('LWO', 'UKLL', 'Міжнародний аеропорт «Львів» імені Данила Галицького', 'Львів', 'Україна', 'Europe/Kiev', 1, 1, '49.8125, 23.956111'),
('ODS', 'UKOO', 'Міжнародний аеропорт «Одеса»', 'Одеса', 'Україна', 'Europe/Kiev', 1, 1, '46.426767, 30.676533'),
('DNK', 'UKDD', 'Міжнародний аеропорт «Дніпро»', 'Дніпро', 'Україна', 'Europe/Kiev', 1, 1, '48.357222, 35.100556'),
('HRK', 'UKHH', 'Міжнародний аеропорт «Харків»', 'Харків', 'Україна', 'Europe/Kiev', 1, 1, '49.924722, 36.290000'),
('ZAP', 'UKDE', 'Міжнародний аеропорт «Запоріжжя»', 'Запоріжжя', 'Україна', 'Europe/Kiev', 1, 1, '47.867222, 35.315833'),
('IFO', 'UKLI', 'Міжнародний аеропорт «Івано-Франківськ»', 'Івано-Франківськ', 'Україна', 'Europe/Kiev', 1, 1, '48.884167, 24.686111'),
('CWC', 'UKLN', 'Міжнародний аеропорт «Чернівці»', 'Чернівці', 'Україна', 'Europe/Kiev', 1, 1, '48.259167, 25.980833'),
('PLV', 'UKON', 'Міжнародний аеропорт «Полтава»', 'Полтава', 'Україна', 'Europe/Kiev', 1, 1, '49.584444, 34.397222'),

-- Європейські аеропорти
('FRA', 'EDDF', 'Frankfurt Airport', 'Франкфурт', 'Німеччина', 'Europe/Berlin', 2, 4, '50.033333, 8.570556'),
('CDG', 'LFPG', 'Charles de Gaulle Airport', 'Париж', 'Франція', 'Europe/Paris', 3, 4, '49.009722, 2.547778'),
('LHR', 'EGLL', 'Heathrow Airport', 'Лондон', 'Велика Британія', 'Europe/London', 5, 2, '51.4775, -0.461389'),
('AMS', 'EHAM', 'Amsterdam Airport Schiphol', 'Амстердам', 'Нідерланди', 'Europe/Amsterdam', 1, 6, '52.308056, 4.764167'),
('MAD', 'LEMD', 'Adolfo Suárez Madrid–Barajas Airport', 'Мадрид', 'Іспанія', 'Europe/Madrid', 4, 4, '40.472222, -3.560833'),
('FCO', 'LIRF', 'Leonardo da Vinci–Fiumicino Airport', 'Рим', 'Італія', 'Europe/Rome', 4, 4, '41.800278, 12.238889'),
('VIE', 'LOWW', 'Vienna International Airport', 'Відень', 'Австрія', 'Europe/Vienna', 3, 2, '48.110833, 16.570833'),
('WAW', 'EPWA', 'Warsaw Chopin Airport', 'Варшава', 'Польща', 'Europe/Warsaw', 2, 2, '52.165833, 20.967222'),
('IST', 'LTFM', 'Istanbul Airport', 'Стамбул', 'Туреччина', 'Europe/Istanbul', 5, 3, '41.275556, 28.751944'),
('BUD', 'LHBP', 'Budapest Ferenc Liszt International Airport', 'Будапешт', 'Угорщина', 'Europe/Budapest', 2, 2, '47.438889, 19.261944'),

-- Азіатські аеропорти
('DXB', 'OMDB', 'Dubai International Airport', 'Дубай', 'ОАЕ', 'Asia/Dubai', 3, 2, '25.252778, 55.364444'),
('SIN', 'WSSS', 'Singapore Changi Airport', 'Сінгапур', 'Сінгапур', 'Asia/Singapore', 4, 2, '1.359167, 103.989444'),
('HKG', 'VHHH', 'Hong Kong International Airport', 'Гонконг', 'Китай', 'Asia/Hong_Kong', 2, 2, '22.308889, 113.914444'),
('NRT', 'RJAA', 'Narita International Airport', 'Токіо', 'Японія', 'Asia/Tokyo', 3, 2, '35.765556, 140.385556'),
('ICN', 'RKSI', 'Incheon International Airport', 'Сеул', 'Південна Корея', 'Asia/Seoul', 2, 3, '37.4625, 126.439444'),
('BKK', 'VTBS', 'Suvarnabhumi Airport', 'Бангкок', 'Таїланд', 'Asia/Bangkok', 1, 2, '13.681389, 100.747222'),
('DEL', 'VIDP', 'Indira Gandhi International Airport', 'Делі', 'Індія', 'Asia/Kolkata', 3, 3, '28.5665, 77.103056'),
('BOM', 'VABB', 'Chhatrapati Shivaji Maharaj International Airport', 'Мумбаї', 'Індія', 'Asia/Kolkata', 2, 2, '19.088611, 72.867778'),
('PEK', 'ZBAA', 'Beijing Capital International Airport', 'Пекін', 'Китай', 'Asia/Shanghai', 3, 3, '40.080111, 116.584556'),
('PVG', 'ZSPD', 'Shanghai Pudong International Airport', 'Шанхай', 'Китай', 'Asia/Shanghai', 2, 4, '31.143333, 121.805278'),

-- Американські аеропорти
('JFK', 'KJFK', 'John F. Kennedy International Airport', 'Нью-Йорк', 'США', 'America/New_York', 6, 4, '40.639722, -73.778889'),
('LAX', 'KLAX', 'Los Angeles International Airport', 'Лос-Анджелес', 'США', 'America/Los_Angeles', 9, 4, '33.9425, -118.408056'),
('ORD', 'KORD', 'O\'Hare International Airport', 'Чикаго', 'США', 'America/Chicago', 4, 8, '41.978611, -87.904722'),
('ATL', 'KATL', 'Hartsfield–Jackson Atlanta International Airport', 'Атланта', 'США', 'America/New_York', 7, 5, '33.636667, -84.428056'),
('MIA', 'KMIA', 'Miami International Airport', 'Маямі', 'США', 'America/New_York', 3, 4, '25.793333, -80.290556'),
('YYZ', 'CYYZ', 'Toronto Pearson International Airport', 'Торонто', 'Канада', 'America/Toronto', 2, 5, '43.677222, -79.630556'),
('YVR', 'CYVR', 'Vancouver International Airport', 'Ванкувер', 'Канада', 'America/Vancouver', 3, 3, '49.194722, -123.183889'),
('YUL', 'CYUL', 'Montréal-Pierre Elliott Trudeau International Airport', 'Монреаль', 'Канада', 'America/Montreal', 1, 3, '45.470556, -73.740833'),
('GRU', 'SBGR', 'São Paulo–Guarulhos International Airport', 'Сан-Паулу', 'Бразилія', 'America/Sao_Paulo', 3, 2, '-23.435556, -46.473056'),
('MEX', 'MMMX', 'Mexico City International Airport', 'Мехіко', 'Мексика', 'America/Mexico_City', 2, 2, '19.436111, -99.072222'),

-- Африканські та австралійські аеропорти
('JNB', 'FAJS', 'O. R. Tambo International Airport', 'Йоганнесбург', 'ПАР', 'Africa/Johannesburg', 2, 2, '-26.133333, 28.25'),
('SYD', 'YSSY', 'Sydney Kingsford Smith Airport', 'Сідней', 'Австралія', 'Australia/Sydney', 3, 3, '-33.946111, 151.177222'),
('MEL', 'YMML', 'Melbourne Airport', 'Мельбурн', 'Австралія', 'Australia/Melbourne', 4, 2, '-37.673333, 144.843333'),
('AKL', 'NZAA', 'Auckland Airport', 'Окленд', 'Нова Зеландія', 'Pacific/Auckland', 2, 2, '-37.008056, 174.791667'),
('CAI', 'HECA', 'Cairo International Airport', 'Каїр', 'Єгипет', 'Africa/Cairo', 3, 3, '30.121944, 31.405556'),
('CPT', 'FACT', 'Cape Town International Airport', 'Кейптаун', 'ПАР', 'Africa/Johannesburg', 1, 2, '-33.969444, 18.597222'),
('CMN', 'GMMN', 'Mohammed V International Airport', 'Касабланка', 'Марокко', 'Africa/Casablanca', 2, 2, '33.367222, -7.589722'),
('LOS', 'DNMM', 'Murtala Muhammed International Airport', 'Лагос', 'Нігерія', 'Africa/Lagos', 2, 2, '6.577222, 3.321111'),
('NBO', 'HKJK', 'Jomo Kenyatta International Airport', 'Найробі', 'Кенія', 'Africa/Nairobi', 4, 1, '-1.319167, 36.927778'),
('ADD', 'HAAB', 'Addis Ababa Bole International Airport', 'Аддіс-Абеба', 'Ефіопія', 'Africa/Addis_Ababa', 2, 3, '8.977778, 38.799722'); 