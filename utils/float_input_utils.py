# float_input_utils.py

def get_float_input(prompt):
    while True:
        try:
            value = input(prompt).replace(',', '.')
            return float(value)
        except ValueError:
            print("Некорректный ввод. Пожалуйста, введите число.")
