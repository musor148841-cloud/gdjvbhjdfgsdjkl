# 💱 Currency Converter

**Author:** Манукян Айк

## 📝 Описание
Desktop приложение для конвертации валют с использованием реальных курсов из API. Поддерживает историю конвертаций, экспорт данных и удобный GUI интерфейс.

## 🔑 Как получить API-ключ

1. Перейдите на [ExchangeRate-API](https://app.exchangerate-api.com/sign-up)
2. Зарегистрируйтесь (бесплатный тариф: 1500 запросов/месяц)
3. Подтвердите email
4. Скопируйте API-ключ из панели управления (16 символов)
5. Вставьте ключ в файл `currency_converter.py`:
   ```python
   self.api_key = "ВАШ_КЛЮЧ"


   Установка
bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-username/currency-converter.git
cd currency-converter

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Запустите приложение
python currency_converter.py
